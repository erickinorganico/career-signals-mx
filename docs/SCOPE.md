# Alcance — Brújula Laboral MX

Estado del documento: **baseline de planeación aceptado en M0**. Este documento
define el producto; la implementación, las pruebas y el release analítico
permanecen incompletos.

## Propósito

Brújula Laboral MX es un repositorio abierto de investigación analítica que
ayuda a estudiantes y personas que consideran cambiar de carrera a interpretar
señales del mercado laboral mexicano. Produce datos trazables, validaciones,
gráficas estáticas y briefs con evidencia. No ofrece una recomendación
individual ni predice resultados personales.

El producto se usa localmente mediante scripts y CLI. Sus salidas son tablas
DuckDB, CSV/Parquet cuando la licencia lo permite, gráficas SVG/PNG y reportes
Markdown/HTML. No es una aplicación, plataforma, frontend, backend ni servicio
web.

## Alcance inicial

La primera liberación verificable usa exclusivamente un fixture sintético y
visiblemente ilustrativo:

- campos de estudio: Derecho, Comunicación y periodismo, y Ciencias políticas;
- periodos: 2025-Q2, 2025-Q3 y 2025-Q4;
- geografías: México nacional y un segmento ilustrativo de Jalisco;
- métricas: `mean_monthly_income`, `employed_people` y `female_share`;
- estados públicos: `MEASURED`, `REVIEW`, `UNKNOWN` y `BLOCKED`, aunque todo
  valor sintético no nulo debe permanecer en `REVIEW`;
- almacenamiento local, validación de contrato, comparabilidad, recibos de
  ejecución, reportes estáticos y agentes deterministas de solo lectura.

El fixture demuestra el flujo y las salvaguardas. No representa estimaciones de
México, no contiene microdatos ENOE y no valida conclusiones sustantivas sobre
las tres carreras.

## Entregables de la primera liberación

1. Contratos JSON versionados para dataset, evidencia e insight packets.
2. Catálogo separado de fuentes oficiales candidatas, con términos, cobertura,
   método, estado de acceso y decisión de uso.
3. Fixture sintético con nulos intencionales, provenance y advertencia visible
   en cada salida.
4. Pipeline local reproducible con raw content-addressed, recibos inmutables,
   quality gate, DuckDB y exportaciones permitidas.
5. Comparaciones descriptivas que se bloquean cuando cambian fuente, universo,
   geografía, métrica, unidad, base de precios, metodología, concepto o
   condición sintética.
6. Gráficas y reportes estáticos en español, con documentación del repositorio
   en español e inglés.
7. Agentes de apoyo de solo lectura que proponen investigación, anomalías,
   mapeos o briefs; ninguna propuesta activa una fuente, bridge o publicación.
8. Pruebas unitarias, integración y E2E, más revisión metodológica adversarial,
   revisión de secretos/licencias y recibo de liberación.

## Fuera del alcance inicial

- frontend, backend, API servida, dashboard interactivo o aplicación navegable;
- asesoría personal, ranking normativo de carreras o promesas de empleabilidad;
- inferencia causal, pronósticos o equivalencia entre carrera, ocupación y
  vacante;
- scraping contrario a términos, APIs pagadas, credenciales externas, hosting
  obligatorio o servicios de inferencia;
- cifras de OLA, Data México o IMCO empaquetadas como dataset;
- observaciones ENOE numéricas, informalidad o salarios reales/deflactados;
- comparación automática entre periodos o países con metodología incompatible;
- alertas, instituciones educativas, cobertura LATAM o interfaz local visual.

## Extensión real posterior

México se amplía antes de considerar LATAM. La primera extensión candidata es
ENOE 2025-Q2 nacional y solo puede entrar al dataset tras validar de forma
conjunta:

- paquete, diccionario, variables y códigos CMPE oficiales;
- población y denominadores por métrica;
- factor de expansión, estrato, UPM, estimación de varianza y reglas de
  precisión;
- URL exacta, términos, atribución, SHA-256, parámetros, fecha de consulta y
  versión del código;
- compatibilidad conceptual y temporal con cada observación que se compare.

Que un archivo sea público no activa su uso. Los términos de redistribución, el
contrato metodológico y el source record deben quedar aprobados y verificables.
Informalidad, geografía subnacional y periodos adicionales requieren gates
metodológicos propios. LATAM requiere una revisión por país antes de compartir
ontología o series.

## Límites semánticos y de evidencia

`field_of_study`, `occupation`, `industry`, `geography`, `period` y `source`
son dimensiones distintas. Un bridge es un artefacto editorial con provenance,
confianza y estado `REVIEW`; nunca convierte un campo de estudio en ocupación.

Una ausencia permanece `null`. `UNKNOWN` y `BLOCKED` no se grafican como cero.
Cada claim debe resolver a evidence refs existentes y a un recibo con hash de
entrada. Un refresh fallido invalida la publicación actual; un éxito histórico
no puede presentarse como vigente.

## Autoridad y holds legítimos

El trabajo local de documentación, fixtures, código, pruebas aisladas y
preparación de publicación está autorizado. También está autorizada la
publicación en `erickinorganico/career-signals-mx` después de los checks de
secretos y licencias.

Se aplica un hold únicamente cuando falta una decisión material que no puede
inferirse: términos de redistribución, acceso a un dataset, activación de una
fuente o bridge, o una publicación externa distinta del repositorio autorizado.
El hold debe registrar el objeto exacto y no detener trabajo independiente ya
autorizado.

## Criterio de cierre del alcance inicial

El alcance se considera entregado cuando un entorno limpio puede instalar,
verificar y ejecutar la demo sin credenciales; todas las salidas identifican la
condición sintética; los casos rojos bloquean falsos ceros, series incompatibles
y claims sin evidencia; el reporte, las tablas y los recibos se reconstruyen de
forma determinista; y la revisión principal confirma pruebas, términos,
secretos y trazabilidad. La existencia de archivos o código parcial no satisface
este criterio.
