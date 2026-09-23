# Plan de ejecución — Brújula Laboral MX

Baseline: 2026-09-22. Este plan convierte [PRD.md](PRD.md) en tareas pequeñas y
verificables. El paquete de planeación M0 está **aceptado** y la
implementación/runtime del MVP sintético está **verificada localmente**. La
publicación del release y su revisión final siguen pendientes.

## Resultado del release inicial

Un repositorio de investigación local que reproduce un bundle sintético para
tres campos de estudio, tres periodos, México y Jalisco ilustrativo, con tres
métricas, quality/comparability gates, receipts, DuckDB, exports, gráficas y
briefs estáticos. No incluye frontend, backend, servicio web ni cifras ENOE.

## Decisiones de arquitectura fijadas

- Python 3.12+, DuckDB, jsonschema y Matplotlib; dependencias fijadas y sin
  servicios pagados.
- Dataset JSON como contrato de intercambio; DuckDB y exportaciones son
  derivados que solo se crean después del quality gate.
- Raw content-addressed y recibo por intento; `current` refleja el último
  intento, incluso cuando falla.
- Campos, ocupaciones, industrias, geografías, periodos y fuentes permanecen
  separados. Los bridges editoriales siempre usan `REVIEW`.
- Cálculo, joins, comparabilidad y render son deterministas. Los agentes son de
  solo lectura y producen propuestas estructuradas.
- Reportes Markdown/HTML y gráficas SVG/PNG son el producto de lectura; no se
  construye una aplicación.

## Definition of Ready de una tarea

Una tarea puede empezar cuando tiene owner, dependencias aceptadas, archivos
propios (máximo cinco), criterios observables, fixtures disponibles y ningún
conflicto de ownership. Si depende de términos, dataset o source activation no
resueltos, queda `BLOCKED`; no se crea un gate nuevo para trabajo local ya
autorizado.

## Definition of Done de una tarea

El owner completa sus criterios, ejecuta los checks indicados, conserva output
o receipt, actualiza la trazabilidad REQ→evidencia y entrega al integrador. El
integrador revisa el diff y repite los checks afectados. “Archivo creado”,
“código escrito” o “test existe” no equivalen a done.

## Estado inicial verificable

| Elemento | Estado | Evidencia o límite |
|---|---|---|
| Repositorio público y rama `main` | `VERIFIED` | `erickinorganico/career-signals-mx`, push inicial `acace35`; los pushes posteriores requieren sus propios checks |
| Auditoría de fuentes | `DOCUMENTED` | `SOURCES.md` y `source-research.json`; documentar candidatos no activa datos numéricos reales |
| Planeación y specs | `PLANNING COMPLETE` | M0 fue revisado como baseline documental; no acredita implementación ni release |
| Implementación local | `VERIFIED` | Suite integrada y replay offline PASS; fixture sintético y artefactos trazables |
| Release reproducible | `PENDING` | Verificación local PASS; publicación y cierre del integrador pendientes |

Ledger actual: `TASK-001`–`TASK-014` están completos y verificados localmente;
`TASK-015` queda pendiente de revisión/publicación del release; `TASK-016`–
`TASK-018` son condicionales de M6 y requieren activar una fuente oficial.

## Backlog ordenado

### M0 — Planeación y publicación inicial

#### TASK-001 — Consolidar autoridad, alcance y requisitos

- **Owner/modelo:** Sol, medium.
- **Dependencias:** ninguna.
- **Archivos:** `docs/PROJECT-CHARTER.md`, `docs/SCOPE.md`, `docs/PRD.md`,
  `docs/CONTRACT.md`, `AGENTS.md`.
- **Aceptación:** autoridad y precedencia no se contradicen; REQ-001–REQ-018 son
  estables; publicación autorizada y límites no-app quedan explícitos.
- **Checks:** revisión de links relativos; búsqueda de términos de UI para
  confirmar que solo aparecen como exclusiones/futuro; diff sin rutas privadas.
- **Cubre:** REQ-001–REQ-018 como baseline documental.

#### TASK-002 — Cerrar auditoría y contratos metodológicos

- **Owner/modelo:** Sol, medium; escalamiento a Astra para conflicto
  metodológico.
- **Dependencias:** TASK-001.
- **Archivos:** `docs/SOURCES.md`, `docs/source-research.json`,
  `docs/METHODOLOGY.md`, `docs/GLOSSARY.md`, `docs/SPEC.md`.
- **Aceptación:** fuentes candidatas, términos, población, grain, periodicidad y
  decisiones coinciden; OLA/IMCO/Data México no se presentan como ingesta; ENOE
  queda como extensión condicionada.
- **Checks:** JSON válido; cada URL/decisión documental tiene ID; glosario separa
  campo, ocupación, industria y vacante.
- **Cubre:** REQ-001, REQ-004.

#### TASK-003 — Revisar paquete M0 y matriz de trazabilidad

- **Owner/modelo:** integrador principal, Sol; revisión difícil con Astra.
- **Dependencias:** TASK-001, TASK-002.
- **Archivos:** `docs/ROADMAP.md`, `docs/RISKS.md`, `docs/PLAN.md`,
  `docs/SPEC.md`, `README.md`.
- **Aceptación:** cada requisito tiene hito, tarea y evidencia prevista; links
  pasan; el estado se marca `PLANNING COMPLETE` sin afirmar runtime completo.
- **Checks:** link checker documental, secret/path scan, revisión del diff y
  coherencia M0–M6.
- **Cubre:** control de todos los requisitos.

**Checkpoint M0:** solo el integrador cambia M0 a completado tras aceptar
TASK-001–003. El resultado habilita implementación; no habilita una fuente real.

### M1 — Contrato y slice sintético

#### TASK-004 — Congelar schemas v1

- **Owner/modelo:** Luna, medium.
- **Dependencias:** TASK-003.
- **Archivos:** `contracts/dataset.schema.json`,
  `contracts/insight.schema.json`, `tests/test_data.py`.
- **Aceptación:** schemas rechazan estructura incompleta, campos inesperados,
  enums inválidos y tipos incorrectos; las reglas semánticas no expresables en
  schema quedan asignadas al quality gate.
- **Checks:** `python -m pytest tests/test_data.py -q`.
- **Cubre:** REQ-002, REQ-004, REQ-005.

#### TASK-005 — Completar fixture sintético y loader

- **Owner/modelo:** Luna, medium.
- **Dependencias:** TASK-004.
- **Archivos:** `data/fixtures/pilot.json`, `brujula/data.py`,
  `tests/test_data.py`, `data/catalog/sources.json`.
- **Aceptación:** target de 54 combinaciones (3×3×2×3), o estado/nulo explícito
  para cada combinación; IDs editoriales `demo_`; valores sintéticos no nulos
  en `REVIEW`; catálogo oficial separado.
- **Checks:** test de schema, cobertura, refs, nulos y ausencia de cifras OLA/
  ENOE canónicas. El fixture implementado tiene 54 grains, con 7 filas `UNKNOWN` y `null` explícitos.
- **Cubre:** REQ-001–REQ-005.

**Checkpoint M1:** aceptado localmente; el integrador verificó el fixture desde
cero y ninguna salida puede presentarlo como medición real.

### M2 — Calidad, comparabilidad y trazabilidad

#### TASK-006 — Implementar quality, freshness y comparaciones

- **Owner/modelo:** Luna, high por invariantes estadísticos.
- **Dependencias:** TASK-005.
- **Archivos:** `brujula/quality.py`, `tests/test_quality.py`,
  `data/fixtures/pilot.json`, `brujula/pipeline.py`.
- **Aceptación:** duplicados, refs, rangos, estados, nulos y unidades bloquean
  correctamente; freshness usa period end; todos los ejes de comparabilidad
  emiten razones y omiten delta incompatible.
- **Checks:** `python -m pytest tests/test_quality.py -q`, incluidos casos rojos
  MOPRADEF y falso cero.
- **Cubre:** REQ-006–REQ-008.

#### TASK-007 — Implementar raw content-addressed y receipts

- **Owner/modelo:** Sol, medium.
- **Dependencias:** TASK-006.
- **Archivos:** `brujula/pipeline.py`, `tests/test_pipeline.py`,
  `contracts/run.schema.json`, `docs/SPEC.md`.
- **Aceptación:** éxito y fallo conservan hash, timestamps, parámetros, versión,
  status/error; fallo reemplaza `current` por `BLOCKED` y no recicla histórico.
- **Checks:** tests de éxito, fallo después de éxito y replay con igual input.
- **Cubre:** REQ-009.

#### TASK-008 — Materializar DuckDB y exports

- **Owner/modelo:** Luna, medium.
- **Dependencias:** TASK-006, TASK-007.
- **Archivos:** `brujula/warehouse.py`, `tests/test_warehouse.py`,
  `brujula/export.py`, `tests/test_export.py`.
- **Aceptación:** dimensiones/observaciones/bridges quedan separados; no hay
  agregación por bridge; exports preservan provenance/status/synthetic y solo se
  liberan para un bundle publicable. El staging diagnóstico de un intento
  fallido puede existir, pero nunca se promueve como salida actual.
- **Checks:** tests de conteo, round-trip, nulos, bloqueo y columnas requeridas.
- **Cubre:** REQ-010, REQ-011.

**Checkpoint M2:** aceptado localmente; quality, comparabilidad, receipts,
DuckDB y exports pasan sus checks. El receipt no es una autorización de release.

### M3 — Reportes y briefs estáticos

#### TASK-009 — Renderizar reporte y tablas accesibles

- **Owner/modelo:** Terra, medium.
- **Dependencias:** TASK-008.
- **Archivos:** `brujula/report.py`, `tests/test_report.py`,
  `docs/VISUALIZATION.md`.
- **Aceptación:** Markdown/HTML muestra advertencia sintética, fuente, periodo,
  geografía, unidad, población, base y precisión; cada gráfica tiene tabla
  alternativa; no hay red, CDN ni servidor.
- **Checks:** snapshots estructurales y búsqueda de etiquetas obligatorias.
- **Cubre:** REQ-012, REQ-013.

#### TASK-010 — Renderizar gráficas deterministas

- **Owner/modelo:** Terra, medium.
- **Dependencias:** TASK-009.
- **Archivos:** `brujula/report.py`, `tests/test_report.py`,
  `data/fixtures/pilot.json`.
- **Aceptación:** SVG/PNG son deterministas; nulos son gaps; `BLOCKED` no se
  grafica; no se conectan series incompatibles; comparaciones vienen del bundle.
- **Checks:** hashes/estructura para input fijo y casos de nulo/incompatibilidad.
- **Cubre:** REQ-012, REQ-013.

#### TASK-011 — Generar insight packets y briefs

- **Owner/modelo:** Sol, high.
- **Dependencias:** TASK-006, TASK-010.
- **Archivos:** `brujula/insights.py`, `contracts/insight.schema.json`,
  `tests/test_insights.py`, `brujula/report.py`.
- **Aceptación:** observación, interpretación, recomendación y unknowns están
  separados; refs resuelven; no hay causalidad/significancia inventada.
- **Checks:** validación de packets y fixtures rojos de evidencia huérfana.
- **Cubre:** REQ-014.

**Checkpoint M3:** revisión visual y textual sobre artefactos generados, además
de tests; que un archivo abra no basta para aceptar el claim.

### M4 — Agentes read-only y evals

#### TASK-012 — Definir roles y ejecución read-only

- **Owner/modelo:** Sol, medium.
- **Dependencias:** TASK-007, TASK-011.
- **Archivos:** `brujula/agents.py`, `brujula/scout.py`,
  `contracts/agent-run.schema.json`, `tests/test_agents.py`,
  `tests/test_scout.py`.
- **Aceptación:** roles reciben inputs validados, producen propuestas
  estructuradas y carecen de rutas para activar, mutar o publicar.
- **Checks:** tests de schema, tools permitidas y rechazos de autoridad.
- **Cubre:** REQ-015.

#### TASK-013 — Construir evals de claims y autoridad

- **Owner/modelo:** Sol, high; Astra revisa casos límite.
- **Dependencias:** TASK-012.
- **Archivos:** `evals/cases.json`, `evals/run.py`, `tests/test_evals.py`,
  `docs/EVALS.md`.
- **Aceptación:** casos cubren cero falso, mezcla conceptual, evidencia ausente,
  causalidad, serie incompatible, no-match e input con apariencia de instrucción.
- **Checks:** runner determinista con cero violaciones críticas; resultado y
  versión quedan en receipt.
- **Cubre:** REQ-016.

**Checkpoint M4:** el principal revisa que los evals midan outputs y autoridad,
no solo formato. Laya se registra `not applicable` salvo caller real validable.

### M5 — Integración y release reproducible

#### TASK-014 — Integrar CLI, demo y verificación limpia

- **Owner/modelo:** integrador principal, Sol high.
- **Dependencias:** TASK-008, TASK-011, TASK-013.
- **Archivos:** `brujula/cli.py`, `brujula/__main__.py`, `scripts/demo.ps1`,
  `scripts/demo.sh`, `scripts/verify.ps1`.
- **Aceptación:** un comando verifica y otro genera el bundle completo desde
  cero; funciona offline tras instalación; un fallo devuelve código no cero y
  current `BLOCKED`.
- **Checks:** suite completa, E2E en directorio temporal y segunda ejecución
  para determinismo.
- **Cubre:** REQ-017.

#### TASK-015 — Revisar, documentar y publicar el release

- **Owner/modelo:** principal; Astra high para revisión adversarial.
- **Dependencias:** TASK-014.
- **Archivos:** `README.md`, `docs/SPEC.md`, `docs/ORCHESTRATION.md`,
  `docs/RELEASE.md`, `CHANGELOG.md`.
- **Aceptación:** instalación y comandos coinciden con evidencia; cada REQ tiene
  test/artefacto; metodología y claims adversarialmente revisados; secrets y
  licencias limpios; commit publicado en el repo autorizado.
- **Checks:** clean-room replay, tests completos, link check, secret/license
  scan y comparación de artefactos con receipt.
- **Cubre:** REQ-017, REQ-018.

**Checkpoint M5:** el principal puede declarar el release reproducible solo con
TASK-015 aceptada. Hasta entonces el estado visible sigue “en construcción”.

### M6 — ENOE real para México (condicional, posterior al release)

#### TASK-016 — Activar un paquete ENOE concreto

- **Owner/modelo:** Sol + Astra high.
- **Dependencias:** TASK-015; decisión explícita de source activation.
- **Archivos:** `data/catalog/sources.json`, `docs/SOURCES.md`,
  `docs/METHODOLOGY.md`,
  `docs/decisions/0006-enoe-source-activation.md`.
- **Aceptación:** términos, URL, paquete, diccionario, CMPE, atribución y
  redistribución quedan resueltos; si no, estado `BLOCKED` sin descarga.
- **Checks:** revisión de fuente primaria y catálogo/schema.

#### TASK-017 — Implementar estimación ENOE nacional

- **Owner/modelo:** Terra implementa; Astra revisa estadística.
- **Dependencias:** TASK-016 aceptada.
- **Archivos:** `brujula/sources/enoe.py`, `brujula/survey.py`,
  `tests/test_enoe.py`, `tests/fixtures/enoe_minimal/`,
  `docs/METHODOLOGY.md`.
- **Aceptación:** factor, estrato, UPM, denominadores, varianza y precisión son
  reproducibles; ninguna fila pasa a `MEASURED` sin todos los campos.
- **Checks:** fixtures conocidos, estimaciones/varianza y casos de campo ausente.

#### TASK-018 — Publicar el primer snapshot real separado

- **Owner/modelo:** principal + Astra high.
- **Dependencias:** TASK-017 y nueva revisión adversarial.
- **Archivos:** `data/catalog/sources.json`, `docs/RELEASE.md`,
  `docs/SPEC.md`, `CHANGELOG.md`.
- **Aceptación:** fixture y real permanecen separados; provenance y precisión
  aparecen en todas las salidas; el snapshot pasa secret/license/method review.
- **Checks:** replay, comparación bloqueada contra sintético y receipt asociado
  a versión/hash.

M6 no tiene deadline comprometido. Informalidad, geografía subnacional, precios
reales y LATAM se planifican después como slices separados.

## Dependencias resumidas

```text
TASK-001 → TASK-002 → TASK-003
                         ↓
TASK-004 → TASK-005 → TASK-006 → TASK-007 → TASK-008
                                  │           ↓
                                  └──────→ TASK-009 → TASK-010 → TASK-011
                                                │             ↓
                                                └──────→ TASK-012 → TASK-013
                                                                      ↓
                                                       TASK-014 → TASK-015
                                                                      ↓
                                                       TASK-016 → TASK-017 → TASK-018
```

## Política de cambios y bloqueos

Los cambios de requisito actualizan PRD, trazabilidad y tarea antes de
implementarse. Un bloqueo registra requisito, evidencia faltante, owner y
condición de desbloqueo. Solo términos/datos/source activation o una decisión
material fuera de autoridad justifican esperar al usuario; fallos locales,
tests y correcciones dentro del alcance siguen hasta quedar verificados.
