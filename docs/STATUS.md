# Estado publicado — v0.9.0-preview.1

Se entrega el [informe real y sus agregados](https://github.com/erickinorganico/career-signals-mx/releases/tag/v0.9.0-preview.1) como publicación preliminar. La implementación local y el plan 04-06 tienen evidencia de aceptación; la [CI nativa](https://github.com/erickinorganico/career-signals-mx/actions/runs/36053551361) pasó en Windows y Ubuntu para el checkout registrado entonces. La verificación técnica independiente de Fase 4 pasó 5/5; la aprobación visual humana sigue pendiente. Fase 5, el paquete Python 1.0.0 candidato, su CI exacta y la auditoría final GSD permanecen separados. No se declara release público final 1.0.0. Los detalles que siguen son registros históricos anteriores a esta actualización.

Preparación técnica al 2026-09-28: el candidato `611d2f5` pasó CI en Windows y Ubuntu (595 pruebas y 30 controles por sistema; seis casos dependen del entorno local). El wheel de entrega procede de esa CI y sus archivos coinciden en ambos sistemas. La auditoría aprobó los cinco archivos de entrega y sus 147 miembros internos; los verificadores de inventario y portabilidad pasaron contra los bytes reales. Véanse [portabilidad](evidence/phase-05-portability.json) e [inventario](evidence/phase-05-release-inventory.json). El borrador 1.0.0 ya está cargado y sus cinco archivos descargados coinciden con el inventario; [recibo del borrador](evidence/phase-05-release-acceptance.json). La revisión visual humana y el cierre público/GSD siguen pendientes.

---

# Brújula Laboral MX — estado verificable

La versión final de investigación real **1.0.0 sigue en construcción; Phases 1–3 están aceptadas**. El
[estado GSD](../.planning/STATE.md) y el
[roadmap activo](../.planning/ROADMAP.md) registran su avance. La fase de fuentes
y contrato y la fase estadística están aceptadas: ocho trimestres, 23 indicadores
con denominadores explícitos y 6,739 celdas evaluadas. El cálculo pasó los 26
casos reales y cuatro controles analíticos de R, ambas referencias oficiales y
una repetición idéntica. Phase 3 añadió el paquete de hallazgos soportados:
6,739 registros reales, 4,209 comparaciones, 38 claims y 3 aperturas; su JSON
persistido recarga y valida con cero errores. La revisión independiente verificó
42/42 verdades y 4/4 criterios de roadmap; seguridad cerró 15/15 entradas de
amenazas, sin abiertas, y Nyquist pasó 31/31. La precisión propia continúa siendo no oficial, con las
discrepancias documentadas. La [evidencia numérica](evidence/phase-02-numerical-acceptance.json)
conserva los intentos y hashes, y la [evidencia de Phase 3](evidence/phase-03-analysis-acceptance.json)
conserva el digest del paquete. Phase 4 debe producir la publicación offline;
Phase 5 debe cerrar el release. Estas frases reflejan el estado histórico
previo a la publicación preliminar enlazada arriba.
El repositorio conserva la versión pública sintética 0.1.0 y el preview real,
ambos separados del futuro release final.

La evidencia que sigue es el registro histórico de la demo sintética 0.1.0;
sus bloqueos de ingesta y cifras de pruebas no describen el alcance activo.

Fecha local: 2026-09-22. **MVP sintético 0.1.0 terminado y publicado; CI PASS en Windows y Linux.**
M0 conserva su aceptación documental. M1–M5 están completos dentro del alcance
sintético. [Release público v0.1.0](https://github.com/erickinorganico/career-signals-mx/releases/tag/v0.1.0),
con wheel y bundle cuyos hashes remotos coinciden con los artefactos verificados.

| Superficie | Evidencia verificada |
|---|---|
| Planeación | 18 requisitos, 18 tareas, 5 ADRs; revisión documental PASS |
| Datos | 54 observaciones sintéticas, siete UNKNOWN/null; schemas, refs, grain y rangos |
| Calidad y comparabilidad | Negativos de identidad, nulos, precisión, cobertura, periodos y overflow |
| Pipeline | Raw inmutable, receipts, current verificado, fallos e interrupciones recuperables |
| Almacén y exports | DuckDB normalizado; CSV/Parquet/JSON con provenance y sin agregación por bridges |
| Reportes | Markdown/HTML offline; cuatro gráficas PNG/SVG, tablas equivalentes y tres insights REVIEW |
| Agentes | Seis roles deterministas de solo lectura; doce evals sin violaciones críticas |
| Integración | 89 tests PASS locales y en Windows/Linux CI; replay limpio y wheel fuera del checkout |
| Revisión independiente | PASS; cinco hallazgos corregidos y reproducidos |
| Dependencias | 23 paquetes fijados; licencia identificada y cero vulnerabilidades conocidas al escanear |
| Datos oficiales | BLOCKED BY DESIGN: official_snapshot requiere source_activation de M6 |

El [recibo del release](evidence/release-receipt.json) conserva timestamps UTC,
hashes y estados de publicación/CI. Los comandos y límites están en
[RELEASE](RELEASE.md); el [ejemplo](../examples/synthetic/README.md) es un snapshot
sintético estático. Ninguna cifra representa el mercado laboral mexicano real.

```powershell
python -m brujula verify
python -m brujula demo --as-of 2026-09-22 --output artifacts/demo
python -m brujula report --output artifacts/demo --format html
```

`report` resuelve current y verifica raw, manifest y artefactos. Los nulos no son
ceros; los bridges no crean equivalencia; un fallo invalida current. El archivo
del lock del sistema permanece normalmente y no debe borrarse para recuperar un
run. El replay no usa red después de instalar dependencias.

El [recibo histórico M0](evidence/planning-receipt.json) acredita la planeación
y su publicación de aquel checkpoint; no sustituye el receipt de este release.
