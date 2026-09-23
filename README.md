# Brújula Laboral MX

**Investigación reproducible para interpretar el mercado laboral mexicano.**
Un repositorio de Analytics, pipelines locales y automatización con evidencia,
para explorar qué se puede observar sobre estudiar un campo y trabajar en una
ocupación sin tratarlos como equivalentes.

[English](README.en.md) · [Documentación](docs/README.md) · [Alcance](docs/SCOPE.md) · [Estado verificado](docs/STATUS.md)

> **Versión 0.1.0: MVP sintético implementado y verificado.** La
> demo local genera artefactos reproducibles. Los datos incluidos son **sintéticos** y no
> representan estimaciones de México, oportunidades de empleo ni recomendaciones
> para elegir una carrera. Consulta los bloqueadores y resultados de pruebas en
> [STATUS](docs/STATUS.md).

## Qué construimos

El objetivo es un observatorio analítico que pueda repetirse desde sus fuentes:
registro de autoridad y términos, captura con recibos y hashes, tablas con
conceptos separados, controles de calidad y comparabilidad, gráficas exportables
y briefs que distingan observación, interpretación y recomendación.

La interacción de esta versión ocurre mediante **archivos, scripts y CLI**.
Las salidas son DuckDB, CSV/Parquet/JSON, gráficas SVG/PNG y reportes
Markdown/HTML. No incluye frontend, backend de aplicación ni sitio navegable.
No requiere servicios de inferencia pagados ni hosting.

## Piloto definido

| Aspecto | Decisión de diseño |
|---|---|
| Campos | Derecho; Comunicación y periodismo; Ciencias políticas |
| Geografías | México y Jalisco ilustrativo |
| Periodos | 2025-Q2, 2025-Q3 y 2025-Q4 |
| Medidas | Personas ocupadas, ingreso mensual medio nominal y participación de mujeres |
| Datos | Fixture propio, inequívocamente sintético; 54 observaciones y 7 filas `UNKNOWN`/`null` |
| Fuente real futura | ENOE de INEGI, condicionada a validar licencia, clasificación, ponderación y precisión |

Esta selección sirve para probar el flujo analítico. No identifica las mejores
carreras ni reproduce las cifras de OLA o IMCO. Informalidad, vacantes,
recomendación individual y cobertura LATAM quedan fuera del primer piloto.

## Empezar por las decisiones

1. [Mandato y reglas de autoridad](docs/PROJECT-CHARTER.md): qué está autorizado.
2. [Scope](docs/SCOPE.md) y [PRD](docs/PRD.md): preguntas, usuarios, requisitos y exclusiones.
3. [Especificación](docs/SPEC.md), [contratos](docs/CONTRACT.md) y [metodología](docs/METHODOLOGY.md): cómo debe funcionar.
4. [Arquitectura](docs/ARCHITECTURE.md) y [ADRs](docs/decisions/README.md): decisiones y alternativas.
5. [Plan de trabajo](docs/PLAN.md), [roadmap](docs/ROADMAP.md) y [riesgos](docs/RISKS.md): dependencias y criterios de cierre.
6. [Validación](docs/VALIDATION-PLAN.md), [revisión adversarial](docs/PLANNING-REVIEW.md) y [estado actual](docs/STATUS.md): qué debe probarse y qué se comprobó.

## Ejecutar la demo local

Requisitos para estos comandos: Git, Python 3.12 y `uv` disponible. También se
puede crear un `venv` con Python e instalar `requirements.txt` con `pip`. El
entorno y las dependencias quedan fuera del repositorio.

```powershell
git clone https://github.com/erickinorganico/career-signals-mx.git
cd career-signals-mx
uv venv --python 3.12
uv pip sync requirements.txt
.venv/Scripts/python.exe scripts/check_docs.py
.venv/Scripts/python.exe -m brujula demo --as-of 2026-09-22 --output artifacts/demo
.venv/Scripts/python.exe -m brujula report --output artifacts/demo --format html
.venv/Scripts/python.exe -m brujula verify
```

En Linux/macOS cambia `.venv/Scripts/python.exe` por `.venv/bin/python`.
La alternativa sin `uv` es `python -m venv .venv` seguida de
`.venv/Scripts/python.exe -m pip install -r requirements.txt`. Los artefactos
de la demo quedan en `artifacts/demo/`, incluyendo `current.json`, el run
sellado y `report/report.html`; `report` solo resuelve un `current` validado.
La verificación cubre contratos, negativos, evals, reportes y ejecución offline.
Consulta el [release y sus límites](docs/RELEASE.md), el
[recibo verificable](docs/evidence/release-receipt.json) y el
[ejemplo sintético](examples/synthetic/README.md). La demo no necesita red
ni datos externos después de instalar las dependencias.

La CLI incluye `build`, `demo`, `verify`, `report --output DIR --format
html|markdown` y `scout`. Scout es una
lectura de metadata optativa; un resultado de lectura no autoriza incorporar
cifras ni confirma que una metodología siga igual.

## Reglas de evidencia

- Un campo de estudio no es una ocupación; una persona ocupada no es una vacante.
- Un dato ausente permanece `null`. No es cero.
- `MEASURED`, `REVIEW`, `UNKNOWN` y `BLOCKED` expresan estados de evidencia;
  los datos sintéticos permanecen identificados y en revisión.
- Un cambio de universo, método, fuente, unidad o base de precios puede impedir
  comparar. Un ingreso nominal no mide poder adquisitivo.
- Un fallo de actualización invalida la salida actual, conservando el historial
  como historial; el lock de sistema se recupera tras una interrupción.
- Los agentes del prototipo usan replay determinista. No se afirma autonomía
  de investigación ni inferencia LLM en producción.

La auditoría de fuentes está en [SOURCES](docs/SOURCES.md). No se redistribuyen
microdatos ENOE ni cifras extraídas de fuentes con términos sin resolver.

## Estructura

```text
docs/                 Plan, specs, metodología, ADRs y estado
contracts/            Schemas versionados del dataset, runs, insights y agentes
data/catalog/         Catálogo de fuentes y permisos por uso
data/fixtures/        Datos sintéticos del MVP
brujula/              Loader, quality, pipeline, warehouse, reports y CLI
tests/                Pruebas offline y de integración local
scripts/              Comandos auxiliares y verificación documental
```

Consulta [CONTRIBUTING](CONTRIBUTING.md) para continuar el trabajo,
[ORCHESTRATION](docs/ORCHESTRATION.md) para la colaboración entre modelos y
[PROJECT-EFFICIENCY](PROJECT-EFFICIENCY.md) para el criterio de uso de Laya.
Código, documentación y fixtures originales bajo [MIT](LICENSE); las fuentes
externas conservan sus condiciones y atribución propias en los
[avisos de terceros](THIRD_PARTY_NOTICES.md).
