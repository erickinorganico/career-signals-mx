# Brújula Laboral MX — estado verificable

Fecha de auditoría: 2026-09-22. **Planeación M0: aceptada. Release analítico:
BLOCKED.** Las pruebas del prototipo se ejecutaron offline; la identidad y la
publicación en GitHub se comprobaron por separado. El repositorio es público,
rama `main`, cuenta `erickinorganico` con permiso `ADMIN`: commit inicial
`acace35` y checkpoint incompleto `7c34e66` publicados.

La revisión adversarial de la planeación obtuvo **PASS**, con ocho hallazgos
corregidos y verificados en [PLANNING-REVIEW](PLANNING-REVIEW.md). La referencia
técnica es [CONTRACT](CONTRACT.md); las tareas pendientes están en [PLAN](PLAN.md).

## Estado por superficie

| Superficie | Estado | Evidencia actual | Límite o siguiente gate |
|---|---|---|---|
| Planeación, alcance y decisiones | VERIFIED — documentación | 18 requisitos, 18 tareas, 5 ADRs; revisión adversarial PASS y aceptación del principal | M0 aceptado; M1–M5 pendientes, M6 condicional |
| Carga/schema de dataset | IMPLEMENTED | `brujula/data.py`, `contracts/dataset.schema.json`, `data/fixtures/pilot.json` existen; la prueba `tests/test_data.py::test_load_fixture_is_strict_and_keeps_nulls` se recoge | Fixture auditada: 9 filas/9 combinaciones únicas frente a target 54; faltan 45 combinaciones, sin reparación en esta auditoría |
| Calidad y comparabilidad | IMPLEMENTED | `brujula/quality.py` y `tests/test_quality.py` existen; subconjunto ejecutado: 7 passed, exit code 0 | Requiere ampliar negativos y comprobar estados y gates contra la validación completa |
| DuckDB | IMPLEMENTED | `brujula/warehouse.py` y `tests/test_data.py::test_warehouse_materializes_normalized_tables` se recogen | La materialización integrada debe formar parte del replay completo |
| Pipeline, receipts y refresh fallido | PARTIAL | `brujula/pipeline.py`, `tests/test_pipeline.py` y `scripts/verify.ps1` existen; hay casos de receipts y refresh en el código de pruebas | No hay validación de suite completa por error de colección en reportes |
| Source Scout | VERIFIED | `brujula/scout.py`, `tests/test_scout.py` y catálogo local existen; `pytest tests/test_scout.py -q` produjo 11 passed, exit code 0 | La promoción/publicación requiere gate de integración |
| Agentes, referencias e insights | PARTIAL | `brujula/agents.py` existe y `pipeline.py` lo invoca | `contracts/agent-run.schema.json` no existe en la auditoría; falta verificar refs, inyección y publicación |
| Reportes Markdown/HTML y gráficas | BLOCKED | `tests/test_report.py` importa `brujula.report` | `brujula/report.py` no existe; la colección completa falla antes de ejecutar reportes |
| Visualización analítica | DOCUMENTED | `docs/VISUALIZATION.md` define Matplotlib, null como gap, metadata y separación campo/ocupación | No hay evidencia ejecutable hasta restaurar `brujula/report.py` |
| README y licencia | VERIFIED — documentación | README ES/EN, MIT y THIRD_PARTY_NOTICES revisados; checker documental comprueba entregables, enlaces locales, JSON y patrones de secretos/rutas privadas | No es auditoría exhaustiva de seguridad ni de dependencias; clean setup sigue pendiente |
| Publicación GitHub | VERIFIED — checkpoint | Push `7c34e66` verificado en [erickinorganico/career-signals-mx](https://github.com/erickinorganico/career-signals-mx), público y rama `main` | La publicación del código incompleto y los documentos no constituye un release analítico |

## Checks ejecutados

El 2026-09-22 se ejecutó con `.venv/Scripts/python.exe`:

```text
pytest --collect-only -q
25 tests collected, 1 error
exit code 2
ERROR tests/test_report.py: ModuleNotFoundError: No module named 'brujula.report'
```

El subconjunto de datos y calidad se ejecutó así:

```text
pytest tests/test_data.py tests/test_quality.py -q
7 passed in 1.49s
exit code 0
```

La suite de Scout se ejecutó por separado:

```text
pytest tests/test_scout.py -q
11 passed in 0.51s
exit code 0
```

La auditoría de cobertura de la fixture reportó:

```text
rows=9
target=54  # 3 fields × 2 geographies × 3 periods × 3 metrics
unique_combinations=9
missing=45
extra=0
null_values=2
status_counts={'REVIEW': 7, 'UNKNOWN': 2}
```

El target de 54 y la brecha de 45 quedan registrados como deuda de datos; no
se implementaron cambios en la fixture durante esta auditoría.

Los `7 passed` solo acreditan ese subconjunto y esa versión del árbol durante
esta auditoría. No acreditan pipeline, Scout, agentes ni reportes. La colección
completa no es verde porque falta `brujula.report`.

## Decisión de release

La entrega de planeación M0 está aceptada como baseline implementable. Su
validación documental se ejecuta con `python scripts/check_docs.py` y
`git diff --check`; incluye revisión de enlaces, JSON, rutas privadas,
patrones de credenciales y atribución del contenido que se publica. No incluye
revalidación de fuentes remotas ni un audit de vulnerabilidades.

Estado del release analítico: **BLOCKED**. El prototipo no debe presentarse
como release ni como medición laboral real. Para avanzar se
requieren, como mínimo, el módulo de reportes, su validación integrada, el
schema/contrato de agent run, el replay limpio y los gates de licencia, secretos,
receipts y publicación descritos en [VALIDATION-PLAN.md](VALIDATION-PLAN.md).
