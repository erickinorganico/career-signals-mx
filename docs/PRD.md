# Brújula Laboral MX — Requisitos del producto / Product requirements

> This guide defines the real-data product and its evidence gates. Phases 1–3 are independently accepted. Phase 4 has integrated local and hosted acceptance evidence; independent phase verification and the Phase 5 final release remain open. See `.planning/REQUIREMENTS.md` for current requirement status.

## Español

### Resultado esperado y lectores

El producto permite a estudiantes, personas que exploran opciones profesionales, analistas, periodistas y colaboradores técnicos entender y verificar evidencia laboral descriptiva. Distingue campo de estudio de ocupación, personas ocupadas de vacantes y valores faltantes de cero. El informe debe comenzar con preguntas y hallazgos sustentados, e indicar población, período, medida, incertidumbre, fuente y límites. Las preguntas sin evidencia suficiente conservan una respuesta explícita de no disponibilidad.

### Requisitos funcionales y aceptación

| ID | Requisito | Evidencia prevista | Control |
|---|---|---|---|
| PUB-01 | Informe en español organizado por preguntas, con hasta tres hallazgos sustentados, contexto nacional, perfiles, evolución, territorio, límites, método y fuentes. | Revisión editorial y de cobertura del informe real. | Publicación, Fase 4 |
| PUB-02 | Un mismo run validado produce HTML offline, Markdown equivalente y PDF imprimible, sin credenciales, servidor, JavaScript ni recursos de red. | Lectura de los tres formatos e inspección de recursos. | Publicación, Fase 4 |
| PUB-03 | Figuras SVG/PNG y tablas semánticas muestran unidades, incertidumbre, fuente, universo y estados; son legibles en impresión, móvil y ampliación al 200%. | Paridad de puntos y tablas; revisión visual, de acentos y paginación. | Publicación, Fase 4 |
| PUB-04 | CSV, Parquet y DuckDB conservan dimensiones, nulos, precisión permitida y procedencia, con diccionario y claves que enlazan figuras y afirmaciones. | Lectura de esquemas, valores y uniones de cada formato. | Publicación, Fase 4 |
| PUB-05 | Una proyección pública impide que estimaciones internas suprimidas o diagnósticos que las revelen reaparezcan en cualquier formato o texto alternativo. | Controles de supresión, reconstrucción y divulgación en los archivos emitidos. | Publicación, Fase 4 |
| OPS-01 | La CLI documenta adquisición, refresco y replay offline; este último reproduce los mismos resultados numéricos separando contenido de fechas e identificadores de ejecución. | Ejecución instalada y recibos de reproducción real. | Operación, Fase 4 |
| OPS-02 | El pipeline sella cada run con hashes, recibo final y manifiesto antes de actualizar current; un fallo impide resolverlo como vigente y conserva el historial. | Matriz de fallos y lectura de manifiestos, recibos y current. | Operación, Fase 4 |
| OPS-03 | Los consumidores verifican manifiesto, hashes, catálogo y adquisiciones requeridas antes de abrir informes o exportaciones; fallos posteriores invalidan current. | Rechazo de archivos alterados y adquisiciones fallidas. | Operación, Fase 4 |
| REL-01 | Documentación en español e inglés de alcance, requisitos, arquitectura, método, instalación, comandos, actualización, contribución, citación y límites. | Revisión contra interfaces y evidencia aceptadas. | Release, Fase 5 |
| REL-02 | Instalaciones limpias y pruebas de fixtures en Windows/Ubuntu; revisión numérica, conceptual y visual independiente del bundle real, más replay offline. | Recibos separados de portabilidad, reproducción y auditoría real. | Release, Fase 5 |
| REL-03 | Revisión de secretos, licencias, atribución y ausencia de microdatos; sólo artefactos validados en el repositorio autorizado. | Inventario público cerrado y auditoría de su contenido. | Release, Fase 5 |
| REL-04 | Release 1.0.0 enlaza código, informe, figuras, agregados, manifiesto y aceptación, sin controles materiales pendientes. | Descarga pública y comprobación de hashes y versión. | Release, Fase 5 |
| GSD-01 | Requisitos, planes revisados, ejecución, verificaciones, revisión de código y auditoría final son trazables en GSD. | Matriz de trazabilidad y auditoría final. | Release, Fase 5 |

### Requisitos de operación y calidad

La operación se ejecuta localmente. La reproducción puede realizarse offline una vez instaladas las dependencias y adquiridos los cortes aprobados. El contenido numérico se reproduce para los mismos insumos e implementación; los identificadores, fechas y bytes propios del contenedor se verifican por separado. No se requiere una API pagada, inferencia externa, credenciales ni una aplicación hospedada. Los microdatos y marcos individuales permanecen locales; los artefactos públicos contienen agregados redistribuibles bajo términos revisados. El informe es en español y la documentación permite trabajar en español e inglés. La legibilidad y semántica se verifican en los archivos reales; generar un PDF no acredita por sí solo PDF/UA ni compatibilidad completa con lectores de pantalla.

### Alcance analítico y límites

El producto cubre ocho trimestres, dos poblaciones, tres campos focales y 23 medidas. El detalle de otros campos, sexo registrado y 32 entidades corresponde al último trimestre. No mide demanda de contratación o vacantes, efectos causales, resultados individuales ni significancia de los cambios. Las definiciones incompatibles bloquean comparaciones. Un refresco fallido impide presentar la publicación dependiente como vigente, aunque exista un resultado histórico aceptado.

## English

### Outcome and users

The product lets a student, career-change reader, analyst, journalist, or technical contributor understand and verify descriptive labor evidence without confusing field of study with occupation, occupied people with vacancies, or missing data with zero. The report must lead with reader questions and supported findings, then show population, period, measure, uncertainty, source, and limitations. It must preserve unanswered questions instead of manufacturing conclusions.

### Functional requirements and acceptance matrix

| ID | Requirement | Planned evidence or format | Gate |
|---|---|---|---|
| PUB-01 | Spanish report organized by questions: up to three supported openings, national context, professional cohort, three focal profiles, evolution, recorded sex, territory, coverage, limitations, method, and exact sources. | HTML/Markdown/PDF editorial parity; unsupported cells and reasons visible. | Phase 4 publication |
| PUB-02 | One validated run produces offline HTML, equivalent Markdown and printable PDF without credentials, a server, JavaScript or network resources. | Readback of all three formats and resource inspection. | Phase 4 publication |
| PUB-03 | Figures and semantic tables expose units, uncertainty, population, period, source, status, and missingness; SVG/PNG carry equivalent data. | Print, mobile, 200% zoom, contrast, accents, PDF text and pagination review. | Phase 4 publication |
| PUB-04 | Public aggregate exports preserve the v2 grain, dimensions, null/status meanings, precision fields permitted by suppression, provenance, stable join keys, and dictionary. | CSV/Parquet/DuckDB schema and row/key parity against the public projection. | Phase 4 publication |
| PUB-05 | One public projection prevents suppressed internal estimates or revealing diagnostics from reappearing in any format or alternative text. | Suppression, reconstruction and disclosure checks on emitted files. | Phase 4 publication |
| OPS-01 | Local operation acquires approved snapshots, supports offline replay, and reproduces numerical/public content for identical inputs while separating run timestamps from content identity. | Documented installed operation and replay receipt. | Phase 4 operation |
| OPS-02 | The pipeline seals each run with hashes, a final receipt and manifest before updating current; a failure prevents current resolution while preserving history. | Failure matrix, manifest, hashes, and current-resolution readback. | Phase 4 operation |
| OPS-03 | Consumers verify required source, method, catalog, manifest, and current status before opening reports or exports. | Fail-closed consumer check after changed or failed acquisition. | Phase 4 operation |
| REL-01 | Spanish and English documentation covers README, scope, requirements, architecture, method, installation, commands, updates, contribution, citation and limits. | Bilingual docs review against accepted receipts and current interfaces. | Phase 5 final release |
| REL-02 | Clean installations and fixture tests pass on Windows/Ubuntu; the real bundle receives independent numerical, conceptual and visual review plus offline replay. | Separate portability, real reproduction and independent audit evidence. | Phase 5 final release |
| REL-03 | Public package passes secret, license, attribution, and no-microdata review; only validated aggregate artifacts are eligible for publication. | Public-safe scan and review receipt. | Phase 5 final release |
| REL-04 | Final release binds code, report, figures, aggregate exports, manifest, and acceptance evidence with exact version/SHA references. | Final release manifest and public readback. | Phase 5 final release |
| GSD-01 | Requirements, plans, execution, verification, review, and final audit remain traceable without silently marking pending gates complete. | GSD traceability matrix and final status audit. | Phase 5 final release |

### Non-functional requirements

The workflow runs locally. Reproduction can run offline once dependencies are installed and approved snapshots acquired. Numerical content is reproducible for identical inputs and implementation; run IDs, clocks and format-container bytes are checked separately. No paid API, external inference, credential or hosted application is required. Raw microdata and person-derived frames remain local; public artifacts contain aggregates redistributable under reviewed terms. The report is in Spanish and documentation supports Spanish and English. Legibility and semantics are checked in actual files; successful PDF generation alone does not establish PDF/UA or full screen-reader conformance.

### Research limits

The product covers eight quarters, two populations, three focal fields and 23 measures. Detail for other fields, recorded sex and all 32 states covers the latest quarter. It does not measure hiring demand, vacancies, causal effects, individual outcomes or statistical significance of changes. Incompatible definitions block comparisons. A failed refresh prevents dependent publication from being presented as current, even when a historical accepted result exists.

## Authority notes

- Scope and product baseline: `docs/SCOPE.md`, `docs/PRD.md`, `.planning/PROJECT.md`, `.planning/REQUIREMENTS.md`.
- Publication and editorial authority: `.planning/phases/04-offline-publication-and-reproducible-operation/04-CONTEXT.md` and `04-EDITORIAL-SPEC.md`.
- Accepted analysis authority: `docs/evidence/phase-03-analysis-acceptance.json` (`status: PASS`, `implementation_commit: a6696a1a62e91cd72ac26bde149d201f3ea07e82`, `accepted_numeric_digest: 8db575e9d664864d1513e3b9658bd9b060c4cb3bed8b51561f208adeb97b9a00`).
- Immutable preparation checkpoint: `d9246e416b944f8a6ec01811b6e885da0141493b`.
