# Contrato de investigación ENOE v2

Versión `2.0` · JSON UTF-8 · Draft 2020-12 · investigación local.
Este contrato es independiente del [contrato v1](CONTRACT.md). No cambia el
schema, la calidad ni el fixture sintético v1. `research-v2.schema.json` acepta
diagnósticos internos; `research-v2-public.schema.json` acepta solo la
proyección pública. Ambos viajan como recursos del paquete Python existente.

## Interfaces y autoridad

`validate_research_v2(payload) -> list[dict]` y
`validate_public_research_v2(payload) -> list[dict]` devuelven `[]` cuando el
objeto pasa schema y semántica; los fallos tienen `id` y `message` ordenados.
`public_research_projection(payload) -> dict` exige primero el contrato interno,
construye el objeto público por lista permitida y lo valida antes de devolverlo.
El publicador, exportador y renderer de fases posteriores deben consumir esa
salida, nunca `estimate` ni el bundle diagnóstico.

La raíz exige `schema_version`, `sources`, `populations`, `fields_of_study`,
`occupations`, `industries`, `geographies`, `recorded_sexes`, `periods`,
`metrics`, `methods`, `evidence` y `records`. Cada catálogo tiene IDs únicos;
las referencias deben resolver. Fuente y registro comparten periodo; método,
versión y diseño deben admitir la fuente. Las referencias de evidencia del
registro deben pertenecer a su fuente. El periodo tiene fechas válidas sin
superposición; trimestres adyacentes son distintos y válidos.

El grain único de `records` es:

```text
(source_snapshot_id, population_id, field_of_study_id, occupation_id,
 industry_id, geography_id, recorded_sex_id, period_id, metric_id, method_id)
```

`all` designa agregación deliberada y `unknown` categoría desconocida cuando
el catálogo correspondiente los declara. JSON `null` significa dato no
disponible, nunca cero. Campo de estudios, ocupación e industria no se unen ni
intercambian automáticamente. Cada `population_id` debe existir en
`POPULATION_DEFINITIONS` de `brujula.populations`: ese módulo es la única
autoridad para `national_15_plus_context` y
`completed_professional_known_age`. El primero incluye EDA 98 como edad
operativamente desconocida; el segundo acepta 15–97 y estudios profesionales
terminados. Ninguno implica que la carrera reportada sea toda licenciatura
previa de una persona.

## Registro interno y proyección pública

| Campo | Interno | Público |
|---|---|---|
| `estimate` | Requerido; número diagnóstico o null | Prohibido |
| `value` | Valor autorizado por el gate o null | Igual valor autorizado o null |
| `weighted_denominator` | Número ponderado o null; jamás `sample_size` | Null cuando `value` es null |
| `sample_size` | n observado, entero | Se conserva como cobertura observada |
| `support.n_psu_design`, `n_strata_design`, `n_psu_domain`, `n_strata_domain`, `design_df` | Soporte no ponderado del diseño completo y dominio contribuyente | Se conserva, con nombres explícitos |
| `support.weighted_support_total` | Agregado ponderado diagnóstico o null | Null cuando `value` es null |
| `precision.standard_error`, `coefficient_variation`, `ci90_lower`, `ci90_upper` | Diagnósticos numéricos o null | Null cuando `value` es null |
| `precision.method`, `ci_method`, `level`, `singleton_policy`, `official_precision` | Procedencia y política de precisión | Se conservan; `level` es 0.90 |
| `status`, `reason`, `evidence_refs`, `synthetic` | Estado, motivo, evidencia y origen explícitos | Se conservan |

`UNKNOWN` y `BLOCKED` obligan `value=null` y motivo. `REVIEW` puede tener
valor si el gate de precisión lo autorizó (por ejemplo, CV de revisión o
ajuste singleton documentado), o quedar suprimido con motivo. `REVIEW` por sí
solo no borra el valor. `MEASURED` requiere valor, motivo null y origen no
sintético. Un `value` visible coincide exactamente con el `estimate` autorizado;
redondear corresponde a la presentación, no a este contrato. Los registros
sintéticos llevan `synthetic=true` y no afirman medición oficial.

El validador rechaza un valor visible con `sample_size<30`, menos de dos UPM
contribuyentes, cero grados de libertad del diseño, denominador ponderado
ausente o no positivo, error estándar ausente o cero, CV ausente o al menos
30%, IC90 ausente/degenerado, valor cero con CV indefinido, o proporción en
0/100. `MEASURED` exige además CV menor que 15%; CV de 15% a menos de 30%
puede ser `REVIEW` con motivo. Un ajuste singleton del proyecto también puede
ser `REVIEW` con valor y `official_precision=false` si supera los demás gates.
Estas comprobaciones validan diagnósticos provistos; fase 2 calcula las
estimaciones y varianzas y contrasta su precisión con R e INEGI.

Cuando el valor es null, la proyección pone null en denominador ponderado,
total ponderado de soporte, error estándar, CV y ambos extremos del IC90.
Conserva n observado, UPM, estratos, grados de libertad, método, nivel y
motivo para mostrar cobertura sin revelar la estimación. El schema público
rechaza tanto la clave `estimate` como cualquier cifra diagnóstica en una fila
suprimida. Las pruebas usan sentinelas idénticos para `estimate`, denominador
y total ponderado anidado, más un centinela de intervalo independiente.

Los componentes de precisión no se certifican por este contrato. El método
de varianza (`precision.method`) y el de intervalo (`precision.ci_method`) se
separan; por ejemplo, Taylor linealizado y `normal_wald_90` o
`logit_delta_normal_90`. `singleton_policy=adjust` requiere revisión y
`official_precision=false`; el ajuste del proyecto no se presenta como
tratamiento oficial del INEGI. Soporte de diseño y dominio son contadores
distintos. Fase 2 calcula y contrasta los intervalos, CV y soporte real.

`unit` admite `people`, `percent`, `MXN/month` y `hours/week`. Solo
`MXN/month` usa `price_basis=nominal`; las otras unidades usan
`not_applicable`. Ingresos positivos conocidos requieren un denominador
propio: `ING7C=6` identifica sin ingreso, `7` no especificado y
`INGOCUP=0` por sí solo no demuestra salario cero. Las funciones puras de
`brujula.populations` separan n observado y sumas ponderadas; ni una suma de
pesos ni `design_df` son tamaño muestral efectivo.

## Custodia, límites y compatibilidad

Cada fuente conserva `url`, SHA-256, términos INEGI, autoridad y hora de
adquisición. `evidence_refs` resuelve a la misma fuente que el registro.
Fuente: INEGI, Encuesta Nacional de Ocupación y Empleo; selección, estimación
y transformación de Brújula Laboral MX, no realizadas ni avaladas por INEGI.
ZIP y filas de personas permanecen locales. Este contrato no activa una
fuente, aprueba una cifra ni autoriza publicar microdatos.

La equivalencia conceptual de `ENT` con `CVE_ENT` sigue en revisión de fase 3
(`ANA-03`). La codificación completa de filas de personas y el tratamiento
numérico de ingresos siguen en fase 2 (`STAT-01`/`STAT-06`). La reconciliación
de errores estándar con R e INEGI y la política singleton siguen siendo gates
numéricos posteriores. Los ocho paquetes y sus miembros están documentados en
[SOURCES.md](SOURCES.md).
