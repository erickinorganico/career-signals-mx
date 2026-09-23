# Revisión adversarial de implementación M1–M5

Fecha: 2026-09-22. Alcance: MVP sintético local, sin lectura de fuentes reales ni ENOE. Revisión independiente de código y pruebas aisladas; este documento no acredita publicación remota.

Estado: **PASS — revisión de implementación sintética**. Los cinco hallazgos de esta revisión tienen corrección verificada; no quedan bloqueos funcionales conocidos en el alcance revisado. La publicación remota y el sellado del paquete final tienen evidencia de release separada.

## Hallazgos reproducidos

| ID | Prioridad | Hallazgo | Evidencia inicial | Estado |
|---|---|---|---|---|
| IMPL-01 | P1 | IDs compartidos entre dimensiones confunden campo y ocupación en reportes e insights | Agregar una ocupación con el ID de Derecho y otra etiqueta conserva `quality.publishable=true`, pero `_maps` sustituye la etiqueta del campo por la ocupación | CERRADO: reportes e insights con repro independiente PASS |
| IMPL-02 | P2 | Un null inicial puede desordenar el eje temporal de ingreso | Anular la primera observación del primer grupo ordenado conserva publicación; el eje real de Matplotlib queda `2025 Q3, 2025 Q4, 2025 Q2` | CERRADO: repro independiente PASS |
| IMPL-03 | P2 | Wheel omite recursos requeridos fuera de `brujula` | `packages=["brujula"]` excluye contratos, catálogo y fixture, mientras el runtime busca esos recursos bajo el padre del paquete | CERRADO: wheel instalado sin checkout; demo y resolver PASS |
| IMPL-04 | P2 | Recuperación de crash pierde hash del input ya procesado | Interrumpir renderer deja un raw preservado pero journal/hash null; siguiente build sella el receipt recuperado `FAILED` con `input_sha256=null` | CERRADO: repro independiente PASS |
| IMPL-05 | P1 | Gate de insights admite prosa causal/números en palabras y comparación sintética marcada real | Tres packets alterados pasan `validate_agent_run` sin errores | CERRADO: tres negativos independientes rechazados y baseline aceptado |

IMPL-05 (P1, cerrado tras corrección): el validador M4 admitía inferencias nuevas fuera de la observación exacta. Cambiar `interpretation` a “La formación en este campo incrementa el ingreso.” o “El ingreso observado es de diez millones de pesos.” retornaba cero errores. Además, un packet con texto/id/refs exactos de una comparación sintética aceptaba `synthetic=false` y título “Cifras oficiales”, porque el anchor de comparación no deriva modo/título de las filas. El generador actual usa plantillas de observaciones y no produce esos packets, pero el validador anterior anunciado como gate semántico los aceptaba. Corrección verificada: la prosa se vincula a plantillas canónicas y v1 se abstiene de packets de comparación hasta contar con un contrato completo de provenance. Los tres probes originales ahora se rechazan; el baseline permanece aceptado. Esto no elimina las comparaciones deterministas usadas por las gráficas.

IMPL-01 afecta la identidad conceptual, incluso sin usar bridges. El esquema permite el mismo ID en dimensiones de distinto tipo; consumidores deben resolver `(concept_type, concept_id)`.

IMPL-02 no requiere fechas inválidas: falta el primer valor de una serie válida. La escala categórica adopta el orden de primera aparición de valores disponibles, no un calendario global. Se requiere fijar posiciones temporales compartidas por todas las series.

IMPL-04 se reprodujo con `patch("brujula.report.render_report", side_effect=KeyboardInterrupt)`, seguido por un nuevo build con input ausente para activar recuperación. Antes de recuperar existe un raw; después, el receipt del run interrumpido sigue sin hash. Se requiere persistir la procedencia antes de etapas posteriores y recuperarla del journal validado.

## Verificación de correcciones

Se repitieron los dos probes originales contra el renderer corregido: la etiqueta de Derecho permanece en `("field_of_study", id)` y la ocupación conserva su propia etiqueta; el eje con null inicial muestra `2025 Q2, 2025 Q3, 2025 Q4`. Ambos datasets mantienen `quality.publishable=true`. La revisión independiente reutilizó los checks afectados del owner, sin repetir el suite completo.

También se repitió el crash del renderer: current y journal conservan el SHA-256 exacto del fixture y el siguiente build recupera un receipt `FAILED` con ese mismo hash. IMPL-04 queda cerrado.

## Revisión ya realizada

- Inspección de `data.py`, `quality.py`, `warehouse.py`, `export.py`, `pipeline.py`, `runlock.py`, `report.py`, schemas de dataset/run y tests asociados.
- Confirmación por código: parseo rechaza JSON duplicado/NaN/Infinity; gates preservan null y estados; comparabilidad resuelve rangos de periodos y bloquea diferencias contractuales.
- Confirmación por código: materialización normalizada sin agregación por bridge; CSV neutraliza fórmulas; exportación precede al commit canónico y queda solo diagnóstica ante un fallo posterior.
- Confirmación por código: OS lock persistente se libera por cierre/crash; current es autoridad única; resolver verifica manifest/hashes y rechaza RUNNING/BLOCKED; índice humano carece de enlaces activos que puedan quedar obsoletos.
- Las comprobaciones positivas anteriores describen inspección, no sustituyen el registro de tests del release. No se repitió el suite completo durante la revisión.

También se inspeccionaron las correcciones visuales finales en `report.py` y la regresión de campos faltantes de `tests/test_report.py`:

- Los puntos y segmentos de cada serie usan el mismo color; la leyenda está fuera del área de datos. La figura PNG instalada de ingreso confirma este comportamiento y conserva el aviso sintético y la metadata.
- Las barras eligen el último periodo considerando todas las filas. Conservan los campos sin valor mediante la etiqueta “Sin dato”, sin barras de cero ni sustitución por periodos anteriores. La figura PNG instalada de participación de mujeres muestra tres campos, dos sin dato y una sola barra de 57.0%; la tabla mantiene sus ausencias.
- El principal reportó 10 tests de reportes verdes, incluida la regresión nueva de campos faltantes. La revisión inspeccionó esa prueba y las dos figuras finales; no volvió a ejecutar el suite.

## Evidencia integrada inspeccionada

- `artifacts/verification/verify.json`: PASS; docs, evals y pytest con exit 0.
- `artifacts/verification/junit.xml`: 88 tests, cero errores, fallos o skips. Se reutilizó esta ejecución del principal y no se repitió el suite completo en la revisión.
- `.cache/final-wheel-outside/wheel-check.json`: wheel instalado con `CHECKOUT_ROOT=None`; 54 filas, 7 nulos, 8 archivos de gráficas, 3 insights y manifest verificado.
- Run instalado inspeccionado: `20260923T010637-56a4720edd1b`, `SUCCEEDED`, estado analítico `REVIEW`, input SHA-256 `52a35afa56cd50ec71f69d1f959ba7192f861120867b5ca043ae8e35a4c34d3c`. La revisión volvió a ejecutar únicamente el resolver de integridad, que validó current, manifest, raw y artefactos.
- Wheel final: `artifacts/packages/final/career_signals_mx-0.1.0-py3-none-any.whl`, SHA-256 `55e7a9f35a7e54d23e86c02f2046522a309552cb69518f141213f3df346cf3dd`. Esta revisión recalculó el hash y comparó independientemente los 20 archivos runtime/recursos del wheel con el checkout: coincidencia exacta. Quedó resuelta la diferencia editorial anterior.
- La evidencia instalada registra Python 3.12.13, `CHECKOUT_ROOT=None`, ejecución fuera del checkout y `manifest_verified=true`. La revisión volvió a validar el current, raw, manifest y artefactos del run final. No hay requisito pendiente de reconstrucción del wheel.
- Los 88 tests del registro anterior y del source archive `3f3be9c` no se presentan como el conteo final después de agregar la nueva prueba de reportes. La verificación final integrada y CI se registran separadamente por el principal.

## Cierre y límites

El integrador ejecutó posteriormente la suite final: 89 tests PASS y 12 evals
PASS. Para publicar normalizó el fixture a LF, conforme a `.gitattributes`, y
repitió el empaquetado y replay aislado. Esta normalización conserva exactamente
el contenido JSON; los hashes del paquete y run canónicos están en el
[recibo de release](evidence/release-receipt.json). Los hashes anteriores de este
informe documentan la revisión independiente, no identifican el asset final.

IMPL-01 a IMPL-05 están corregidos y verificados en su alcance. El wheel final coincide con el código y los recursos revisados; no quedan acciones pendientes dentro de esta revisión. Esta revisión no sustituye el scan de secretos/licencias, la verificación final integrada/CI ni la evidencia separada de publicación remota.

La aceptación se limita al MVP sintético y al replay determinista. No acredita ENOE, ingesta real, estimaciones oficiales, inferencia externa ni prose agentic de comparaciones. La inspección cubre rutas identificadas y los negativos descritos; no constituye prueba de ausencia de cualquier defecto posible.
