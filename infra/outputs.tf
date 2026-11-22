output "web_url" {
  description = "URL pública de la app."
  value       = "https://${aws_cloudfront_distribution.web.domain_name}"
}

output "api_url" {
  value = aws_apigatewayv2_api.http.api_endpoint
}

output "docs_bucket" {
  value = aws_s3_bucket.docs.id
}

output "knowledge_base_id" {
  value = aws_bedrockagent_knowledge_base.docs.id
}

output "data_source_id" {
  value = aws_bedrockagent_data_source.docs.data_source_id
}
