# Benchmark de repositorios comparables

Revisión: 2026-09-22. Se consultaron las páginas públicas de GitHub, los
README, árboles de archivos y archivos de implementación o documentación
enlazados por cada repositorio. La revisión sirve para diseñar la versión final
de Brújula; no copia código, datos ni licencias. Las afirmaciones sobre cada
repositorio se limitan a lo visible en sus fuentes primarias.

## Criterio de comparación

Se priorizaron repositorios que resuelven al menos dos de estas superficies:
encuestas complejas, datos laborales/educativos, trazabilidad de fuentes,
reproducibilidad offline, incertidumbre, QA de datos o publicación de resultados.
Los repositorios de software estadístico son referencias de método; los
paquetes centrados en ENOE y los observatorios son referencias de producto
laboral; los ejemplos educativos no se tratan como equivalentes de producción.

| Repositorio | Revisión observada | Licencia | Tipo y cobertura | Robustez para este benchmark |
|---|---|---|---|---|
| [aniuxa/renoe](https://github.com/aniuxa/renoe) | rama `master`, 19 commits; README, árbol `R/` y `descarga_enoe.R`/`utils.R` consultados | AGPL-3.0 | Paquete R de descarga, carga, unión y procesamiento de microdatos ENOE desde 2005; incluye armonización de carreras | **Referencia de producto/datos laboral muy próxima; no es un release final de observatorio** |
| [jcms2665/joinENOE](https://github.com/jcms2665/joinENOE) | rama `master`, 13 commits; README, `R/`, `data`, `man` y `DESCRIPTION` consultados | No se identificó una licencia clara en la página revisada | Utilidad R estrecha para unir tablas ENOE y módulos mediante claves identificadas | **Referencia de integración ENOE; no evidencia de producto, incertidumbre o release** |
| [simonaseno/NHANES](https://github.com/simonaseno/NHANES) | rama `main`, 28 commits; README y árbol consultados | MIT para código/documentación; datos CDC conservan sus términos | Pipeline R manifest-driven para CBC y DEMO de NHANES, ciclos 1999–2018; datos públicos de salud, no laborales | **Robusto y directamente comparable en pipeline** |
| [CDCgov/surveytable](https://github.com/CDCgov/surveytable) | rama `master`, 168 commits; README, estructura R y ejemplo NAMCS 2019 | Apache-2.0 | Paquete R para encuestas complejas: pesos, estratos, conglomerados, SE, IC y baja precisión; ejemplo integrado | **Robusto como componente estadístico** |
| [samplics-org/svy](https://github.com/samplics-org/svy) | rama `main`, 312 commits; README, `pyproject.toml`, `uv.lock`, paquetes | MIT | Ecosistema Python/Rust para diseño, ponderación, estimación, pruebas y modelos de encuestas; ejemplo offline incluido | **Robusto como referencia de incertidumbre** |
| [sheffield-health-and-work-modelling/lfsclean](https://github.com/sheffield-health-and-work-modelling/lfsclean) | rama `master`, 80 commits; README, `R/`, `data-raw/`, `man/`, tests y vignettes | GPL-3.0 | Limpieza de Labour Force Survey británica, cortes trimestrales y longitudinales de cinco trimestres, 1993–2023 | **Robusto para armonización laboral; no es un observatorio final** |
| [uscensusbureau/DAS_2020_GLS_Uncertainty_Evaluation](https://github.com/uscensusbureau/DAS_2020_GLS_Uncertainty_Evaluation) | rama `main`, 14 commits; README, `GLS/`, drivers, script de covarianza y `DATA_PRODUCT_README` | CC0-1.0 | Código Census Bureau para IC de GLS y evaluación de incertidumbre de privacidad en Census 2020; requiere Spark/EMR | **Robusto en incertidumbre, requiere infraestructura ajena a la operación local prevista** |
| [alan-turing-institute/QUIPP-pipeline](https://github.com/alan-turing-institute/QUIPP-pipeline) | rama `develop`, 550 commits; archivado el 2025-09-10; `datasets`, `metrics`, `synth-methods`, Docker y workflows | MIT | Generación de población sintética con métricas de utilidad y privacidad; los datasets pueden ser restringidos/sintéticos según flujo | **Robusto en separación método-métrica; ejemplo archivado** |
| [IngBilbao/observatorio-mercado-laboral](https://github.com/IngBilbao/observatorio-mercado-laboral) | rama `main`, 0 estrellas; `proyecto.md` y estructura declarativa consultados | No se identificó una licencia de código clara en la página revisada | Propuesta de observatorio de habilidades con Python, Excel, Power BI, scraping y modelos; fuentes heterogéneas | **Ejemplo de producto, no evidencia de pipeline robusto** |

La comparación de producto laboral queda concentrada en `renoe`, `joinENOE` y
el observatorio de Bilbao. NHANES, `surveytable`, `svy`, `lfsclean`, DAS y
QUIPP son comparables principalmente por método, QA o publicación reproducible;
no se presentan como competidores de cobertura mexicana.

## Hallazgos por repositorio

### renoe: referencia de dominio ENOE y carreras

El repositorio [aniuxa/renoe](https://github.com/aniuxa/renoe) separa `R/`,
`man`, `vignettes`, tests y documentación. El README y la implementación
publicada muestran funciones para descargar, leer y fusionar `viv`, `hog`,
`sdem`, `coe1` y `coe2`, además de procesar variables sociodemográficas,
laborales y de tiempo. También contiene funciones de armonización de carreras
y SINCO. La licencia declarada es AGPL-3.0; por ello se usa como evidencia de
diseño y no como dependencia o código reutilizable aquí.

La función interna `.construir_url_enoe()` en
[`R/utils.R`](https://github.com/aniuxa/renoe/blob/master/R/utils.R) registra
estas rutas oficiales observadas en el código: base
`https://www.inegi.org.mx/contenidos/programas/enoe/15ymas/datosabiertos/`;
para 2017 y 2018-T1, `{año}/{año}_trim{trimestre}_enoe_csv.zip`; para
2018-T2, `{año}/conjunto_de_datos_enoe{año}_{trimestre}t_csv.zip`; para
ENOEN 2020-T3–2022, `{año}/conjunto_de_datos_enoen_{año}_{trimestre}t_csv.zip`;
y para la estructura normal, `{año}/conjunto_de_datos_enoe_{año}_{trimestre}t_csv.zip`.
Además, el tratamiento especial 2022-T1 observa
`https://www.inegi.org.mx/contenidos/programas/enoe/15ymas/microdatos/enoe_n_2022_trim1_csv.zip`.
Estas son rutas leídas del código, no una descarga o aprobación de fuente para
Brújula. La revisión no encontró el literal `CS_P14_C` dentro de ese
constructor; la variable sí aparece en la [documentación oficial de
ENOE](https://www.inegi.org.mx/programas/enoe/) como la clave de carrera, por
lo que debe tratarse como concepto/variable catalogada y no como nombre
supuesto de ZIP.

La descarga valida año/trimestre, contempla la ausencia de 2020-T2, limita
2026 a T1/T2, reintenta la descarga, extrae el ZIP y busca CSV por tabla. El
flujo también expone una limitación relevante: en el procesamiento de tiempo,
valores faltantes pueden convertirse en cero para construir agregados. Eso
requiere una decisión metodológica explícita antes de adoptarlo.

Adopción concreta: registrar por trimestre la URL exacta, formulario/tabla,
variable de carrera, cobertura, versión del clasificador, SHA del raw y
resultado de cardinalidad de cada unión. Mantener la implementación propia y
la separación `field_of_study`/`occupation`; no copiar código AGPL ni inferir
que una ruta observada autoriza activación oficial.

### joinENOE: unión ENOE como componente acotado

[`jcms2665/joinENOE`](https://github.com/jcms2665/joinENOE) es un paquete R
pequeño que recibe una tabla de origen, una tabla de destino y un grupo de
variables, y ayuda a unir tablas ENOE y módulos descargados por el usuario
desde INEGI. Su estructura (`R/`, `data`, `man`, `DESCRIPTION`) y README son
útiles para documentar claves y relaciones, pero la página revisada no muestra
una licencia clara, pruebas de release, incertidumbre, manifest de raw ni
reporte reproducible.

Adopción concreta: exigir una especificación de unión por tabla con claves,
cardinalidad esperada, filas antes/después y evidencia de duplicados; conservar
las tablas y periodos separados hasta que el contrato de Brújula valide la
comparabilidad. `joinENOE` no es evidencia suficiente para activar una fuente
ni para publicar estimaciones.

### NHANES: el patrón más cercano para adquisición y provenance

El repositorio separa `config`, `data`, `pipelines`, `scripts`, `tests`,
`outputs/sample`, `renv.lock` y documentación Quarto. El README declara un
alcance validado de CBC/DEMO, distingue el segundo examen no ponderado y evita
inventar un peso universal. La salida incluye RDS derivados, `provenance.csv`
con URL/tamaño/SHA-256/fecha/dimensiones y `validation.csv` con filas,
columnas y participantes únicos. Workflows separados descargan, prueban,
publican documentación y generan artefactos de release.

Adopción concreta: una tabla de catálogo por archivo/periodo/rol, una
provenance row por raw artifact, validación de cardinalidad antes de joins y
un output sample pequeño que pueda inspeccionarse sin descargar toda la fuente.
Limitación: no resuelve por sí solo la definición mexicana de campo de estudio,
ocupación o ingreso.

### surveytable: incertidumbre visible en la tabla final

Es un paquete R con `R/`, `vignettes`, `man`, datos de ejemplo y licencia
Apache-2.0. El ejemplo `namcs2019sv` expone diseño estratificado y cluster,
número de observaciones, conteo estimado, SE, límites de IC, porcentaje y SE.
También ofrece detección de estimaciones de baja precisión mediante reglas NCHS
u otras reglas elegidas por el usuario.

Adopción concreta: cada resultado publicado debe mostrar estimación, error o
IC, tamaño muestral y una bandera de precisión; la tabla alternativa del
reporte debe conservar esos campos. Limitación: es una biblioteca, no un
pipeline de fuente, receipt o publicación.

### svy: diseño de encuesta como objeto inmutable

El repositorio Python tiene `pyproject.toml`, `uv.lock`, paquetes y documentación
de quick tour. Su README describe un `Sample` inmutable que conserva el diseño
durante transformaciones y subpoblaciones; ajusta pesos de no respuesta,
calibración, raking y trimming junto con replicate weights. Declara validación
contra R `survey` a seis cifras significativas y resultados serializables con
semillas explícitas. Incluye una encuesta empaquetada que corre offline y una
opción de reportes HTML.

Adopción concreta: un objeto/contrato de diseño que viaje con la observación,
una ruta de validación cruzada contra referencia independiente y semillas en
receipts. Limitación: sus métodos no autorizan activar ENOE ni resuelven
clasificaciones mexicanas.

### lfsclean: armonización laboral y advertencias de comparabilidad

El paquete R separa `data-raw`, `data`, `R`, `man`, `vignettes`, `public` y
tests. Limpia la LFS trimestral y longitudinal, crea valores reales con CPIH o
RPI y advierte que problemas de calidad motivaron la transición a TLFS/APS.
La estructura de paquete y documentación es más mantenible que un notebook
monolítico.

Adopción concreta: registrar transformación nominal/real, versión del índice,
regla de comparabilidad y periodo de transición como metadatos verificables.
Limitación: GPL-3.0 y cobertura UK hacen que sea referencia de diseño, no una
dependencia candidata.

### Census DAS GLS: incertidumbre como producto reproducible

El repositorio del U.S. Census Bureau contiene `GLS`, drivers, `run_cluster.sh`,
`setup_environment.sh` y un `DATA_PRODUCT_README`. Los drivers estiman IC por
nivel geográfico; un script construye covarianzas y contrasta pares de unidades
con derivaciones publicadas. El README exige Spark/EMR y dimensionamiento de
cluster, por lo que es una referencia fuerte de método, pero no un quick start
local.

Adopción concreta: publicar el estimando, la matriz o componentes de varianza,
el dominio geográfico y las limitaciones de la incertidumbre junto con el
resultado. Limitación: no trasladar el backend distribuido al piloto por
analogía.

### QUIPP: utilidad y privacidad junto al dato sintético

El repositorio archivado separa `datasets-raw`, `datasets`, `metrics`,
`synth-methods`, `examples`, Docker y workflows. Su objetivo explícito es
generar poblaciones sintéticas y emitir medidas de utilidad y privacidad; el
proyecto advierte que esos objetivos deben evaluarse simultáneamente.

Adopción concreta: cuando llegue una fuente real, mantener un track de utilidad
y otro de privacidad/licencia, con métricas y umbrales separados del resultado
analítico. Limitación: está archivado y el costo de los métodos no cabe en la
versión final de Brújula sin una decisión explícita.

### Observatorio de mercado laboral: útil como contraste de alcance

El documento describe una arquitectura Python → Excel → Power BI → Power
Automate, con scraping, NLP de habilidades, clustering, forecast Prophet y
regresión salarial. También propone reportes y alertas, pero la evidencia
visible es un plan de carpetas y scripts, no un dataset versionado, licencia
clara, manifest, tests de datos o reporte reproducido.

Conclusión acotada: adopta la separación conceptual entre extracción,
transformación y presentación solo como interfaz; no adoptes scraping,
pronósticos o dashboards como evidencia de una observación laboral.

## Benchmark de requisitos para la versión final

Estos requisitos son verificables en nuestro repositorio y no implican copiar la
implementación de los comparables.

| ID | Requisito verificable | Evidencia mínima esperada |
|---|---|---|
| BENCH-01 | Catálogo y raw provenance por fuente/periodo | URL, licencia, población, cobertura, fecha, SHA y rol por artifact |
| BENCH-02 | Diseño y universo viajan con cada estimando | contrato con universo, grain, peso, PSU/estrato/replicates o `not_applicable` explícito |
| BENCH-03 | Incertidumbre y precisión son visibles | SE/IC/CV, tamaño muestral, umbral y estado de baja precisión |
| BENCH-04 | Comparabilidad bloquea cambios semánticos | fuente, universo, geografía, método, unidad, base, periodo y concepto comparados |
| BENCH-05 | Pipeline reproducible desde entorno limpio | lockfile/requirements, comando offline, tests, receipt, manifest y raw hash |
| BENCH-06 | Artefactos de resultados son auditables | tabla accesible, reporte estático, metadata de fuente/periodo y hashes |
| BENCH-07 | QA separa cuarentena, desconocido y cero | casos rojos de duplicados, null, fuera de rango, cobertura y referencias |
| BENCH-08 | Release y límites tienen prueba independiente | revisión adversarial, licencia/secret scan, evaluación cruzada y publicación versionada |
| BENCH-09 | Datos sintéticos y reales no se mezclan | `synthetic`, source activation y estado de publicación bloquean bypasses |
| BENCH-10 | Cambios de fuente dejan historial recuperable | current failure wins, receipt write-once, publication-failure y runs históricos |

## Decisión para Brújula

La versión final debe adoptar de NHANES la separación de adquisición,
armonización y análisis; de `surveytable`/`svy` la incertidumbre visible y la
validación independiente; de `lfsclean` la comparabilidad nominal/real y las
advertencias laborales; y de QUIPP/DAS la medición explícita de utilidad,
privacidad o incertidumbre cuando corresponda. El observatorio de Bilbao queda
como contraste de producto y no como evidencia de rigor.

No se activará ENOE ni se importarán datasets de estos repositorios por esta
comparación. La fuente oficial seguirá bloqueada hasta cumplir M6, y las
licencias de software/datos se revisarán por separado antes de cualquier
publicación.
