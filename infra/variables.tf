variable "project" {
  description = "Prefijo para nombrar los recursos."
  type        = string
  default     = "doc-assistant"
}

variable "region" {
  description = "Región de AWS. Las cuentas de proyecto solo permiten crear recursos en la región asignada (Américas: us-east-2)."
  type        = string
  default     = "us-east-2"
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

variable "generation_model_id" {
  description = "Modelo que genera las respuestas. Se puede cambiar sin tocar el resto."
  type        = string
  default     = "amazon.nova-lite-v1:0"
}
