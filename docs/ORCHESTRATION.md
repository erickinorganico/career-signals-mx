# Registro de orquestación

Fecha: 2026-09-22. Los modelos se eligieron en subtareas explícitas dentro de
Codex. No hubo selección automática a mitad de una tarea ni inferencia en
proveedores con facturación separada.

## Trabajo previo y corrección de alcance

| Fase | Agente/modelo | Esfuerzo | Responsabilidad | Resultado y aceptación |
|---|---|---|---|---|
| Auditoría inicial | `sol_plan_sources` / gpt-5.6-sol | medium | Fuentes, términos y primer plan | Auditoría utilizada como insumo; números OLA retirados de la publicación por licencia sin resolver |
| Prototipo de datos | `luna_data` / gpt-5.6-luna nativo | medium | Adaptador, schema, fixture, calidad y DuckDB | Parcial: 9 filas frente a 54 requeridas; subconjunto de 7 pruebas verde; no aceptado como cierre de datos |
| Primera visualización | `terra_frontend` / gpt-5.6-terra | medium | Interfaz inicial bajo el handoff anterior | Reemplazada por la corrección del titular: no se publica una app |
| Conversión a reportes | `terra_frontend` / gpt-5.6-terra | medium | Gráficas y reportes estáticos | Interrumpida durante correcciones; módulo de reportes ausente en el checkpoint; no aceptada como entrega terminada |
| Integración inicial | Principal / GPT-6 Astra | activo en la tarea principal | CLI, receipts, pipeline, pruebas de integración | Checkpoint incompleto preservado; E2E bloqueado |
| Acceso y publicación | Principal | tarea principal | Identidad GitHub, remoto y primer push | Cuenta personal autenticada; repositorio público y commit inicial `acace35` verificados |

La pausa solicitada para configurar GitHub detuvo implementación. El siguiente
pedido del titular priorizó planeación, specs, README, scope y publicación; los
agentes de esta etapa no retomaron features pendientes.

## Paquete de planeación

| Tarea | Modelo/esfuerzo despachado | Ownership | Estado de entrega |
|---|---|---|---|
| `sol_planning` | gpt-5.6-sol / medium | SCOPE, PRD, PLAN, ROADMAP, RISKS | Entregado y corregido tras revisión; 18 requisitos y 18 tareas |
| `sol_plan_sources` reutilizado | gpt-5.6-sol / medium | ARCHITECTURE, SPEC, CONTRACT, METHODOLOGY, GLOSSARY, ADRs | Entregado y corregido tras revisión; 18 specs y 5 ADRs |
| `luna_data` reutilizado | gpt-5.6-luna / medium | STATUS y VALIDATION-PLAN; auditoría sin reparaciones | Entregado: 7 tests datos/calidad y 11 scout; colección global bloqueada |
| `astra_docs_review` | gpt-6-astra / high | Revisión adversarial documental; PLANNING-REVIEW | PASS en segunda revisión; ocho hallazgos resueltos |
| Principal | modelo de la tarea principal | README ES/EN, mandato, índice, fuentes públicas, eficiencia, integración y publicación | Acepta M0; checkpoint `7c34e66` y documentos `a6da031` publicados; identidad, visibilidad y SHA remoto verificados |

El runtime no permitió abrir otra subtarea Terra al alcanzar el límite de
agentes. Se reutilizó el Sol disponible para los specs; no se afirma que Terra
haya participado en esta etapa documental. La revisión adversarial y las
resoluciones están en [PLANNING-REVIEW](PLANNING-REVIEW.md). El principal
alineó VALIDATION-PLAN con los IDs canónicos y cerró las aclaraciones sobre
crashes, staging, receipt final y el índice humano. La aceptación cubre la
planeación; los bloqueadores del prototipo permanecen en [STATUS](STATUS.md).
El [recibo M0](evidence/planning-receipt.json) registra el commit publicado y
el manifiesto SHA-256 del paquete aceptado. Sus hashes usan blobs Git para evitar
diferencias de finales de línea entre sistemas.

## Reglas para continuar

Cada tarea futura declara archivos propios, entradas, dependencias, modelo,
esfuerzo, evidencia de verificación y aceptación del principal. Un resultado
incorrecto retorna al owner adecuado; una contradicción metodológica o un fallo
difícil escala a Astra. Los subagentes no publican en GitHub por separado.

El release completo exige Sol para integración y Astra para revisión adversarial
de metodología, comparabilidad y afirmaciones. Una revisión documental no
acredita una revisión adversarial del software terminado. El recibo final debe
identificar commit, tests, artefactos/hashes, límites y publicación verificada.
