export AWS_PROFILE ?= poc
TF := terraform -chdir=infra

.PHONY: login deploy seed url destroy

login:  ## Inicia sesión en la cuenta del POC (abre el navegador)
	aws login --profile $(AWS_PROFILE) --region us-east-2

deploy:  ## Crea/actualiza toda la infraestructura
	$(TF) init -upgrade
	$(TF) apply

seed:  ## Sube los documentos de ejemplo (dispara la ingesta automáticamente)
	aws s3 sync sample-docs/ s3://$$($(TF) output -raw docs_bucket)/

url:  ## Muestra la URL de la app
	@$(TF) output -raw web_url; echo

destroy:  ## Borra todo lo creado
	$(TF) destroy
