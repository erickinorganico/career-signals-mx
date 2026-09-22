# Revisión adversarial del paquete de planeación

Fecha: 2026-09-22. Revisor: `gpt-6-astra`, esfuerzo `high`.
Estado final: **PASS — planeación y especificaciones**, tras correcciones y
segunda revisión. Los ocho hallazgos documentales quedaron resueltos. No es una
aceptación del runtime, una auditoría de cifras reales ni el release analítico.

Se revisaron el mandato, alcance, PRD, plan, especificación, contratos,
arquitectura, metodología, catálogo/auditoría de fuentes, ADRs, riesgos,
validación, estado, README, visualización, orquestación y eficiencia. Las
referencias de línea siguientes identifican la primera versión revisada; la
resolución deberá citar el texto corregido porque las líneas pueden cambiar.

## Hallazgos iniciales — resueltos en la segunda revisión

| ID | Prioridad | Evidencia inicial | Problema y remedio |
|---|---|---|---|
| APR-001 | P1 | `docs/METHODOLOGY.md:35,56-62`; `docs/CONTRACT.md:9` | La fórmula de `female_share` usa población elegible del campo sin filtrar ocupadas; el contrato exige participación entre ocupadas. Definir un universo ocupado con sexo registrado válido para numerador y denominador, tratamiento de no respuesta y denominador cero. Distinguir sexo registrado de identidad de género. |
| APR-002 | P1 | `docs/source-research.json:299`; `docs/METHODOLOGY.md:151-157`; `data/catalog/sources.json:14-17` | La auditoría permite publicar cifras reales como REVIEW antes de varianza, pero la promoción exige varianza validada. Las notas del catálogo también dicen approved pese `approved=false`. Mantener cifras sin diseño/varianza fuera del release; REVIEW solo admite investigación interna en ese caso. Usar lenguaje de candidata no activada. |
| APR-003 | P1 | `docs/METHODOLOGY.md:78-80`; `docs/CONTRACT.md:26` | La excepción de bridge/versionado REVIEW podría permitir deltas automáticos tras una ruptura metodológica. Bloquear siempre esos deltas en v1; una armonización futura necesita contrato separado y validación, no el solo estado REVIEW. |
| APR-004 | P1 | `docs/ARCHITECTURE.md:144-155`; `docs/SPEC.md:77-95`; `docs/decisions/0005-current-failure-wins-over-historical-success.md:18-31` | Reemplazar individualmente current.json y report.md no es una transacción; un crash puede dejar un reporte antiguo visible. Además, el flujo exporta antes de render y promete ningún export ante un fallo posterior. Especificar un puntero autoritativo con commit atómico único, reporte raíz sin cifras vigentes propias, staging/manifest y recuperación fail-closed. Incluir fallos antes/después de commit y entre escrituras en validación. |
| APR-005 | P2 | `docs/SPEC.md:77,88-105`; `docs/CONTRACT.md:25` | Los enums no definen cómo se reducen estados de filas al quality/bundle ni distinguen estado público de ejecución. Fijar reglas para BLOCKED, REVIEW+UNKNOWN, todas UNKNOWN y synthetic; definir publishable por separado y usar execution_state para RUNNING/FAILED. |
| APR-006 | P2 | `docs/SPEC.md:100-105`; `docs/ARCHITECTURE.md:71-75` | Distintos/ordenados no define orden temporal seguro. Exigir fechas ISO válidas, start<=end, referencias resueltas y current.start>previous.end; bloquear periodos invertidos o solapados sin ordenar IDs arbitrarios. Mantener delta absoluto permitido y relativo null con base cero. |
| APR-007 | P2 | `docs/PRD.md:85-102`; `docs/VALIDATION-PLAN.md:24-41`; `docs/PLAN.md:91,218,259` | La primera matriz de validación asigna significados diferentes a los REQ canónicos; PLAN además menciona agent.schema en lugar de agent-run.schema y una matriz TRACEABILITY ausente. Alinear PRD→PLAN→SPEC→VALIDATION sin segundo catálogo de requisitos y usar rutas canónicas o declarar tareas futuras precisas. El integrador ya había detectado el mapa REQ al empezar esta revisión. |
| APR-008 | P2 | `docs/VISUALIZATION.md:3`; `docs/STATUS.md:21,73-78` | La visualización afirma que render_report genera salidas, mientras el estado registra el módulo ausente. Marcar expresamente el documento como comportamiento objetivo, no capacidad ejecutada. La falta de renderer no bloquea la entrega de planeación si permanece visible. |

## Aceptaciones y límites comprobados en la documentación

- El mandato distingue publicación autorizada del checkpoint documental/código
  de un release analítico validado. No hace falta una autorización nueva para
  publicar este paquete en el repositorio ya autorizado.
- El alcance excluye aplicación, frontend, backend y servicio. dbt es opcional;
  ninguna aceptación exige una aplicación ni datos reales para cerrar el piloto.
- El objetivo sintético de 54 combinaciones se distingue de las 9 filas del
  prototipo. Los tests parciales y la colección bloqueada se declaran como tales.
- Campo, ocupación, industria y vacante permanecen separados; nominal no se
  presenta como poder adquisitivo. La ENOE futura requiere diseño muestral,
  población, ponderación, varianza y precisión, sujetos a APR-001/002.
- Los candidatos con términos sin resolver no se activan por propuestas de
  agente. La captura de metadata y el hash no acreditan precisión estadística.
- El replay agentic determinista no se presenta como inferencia LLM autónoma.
  Laya `not applicable` se justifica por la ausencia de un caller repetido útil;
  no se afirma ahorro ni se introduce inferencia pagada.
- No se volvieron a auditar fuentes remotas ni se ejecutó el prototipo durante
  esta revisión. Sus resultados previos se evalúan como evidencia declarada en
  STATUS, no como checks nuevos del revisor.

## Segunda revisión y aceptación

Se volvieron a leer los textos corregidos; las referencias siguientes apuntan
a la versión aceptada de esta revisión, no a la versión inicial de los hallazgos.

| Hallazgo | Resolución verificada | Evidencia de cierre |
|---|---|---|
| APR-001 | Universo ocupado con sexo válido en ambos términos; sexo registrado distinto de identidad de género | `docs/METHODOLOGY.md:54-67` |
| APR-002 | Sin diseño/varianza, real permanece investigación interna no publicable; ENOE candidata no activada | `docs/METHODOLOGY.md:113-117`; `docs/source-research.json:299`; `data/catalog/sources.json:14-17` |
| APR-003 | Bridge/versionado no restaura deltas v1; armonización futura requiere serie nueva validada | `docs/METHODOLOGY.md:83-88` |
| APR-004 | Current es único commit; índice discrepante se rechaza; staging no publicable; receipt final write-once; recuperación distingue fallo y crash | `docs/CONTRACT.md:99-110,137-159`; `docs/ARCHITECTURE.md:148-168`; `docs/decisions/0005-current-failure-wins-over-historical-success.md:18-24`; `docs/VALIDATION-PLAN.md:54-65,87-114` |
| APR-005 | Tabla de reducción ordenada separa vacío, all UNKNOWN, REVIEW con valor, freshness y BLOCKED; estado de ejecución separado | `docs/SPEC.md:77-79,103-125`; `docs/CONTRACT.md:105-110`; `docs/VALIDATION-PLAN.md:33-36` |
| APR-006 | Orden por fechas ISO resueltas y no solapadas; firma target recibe periods_by_id y declara migración pendiente; base cero solo admite delta absoluto | `docs/SPEC.md:127-137`; `docs/CONTRACT.md:65-69`; `docs/VALIDATION-PLAN.md:35` |
| APR-007 | IDs canónicos preservados en PRD, PLAN, SPEC y VALIDATION; FK semánticas asignadas al quality gate; agent-run y matriz SPEC son rutas canónicas | `docs/PRD.md:86-103`; `docs/PLAN.md:91,220,261`; `docs/SPEC.md:29-48`; `docs/VALIDATION-PLAN.md:22-45` |
| APR-008 | Visualización declarada especificación objetivo con renderer ausente y demo sin verificar | `docs/VISUALIZATION.md:3-6` |

**Aceptación:** no quedan hallazgos abiertos que bloqueen el paquete de
planeación. El integrador puede cerrar M0 y publicar el paquete documental
después del chequeo final de enlaces, JSON, secretos/licencias y diff previsto
para este checkpoint. Esta revisión no exige ejecutar o completar el prototipo.

El PASS acepta coherencia documental y contratos implementables del alcance
actual. M1–M5, runtime, demo, estimaciones reales, adopción y efecto en usuarios
permanecen pendientes según sus propios gates. No certifica fuentes remotas,
licencias como asesoría legal, ausencia exhaustiva de secretos ni una ejecución
que el revisor no realizó. El checker documental y la publicación final deben
registrarse por el integrador con su evidencia propia.
