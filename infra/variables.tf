variable "project" {
  description = "Prefijo para nombrar los recursos."
  type        = string
  default     = "doc-assistant"
}

variable "region" {
  description = "Región de AWS (us-east-1 tiene más modelos de Bedrock y S3 Vectors)."
  type        = string
  default     = "us-east-1"
}

variable "embedding_model_id" {
  description = "Modelo de embeddings usado por la Knowledge Base."
  type        = string
  default     = "amazon.titan-embed-text-v2:0"
}

variable "embedding_dimensions" {
  description = "Dimensión de los vectores (debe coincidir con el modelo de embeddings)."
  type        = number
  default     = 1024
}

variable "generation_model_arn" {
  description = "Modelo o inference profile que genera las respuestas. Se puede cambiar sin tocar el resto."
  type        = string
  default     = "arn:aws:bedrock:us-east-1::foundation-model/amazon.nova-lite-v1:0"
}
