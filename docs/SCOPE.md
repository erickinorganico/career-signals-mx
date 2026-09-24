# Brújula Laboral MX — Alcance / Scope

> Phases 1–3 and the integrated Phase 4 plan have accepted numerical, analytical and local publication evidence. Final independent Phase 4 verification and the Phase 5 release audit remain separate gates. This guide describes the full real-data scope without claiming v1.0.0 completion.

## Español

### Propósito y preguntas del lector

Brújula Laboral MX es una publicación de investigación que se ejecuta localmente y permite entender qué dicen los datos oficiales de México sobre el trabajo entre personas con estudios profesionales terminados. Responde preguntas delimitadas: ¿qué población y medida describe cada cifra?, ¿cómo evolucionan las tres áreas focales durante ocho trimestres?, ¿qué diferencias descriptivas aparecen por sexo registrado o entidad en el último trimestre?, ¿qué cobertura, datos faltantes y precisión limitan la lectura?, ¿cómo se verifica una conclusión desde su fuente, método y registros? Su uso es investigar y comprobar evidencia. No recomienda una carrera, predice resultados individuales, mide vacantes o demanda de contratación, ni atribuye impacto económico.

### Poblaciones, campos, períodos y medidas

La ventana comprende ocho cortes trimestrales de la ENOE: 2024-Q3 a 2026-Q2. Separa el contexto nacional operativo de 15 años o más de la cohorte residente con estudios profesionales terminados y edad conocida. Los campos focales son Derecho (`033100`), Comunicación y periodismo (`032100`) y Ciencias políticas (`031300`), según la CMPE. La evolución cubre los ocho trimestres para el contexto nacional, la cohorte profesional y esos tres campos. El detalle de otros campos identificables, sexo registrado y 32 entidades corresponde al último trimestre, 2026-Q2. Cada registro conserva separados campo de estudio, ocupación, industria, geografía, sexo registrado, período, fuente, población, métrica y método.

El catálogo contiene 23 medidas: población, ocupación, población económicamente activa y desocupación; tasas de empleo, participación y desocupación; ingreso mensual nominal positivo conocido y su cobertura; conteos y proporciones sin ingreso o con ingreso no especificado; informalidad del empleo principal; mujeres entre personas ocupadas; cuatro proporciones de posición en la ocupación; conteo y tasa de subocupación; media y cobertura de horas conocidas. Los valores faltantes permanecen nulos con estado explícito. El tamaño observado de muestra se distingue del soporte y denominador ponderados y del tamaño efectivo de muestra. La precisión es una aproximación del proyecto, no precisión oficial del INEGI. Las diferencias trimestrales, anuales, por sexo o por entidad son descriptivas y no establecen causalidad ni significancia estadística.

### Preguntas que pueden responderse y límites

Se pueden describir niveles y cobertura de una población y campo definidos, cambios entre trimestres adyacentes o equivalentes de años consecutivos que sean comparables, y contrastes de sexo registrado y entidad en el último trimestre. Cada afirmación se vincula a un registro público aceptado o una comparación validada. El informe incluye las 32 entidades con disponibilidad y motivos de ausencia visibles; el detalle de otros campos sigue el orden de clasificación oficial, sin implicar una clasificación de mejores y peores carreras.

Los datos no permiten responder cuántas vacantes existen, si un título causa un resultado laboral, cuál carrera es universalmente mejor, cuánto ganará una persona ni si las diferencias son estadísticamente significativas. Campo educativo y ocupación no se consideran equivalentes. Las definiciones incompatibles de fuente, universo, geografía, medida, precios, método, concepto, edición o período bloquean la comparación. Los valores desconocidos, sin soporte o suprimidos no se convierten en cero ni se reconstruyen mediante totales.

### Fuentes, evidencia y entregables

El análisis usa ocho cortes aprobados de la ENOE del INEGI, fijados mediante hashes, diccionarios, catálogos y recibos de adquisición. Sólo se distribuyen agregados después de revisar licencias, atribución y ausencia de secretos y microdatos. Los entregables previstos son un informe editorial en español en HTML offline, Markdown y PDF imprimible, figuras SVG/PNG, tablas semánticas y agregados CSV/Parquet/DuckDB con diccionario, procedencia, claves de unión y estados de los valores. La operación consiste en scripts y procesos reproducibles locales. No requiere una aplicación, un servicio hospedado ni inferencia pagada.

### Estado de aceptación

La Fase 3 acredita 6,739 registros públicos, 4,209 comparaciones, 38 afirmaciones y tres hallazgos de apertura, sin errores al validar el JSON guardado; cinco totales permanecen nulos por supresión complementaria. La Fase 4 ejecutó aceptación numérica instalada, informe y revisión visual, sellado, invalidación tras fallos, resolución de la publicación vigente y CI nativa Windows/Ubuntu. Su recibo público es `docs/evidence/phase-04-publication-acceptance.json`. Aún faltan la verificación independiente de fase y la auditoría y publicación final de la Fase 5.

## English

### Purpose and reader questions

Brújula Laboral MX is a local-first research publication for readers who want to understand what official Mexican labor data can and cannot say about completed professional studies. It answers bounded questions: what population and measure does each number describe; how do the three focal fields behave across eight quarters; what descriptive contrasts appear by recorded sex or entity; what coverage, missingness, and precision limit interpretation; and can another reader trace a conclusion to its source, method, record, and comparison? The output supports investigation and verification; it does not recommend a career, predict an individual outcome, measure vacancies or hiring demand, or infer economic impact.

### Population, fields, periods, and measures

The analytical window is eight ENOE snapshots from 2024-Q3 through 2026-Q2. It keeps two populations distinct: the national operational 15+ context and the resident cohort with completed professional studies and known age. The focal fields are Law, Communication and journalism, and Political science, with official CMPE codes `033100`, `032100`, and `031300`. Eight-quarter trends cover the national context, professional cohort and these three fields. Detail for other identifiable fields, recorded sex and all 32 states covers the latest quarter, 2026-Q2. The grain keeps field of study, occupation, industry, geography, recorded sex, period, source, population, metric, and method separate.

The accepted metric catalog contains 23 measures: population, occupied, labor force, unemployed, employment, participation and unemployment rates; positive-known nominal monthly income and its coverage; no-income and unspecified-income counts and shares; main-job informality; women among occupied people; four occupational-position shares; suboccupied count and rate; and known-hours mean and coverage. Missing values remain null with explicit status. Observed sample size is distinct from weighted support, weighted denominator, and ESS. Precision is a project approximation, not official INEGI precision; descriptive qoq/yoy, sex, and entity contrasts do not establish causality or statistical significance.

### Supported and unanswered questions

The scope supports descriptive statements tied to an accepted public record or validated comparison: levels and coverage for the stated population and field, changes between comparable adjacent or like-year quarters, same-quarter recorded-sex contrasts, and same-quarter entity contrasts including all 32 official entities when evidence exists. It supports a national context alongside the professional cohort, three complete focal profiles, other official fields ordered by classification code, visible availability, and documented reasons for unavailable cells.

The scope cannot answer how many vacancies exist, whether a degree causes employment or income, which career is universally best, whether a contrast is statistically significant, what an individual will earn, or whether observed field and occupation are equivalent. It cannot compare incompatible source, universe, geography, measure, price basis, method, concept, edition, or period definitions. It cannot turn null, unknown, unsupported, or suppressed cells into zero or reconstruct a hidden child from a visible parent.

### Evidence, sources, and delivery boundary

The accepted analysis uses the approved INEGI ENOE source family and eight pinned snapshots with source custody, dictionaries, catalogs, and receipts. Public output is aggregate-only and redistributable after source, license, secret, and microdata review. The intended delivery is a Spanish editorial report with offline HTML, Markdown, printable PDF, SVG/PNG figures, semantic tables, and public CSV/Parquet/DuckDB aggregates with dictionary, provenance, stable join keys, null/status meanings, and claim/evidence links. It is a static local publication and reproducible batch workflow, not a frontend, backend, hosted service, dashboard, or paid inference system.

### Acceptance boundary

Phase 3 acceptance records 6,739 sanitized records, 4,209 comparisons, 38 claims, three opening claim IDs, zero persisted JSON validation errors, and five null complementary-suppression parents. Phase 4 executed installed numerical acceptance, report and visual review, sealing, failure invalidation, current resolution and native Windows/Ubuntu CI; see `docs/evidence/phase-04-publication-acceptance.json`. Independent phase verification and Phase 5 documentation, release inventory, audits and public v1.0.0 readback remain open.

## Authority notes

- Current planning authority: `.planning/PROJECT.md` and `.planning/REQUIREMENTS.md`.
- Editorial/design authority: `.planning/phases/04-offline-publication-and-reproducible-operation/04-CONTEXT.md` and `04-EDITORIAL-SPEC.md`.
- Accepted analytical authority: `docs/evidence/phase-03-analysis-acceptance.json` (`status: PASS`, `implementation_commit: a6696a1a62e91cd72ac26bde149d201f3ea07e82`, `accepted_numeric_digest: 8db575e9d664864d1513e3b9658bd9b060c4cb3bed8b51561f208adeb97b9a00`), with Phase 2 numerical evidence as its upstream authority.
- Immutable preparation checkpoint: `d9246e416b944f8a6ec01811b6e885da0141493b`.
