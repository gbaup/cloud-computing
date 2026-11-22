# Guía de la plataforma Nimbus

> Documento ficticio creado para la demo del asistente.

Nimbus es la plataforma interna de Future Unicorn para desplegar y operar servicios. Corre sobre AWS y está administrada por el equipo de Plataforma.

## Entornos

| Entorno | Uso | Quién despliega | Datos |
|---|---|---|---|
| `dev` | Pruebas de cada equipo | Cualquier dev, automático en cada push | Sintéticos |
| `staging` | Validación antes de producción | Pipeline, al mergear a `main` | Copia anonimizada semanal |
| `prod` | Clientes | Pipeline, con aprobación manual | Reales |

## Proceso para pasar un cambio a producción

1. Abrir un Pull Request contra `main`. Requiere **2 aprobaciones**, una de ellas de alguien con rol "owner" del servicio.
2. El pipeline corre tests unitarios, análisis estático y escaneo de dependencias. Si alguno falla, no se puede mergear.
3. Al mergear, el cambio se despliega automáticamente a `staging`.
4. QA o el propio equipo valida en `staging` (smoke tests automáticos + prueba manual si aplica).
5. Para ir a `prod`, el líder técnico aprueba el paso manual en el pipeline. Los despliegues usan estrategia **canary**: 10% del tráfico durante 15 minutos y, si las métricas se mantienen sanas, 100%.
6. **Ventana de congelamiento**: no se despliega a producción los viernes después de las 15:00 ni durante la última semana de diciembre, salvo hotfixes aprobados por el on-call.

## Rollback

Cualquier persona del equipo dueño puede hacer rollback desde el pipeline ("Redeploy previous version"). El rollback no requiere aprobación. Después de un rollback se abre un ticket de seguimiento.

## Guardias (on-call)

- Cada equipo tiene una rotación semanal, de lunes 10:00 a lunes 10:00.
- La persona de guardia debe responder a una alerta en menos de **15 minutos** fuera de horario.
- La guardia se compensa con medio día libre por semana de guardia, más horas extra si hubo incidentes nocturnos.

## Severidades de incidentes

- **SEV1**: caída total o pérdida de datos. Se abre sala de guerra, se comunica a clientes en 30 minutos y se hace postmortem obligatorio.
- **SEV2**: degradación importante de una funcionalidad clave. Postmortem obligatorio.
- **SEV3**: problema menor con workaround. Se resuelve en horario laboral.

## Objetivos de nivel de servicio (SLO)

- Disponibilidad de la API pública: **99,5% mensual**.
- Latencia p95 de la API: menor a 400 ms.
- Si se consume más del 50% del presupuesto de error del mes, se congelan las features nuevas del servicio hasta recuperarse.

## Costos

Cada servicio tiene etiquetas `team` y `service` obligatorias. Los costos se revisan mensualmente por equipo; si un servicio crece más de un 20% mes a mes sin explicación, Plataforma abre un ticket al equipo dueño.
