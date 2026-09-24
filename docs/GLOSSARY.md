# Glossary / Glosario

> These definitions describe the accepted v2 analytical and Phase 4 publication boundary. They do not activate sources or certify the final v1.0.0 release.

## Español

| Término | Definición operativa |
|---|---|
| Campo de estudio (`field_of_study`) | Dimensión educativa derivada de `CS_P14_C` y validada contra el catálogo CMPE del snapshot. No se intercambia con ocupación ni industria. |
| Ocupación (`occupation`) | Dimensión laboral de la ocupación declarada. No se asigna desde el campo de estudio ni se aproxima por texto. |
| Industria (`industry`) | Dimensión de actividad económica. No se infiere desde campo u ocupación. |
| Población (`population`) | Universo explícito de una medida. `national_15_plus_context` conserva EDA 98 como edad operativamente desconocida; `completed_professional_known_age` exige estudios profesionales terminados y edad conocida. |
| Geografía (`geography`) | Contexto nacional `mx` o entidad oficial. `ENT` y `CVE_ENT` son alias solo cuando el puente conceptual, catálogo y fuente exacta están revisados. |
| Periodo (`period`) | Trimestre del snapshot y de la publicación. No significa que toda variable mida todo el trimestre; condiciones económicas refieren a la semana anterior e ingresos al mes anterior. |
| Fuente (`source`) | Snapshot ENOE específico, con URL, SHA-256, autoridad, términos, periodo y receipt. Una fuente catalogada no queda activa por su sola presencia. |
| Grano de diez claves (`ten-key grain`) | `(source_snapshot_id, population_id, field_of_study_id, occupation_id, industry_id, geography_id, recorded_sex_id, period_id, metric_id, method_id)`. Las dimensiones son independientes y no se intercambian automáticamente. |
| `observed_n` / `sample_size` | Número de personas observadas que contribuyen al denominador pertinente. No es suma de pesos ni tamaño de muestra efectivo (ESS). |
| `weighted_count` / denominador ponderado | Suma ponderada con `FAC_TRI` del universo pertinente. Es una estimación de encuesta, no un conteo administrativo. No sustituye `observed_n` ni ESS. |
| ESS | Effective sample size. No se inventa a partir de pesos, `weighted_count` o `design_df`; no es sinónimo de `observed_n`. |
| Ingreso nominal (`nominal_income`) | Monto mensual en pesos nominales. No se ajusta por poder adquisitivo. `positive_income_mean` usa solo `ING7C∈{1,…,5}` y `INGOCUP∈[1,999998]`; cero, sin ingreso y no especificado conservan sus estados. |
| Estados públicos | `MEASURED`: satisface los controles de evidencia y precisión aplicables; `REVIEW`: requiere cautela o revisión documentada; `UNKNOWN`: valor no determinable; `BLOCKED`: un control impide la publicación o comparación. `UNKNOWN`/`BLOCKED` tienen valor nulo. Supresión es una decisión expresada por valor nulo y motivo, no un quinto estado. |
| `null` | Dato no disponible, no soportado, suprimido o bloqueado según el estado y motivo. Nunca significa cero. |
| Supresión | Elimina el valor y diagnósticos ponderados/de precisión que podrían revelarlo. Cuando restar hermanos conocidos de un padre visible permitiría reconstruir una celda hija suprimida, la supresión complementaria oculta el padre y las copias pertinentes. |
| Precisión del proyecto | Aproximación no oficial de INEGI. El ajuste singleton explícito obliga `REVIEW` y `official_precision=false`; un valor solo se conserva si pasa los demás controles de soporte y supresión. El contraste independiente con R no convierte la precisión en oficial. |
| Hora de adquisición | Fecha/hora operativa de descarga o lectura del insumo. Se registra en su recibo; la verificación de bytes y hashes establece custodia. La hora por sí sola no demuestra contenido numérico ni publicación. |
| Contenido numérico | Resultados y digest de cálculos agregados. El determinismo del contenido se verifica por separado de relojes y de la identidad del código/método; la aceptación sigue exigiendo verificar todos esos componentes. |
| Recibo (`receipt`) | Registro final inmutable de un intento, con estado, tiempos, hashes y alcance. El fallo invalida el current correspondiente y sus consumidores dependientes; un éxito histórico no reemplaza un estado vigente fallido. |
| `current` | Puntero mutable al intento vigente, que puede estar en ejecución, fallido o exitoso. El consumidor solo resuelve artefactos después de verificar éxito, recibo, manifiesto, hashes y dependencias actuales. |
| `seal` | Vinculación inmutable de entradas, código, método y salidas en una fase de publicación. La Fase 4 conserva esa evidencia; la auditoría final de Fase 5 es independiente. |
| IDs tipados v2 | `v2r` identifica registros, `v2c` comparaciones y `v2k` claims. El prefijo y la carga canónica son parte de la identidad; no se sustituyen por IDs inventados. |
| Detalle profesional | `completed_professional_known_age` acepta EDA 15–96 como edades ordinarias y EDA 97 como categoría top-coded de 97 años o más; EDA 98/99 y faltantes se excluyen de esa cohorte. |
| Detalle nacional operativo | `national_15_plus_context` incluye EDA 98 como edad operativamente desconocida cuando el universo lo admite. Esto no convierte 98 en una edad exacta. |
| Detalle más reciente | Campos de estudio, sexo registrado y las 32 entidades solo tienen detalle del snapshot más reciente, 2026-Q2. La cobertura de ocho periodos aplica al contexto nacional, la cohorte profesional y los campos focales. |

## English

| Term | Operational definition |
|---|---|
| Field of study | Educational dimension from `CS_P14_C`, validated against the snapshot CMPE catalog. It is separate from occupation and industry. |
| Occupation | Declared labor occupation dimension. It is not assigned from field of study or approximated by text. |
| Industry | Economic-activity dimension. It is not inferred from field or occupation. |
| Population | Explicit universe for a measure. `national_15_plus_context` retains EDA 98 as operationally unknown age; `completed_professional_known_age` requires completed professional studies and known age. |
| Geography | National `mx` context or official entity. `ENT` and `CVE_ENT` are aliases only when the concept bridge, catalog, and exact source evidence are reviewed. |
| Period | Snapshot and publication quarter. It does not mean every variable measures the whole quarter; economic conditions refer to the prior week and income to the prior month. |
| Source | Specific ENOE snapshot with URL, SHA-256, authority, terms, period, and receipt. A catalog entry is not active merely because it exists. |
| Ten-key grain | `(source_snapshot_id, population_id, field_of_study_id, occupation_id, industry_id, geography_id, recorded_sex_id, period_id, metric_id, method_id)`. Dimensions remain independent. |
| `observed_n` / `sample_size` | Number of observed people contributing to the relevant denominator. It is neither a weight sum nor effective sample size (ESS). |
| `weighted_count` / weighted denominator | `FAC_TRI` weighted sum for the relevant universe. It is a survey estimate, not an administrative count; it does not replace `observed_n` or ESS. |
| ESS | Effective sample size. It is not invented from weights, `weighted_count`, or `design_df`, and is not synonymous with `observed_n`. |
| Nominal income | Monthly pesos without purchasing-power adjustment. `positive_income_mean` uses only `ING7C∈{1,…,5}` and `INGOCUP∈[1,999998]`; zero, no-income, and unspecified states remain distinct. |
| Public states | `MEASURED`: satisfies applicable evidence and precision checks; `REVIEW`: requires documented caution or review; `UNKNOWN`: value cannot be determined; `BLOCKED`: a control prevents publication or comparison. `UNKNOWN`/`BLOCKED` carry null values. Suppression is represented by a null value and reason, not a fifth state. |
| `null` | Unavailable, unsupported, suppressed, or blocked data according to status and reason. It never means zero. |
| Suppression | Removes the value and weighted/precision diagnostics that could reveal it. If subtracting known siblings from a visible parent would reconstruct a suppressed child, complementary suppression hides the parent and relevant copies. |
| Project precision | Nonofficial INEGI approximation. Explicit singleton adjustment requires `REVIEW` and `official_precision=false`; a value is retained only if other support and suppression checks pass. Independent comparison with R does not make precision official. |
| Acquisition time | Operational timestamp of input download or reading. Its receipt records it; byte/hash verification establishes custody. Time alone does not establish numerical content or publication. |
| Numerical content | Aggregate results and their digest. Content determinism is checked separately from clocks and code/method identity; acceptance still requires verification of all those components. |
| Receipt | Immutable final attempt record with state, times, hashes and scope. Failure invalidates the corresponding current and dependent consumers; historical success does not replace present failure. |
| `current` | Mutable pointer to the present attempt, which may be running, failed or successful. Consumers resolve artifacts only after checking success, receipt, manifest, hashes and current dependencies. |
| `seal` | Immutable binding of inputs, code, method, and outputs in a publication phase. Phase 4 records that evidence; final Phase 5 audit is separate. |
| Typed v2 IDs | `v2r` identifies records, `v2c` comparisons, and `v2k` claims. Prefix and canonical payload are part of identity; invented IDs are invalid. |
| Professional detail | `completed_professional_known_age` treats EDA 15–96 as ordinary ages and EDA 97 as the top-coded 97-or-more category; EDA 98/99 and missing age are excluded from this cohort. |
| National operational detail | `national_15_plus_context` includes EDA 98 as operationally unknown age when its universe permits it. It does not turn 98 into an exact age. |
| Latest-quarter detail | Field, recorded-sex, and all 32-entity detail are limited to the latest snapshot, 2026-Q2. Eight-period coverage applies to the national context, professional cohort, and focal fields. |

This glossary makes no v1.0.0 release PASS claim. / Este glosario no declara PASS de release v1.0.0.
