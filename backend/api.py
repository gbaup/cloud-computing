"""API del asistente: preguntas (RAG), listado y subida de documentos, estado de indexación."""

import json
import os
import re
import unicodedata

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

DOCS_BUCKET = os.environ["DOCS_BUCKET"]
KNOWLEDGE_BASE_ID = os.environ["KNOWLEDGE_BASE_ID"]
DATA_SOURCE_ID = os.environ["DATA_SOURCE_ID"]
MODEL_ARN = os.environ["MODEL_ARN"]

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md", ".html", ".csv", ".doc", ".docx", ".xls", ".xlsx"}
METADATA_SUFFIX = ".metadata.json"
ALL_SUBJECTS = "__todas__"
NOT_FOUND_ANSWER = "No encontré información sobre eso en los documentos cargados."

# Endpoint regional: con el global, las URLs prefirmadas responden 307 y el navegador no sigue el redirect.
REGION = os.environ["AWS_REGION"]
s3 = boto3.client(
    "s3",
    endpoint_url=f"https://s3.{REGION}.amazonaws.com",
    config=Config(signature_version="s3v4", s3={"addressing_style": "virtual"}),
)
agent = boto3.client("bedrock-agent")
agent_runtime = boto3.client("bedrock-agent-runtime")
bedrock_runtime = boto3.client("bedrock-runtime")

PROMPT_TEMPLATE = """Sos un asistente que responde preguntas usando únicamente los documentos del usuario.
Respondé en el mismo idioma de la pregunta, de forma clara y concisa.
Si la información no está en los resultados de búsqueda, decí que no la encontraste en los documentos; no inventes.

Resultados de búsqueda:
$search_results$

$output_format_instructions$"""


def handler(event, _context):
    route = f"{event['requestContext']['http']['method']} {event['rawPath']}"
    body = json.loads(event.get("body") or "{}")

    try:
        if route == "POST /ask":
            return respond(200, ask(body))
        if route == "GET /documents":
            return respond(200, list_documents())
        if route == "POST /upload-url":
            return respond(200, upload_url(body))
        if route == "GET /status":
            return respond(200, ingestion_status())
        if route == "POST /sync":
            return respond(200, start_sync())
        return respond(404, {"error": "Ruta no encontrada"})
    except ValueError as e:
        return respond(400, {"error": str(e)})
    except ClientError as e:
        print(f"AWS error on {route}: {e}")
        return respond(502, {"error": e.response["Error"]["Message"]})


def ask(body):
    question = (body.get("question") or "").strip()
    if not question:
        raise ValueError("Falta la pregunta")

    # Materia a usar: la que nombra la pregunta, si no la que el usuario ya eligió.
    # ALL_SUBJECTS significa "buscar en todas" sin volver a preguntar.
    subjects = list_subjects()
    subject = mentioned_subject(question, subjects) or body.get("materia")
    if not subject and len(subjects) > 1 and depends_on_subject(question, subjects):
        return {
            "clarify": {
                "message": "Eso cambia según la materia. ¿A cuál te referís?",
                "options": subjects,
            }
        }
    if subject == ALL_SUBJECTS:
        subject = None

    vector_search = {"numberOfResults": 6}
    if subject:
        vector_search["filter"] = {"equals": {"key": "materia", "value": subject}}

    request = {
        "input": {"text": question},
        "retrieveAndGenerateConfiguration": {
            "type": "KNOWLEDGE_BASE",
            "knowledgeBaseConfiguration": {
                "knowledgeBaseId": KNOWLEDGE_BASE_ID,
                "modelArn": MODEL_ARN,
                "retrievalConfiguration": {"vectorSearchConfiguration": vector_search},
                "generationConfiguration": {"promptTemplate": {"textPromptTemplate": PROMPT_TEMPLATE}},
            },
        },
    }
    # Bedrock guarda el historial de la conversación del lado del servidor.
    if body.get("sessionId"):
        request["sessionId"] = body["sessionId"]

    try:
        result = agent_runtime.retrieve_and_generate(**request)
    except ClientError as e:
        if "sessionId" not in request or e.response["Error"]["Code"] != "ValidationException":
            raise
        # La sesión expiró: arrancamos una nueva.
        del request["sessionId"]
        result = agent_runtime.retrieve_and_generate(**request)

    answer, sources = attach_citations(result)
    # Sin ninguna cita la respuesta no se apoya en los documentos: a veces el modelo
    # devuelve texto sin sentido, así que lo decimos explícitamente.
    if not sources:
        answer = NOT_FOUND_ANSWER
    return {"answer": answer, "sources": sources, "sessionId": result["sessionId"], "materia": subject}


def depends_on_subject(question, subjects):
    """Le pregunta al modelo si la respuesta cambia según la materia (reglas del curso, fechas, etc.).

    Comparar scores de la búsqueda no alcanza: los embeddings no separan bien
    "¿cómo se aprueba?" entre dos syllabus parecidos. Las preguntas conceptuales
    no necesitan aclaración porque la búsqueda ya encuentra el contenido correcto.
    """
    prompt = (
        f"Materias cargadas: {', '.join(subjects)}.\n"
        f"Pregunta del estudiante: {question}\n\n"
        "¿La respuesta depende de qué materia sea (por ejemplo: cómo se aprueba, evaluaciones, "
        "parciales, fechas, entregas, asistencia, docentes, horarios, bibliografía) y la pregunta "
        "no indica la materia? Si es una pregunta sobre un concepto o tema, respondé NO.\n"
        "Respondé solo SI o NO."
    )
    response = bedrock_runtime.converse(
        modelId=MODEL_ARN,
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        inferenceConfig={"temperature": 0, "maxTokens": 5},
    )
    answer = response["output"]["message"]["content"][0]["text"]
    return normalize(answer).strip().startswith("si")


def list_subjects():
    response = s3.list_objects_v2(Bucket=DOCS_BUCKET, Delimiter="/")
    return [p["Prefix"].rstrip("/") for p in response.get("CommonPrefixes", [])]


def mentioned_subject(question, subjects):
    """Detecta si la pregunta nombra una materia (ignora mayúsculas y tildes)."""
    normalized = normalize(question)
    for subject in sorted(subjects, key=len, reverse=True):
        if normalize(subject) in normalized:
            return subject
    return None


def normalize(text):
    text = unicodedata.normalize("NFKD", text.lower())
    return "".join(c for c in text if not unicodedata.combining(c))


def attach_citations(result):
    """Inserta marcadores ⟦n⟧ en el texto y devuelve la lista de fuentes numeradas."""
    text = result["output"]["text"]
    sources, index_by_key = [], {}
    out, cursor = [], 0

    for citation in result.get("citations", []):
        markers = []
        for ref in citation.get("retrievedReferences", []):
            uri = ref.get("location", {}).get("s3Location", {}).get("uri", "")
            snippet = ref.get("content", {}).get("text", "")
            key = (uri, snippet)
            if key not in index_by_key:
                sources.append({
                    "n": len(sources) + 1,
                    "file": uri.rsplit("/", 1)[-1],
                    "materia": ref.get("metadata", {}).get("materia"),
                    "snippet": snippet,
                })
                index_by_key[key] = len(sources)
            if index_by_key[key] not in markers:
                markers.append(index_by_key[key])
        if not markers:
            continue

        # Ubicamos el fragmento citado en el texto original para no perder saltos de línea.
        part = citation["generatedResponsePart"]["textResponsePart"]["text"].rstrip()
        found = text.find(part, cursor)
        if found < 0:
            continue
        insert_at = found + len(part)
        out.append(text[cursor:insert_at])
        out.append("".join(f"⟦{n}⟧" for n in markers))
        cursor = insert_at

    out.append(text[cursor:])
    return "".join(out), sources


def list_documents():
    """Documentos agrupables por materia: la materia es la "carpeta" del objeto en S3."""
    docs = []
    for page in s3.get_paginator("list_objects_v2").paginate(Bucket=DOCS_BUCKET):
        for obj in page.get("Contents", []):
            if obj["Key"].endswith(METADATA_SUFFIX):
                continue
            subject, _, name = obj["Key"].rpartition("/")
            docs.append({
                "key": obj["Key"],
                "name": name,
                "materia": subject or None,
                "size": obj["Size"],
                "lastModified": obj["LastModified"].isoformat(),
            })
    return {"documents": sorted(docs, key=lambda d: d["lastModified"], reverse=True)}


def upload_url(body):
    filename = os.path.basename(body.get("filename") or "")
    filename = re.sub(r"[^\w.\- ]", "_", filename)
    if os.path.splitext(filename)[1].lower() not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Formato no soportado. Usá: {', '.join(sorted(ALLOWED_EXTENSIONS))}")

    subject = re.sub(r"\s+", " ", (body.get("materia") or "").replace("/", " ")).strip()[:60]
    if not subject:
        raise ValueError("Indicá a qué materia pertenece el documento")
    key = f"{subject}/{filename}"

    # Archivo de metadata que Bedrock asocia al documento: permite filtrar la búsqueda por materia.
    s3.put_object(
        Bucket=DOCS_BUCKET,
        Key=key + METADATA_SUFFIX,
        Body=json.dumps({"metadataAttributes": {"materia": subject}}, ensure_ascii=False),
        ContentType="application/json",
    )

    content_type = body.get("contentType") or "application/octet-stream"
    url = s3.generate_presigned_url(
        "put_object",
        Params={"Bucket": DOCS_BUCKET, "Key": key, "ContentType": content_type},
        ExpiresIn=300,
    )
    return {"url": url, "key": key, "contentType": content_type}


def ingestion_status():
    jobs = agent.list_ingestion_jobs(
        knowledgeBaseId=KNOWLEDGE_BASE_ID,
        dataSourceId=DATA_SOURCE_ID,
        sortBy={"attribute": "STARTED_AT", "order": "DESCENDING"},
        maxResults=1,
    )["ingestionJobSummaries"]
    if not jobs:
        return {"status": "NEVER_RUN"}
    job = jobs[0]
    return {
        "status": job["status"],
        "startedAt": job["startedAt"].isoformat(),
        "statistics": job.get("statistics", {}),
    }


def start_sync():
    try:
        job = agent.start_ingestion_job(knowledgeBaseId=KNOWLEDGE_BASE_ID, dataSourceId=DATA_SOURCE_ID)
        return {"status": job["ingestionJob"]["status"]}
    except ClientError as e:
        if e.response["Error"]["Code"] == "ConflictException":
            return {"status": "IN_PROGRESS"}
        raise


def respond(status, payload):
    return {
        "statusCode": status,
        "headers": {"content-type": "application/json"},
        "body": json.dumps(payload, ensure_ascii=False, default=str),
    }
