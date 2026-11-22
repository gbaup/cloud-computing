"""Se dispara con cada cambio en el bucket de documentos y re-sincroniza la Knowledge Base."""

import os

import boto3
from botocore.exceptions import ClientError

agent = boto3.client("bedrock-agent")


def handler(event, _context):
    changed = [r["s3"]["object"]["key"] for r in event.get("Records", [])]
    print(f"Documentos modificados: {changed}")

    try:
        job = agent.start_ingestion_job(
            knowledgeBaseId=os.environ["KNOWLEDGE_BASE_ID"],
            dataSourceId=os.environ["DATA_SOURCE_ID"],
        )
        print(f"Ingesta iniciada: {job['ingestionJob']['ingestionJobId']}")
    except ClientError as e:
        if e.response["Error"]["Code"] != "ConflictException":
            raise
        # Ya hay una ingesta corriendo. Fallamos a propósito para que Lambda reintente
        # (invocación asíncrona) y el documento nuevo entre en la próxima sincronización.
        raise RuntimeError("Ingesta en curso, se reintenta más tarde") from e
