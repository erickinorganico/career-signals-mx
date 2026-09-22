# Contrato de interfaces y artefactos v1

Fecha: 2026-09-22 · Python 3.12+ · JSON `snake_case` · UTF-8.

Este contrato distingue **existente**, **faltante** y **target**. El checkout
auditado contiene schema de dataset/insight, fixture, quality, warehouse,
pipeline, scout y agentes parciales. `brujula/report.py` y
`contracts/agent-run.schema.json` faltan; el build completo no está demostrado.

## Dataset JSON — existente, sujeto a alineación

Raíz: `schema_version,id,label,mode,description,sources,dimensions,metrics,evidence,observations`.

- concept: `{id,label,description}`.
- geography: `{id,label}`.
- period: `{id,label,start,end}`, ISO y `start<=end`.
- bridge: `{id,from_type,from_id,to_type,to_id,method,confidence,status,evidence_refs}`;
  status siempre `REVIEW`.
- dimensions: `{fields,occupations,industries,geographies,periods,bridges}`.
- metric: `{id,label,unit,description,price_basis}`.
- units: `MXN/month|people|percent`; price: `nominal|not_applicable`.
- observation:
  `{id,concept_type,concept_id,geography_id,period_id,metric_id,value,source_id,population,methodology_id,unit,price_basis,sample_size,coefficient_variation,status,precision_note,evidence_refs,synthetic}`.

Status: `MEASURED|REVIEW|UNKNOWN|BLOCKED`. Grain unique:
concept type/id×geografía×periodo×métrica. UNKNOWN/BLOCKED no se convierten en
cero; sintético no nulo es REVIEW; refs resuelven; unit/basis coinciden con
métrica; evidence pertenece a source.

### Fuentes activas vs catálogo

Una source dentro del dataset está activa para ese dataset:
`{id,name,url,terms_url,license,authority,access_status,approved,checked_at,population,coverage,periodicity,methodology,notes}`.
No equivale a `data/catalog/sources.json`, que contiene candidatos. En fixture,
`approved=true` solo autoriza el fixture sintético.

Evidence: `{id,source_id,label,url,kind,note}`.

## Quality — existente, target uppercase

```json
{
  "status":"REVIEW",
  "publishable":true,
  "checks":[{"id":"schema","status":"PASS","message":"..."}],
  "row_statuses":{"observation_id":"REVIEW"},
  "freshness":{"status":"REVIEW","as_of":"2026-09-22","latest_period_end":"2025-12-31","age_days":265,"threshold_days":180,"message":"Synthetic fixture; illustrative"}
}
```

El target público usa los cuatro estados uppercase. La implementación auditada
aún devuelve estados lowercase/internos en algunas rutas; es deuda previa al E2E.
`quality.status`, `row_statuses` y `freshness.status` usan el enum público. En
cambio, `checks[*].status` es un veredicto diagnóstico interno
`PASS|FAIL|BLOCKED`; no representa el estado de una observación ni se expone
como clasificación estadística. Esta reutilización del nombre `status` se
mantiene por compatibilidad v1 y debe documentarse en consumidores.

## Comparisons — existente

`{previous_id,current_id,status,comparable,absolute_change,relative_change_pct,reasons,evidence_refs}`.
Si no comparable, deltas null. Status target: REVIEW para descripción sintética,
BLOCKED para incompatibilidad. No implica significancia estadística.

La firma existente `compare_observations(previous,current)` solo ve IDs. La
firma target es `compare_observations(previous,current,periods_by_id)` para
resolver `start/end` desde `dim_period` y exigir
`current.start>previous.end`. Este cambio de API obliga a migrar pipeline y
tests; observation no contiene fechas.

## Insights — schema existente

`{id,status,title,observation,interpretation,recommendation,evidence_refs,unknowns,synthetic}`.
Strict, evidence no vacía. Observation deriva de fila; interpretación y
recomendación no introducen números o causalidad nuevos.

## Agent run — target, schema faltante

Estructura raíz target:
`{mode:"deterministic_replay",publication_allowed,roles,insights}`. `roles`
contiene exactamente seis entradas y `insights` cumple el schema de insight.
Fragmento ilustrativo de una entrada de rol (no es un agent-run completo):

```json
{"id":"source_scout","label":"Source Scout","status":"REVIEW","read_only":true,"summary":"...","proposals":[{"action":"review_source","target_id":"...","status":"REVIEW","rationale":"..."}],"evidence_refs":[]}
```

Exactamente seis roles: source_scout, schema_mapper, data_quality_guardian,
insight_analyst, visualization_planner, publisher. Proposals nunca superan
REVIEW. `contracts/agent-run.schema.json` está planeado y falta.

## Catálogo candidato

Cada record conserva autoridad, URL, términos, acceso, población, cobertura,
periodicidad, método, fecha y decisión. Separa `monitor_allowed`,
`numeric_ingestion_allowed` y activación. ENOE es candidata priorizada con
`numeric_ingestion_allowed=false` en v1.

## Receipt

Mínimos:
`schema_version,run_id,status,build_status,input_name,input_sha256,adapter_version,started_at,completed_at,as_of,parameters,error`.
Éxito añade `observation_count,mode,warehouse`. Fallo admite hash null si no leyó
input y `error:{type,message}`. Nunca incluye secretos, headers o credenciales.
`status` es el estado público `MEASURED|REVIEW|UNKNOWN|BLOCKED`;
`build_status` es el estado de ejecución `RUNNING|SUCCEEDED|FAILED`. No se
intercambian ni se reducen con la misma regla.
El estado RUNNING vive en current/journal mutable. `receipt.json` es el recibo
final write-once y solo se crea con SUCCEEDED o FAILED; no se reescribe desde
RUNNING.

## Research bundle — target

`runs/<run_id>/bundle.json` contiene
`{schema_version,generated_at,run_id,status,publishable,dataset,quality,comparisons,insights,agent_run,receipt,catalog,reports}`.

Fallo: BLOCKED, publishable false, dataset null, insights vacíos, sin cifras
heredadas. Éxito sintético: REVIEW, publishable true y warning obligatorio.

## Reports — target, renderer faltante

`render_report(payload,output_dir)->{markdown:"report.md",html:"report.html",charts:[...]}`.
Documentos estáticos sin browser/servidor. HTML escapa payload, no scripts/red.
Cada gráfica tiene tabla alternativa y metadata.

## CLI y códigos de salida

| Comando | Output | Exit 0 | Exit 1 |
|---|---|---|---|
| build/demo | run bundle + current | publicable | BLOCKED/error |
| verify | verify.json | checks pasan | algún check falla |
| scout | metadata receipt | REVIEW/MEASURED metadata | BLOCKED |

MEASURED del scout solo significa metadata sin cambio según contrato; no permite
ingesta numérica.

## Filesystem y atomicidad

- `artifacts/raw/<sha256>.json`: create-exclusive.
- `artifacts/runs/<run_id>/`: histórico inmutable.
- `artifacts/current.json`: único commit canónico por replace atómico; apunta a
  un run completo exitoso o al fallo vigente.
- `artifacts/report.md`: pointer humano derivado; no es autoridad independiente.
- `artifacts/.build.lock`: escritor único.
- `manifest.json`: hashes relativos; receipt final se sella una vez.

Un consumidor verifica `current.json`, su status y hashes antes de abrir el
reporte. Si el índice humano `report.md` discrepa del puntero por un crash,
su enlace se rechaza; el consumidor puede resolver el run validado directamente
desde `current.json`. Un puntero inválido, RUNNING o BLOCKED falla cerrado.
Un fallo conserva runs previos, pero current apunta al fallo.

## Exports

CSV/Parquet preservan id, concepto, geo, periodo, métrica, valor/null, unidad,
base, status, source, población, synthetic, precisión y evidence refs. CSV
neutraliza prefijos `= + - @`. Los archivos pueden existir en staging antes de
un fallo posterior; hasta el commit de current no son exports publicables. Un
fallo los retiene solo como diagnóstico histórico y no los enlaza desde current.

## Extensión ENOE (M6)

No es contrato activo. Requiere source snapshot versionado y variables de diseño
para pesos/varianza. Claves CMPE no se inventan. Cambiar grain/estados exige
migración de schema, tests y ADR.
