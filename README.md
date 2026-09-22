# Brújula Laboral MX

**Investigación reproducible para interpretar el mercado laboral mexicano.**
Un repositorio de Analytics, pipelines locales y automatización con evidencia,
para explorar qué se puede observar sobre estudiar un campo y trabajar en una
ocupación sin tratarlos como equivalentes.

[English](README.en.md) · [Documentación](docs/README.md) · [Alcance](docs/SCOPE.md) · [Estado verificado](docs/STATUS.md)

> **Estado: planeación aceptada; prototipo parcial.** El repositorio público
> contiene las especificaciones y un checkpoint de implementación. La demo
> completa todavía está bloqueada. Los datos incluidos son **sintéticos** y no
> representan estimaciones de México, oportunidades de empleo ni recomendaciones
> para elegir una carrera. Consulta los bloqueadores y resultados de pruebas en
> [STATUS](docs/STATUS.md).

## Qué construimos

El objetivo es un observatorio analítico que pueda repetirse desde sus fuentes:
registro de autoridad y términos, captura con recibos y hashes, tablas con
conceptos separados, controles de calidad y comparabilidad, gráficas exportables
y briefs que distingan observación, interpretación y recomendación.

La interacción de esta versión ocurre mediante **archivos, scripts y CLI**.
Las salidas previstas son DuckDB, CSV/Parquet/JSON, gráficas SVG/PNG y reportes
Markdown/HTML. No incluye frontend, backend de aplicación ni sitio navegable.
No requiere servicios de inferencia pagados ni hosting.

## Piloto definido

| Aspecto | Decisión de diseño |
|---|---|
| Campos | Derecho; Comunicación y periodismo; Ciencias políticas |
| Geografías | México y Jalisco ilustrativo |
| Periodos | 2025-Q2, 2025-Q3 y 2025-Q4 |
| Medidas | Personas ocupadas, ingreso mensual medio nominal y participación de mujeres |
| Datos | Fixture propio, inequívocamente sintético; cobertura objetivo de 54 observaciones |
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

## Inspeccionar el checkpoint local

Requisitos para estos comandos: Git, Python 3.12 y `uv` disponible. También se
puede crear un `venv` con Python e instalar `requirements.txt` con `pip`. El
entorno y las dependencias quedan fuera del repositorio.

```powershell
git clone https://github.com/erickinorganico/career-signals-mx.git
cd career-signals-mx
uv venv --python 3.12
uv pip install -r requirements.txt
.venv/Scripts/python.exe scripts/check_docs.py
.venv/Scripts/python.exe -m pytest tests/test_data.py tests/test_quality.py tests/test_scout.py -q
```

En Linux/macOS cambia `.venv/Scripts/python.exe` por `.venv/bin/python`.
Estos comandos inspeccionan documentación y un subconjunto del prototipo; no
constituyen evidencia de instalación limpia o E2E completo. La instalación
desde un entorno vacío es un criterio pendiente del release.

Los comandos previstos por la CLI son `python -m brujula demo`,
`python -m brujula verify` y `python -m brujula scout`. **Demo y verify todavía
no cierran en verde**: faltan componentes declarados en STATUS. Scout es una
lectura de metadata optativa; un resultado de lectura no autoriza incorporar
cifras ni confirma que una metodología siga igual.

## Reglas de evidencia

- Un campo de estudio no es una ocupación; una persona ocupada no es una vacante.
- Un dato ausente permanece `null`. No es cero.
- `MEASURED`, `REVIEW`, `UNKNOWN` y `BLOCKED` expresan estados de evidencia;
  los datos sintéticos permanecen identificados y en revisión.
- Un cambio de universo, método, fuente, unidad o base de precios puede impedir
  comparar. Un ingreso nominal no mide poder adquisitivo.
- Un fallo de actualización debe invalidar la salida actual, conservando el
  historial como historial. Esta es una obligación de diseño pendiente de E2E.
- Los agentes del prototipo usan replay determinista. No se afirma autonomía
  de investigación ni inferencia LLM en producción.

La auditoría de fuentes está en [SOURCES](docs/SOURCES.md). No se redistribuyen
microdatos ENOE ni cifras extraídas de fuentes con términos sin resolver.

## Estructura

```text
docs/                 Plan, specs, metodología, ADRs y estado
contracts/            Schemas presentes; los faltantes constan en STATUS
data/catalog/         Catálogo de fuentes y permisos por uso
data/fixtures/        Datos sintéticos del prototipo
brujula/              Código parcial de ingesta, validación y análisis
tests/                Pruebas existentes; suite completa aún bloqueada
scripts/              Comandos auxiliares y verificación documental
```

Consulta [CONTRIBUTING](CONTRIBUTING.md) para continuar el trabajo,
[ORCHESTRATION](docs/ORCHESTRATION.md) para la colaboración entre modelos y
[PROJECT-EFFICIENCY](PROJECT-EFFICIENCY.md) para el criterio de uso de Laya.
Código, documentación y fixtures originales bajo [MIT](LICENSE); las fuentes
externas conservan sus condiciones y atribución propias en los
[avisos de terceros](THIRD_PARTY_NOTICES.md).
