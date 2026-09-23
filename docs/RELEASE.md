# Release 0.1.0 — piloto sintético

[Publicado en GitHub como v0.1.0](https://github.com/erickinorganico/career-signals-mx/releases/tag/v0.1.0).

El primer release implementa M1–M5: validación, comparabilidad, trazabilidad,
DuckDB, exportaciones, reportes estáticos y propuestas deterministas de agentes.
Todas las cifras incluidas son **sintéticas**. No son estimaciones del mercado
laboral mexicano, vacantes ni recomendaciones de carrera.

## Contenido

- Fixture propio: 54 observaciones, tres campos de estudio, dos geografías,
  tres trimestres y tres métricas; siete observaciones `UNKNOWN`/null.
- Contratos JSON Schema y validación semántica; campos, ocupaciones e industrias
  conservan identidades separadas.
- Runs con raw content-addressed, recibos inmutables, manifest verificable y
  current que se invalida ante un fallo. Recuperación tras interrupciones.
- DuckDB normalizado, CSV/Parquet/JSON y reportes Markdown/HTML offline;
  cuatro gráficas en PNG y SVG, tablas alternativas y tres insights `REVIEW`.
- Seis roles deterministas de solo lectura, doce evals de evidencia y autoridad.
- Wheel instalable con fixture, schemas y catálogo incluidos; CLI reproducible
  sin checkout para demo/report/scout. `verify` requiere el checkout y tests.

El [ejemplo sintético](../examples/synthetic/README.md) permite inspeccionar las
salidas sin instalar Python. Es una copia estática del release, no un current
vivo ni una actualización de datos.

## Reproducción

Desde un checkout, con Python 3.12 y las dependencias de `requirements.txt`:

```powershell
python -m brujula verify
python -m brujula demo --as-of 2026-09-22 --output artifacts/demo
python -m brujula report --output artifacts/demo --format html
```

El último comando verifica current, raw, manifest y hashes antes de devolver
la ruta del reporte. No reutilices un enlace histórico como salida actual.
`--as-of` fija el reloj de freshness del replay; ejecutar hoy no hace recientes
los periodos sintéticos de 2025.

Para usar el wheel, instala primero las dependencias fijadas y después el
archivo `.whl` del release con `pip install --no-deps <archivo.whl>`.
Tras instalar, `python -m brujula demo` funciona fuera del checkout sin red.

## Evidencia de aceptación

89 tests y 12 evals PASS. CI PASS en Windows y Linux sobre el commit de la
etiqueta; wheel ejecutado fuera del checkout e integridad remota de assets
confirmada por SHA-256.

El [recibo de release](evidence/release-receipt.json) registra los resultados,
hashes, commits y enlaces de publicación. El recibo distingue la verificación
local, la ejecución instalada y CI remoto. La [revisión de implementación](IMPLEMENTATION-REVIEW.md)
cierra cinco hallazgos reproducidos; la [matriz SPEC](SPEC.md) enlaza requisitos
con sus verificaciones. El checkpoint de planeación conserva su recibo propio.

La revisión de dependencias cubre 23 paquetes fijados; el escaneo no encontró
vulnerabilidades conocidas al ejecutarse. No prueba la ausencia de vulnerabilidades.
El wheel contiene solo código y recursos originales; no incluye dependencias,
credenciales, entornos locales ni microdatos de terceros.

## Límites de esta versión

`official_snapshot` permanece bloqueado. M6 exige activar y validar un paquete
ENOE concreto, términos, clasificación, pesos, diseño muestral y precisión.
Los insights aceptan plantillas canónicas vinculadas a observaciones exactas;
v1 no acepta prosa agentic de comparaciones ni texto libre como evidencia.
Las comparaciones numéricas deterministas siguen disponibles bajo su gate.
No hay modelo de inferencia externo, servicio, frontend ni despliegue web.

El source scout captura metadata optativa del catálogo autorizado; su éxito no
activa una fuente ni autoriza extracción numérica. Las pruebas son locales,
con red deshabilitada y fixtures desechables.
