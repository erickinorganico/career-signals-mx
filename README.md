# Brújula Laboral MX

Investigación reproducible del mercado laboral mexicano con datos públicos de INEGI.

[Descargar publicación](https://github.com/erickinorganico/career-signals-mx/releases/tag/v0.9.0-preview.1) · [Informe PDF](https://github.com/erickinorganico/career-signals-mx/releases/download/v0.9.0-preview.1/brujula-laboral-mx-informe.pdf) · [English](README.en.md)

**Publicación del estado actual, por decisión del propietario.** El informe real cubre ocho trimestres ENOE, de 2024-T3 a 2026-T2. Incluye 97 páginas, nueve grupos de gráficas y 22 tablas enlazadas en CSV, Parquet y DuckDB. El paquete contiene HTML para consulta offline, Markdown, PDF, fuentes y manifiesto de integridad.

Los perfiles nacionales y campos focales tienen seguimiento de ocho trimestres; los demás campos, sexo registrado y 32 entidades se presentan para el último trimestre. Carrera, ocupación e industria se mantienen separadas. Los valores faltantes y suprimidos conservan `null`; la precisión calculada es **no oficial, REVIEW**. No constituye un ranking ni una recomendación personal.

El análisis incluye 6,739 registros, 4,209 comparaciones (las no comparables quedan bloqueadas) y 38 afirmaciones enlazadas a evidencia. La validación local pasó 592 pruebas Python, 30 controles Node, contraste independiente con R y replay numérico. La instalación nativa en [GitHub Actions](https://github.com/erickinorganico/career-signals-mx/actions/runs/36050222714) pasó en Windows y Ubuntu. La verificación independiente de Fase 4 y el cierre de Fase 5 siguen pendientes; no se declara completada la versión 1.0.0.

Descarga y extrae el ZIP; abre `research/report.html` o `research/report.pdf`. Consulta [el método](docs/METHODOLOGY.md), [el alcance](docs/SCOPE.md), [la guía de operación](docs/OPERATIONS.md), [el contrato vigente](docs/CONTRACT-V2.md), [la evidencia de publicación](docs/evidence/phase-04-publication-acceptance.json) y [el estado GSD](.planning/STATE.md). No se distribuyen microdatos ni se requiere una aplicación alojada.

---

## Documentación histórica del piloto sintético 0.1.0

El contenido siguiente describe el piloto anterior. Sus datos, periodos y alcance no son los del informe real enlazado arriba. Las guías bilingües actuales están enlazadas arriba; su auditoría de release final continúa en Fase 5.

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
