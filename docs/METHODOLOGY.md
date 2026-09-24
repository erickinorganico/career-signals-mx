# Método ENOE / ENOE methodology

> This bilingual guide describes the accepted eight-snapshot numerical method and its nonofficial precision limits. Phase 4 installed identity, publication and hosted fixture/PDF checks have evidence in `docs/evidence/phase-04-publication-acceptance.json`. Independent phase verification and final Phase 5 release acceptance remain open.

## Español

### Alcance, poblaciones y unidad conceptual [P01]

El análisis separa dos contextos. `national_15_plus_context` describe el contexto nacional de personas residentes con edades operativas de 15 años o más; admite EDA 15–98 y conserva EDA 98 como edad operativamente desconocida. `completed_professional_known_age` describe personas residentes con estudios profesionales terminados y edad conocida: EDA 15–96 son edades ordinarias y EDA 97 es la categoría top-coded de 97 años o más, nunca la edad literal 97; EDA 98/99 y faltantes de edad se excluyen de esta cohorte según el universo. La respuesta lograda es `R_DEF=00`, la residencia es `C_RES∈{1,3}`, y la cohorte profesional exige `CS_P13_1=07` y `CS_P16=1`; quedan fuera estudios técnicos, de posgrado e incompletos. El producto mide situación laboral de personas cuyo campo educativo declarado cae en el universo definido; no mide vacantes, demanda de contratación ni efectos causales de estudiar una carrera.

### Campo de estudio, ocupación, industria y geografías [P02]

`field_of_study` es el campo educativo `CS_P14_C` validado contra el catálogo CMPE del trimestre, preservando claves de texto y rechazos por conflicto o código no catalogado. Los tres códigos focales son `031300` Ciencias políticas, `032100` Comunicación y periodismo y `033100` Derecho. Campo de estudio, ocupación e industria son dimensiones distintas: el análisis no asigna ocupación o industria desde el campo ni aproxima códigos mediante texto. La identidad de grano conserva también sexo registrado, período, fuente, población y geografía. `mx` representa el contexto nacional y las 32 entidades usan códigos oficiales; `ENT` y `CVE_ENT` se tratan como alias geográficos equivalentes cuando el puente de concepto, catálogo y fuente exacta está revisado, aunque el encabezado cambie a partir de 2025-Q3. Deriva no revisada de concepto, definición o fuente bloquea la comparación.

### Ventana temporal y comparabilidad [P03]

La base aceptada contiene ocho trimestres: 2024-Q3 a 2026-Q2. Las comparaciones adyacentes son `qoq` y las de trimestres equivalentes de años consecutivos son `yoy`; ambas son contrastes descriptivos. Solo se comparan celdas con fuente, universo, geografía, medida, base de precios, método, concepto y período comparables. Las muestras rotatorias pueden solaparse; por ello no se usa un test de muestras independientes, p-valores ni significancia del cambio. Los ingresos se expresan como montos nominales mensuales, sin ajuste por poder adquisitivo. La equivalencia revisada de `ENT`/`CVE_ENT` no bloquea por sí sola; deriva no revisada de alias conceptual, catálogo, edición, definición o fuente sí bloquea la comparación automática.

### Pesos, marco de diseño y estimación [P04]

El estimador usa `FAC_TRI` como peso trimestral final, `EST_D_TRI` como estrato y `UPM` como conglomerado. Se construye primero el marco completo de personas respondentes y residentes antes de restringir edad, campo, entidad, sexo o resultado; así se conservan los conglomerados y estratos necesarios para dominios. La varianza usa Taylor de conglomerados últimos con pesos finales y marco completo (`taylor_ultimate_cluster_wr_final_weights_v1`). Los pesos deben ser finitos y no negativos; los pesos cero requieren auditoría explícita, no cuentan como soporte y no pueden formar una UPM sin soporte positivo.

### Singleton, intervalos y precisión [P05]

Un estrato singleton falla por defecto. La política usada en el paquete aceptado permite el ajuste explícito del proyecto (`singleton_policy=adjust`), centrando el aporte del singleton en la media global de UPM; ese resultado queda en `REVIEW` y `official_precision=false`. Los intervalos son nominales de 90%: Wald normal para totales/medias y logit-delta para proporciones interiores; proporciones 0/100 no reciben intervalos degenerados. `n<30` o menos de dos UPM del dominio producen `UNKNOWN` y `value=null` por falta de soporte. Con soporte suficiente, `MEASURED` requiere CV menor que 15%, todos los demás gates válidos y ningún ajuste singleton; CV de 15% a menos de 30%, ajuste singleton u otra precisión no oficial producen `REVIEW` y pueden conservar valor con motivo. CV de al menos 30%, frontera, varianza cero, denominador cero, IC degenerado o grados de libertad nulos dejan el valor en `null` con razón explícita. La precisión del proyecto es una aproximación no oficial de INEGI.

### Observaciones, ESS y ceros [P06]

`sample_size`/`observed_n` es el número de personas observadas que aporta al denominador pertinente; nunca es la suma de pesos ni un ESS. El denominador ponderado, el soporte ponderado, UPM, estratos y grados de libertad se conservan como diagnósticos separados. Un cero observado solo se conserva cuando la definición de la variable lo confirma; una ausencia, categoría no especificada o dato no soportado permanece nulo/`UNKNOWN` y no se convierte en cero. Las estimaciones públicas suprimidas no filtran denominadores ponderados ni diagnósticos de precisión.

### Ingreso y medida condicionada [P07]

`positive_income_mean` es el promedio mensual nominal condicionado a personas ocupadas con monto positivo exacto conocido: `ING7C∈{1,…,5}` e `INGOCUP∈[1,999998]`. `INGOCUP=0` y `999999` no son montos positivos válidos; `ING7C=6` significa sin ingreso y `ING7C=7` ingreso no especificado. Categorías conocidas sin monto exacto pueden participar en medidas de estado/cobertura, pero no en el promedio positivo; contradicciones entre banda y monto se excluyen. Por eso el promedio positivo y la cobertura de ingreso positivo conocido tienen universos explícitos y no deben interpretarse como ingreso medio de todas las personas ocupadas.

### Estado, soporte y supresión [P08]

Cada celda conserva `status`, `reason`, `value`, `evidence_refs`, método y procedencia. `UNKNOWN` o `BLOCKED` obligan `value=null`; `REVIEW` puede conservar valor únicamente con motivo documentado y precisión no oficial. La supresión elimina también denominador ponderado, soporte ponderado, error estándar, CV e IC del registro público. Cuando una celda hija suprimida podría reconstruirse restando sus hermanos conocidos de un padre visible, se aplica `complementary_suppression` al padre y a su copia pertinente para ocultar esa ruta de deducción; se conserva la relación de evidencia sin reconstruir el valor. La ausencia de observaciones produce estado sin evidencia y `null`, nunca “cero personas”.

### Reconciliación R/INEGI y límites [P09]

La aceptación numérica incluye un oráculo independiente con R `survey` y una reconciliación contra referencias oficiales; ambas pasan como comprobaciones de la implementación para los insumos aceptados. La diferencia relativa de SE nacional sin ajuste/tuning se conserva exactamente como diagnóstico (`-0.0037148696737544095`); no se calibra el resultado para forzar coincidencia. Esto no convierte la precisión del proyecto en precisión oficial: `official_precision=false` y las celdas con aproximación singleton permanecen en `REVIEW`. La coincidencia puntual no basta para certificar varianzas oficiales.

### Qué está aceptado y qué falta [P10]

La aceptación de Fase 2 cubre los ocho snapshots fijados, cálculos agregados, 26 casos del oráculo R, cuatro casos del oráculo analítico y reconciliación oficial; la aceptación de Fase 3 cubre 6,739 registros saneados, 4,209 comparaciones, 38 claims, cero errores de validación JSON persistido y cinco padres de supresión complementaria nulos. La Fase 4 ya tiene evidencia de identidad numérica instalada, informes, sellado, resolución de `current`, publicación real y CI de fixtures/PDF en Windows y Ubuntu. Existe una publicación preliminar; faltan la verificación independiente de Fase 4 y la aceptación final v1.0.0 de Fase 5. Tampoco se deben presentar inferencias causales, rankings o significancia estadística.

## English

### Scope, populations, and conceptual unit [P01]

The method separates two contexts. `national_15_plus_context` describes the national context of resident people with operational ages 15 or older; it admits EDA 15–98 and retains EDA 98 as operationally unknown age. `completed_professional_known_age` describes resident people with completed professional studies and known age: EDA 15–96 are ordinary ages and EDA 97 is the top-coded 97-or-more category, never literal age 97; EDA 98/99 and missing age are excluded from this cohort according to its universe. A completed response is `R_DEF=00`, residence is `C_RES∈{1,3}`, and the professional cohort requires `CS_P13_1=07` and `CS_P16=1`; technical, postgraduate, and incomplete studies are excluded. The product measures labor-market status for people whose declared field of study belongs to the stated universe; it does not measure vacancies, hiring demand, or causal effects of studying a field.

### Field of study, occupation, industry, and geography [P02]

`field_of_study` is educational field `CS_P14_C` validated against the quarter's CMPE catalog, with text keys preserved and conflicts or uncatalogued codes rejected. The three focal codes are `031300` Political science, `032100` Communication and journalism, and `033100` Law. Field of study, occupation, and industry are separate dimensions: the method does not assign occupation or industry from a field, and it does not approximate codes by text. The grain also preserves recorded sex, period, source, population, and geography. `mx` denotes the national context and the 32 entities use official codes; `ENT` and `CVE_ENT` are equivalent geographic aliases when the reviewed concept bridge, catalog, and exact source evidence support that equivalence, while the header change from 2025-Q3 remains explicit. Unreviewed concept, definition, or source drift blocks comparison.

### Time window and comparability [P03]

The accepted base contains eight quarters: 2024-Q3 through 2026-Q2. Adjacent-quarter comparisons are `qoq`, and same-quarter consecutive-year comparisons are `yoy`; both are descriptive contrasts. A cell is compared only when source, universe, geography, measure, price basis, method, concept, and period are comparable. Rotating samples may overlap, so the method does not use an independent-samples test, p-values, or significance claims for changes. Income is monthly nominal money, without purchasing-power adjustment. The reviewed `ENT`/`CVE_ENT` equivalence does not block by itself; unreviewed alias, catalog, edition, definition, or source drift blocks automatic comparison.

### Weights, design frame, and estimation [P04]

The estimator uses `FAC_TRI` as the final quarterly weight, `EST_D_TRI` as the stratum, and `UPM` as the cluster. It first constructs the complete responding resident frame before restricting age, field, entity, sex, or outcome, preserving the clusters and strata needed for domains. Variance uses ultimate-cluster Taylor linearization with final weights and the full frame (`taylor_ultimate_cluster_wr_final_weights_v1`). Weights must be finite and nonnegative; zero weights require explicit audit, do not count as support, and cannot create a PSU without positive support.

### Singletons, intervals, and precision [P05]

A singleton stratum fails by default. The accepted package permits an explicit project adjustment (`singleton_policy=adjust`) that centers the singleton contribution on the grand mean of PSUs; the result remains `REVIEW` with `official_precision=false`. Intervals are nominal 90%: normal Wald for totals/means and logit-delta for interior proportions; proportions at 0/100 do not receive degenerate certainty intervals. `n<30` or fewer than two domain PSUs yields `UNKNOWN` and `value=null` for insufficient support. With sufficient support, `MEASURED` requires CV below 15%, every other gate to pass, and no project singleton adjustment; CV from 15% to below 30%, singleton adjustment, or another nonofficial precision condition yields `REVIEW` and may retain a value with a reason. CV at least 30%, a boundary, zero variance, zero denominator, a degenerate interval, or zero design degrees of freedom leaves `value=null` with an explicit reason. Project precision is an approximation and is not official INEGI precision.

### Observations, ESS, and zeros [P06]

`sample_size`/`observed_n` is the number of observed people contributing to the relevant denominator; it is never a weight sum or an ESS. Weighted denominator, weighted support, PSUs, strata, and design degrees of freedom remain separate diagnostics. An observed zero is retained only when the variable definition confirms it; missing, unspecified, or unsupported data remain null/`UNKNOWN` and are never converted to zero. Suppressed public estimates do not leak weighted denominators or precision diagnostics.

### Income and conditional measure [P07]

`positive_income_mean` is the nominal monthly mean conditional on occupied people with an exact positive known amount: `ING7C∈{1,…,5}` and `INGOCUP∈[1,999998]`. `INGOCUP=0` and `999999` are not valid positive amounts; `ING7C=6` means no income and `ING7C=7` means unspecified income. Known bands without an exact amount may contribute to income-state/share measures, but not to the positive-amount mean; band/amount contradictions are excluded. Therefore the positive mean and positive-known-income coverage have explicit universes and must not be read as the mean income of all occupied people.

### Status, support, and suppression [P08]

Each cell retains `status`, `reason`, `value`, `evidence_refs`, method, and provenance. `UNKNOWN` or `BLOCKED` require `value=null`; `REVIEW` may retain a value only with a documented reason and nonofficial precision. Suppression also removes weighted denominator, weighted support, standard error, CV, and interval fields from the public record. When a suppressed child could be reconstructed by subtracting known siblings from a visible parent, `complementary_suppression` hides the parent and its relevant copy; provenance is retained without reconstructing the value. No observed evidence yields status without evidence and `null`, never “zero people.”

### R/INEGI reconciliation and limits [P09]

Numerical acceptance includes an independent R `survey` oracle and reconciliation against official references; both pass as implementation checks for the accepted inputs. The untuned national SE relative difference is retained exactly as a diagnostic (`-0.0037148696737544095`); the result is not calibrated to force agreement. This does not turn project precision into official precision: `official_precision=false`, and cells using the singleton approximation remain `REVIEW`. Point-estimate agreement alone does not certify official variances.

### Accepted boundary and remaining gates [P10]

Phase 2 acceptance covers the eight pinned snapshots, aggregate calculations, 26 R-oracle cases, four analytical-oracle cases, and official reconciliation; Phase 3 acceptance covers 6,739 sanitized records, 4,209 comparisons, 38 claims, zero persisted JSON validation errors, and five null complementary-suppression parents. Phase 4 has installed numerical identity, report/rendering, sealing, current resolution, actual real publication and hosted Windows/Ubuntu fixture/PDF evidence. A preliminary public snapshot exists; independent Phase 4 verification and Phase 5 v1.0.0 acceptance remain open. Causal inference, rankings, and statistical significance must not be claimed.
