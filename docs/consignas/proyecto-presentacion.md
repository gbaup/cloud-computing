# Proyecto Final — Electiva Cloud Computing

> Consigna "Proyecto: definición y presentación ante el grupo", copiada de la plataforma del curso (última modificación: 5 de octubre de 2026).

## 1. Objetivo del Proyecto Final

El proyecto final tiene como propósito que cada equipo explore e investigue un tema **no abordado en profundidad en el curso**, tomando como base los fundamentos estudiados (Principios Cloud, Servicios, IaC y Automatización).

El trabajo se defenderá mediante una **presentación oral de 15-20 minutos** (15 min de exposición + 5 min de preguntas) apoyada por material visual y, según la naturaleza del tema, una **Prueba de Concepto (PoC) o Análisis de Caso Práctico**.

El objetivo es compartir el conocimiento investigado con el resto del grupo, promoviendo el debate técnico y las conclusiones aplicadas a la ingeniería.

## 2. Modalidad y Entregables

- **Formato:** Grupal (2 a 3 integrantes).
- **Propuesta y Aprobación:** Envío previo de la ficha de tema en el foro para validación docente.
- **Entregables para la sesión final:**
  1. Presentación oral con apoyo visual (diapositivas / diagramas de arquitectura).
  2. Resumen Ejecutivo (Executive Summary): documento breve de 2 a 3 páginas con el marco teórico, comparativas, arquitectura y referencias bibliográficas utilizadas.
  3. Demostración Práctica (PoC o Caso de Estudio):
     - *Temas técnicos/arquitectónicos:* PoC funcional (se recomienda video de respaldo de 2 min o ejecución controlada).
     - *Temas de gobernanza/teóricos:* Análisis profundo de un Caso de Estudio real o Marco de Referencia aplicado.

## 3. Criterios para la Elección del Tema

El tema debe ser **innovador y acotado**. Áreas temáticas y ejemplos de enfoque acotado:

### 3.1 Proveedores Cloud y FinOps
- Análisis comparativo de servicios equivalentes (ej. AWS Cloud Run vs. GCP Cloud Run) bajo métricas de latencia, escalado y costo.
- Estrategias y herramientas de FinOps (ej. KubeCost, OpenCost) para la visibilidad de costos en clústeres de Kubernetes.
- Multi-cloud o híbrido: patrones de arquitectura, desafíos de conectividad y casos reales.

### 3.2 Cloud Native Computing Foundation (CNCF)
- Estudio enfocado de un proyecto graduado o incubado (ArgoCD, Prometheus, Envoy, OpenTelemetry, Cilium, etc.).
- Análisis práctico de un área del CNCF Landscape (Observabilidad, Service Mesh, Security & Compliance, Networking).
- Estándares de contenedores y portabilidad (OCI, runtimes como Containerd/Crio, WebAssembly en la nube).

### 3.3 Temas Teóricos, Protocolos y Gobernanza
- Evolución de arquitecturas Cloud Native e impacto en patrones de diseño de software.
- Service Level Agreements (SLA / SLO / SLI): métricas clave y mecanismos de compensación en la industria.
- Protocolos y estándares: S3 API compatibility, OAuth2 / OIDC en arquitecturas distribuidas, OpenStack.
- Marcos de gobernanza, compliance y soberanía de datos (NIST, ISO/IEC, GDPR, normativas locales y estrategias BYOK/HYOK).

### 3.4 Automatización, GitOps e IaC
- Comparativa práctica de herramientas IaC: Terraform/OpenTofu vs. Pulumi vs. CloudFormation/CDK.
- Flujos de trabajo GitOps avanzados (Push vs. Pull-based) con ArgoCD o Flux.
- CI/CD Cloud Native: pipelines serverless (Tekton, GitHub Actions runners dinámicos) e integración con seguridad (DevSecOps).

### 3.5 Seguridad y Gobernanza en la Nube
- Implementación de modelos Zero Trust en la capa de red e identidad en la nube.
- Postura de Seguridad Cloud (CSPM) y gestión de vulnerabilidades en tiempo de compilación vs. tiempo de ejecución.
- Gestión avanzada de Identidades y Accesos (IAM, Least Privilege, OIDC en Workloads).

### 3.6 Arquitecturas Avanzadas y Tendencias
- Serverless vs. Contenedores: análisis de *Cold Starts*, patrones de eventos y costo a escala.
- Edge Computing vs. Cloud Computing: procesamiento distribuido y reducción de latencia.
- Patrones de resiliencia y Chaos Engineering en entornos Cloud.
- AI Cloud & MLOps: infraestructura para el despliegue de LLMs y bases de datos vectoriales en la nube.

## 4. Proceso de Propuesta y Aprobación

Cada grupo deberá publicar en el foro **"Proyecto Final - Propuestas"** un mensaje estructurado con:

1. Integrantes del equipo
2. Tema elegido y categoría
3. Pregunta u Objetivo de Investigación: ¿qué problema o hipótesis busca responder el trabajo?
4. Alcance de la PoC o Caso de Estudio: breve descripción de la demostración o análisis práctico a realizar.

## 5. Rúbrica de Evaluación

| Criterio | Excelente (5) | Bueno (4) | Aceptable (3) | Insuficiente (1–2) |
|---|---|---|---|---|
| **Relevancia y Acotación** (20%) | Tema claramente vinculado al curso, innovador y con un alcance bien delimitado para el tiempo disponible. | Tema pertinente e innovador, aunque con un alcance ligeramente amplio. | Tema parcialmente relacionado o demasiado extenso/superficial. | Tema no relacionado, descontextualizado o repetitivo. |
| **Rigor Técnico y Documentación** (25%) | Dominio sólido de conceptos; terminología precisa; entrega de Resumen Ejecutivo bien estructurado y referenciado. | Buen manejo de conceptos con leves imprecisiones; documentación completa. | Conocimiento limitado; confusiones menores o falta de rigor en el resumen. | Conocimiento superficial; errores graves; sin soporte bibliográfico. |
| **Claridad y Comunicación Oral** (25%) | Explicación clara, fluida y ajustada al tiempo (10 min); excelente uso del material visual; responde preguntas con solvencia. | Explicación clara con leves fallas de tiempo o fluidez; responde la mayoría de las preguntas. | Explicación desordenada; exceso de texto en diapositivas; dificultades en las preguntas. | Presentación desorganizada; sobrepasa ampliamente el tiempo o no comunica las ideas. |
| **Aplicación Práctica** (PoC / Caso de Estudio) (20%) | PoC funcional/demostrativa o Caso de Estudio profundamente analizado; evidencia dominio técnico real. | PoC/Caso de Estudio en gran parte funcional o bien documentado con explicación suficiente. | Demostración limitada, parcialmente funcional o análisis de caso superficial. | PoC/Caso de Estudio ausente, no funcional o irrelevante. |
| **Originalidad y Análisis Crítico** (10%) | Aporta conclusiones propias, análisis de *trade-offs* (pros/contras) e ideas novedosas. | Presenta comparativas valiosas y análisis crítico adecuado. | Enfoque puramente descriptivo/comercial sin análisis crítico de la tecnología. | Copia directa de documentación oficial o tutoriales sin aporte del grupo. |

> Nota: la consigna indica 15 min de exposición, pero la rúbrica menciona "ajustada al tiempo (10 min)" y el checklist "10–15 minutos". Conviene confirmar con el docente.

## 6. Cronograma y Tiempos de Exposición

- Envío de propuesta de tema: desde la publicación del hilo en el foro.
- Presentaciones orales: penúltima y última sesión de clase.
- Tiempo por grupo: 15 a 20 minutos totales (15 min de exposición/demo + 5 min de preguntas).

---

# Checklist — Proyecto Final

## 1. Tema
- [ ] Tema no visto en clase
- [ ] Relacionado con conceptos del curso: cloud, servicios, IaC, automatización
- [ ] Innovador o con enfoque original

## 2. Preparación de la Presentación
- [ ] Presentación clara y estructurada
- [ ] Duración aproximada: 10–15 minutos
- [ ] Recursos visuales adecuados (diapositivas, diagramas, demos)
- [ ] Explicación coherente y comprensible
- [ ] Preparación para responder preguntas del grupo

## 3. Contenido
- [ ] Relevancia y acotación
- [ ] Rigor técnico y documentación
- [ ] Exposición clara
- [ ] Aplicación práctica / Caso de Estudio

## 4. Prueba de Concepto (PoC) — Opcional
- [ ] PoC funcional y demostrativa
- [ ] Coherente con el tema presentado
- [ ] Evidencia dominio técnico
- [ ] Explicación clara de cómo funciona

## 5. Autoevaluación antes de la exposición
- [ ] ¿Puedo explicar el tema sin leer diapositivas?
- [ ] ¿Tengo respuestas preparadas para posibles preguntas?
- [ ] ¿La PoC (si aplica) funciona correctamente y está lista para mostrar?
