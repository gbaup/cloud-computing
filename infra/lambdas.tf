data "archive_file" "backend" {
  type        = "zip"
  source_dir  = "${path.module}/../backend"
  output_path = "${path.module}/.build/backend.zip"
  excludes    = ["__pycache__"]
}

data "aws_iam_policy_document" "lambda_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

locals {
  lambda_env = {
    DOCS_BUCKET       = aws_s3_bucket.docs.id
    KNOWLEDGE_BASE_ID = aws_bedrockagent_knowledge_base.docs.id
    DATA_SOURCE_ID    = aws_bedrockagent_data_source.docs.data_source_id
    MODEL_ARN         = var.generation_model_arn
  }
}

# ---------- Lambda "api": responde preguntas, lista y sube documentos ----------

resource "aws_iam_role" "api" {
  name               = "${local.prefix}-api-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume.json
}

resource "aws_iam_role_policy_attachment" "api_logs" {
  role       = aws_iam_role.api.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "api" {
  role = aws_iam_role.api.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "bedrock:Retrieve",
          "bedrock:StartIngestionJob",
          "bedrock:ListIngestionJobs",
        ]
        Resource = aws_bedrockagent_knowledge_base.docs.arn
      },
      {
        Effect = "Allow"
        # RetrieveAndGenerate no admite permisos a nivel de recurso.
        Action   = ["bedrock:RetrieveAndGenerate", "bedrock:InvokeModel", "bedrock:GetInferenceProfile"]
        Resource = "*"
      },
      {
        Effect   = "Allow"
        Action   = ["s3:ListBucket"]
        Resource = aws_s3_bucket.docs.arn
      },
      {
        Effect   = "Allow"
        Action   = ["s3:PutObject", "s3:GetObject"]
        Resource = "${aws_s3_bucket.docs.arn}/*"
      },
    ]
  })
}

resource "aws_lambda_function" "api" {
  function_name    = "${local.prefix}-api"
  role             = aws_iam_role.api.arn
  runtime          = "python3.13"
  handler          = "api.handler"
  filename         = data.archive_file.backend.output_path
  source_code_hash = data.archive_file.backend.output_base64sha256
  timeout          = 30
  memory_size      = 256

  environment {
    variables = local.lambda_env
  }
}

# ---------- Lambda "ingest": sincroniza la KB cuando cambia el bucket ----------

resource "aws_iam_role" "ingest" {
  name               = "${local.prefix}-ingest-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume.json
}

resource "aws_iam_role_policy_attachment" "ingest_logs" {
  role       = aws_iam_role.ingest.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "ingest" {
  role = aws_iam_role.ingest.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["bedrock:StartIngestionJob"]
      Resource = aws_bedrockagent_knowledge_base.docs.arn
    }]
  })
}

resource "aws_lambda_function" "ingest" {
  function_name    = "${local.prefix}-ingest"
  role             = aws_iam_role.ingest.arn
  runtime          = "python3.13"
  handler          = "ingest.handler"
  filename         = data.archive_file.backend.output_path
  source_code_hash = data.archive_file.backend.output_base64sha256
  timeout          = 15

  environment {
    variables = local.lambda_env
  }
}

resource "aws_lambda_permission" "ingest_from_s3" {
  statement_id  = "AllowS3Invoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ingest.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.docs.arn
}
