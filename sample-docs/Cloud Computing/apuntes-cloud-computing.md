# Apuntes de Cloud Computing

## Definición (NIST)

Cloud computing es un modelo que permite acceso ubicuo, conveniente y bajo demanda, a través de la red, a un conjunto compartido de recursos de cómputo configurables (redes, servidores, almacenamiento, aplicaciones y servicios) que pueden aprovisionarse y liberarse rápidamente con mínimo esfuerzo de gestión o interacción con el proveedor.

### Cinco características esenciales

1. **Autoservicio bajo demanda**: el usuario aprovisiona recursos sin intervención humana del proveedor.
2. **Amplio acceso a la red**: los recursos se acceden por mecanismos estándar desde distintos dispositivos.
3. **Pool de recursos (multi-tenancy)**: los recursos físicos se comparten entre muchos clientes y se asignan dinámicamente.
4. **Elasticidad rápida**: la capacidad crece o se achica según la demanda, a veces automáticamente.
5. **Servicio medido**: el uso se mide y se cobra (pago por uso).

## Modelos de servicio

- **IaaS (Infraestructura como Servicio)**: el proveedor entrega máquinas virtuales, red y almacenamiento. El cliente administra el sistema operativo, el runtime y la aplicación. Ejemplos: Amazon EC2, Google Compute Engine.
- **PaaS (Plataforma como Servicio)**: el proveedor administra también el sistema operativo y el runtime; el cliente solo despliega su código y datos. Ejemplos: AWS Elastic Beanstalk, Google App Engine, Heroku.
- **SaaS (Software como Servicio)**: el cliente usa una aplicación terminada. Ejemplos: Gmail, Notion, Salesforce.
- **FaaS / Serverless**: el cliente sube funciones que se ejecutan ante eventos; se paga por invocación y tiempo de ejecución, y escala a cero. Ejemplos: AWS Lambda, Google Cloud Functions.

Regla práctica: cuanto más "arriba" en la pila, menos control y menos trabajo operativo para el cliente.

## Modelos de despliegue

- **Nube pública**: infraestructura del proveedor compartida por muchos clientes.
- **Nube privada**: infraestructura dedicada a una sola organización.
- **Nube híbrida**: combinación de pública y privada, con portabilidad de datos o aplicaciones.
- **Multi-cloud**: uso de varios proveedores públicos para evitar dependencia (lock-in) o aprovechar servicios específicos.

## Modelo de responsabilidad compartida

El proveedor es responsable de la seguridad **de** la nube (hardware, centros de datos, red física, hipervisor). El cliente es responsable de la seguridad **en** la nube (configuración, datos, identidades y permisos, cifrado). Cuanto más administrado es el servicio (SaaS > PaaS > IaaS), más responsabilidad asume el proveedor.

## Escalabilidad vs. elasticidad

- **Escalabilidad**: capacidad del sistema de manejar más carga agregando recursos. Puede ser vertical (máquina más grande) u horizontal (más máquinas).
- **Elasticidad**: capacidad de ajustar los recursos automáticamente y en poco tiempo, hacia arriba y hacia abajo, según la demanda real.

## Infraestructura como código (IaC)

Describir la infraestructura en archivos versionados (Terraform, CloudFormation, Pulumi) en lugar de configurarla a mano. Beneficios: reproducibilidad, revisión por pares, entornos idénticos y posibilidad de destruir y recrear todo con un comando.

## RAG (Retrieval-Augmented Generation)

Técnica para que un modelo de lenguaje responda con información propia sin reentrenarlo:

1. **Ingesta**: los documentos se dividen en fragmentos (chunks) y cada uno se convierte en un vector (embedding).
2. **Almacenamiento**: los vectores se guardan en una base vectorial.
3. **Recuperación**: la pregunta también se convierte en vector y se buscan los fragmentos más similares.
4. **Generación**: el modelo recibe la pregunta junto con los fragmentos recuperados y redacta la respuesta, idealmente citando las fuentes.
