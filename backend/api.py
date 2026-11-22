"""API del asistente: preguntas (RAG), listado y subida de documentos, estado de indexación."""

import json
import os
import re

import boto3
from botocore.exceptions import ClientError

DOCS_BUCKET = os.environ["DOCS_BUCKET"]
KNOWLEDGE_BASE_ID = os.environ["KNOWLEDGE_BASE_ID"]
DATA_SOURCE_ID = os.environ["DATA_SOURCE_ID"]
MODEL_ARN = os.environ["MODEL_ARN"]

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md", ".html", ".csv", ".doc", ".docx", ".xls", ".xlsx"}

s3 = boto3.client("s3")
agent = boto3.client("bedrock-agent")
agent_runtime = boto3.client("bedrock-agent-runtime")

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

    request = {
        "input": {"text": question},
        "retrieveAndGenerateConfiguration": {
            "type": "KNOWLEDGE_BASE",
            "knowledgeBaseConfiguration": {
                "knowledgeBaseId": KNOWLEDGE_BASE_ID,
                "modelArn": MODEL_ARN,
                "retrievalConfiguration": {"vectorSearchConfiguration": {"numberOfResults": 6}},
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
    return {"answer": answer, "sources": sources, "sessionId": result["sessionId"]}


def attach_citations(result):
    """Inserta marcadores ⟦n⟧ en el texto y devuelve la lista de fuentes numeradas."""
    sources, index_by_key, parts = [], {}, []

    for citation in result.get("citations", []):
        parts.append(citation["generatedResponsePart"]["textResponsePart"]["text"])
        markers = []
        for ref in citation.get("retrievedReferences", []):
            uri = ref.get("location", {}).get("s3Location", {}).get("uri", "")
            snippet = ref.get("content", {}).get("text", "")
            key = (uri, snippet)
            if key not in index_by_key:
                sources.append({"n": len(sources) + 1, "file": uri.rsplit("/", 1)[-1], "snippet": snippet})
                index_by_key[key] = len(sources)
            if index_by_key[key] not in markers:
                markers.append(index_by_key[key])
        parts.append("".join(f"⟦{n}⟧" for n in markers))

    text = result["output"]["text"]
    if not sources:
        return text, []

    # Texto que quedó después de la última cita.
    last = result["citations"][-1]["generatedResponsePart"]["textResponsePart"]["text"]
    tail_start = text.rfind(last)
    if tail_start >= 0:
        parts.append(text[tail_start + len(last):])
    return "".join(parts), sources


def list_documents():
    response = s3.list_objects_v2(Bucket=DOCS_BUCKET)
    docs = [
        {"name": obj["Key"], "size": obj["Size"], "lastModified": obj["LastModified"].isoformat()}
        for obj in response.get("Contents", [])
    ]
    return {"documents": sorted(docs, key=lambda d: d["lastModified"], reverse=True)}


def upload_url(body):
    filename = os.path.basename(body.get("filename") or "")
    filename = re.sub(r"[^\w.\- ]", "_", filename)
    if os.path.splitext(filename)[1].lower() not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Formato no soportado. Usá: {', '.join(sorted(ALLOWED_EXTENSIONS))}")

    content_type = body.get("contentType") or "application/octet-stream"
    url = s3.generate_presigned_url(
        "put_object",
        Params={"Bucket": DOCS_BUCKET, "Key": filename, "ContentType": content_type},
        ExpiresIn=300,
    )
    return {"url": url, "key": filename, "contentType": content_type}


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
