# Especificación implementable

Versión: 1.0 · Fecha: 2026-09-22 · Estado: implementado y verificado en el MVP sintético 0.1.0.

Esta especificación traduce REQ-001..REQ-018 a contratos verificables. La matriz
señala implementación local y evidencia disponible; no declara por sí sola un
release final.

## Interfaces públicas

```text
python -m brujula build [--input PATH] [--output DIR] [--as-of YYYY-MM-DD]
python -m brujula demo  [--input PATH] [--output DIR] [--as-of YYYY-MM-DD]
python -m brujula verify
python -m brujula scout [--source SOURCE_ID] [--output DIR]
python -m brujula report --output DIR --format html|markdown
```

- `build` y `demo` son aliases del flujo analítico; exit 0 solo si el bundle es
  publicable, exit 1 si queda `BLOCKED`.
- input por defecto: `data/fixtures/pilot.json`.
- output por defecto: `artifacts/`.
- `--as-of` controla freshness, no reemplaza timestamps de run.
- `verify` ejecuta tests offline y escribe `artifacts/verification/verify.json`.
- `scout` es opt-in, restringido a origen allowlisted y solo captura metadata;
  nunca activa fuente ni publica cifras.

## Matriz de requisitos

| SPEC | REQ | Contrato | Estado auditado | Evidencia de aceptación |
|---|---|---|---|---|
| SPEC-001 | REQ-001 | Catálogo candidato separado de fuentes activas | Verificado | `data/catalog/sources.json`, `brujula/scout.py`, `tests/test_scout.py` |
| SPEC-002 | REQ-002 | Schemas versionados, strict y sin campos extra | Verificado | dataset/insight/agent-run/run pasan positivos y rechazan negativos; `tests/test_data.py`, `tests/test_agents.py`, `tests/test_pipeline.py` |
| SPEC-003 | REQ-003 | Slice 3 campos×3 periodos×2 geos×3 métricas | Verificado | 54 grains, con nulos/estado explícitos; `tests/test_data.py` |
| SPEC-004 | REQ-004 | Dimensiones separadas y bridges `REVIEW` | Verificado | `tests/test_data.py`, `tests/test_warehouse.py` |
| SPEC-005 | REQ-005 | `null` no es cero; estados públicos uppercase | Verificado | `tests/test_quality.py`, `tests/test_report.py` |
| SPEC-006 | REQ-006 | Gate de schema, refs, grain, rangos y coherencia | Verificado | `tests/test_data.py`, `tests/test_quality.py` |
| SPEC-007 | REQ-007 | Freshness usa fin del periodo de negocio | Verificado | `tests/test_quality.py` |
| SPEC-008 | REQ-008 | Delta solo entre observaciones compatibles | Verificado | `tests/test_quality.py`, `tests/test_pipeline.py` |
| SPEC-009 | REQ-009 | Raw content-addressed y receipt por intento | Verificado | `tests/test_pipeline.py`, `tests/test_runlock.py` |
| SPEC-010 | REQ-010 | DuckDB normalizado por run | Verificado | `tests/test_warehouse.py` |
| SPEC-011 | REQ-011 | CSV/Parquet solo tras gates | Verificado | `tests/test_export.py`, `tests/test_pipeline.py` |
| SPEC-012 | REQ-012 | Reportes MD/HTML + PNG/SVG accesibles | Verificado | `brujula/report.py`; `tests/test_report.py` |
| SPEC-013 | REQ-013 | Null=gaps; incompatibles no conectados | Verificado | `tests/test_report.py` |
| SPEC-014 | REQ-014 | Insight packet strict y evidence-bound | Verificado | `tests/test_insights.py`, `tests/test_agents.py` |
| SPEC-015 | REQ-015 | Seis roles read-only sin mutación | Verificado | `contracts/agent-run.schema.json`, `brujula/agents.py`, `tests/test_agents.py` |
| SPEC-016 | REQ-016 | Evals verdes/rojos contractuales | Verificado | `tests/test_evals.py`, `docs/EVALS.md` |
| SPEC-017 | REQ-017 | Instalación y E2E offline reproducibles | Verificado | 89 tests, clean source offline y wheel PASS; CI Windows/Linux; recibo de release |
| SPEC-018 | REQ-018 | Release con revisión secreto/licencia/método | Verificado y publicado | `IMPLEMENTATION-REVIEW.md`, inventario/licencias, matriz y [receipt final](evidence/release-receipt.json) |

## Dataset, SQL y cardinalidad

El dataset raíz cumple [dataset.schema.json](../contracts/dataset.schema.json).
Grain de observation:

`concept_type + concept_id + geography_id + period_id + metric_id`

`id` es PK técnica; el grain es unique key semántica. Todas las refs resuelven.
`metric_id` determina unit/price_basis. El fixture target tiene 54 grains
(3×3×2×3), aunque algunos valores sean `null`.

```text
dim_field       1 ─── 0..n observation [concept_type=field_of_study]
dim_occupation  1 ─── 0..n observation [concept_type=occupation]
dim_geography   1 ─── 0..n observation
dim_period      1 ─── 0..n observation
metric          1 ─── 0..n observation
source          1 ─── 0..n observation
field/occupation/industry 1 ─── 0..n bridge endpoint
```

La FK polimórfica de concepto se valida antes de insertar. Los labels de bridge
se resuelven desde dimensiones; bridge no contiene métricas ni autoriza
agregación.

## Flujo exitoso

1. Adquirir lock, crear run y escribir current/journal mutable con public status
   `BLOCKED` y `build_status=RUNNING`. `receipt.json` es final y write-once; se
   crea solo al terminar en `SUCCEEDED` o `FAILED`.
2. Leer ≤16 MB, hash SHA-256 y preservar raw inmutable.
3. Validar schema, refs, grain, rangos, estados y freshness.
4. Leer catálogo candidato sin activar fuentes.
5. Crear comparaciones compatibles.
6. Ejecutar/validar agentes read-only e insights.
7. Materializar DuckDB y exportar CSV/Parquet.
8. Renderizar Markdown, HTML y gráficas deterministas.
9. Escribir bundle, manifest y receipt inmutable.
10. Sellar éxito, receipt y manifest antes del único commit canónico de
    `current.json`; después materializar el pointer humano `report.md`. El CLI
    verifica el hash del manifest y todos sus artefactos antes de mostrarlo.

El bundle sintético target es `REVIEW`; `publishable=true` significa demostración
sintética publicable, no medición real.

## Flujo fallido

Un gate o excepción produce public status `BLOCKED` y receipt
`build_status=FAILED`, bundle bloqueado sin cifras heredadas y current canónico
apuntando al fallo. Si la generación ya selló un receipt `SUCCEEDED` y falla la
publicación, se conserva ese receipt y se escribe un `publication-failure.json`
separado; `current` queda `BLOCKED`. El journal es mutable y permite recuperar
un `RUNNING` interrumpido. Runs exitosos históricos se conservan sin presentarse
como actuales. No se equipara receipt de ejecución con publicación remota.

## Quality y comparabilidad

Estados públicos: `MEASURED`, `REVIEW`, `UNKNOWN`, `BLOCKED`. Quality root usa
esos enums. La reducción es determinista:

| Condición de filas/gates | `quality.status` | `publishable` |
|---|---|---:|
| algún gate estructural falla o cualquier fila `BLOCKED` | `BLOCKED` | false |
| schema válido pero cero observaciones | `UNKNOWN` | false |
| sin bloqueos/review y todas las filas `UNKNOWN` | `UNKNOWN` | false |
| sin bloqueos, al menos un valor disponible y alguna fila `REVIEW` | `REVIEW` | true solo para artefacto etiquetado |
| al menos un valor `MEASURED`, resto `MEASURED|UNKNOWN`, pero freshness u otro warning no crítico | `REVIEW` | true solo con warning visible |
| al menos una `MEASURED`, resto `MEASURED|UNKNOWN`, gates completos | `MEASURED` | true |

Las condiciones se evalúan en el orden de la tabla: el caso “todas UNKNOWN” no
puede ser promovido a REVIEW por freshness. REVIEW publicable siempre exige al
menos un valor no nulo disponible.

Si el contrato de cobertura exige filas y faltan (por ejemplo, el slice 3×3×2×3),
esa ausencia es un gate estructural y reduce a `BLOCKED`, no al caso genérico de
dataset vacío. `publishable=true` en REVIEW permite artefacto de investigación
etiquetado; no activa una fuente real ni autoriza un release numérico cuando el
gate de precisión está pendiente.

Un bundle sintético nunca reduce a `MEASURED`. Comparability requiere igual
concepto/tipo, fuente, población, geo, métrica, unidad, método, base de precio y
synthetic flag, periodos distintos/ordenados y valores disponibles. El orden se
deriva de `dim_period.start/end` ISO, no del texto de `period_id`; para comparar,
`current.start > previous.end`. Como las filas no contienen fechas, la firma
de la API implementada es `compare_observations(previous,current,periods_by_id)` y
`pipeline.make_comparisons` le entrega el mapa validado de periodos. Si falla,
`comparable=false` y deltas `null`. Base cero admite delta absoluto y relative
change `null`.

## Reportes

`render_report(payload, output_dir) -> {markdown,html,charts}` opera offline con
Matplotlib no interactivo, escapa HTML, no emite scripts, muestra banner
sintético, fuente/periodo/geo/unidad/población/precisión y tabla equivalente.
Null es gap; BLOCKED se omite; deltas provienen solo de `comparisons`. Bundle
bloqueado produce diagnóstico sin cifras ni gráficas.

## Agentes y Laya

Firma implementada: `run_agents(dataset,quality,comparisons,catalog)->dict`;
`validate_agent_run(...)->list[str]`. El contrato canónico se llama exactamente
`contracts/agent-run.schema.json`; todas las referencias `$ref` se resuelven
desde ese archivo hacia `insight.schema.json`. Los seis roles de
[ARCHITECTURE.md](ARCHITECTURE.md) solo proponen.

Laya se evalúa únicamente ante un caller repetido, cerrado y observable, con
baseline, dataset etiquetado, impacto de error, umbral, fallback y casos de
español/no-match/ambigüedad/evidencia/instruction-like. Solo pasa de shadow a
validated si supera la política completa sin violaciones críticas. Nunca
calcula estadística, comparabilidad ni autoridad.

## Release

Destino autorizado: `https://github.com/erickinorganico/career-signals-mx`.
Antes de release: tests limpios, diff/secret scan, revisión de licencias/datos,
revisión metodológica adversarial, hashes/manifest y tabla SPEC↔test↔artefacto.

## No aceptación

Falla si UI/servidor es dependencia, faltan módulos/schemas importados, tests no
coleccionan, ausencia aparece como cero, bridge agrega, una cifra real carece de
precisión/evidencia, current apunta a éxito tras fallo o se redistribuye material
sin términos claros. Todo `official_snapshot` permanece `BLOCKED` por
`source_activation` hasta M6; aprobar un registro local no activa una fuente
real.
