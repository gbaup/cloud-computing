"""Diagrama de arquitectura como código.

Genera docs/arquitectura.png con los íconos oficiales de AWS:
    make diagram
"""

from pathlib import Path

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.compute import Lambda
from diagrams.aws.management import Cloudwatch
from diagrams.aws.ml import Bedrock
from diagrams.aws.network import APIGateway, CloudFront
from diagrams.aws.security import IAMRole
from diagrams.aws.storage import SimpleStorageServiceS3Bucket
from diagrams.onprem.client import Users
from diagrams.onprem.iac import Terraform

QUERY = "#3d4fd6"  # flujo de consulta
INGEST = "#d9822b"  # flujo de ingesta
STATIC = "#7a7a7a"  # sitio estático

graph_attr = {"fontsize": "22", "pad": "0.6", "nodesep": "0.7", "ranksep": "1.1", "fontname": "Helvetica", "splines": "spline"}
node_attr = {"fontsize": "12", "fontname": "Helvetica"}
edge_attr = {"fontsize": "11", "fontname": "Helvetica"}


def flow(color, label, **kwargs):
    return Edge(color=color, label=label, fontcolor=color, penwidth="1.8", **kwargs)


with Diagram(
    "Cuaderno: asistente de estudio con RAG sobre AWS",
    filename=str(Path(__file__).with_name("arquitectura")),
    outformat="png",
    direction="LR",
    show=False,
    graph_attr=graph_attr,
    node_attr=node_attr,
    edge_attr=edge_attr,
):
    user = Users("Estudiante\n(navegador)")

    with Cluster("AWS Cloud"):
        cdn = CloudFront("CloudFront\n(CDN + HTTPS)")

        with Cluster("Región us-east-2"):
            web = SimpleStorageServiceS3Bucket("S3 · sitio estático\nindex.html + config.js")

            with Cluster("API serverless"):
                api_gw = APIGateway("API Gateway\nHTTP API")
                api_fn = Lambda("Lambda api\n/ask · /upload-url\n/documents · /status")

            with Cluster("Ingesta orientada a eventos"):
                docs = SimpleStorageServiceS3Bucket("S3 · documentos\n<materia>/archivo.pdf\n+ .metadata.json")
                ingest_fn = Lambda("Lambda ingest")

            with Cluster("Amazon Bedrock (servicios administrados)"):
                kb = Bedrock("Knowledge Base\nchunking + búsqueda\nfiltrada por materia")
                titan = Bedrock("Titan Embeddings v2\n(vectores)")
                nova = Bedrock("Nova Lite\n(generación + clasificación)")
                vectors = SimpleStorageServiceS3Bucket("S3 Vectors\níndice vectorial")

        with Cluster("Transversal"):
            iam = IAMRole("IAM\nun rol por componente")
            logs = Cloudwatch("CloudWatch\nlogs")
            iac = Terraform("Terraform\n(todo como código)")

    # Sitio estático
    user >> flow(STATIC, "HTTPS") >> cdn >> flow(STATIC, "OAC") >> web

    # Consulta
    user >> flow(QUERY, "1. pregunta") >> api_gw >> flow(QUERY, "2") >> api_fn
    api_fn >> flow(QUERY, "3. ¿depende de la materia?") >> nova
    api_fn >> flow(QUERY, "4. RetrieveAndGenerate") >> kb
    kb >> flow(QUERY, "5. búsqueda") >> vectors
    kb >> flow(QUERY, "6. respuesta con citas") >> nova

    # Ingesta
    user >> flow(INGEST, "a. PUT con URL prefirmada") >> docs
    docs >> flow(INGEST, "b. evento S3") >> ingest_fn
    ingest_fn >> flow(INGEST, "c. StartIngestionJob") >> kb
    kb >> flow(INGEST, "d. embeddings") >> titan
    kb >> flow(INGEST, "e. guarda vectores") >> vectors

    # Transversal (sin flechas: aplica a todos los componentes)
    iac - Edge(style="invis") - iam - Edge(style="invis") - logs
