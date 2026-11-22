# Bucket con los documentos fuente. Es el "data source" de la Knowledge Base.
resource "aws_s3_bucket" "docs" {
  bucket        = "${local.prefix}-docs-${local.account_id}"
  force_destroy = true
}

resource "aws_s3_bucket_public_access_block" "docs" {
  bucket                  = aws_s3_bucket.docs.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Permite que el navegador suba archivos directo a S3 con una URL prefirmada.
resource "aws_s3_bucket_cors_configuration" "docs" {
  bucket = aws_s3_bucket.docs.id

  cors_rule {
    allowed_methods = ["PUT"]
    allowed_origins = ["*"]
    allowed_headers = ["*"]
    max_age_seconds = 3000
  }
}

# Cada vez que se sube o borra un documento, S3 dispara la Lambda de ingesta.
resource "aws_s3_bucket_notification" "docs" {
  bucket = aws_s3_bucket.docs.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.ingest.arn
    events              = ["s3:ObjectCreated:*", "s3:ObjectRemoved:*"]
  }

  depends_on = [aws_lambda_permission.ingest_from_s3]
}

# Vector store: S3 Vectors (pago por uso, sin costo fijo como OpenSearch Serverless).
resource "aws_s3vectors_vector_bucket" "kb" {
  vector_bucket_name = "${local.prefix}-vectors-${local.account_id}"
}

resource "aws_s3vectors_index" "kb" {
  vector_bucket_name = aws_s3vectors_vector_bucket.kb.vector_bucket_name
  index_name         = "docs-index"
  data_type          = "float32"
  dimension          = var.embedding_dimensions
  distance_metric    = "cosine"

  # Bedrock guarda el texto del chunk como metadata; tiene que ser no-filtrable
  # porque supera el límite de tamaño de la metadata filtrable.
  metadata_configuration {
    non_filterable_metadata_keys = ["AMAZON_BEDROCK_TEXT", "AMAZON_BEDROCK_METADATA"]
  }
}
