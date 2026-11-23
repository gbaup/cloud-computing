locals {
  embedding_model_arn  = "arn:aws:bedrock:${var.region}::foundation-model/${var.embedding_model_id}"
  generation_model_arn = "arn:aws:bedrock:${var.region}::foundation-model/${var.generation_model_id}"
}

# Rol que asume Bedrock para leer los docs, generar embeddings y escribir vectores.
resource "aws_iam_role" "kb" {
  name = "${local.prefix}-kb-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "bedrock.amazonaws.com" }
      Action    = "sts:AssumeRole"
      Condition = { StringEquals = { "aws:SourceAccount" = local.account_id } }
    }]
  })
}

resource "aws_iam_role_policy" "kb" {
  role = aws_iam_role.kb.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["bedrock:InvokeModel"]
        Resource = local.embedding_model_arn
      },
      {
        Effect   = "Allow"
        Action   = ["s3:ListBucket"]
        Resource = aws_s3_bucket.docs.arn
      },
      {
        Effect   = "Allow"
        Action   = ["s3:GetObject"]
        Resource = "${aws_s3_bucket.docs.arn}/*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3vectors:PutVectors",
          "s3vectors:GetVectors",
          "s3vectors:DeleteVectors",
          "s3vectors:QueryVectors",
          "s3vectors:GetIndex",
        ]
        Resource = aws_s3vectors_index.kb.index_arn
      },
    ]
  })
}

# IAM es eventualmente consistente: sin esta espera la creación de la KB a veces falla.
resource "time_sleep" "kb_role_propagation" {
  depends_on      = [aws_iam_role_policy.kb]
  create_duration = "15s"
}

resource "aws_bedrockagent_knowledge_base" "docs" {
  name     = "${local.prefix}-kb"
  role_arn = aws_iam_role.kb.arn

  knowledge_base_configuration {
    type = "VECTOR"
    vector_knowledge_base_configuration {
      embedding_model_arn = local.embedding_model_arn
      embedding_model_configuration {
        bedrock_embedding_model_configuration {
          dimensions          = var.embedding_dimensions
          embedding_data_type = "FLOAT32"
        }
      }
    }
  }

  storage_configuration {
    type = "S3_VECTORS"
    s3_vectors_configuration {
      index_arn = aws_s3vectors_index.kb.index_arn
    }
  }

  depends_on = [time_sleep.kb_role_propagation]
}

resource "aws_bedrockagent_data_source" "docs" {
  name              = "${local.prefix}-s3-docs"
  knowledge_base_id = aws_bedrockagent_knowledge_base.docs.id

  # RETAIN evita que el destroy falle intentando borrar vectores de un índice que ya no existe.
  data_deletion_policy = "RETAIN"

  data_source_configuration {
    type = "S3"
    s3_configuration {
      bucket_arn = aws_s3_bucket.docs.arn
    }
  }

  vector_ingestion_configuration {
    chunking_configuration {
      chunking_strategy = "FIXED_SIZE"
      fixed_size_chunking_configuration {
        max_tokens         = 300
        overlap_percentage = 20
      }
    }
  }
}
