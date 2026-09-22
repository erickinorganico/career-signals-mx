# Documentación de Brújula Laboral MX

El repositorio entrega en esta etapa un paquete de planeación y especificación.
El prototipo tiene partes incompletas; [STATUS](STATUS.md) es la referencia de
verificación y no debe sustituirse por una lectura optimista del plan.

| Necesidad | Documento | Qué decide o prueba |
|---|---|---|
| Entender el proyecto | [README ES](../README.md), [README EN](../README.en.md) | Propósito, entrada y límites actuales |
| Resolver autoridad | [PROJECT-CHARTER](PROJECT-CHARTER.md) | Mandato, publicación autorizada, precedencia |
| Delimitar la entrega | [SCOPE](SCOPE.md) | Dentro/fuera del MVP y fases posteriores |
| Entender la decisión del usuario | [PRD](PRD.md) | Preguntas, hipótesis y requisitos REQ |
| Implementar | [SPEC](SPEC.md), [CONTRACT](CONTRACT.md) | Comportamientos, schemas, interfaces y fallos |
| Entender el diseño | [ARCHITECTURE](ARCHITECTURE.md), [ADRs](decisions/README.md) | Flujo, responsabilidades, alternativas |
| Interpretar indicadores | [METHODOLOGY](METHODOLOGY.md), [GLOSSARY](GLOSSARY.md) | Universos, fórmulas, precisión y términos |
| Incorporar fuentes | [SOURCES](SOURCES.md), [catálogo](../data/catalog/sources.json) | Autoridad, términos, acceso y usos permitidos |
| Preparar gráficas | [VISUALIZATION](VISUALIZATION.md) | Contrato de reportes y metadatos |
| Ejecutar el trabajo | [PLAN](PLAN.md), [ROADMAP](ROADMAP.md) | Tareas, dependencias, hitos y expansión |
| Evitar fallos | [RISKS](RISKS.md), [VALIDATION-PLAN](VALIDATION-PLAN.md) | Riesgos, casos rojos y evidencias de cierre |
| Saber qué está probado | [STATUS](STATUS.md) | Resultados actuales, bloqueadores y límites |
| Revisar la planeación | [PLANNING-REVIEW](PLANNING-REVIEW.md) | Hallazgos adversariales y resolución, con alcance documental |
| Verificar la entrega | [Recibo M0](evidence/planning-receipt.json) | Commit remoto, hashes documentales, checks y límites de la entrega |
| Coordinar agentes | [ORCHESTRATION](ORCHESTRATION.md), [eficiencia](../PROJECT-EFFICIENCY.md) | Routing efectivo y condiciones para Laya |
| Contribuir | [CONTRIBUTING](../CONTRIBUTING.md) | Cambios acotados y verificación proporcional |
| Revisar licencias | [LICENSE](../LICENSE), [avisos](../THIRD_PARTY_NOTICES.md) | Autoría original, dependencias y atribución de fuentes |

Los archivos técnicos actuales viven en [brujula](../brujula),
[contracts](../contracts), [data](../data) y [tests](../tests). Su presencia no
demuestra que el flujo completo funcione. Las rutas futuras se indican como
código inline para no ofrecer enlaces a archivos inexistentes.

Validación documental local: `python scripts/check_docs.py` desde la raíz.
Comprueba enlaces locales, presencia de entregables, sintaxis JSON y patrones
de credenciales/rutas privadas. No verifica páginas externas ni sustituye la
revisión semántica, metodológica o una auditoría exhaustiva de secretos.
