# Sources / Fuentes

> This guide documents the accepted ENOE input boundary. Phase 4 has integrated publication evidence; Phase 5 final release acceptance remains open. This guide does not activate another source or authorize microdata publication.

## Español

### Fuente primaria y límite de autoridad

La fuente primaria del análisis aceptado es el Instituto Nacional de Estadística y Geografía (INEGI), Encuesta Nacional de Ocupación y Empleo (ENOE). El alcance analítico aceptado usa ocho snapshots: 2024-Q3, 2024-Q4, 2025-Q1, 2025-Q2, 2025-Q3, 2025-Q4, 2026-Q1 y 2026-Q2. La aprobación registrada es de **adquisición** de esos ocho insumos. No autoriza publicar microdatos, activar futuras ediciones, ni convertir el catálogo en una orden automática de actualización.

El campo `publication_approved=false` del registro de snapshots conserva la prohibición de publicar microdatos, que el lector del inventario exige explícitamente. La autorización y validación de agregados se verifican en la publicación correspondiente; no se cambia ese indicador para liberar un informe.

Los ZIP y las filas de personas permanecen locales. Los artefactos públicos pueden contener resultados agregados validados y metadatos necesarios, pero no redistribuyen microdatos. La atribución debe conservar la autoridad, los metadatos, la URL, el SHA-256 y el aviso de transformación: los cálculos y la transformación son de Brújula Laboral MX; no fueron realizados ni avalados por INEGI.

### Registro de los ocho insumos aceptados

| Snapshot | Periodo | URL exacta | SHA-256 del ZIP |
|---|---|---|---|
| `enoe_2024_q3` | 2024-Q3 | https://www.inegi.org.mx/contenidos/programas/enoe/15ymas/datosabiertos/2024/conjunto_de_datos_enoe_2024_3t_csv.zip | `f384a1b8872e051856ed2241289400302b13a8701489b1c596390452c183cd01` |
| `enoe_2024_q4` | 2024-Q4 | https://www.inegi.org.mx/contenidos/programas/enoe/15ymas/datosabiertos/2024/conjunto_de_datos_enoe_2024_4t_csv.zip | `bb6d958c9bca11672d367d2c051cd08bf1654c471c2f32c8e21992c126a3b426` |
| `enoe_2025_q1` | 2025-Q1 | https://www.inegi.org.mx/contenidos/programas/enoe/15ymas/datosabiertos/2025/conjunto_de_datos_enoe_2025_1t_csv.zip | `3931e7c9242147da6ebf9badb1e2b9a59d43d95a9811e077232be406c4ce6691` |
| `enoe_2025_q2` | 2025-Q2 | https://www.inegi.org.mx/contenidos/programas/enoe/15ymas/datosabiertos/2025/conjunto_de_datos_enoe_2025_2t_csv.zip | `9530a017e3defb0658418b73a47a6039eeb54abf11342fa10693374736515127` |
| `enoe_2025_q3` | 2025-Q3 | https://www.inegi.org.mx/contenidos/programas/enoe/15ymas/datosabiertos/2025/conjunto_de_datos_enoe_2025_3t_csv.zip | `7138b2bfabc740a9805b83b3fd0dae28287fc2aab3781a596a741b8fc7861566` |
| `enoe_2025_q4` | 2025-Q4 | https://www.inegi.org.mx/contenidos/programas/enoe/15ymas/datosabiertos/2025/conjunto_de_datos_enoe_2025_4t_csv.zip | `e4d4284cc9924a40c39544a5530715f320a5627cd81997214c0430827616d9d6` |
| `enoe_2026_q1` | 2026-Q1 | https://www.inegi.org.mx/contenidos/programas/enoe/15ymas/datosabiertos/2026/conjunto_de_datos_enoe_2026_1t_csv.zip | `429c288af46e408de743e5dfb92750f668df7e42789be5824f7cdf1c5ff56580` |
| `enoe_2026_q2` | 2026-Q2 | https://www.inegi.org.mx/contenidos/programas/enoe/15ymas/datosabiertos/2026/conjunto_de_datos_enoe_2026_2t_csv.zip | `9ef8877c363f6097da1a04b2077cbda96300cc474b38f835c4963d1dd8f953df` |

En cada snapshot, el miembro SDEM es `conjunto_de_datos_sdem_enoe_YYYY_Nt/conjunto_de_datos/conjunto_de_datos_sdem_enoe_YYYY_Nt.csv`; el diccionario es el miembro hermano `diccionario_de_datos/diccionario_datos_sdem_enoe_YYYY_Nt.csv`; y el catálogo de campo es `catalogos/cs_p14_c.csv`. El catálogo versionado `data/catalog/enoe-snapshots.json` conserva los ZIP aprobados; `docs/SOURCES.md` conserva el inventario público de metadatos. Los recibos públicos de aceptación de Fases 2–4 establecen el alcance validado; las rutas `.cache` no son dependencias para el lector.

### Qué significa “aceptado”

La aceptación de Fase 2 cubre cálculos agregados, oráculos numéricos y reconciliación para los ocho snapshots. La aceptación de Fase 3 cubre el paquete analítico persistido. La Fase 4 añade identidad instalada, exportaciones, informes, sellado, resolución de `current`, replay y controles integrados; su recibo público está en `docs/evidence/phase-04-publication-acceptance.json`. La auditoría y publicación final de Fase 5 siguen siendo gates independientes.

### Referencias y fuentes no activas

OLA, Data México e IMCO son referencias o benchmarks documentales. No se usan aquí como fuente de ingesta, no activan snapshots, y no se redistribuyen sus cifras. OLA conserva una ambigüedad de unidad; Data México combina cubos con grains y términos distintos; IMCO tiene metodología y derechos propios. MOPRADEF es un control negativo de comparabilidad y queda fuera del dominio laboral.

El catálogo de fuentes puede contener candidatos o futuras ediciones. La presencia de una URL, una propuesta de agente o una comparación manual nunca activa automáticamente una fuente. Una nueva edición requiere aprobación, adquisición controlada, receipt, hash, revisión de términos y validación del contrato antes de entrar al alcance.

## English

### Primary source and authority boundary

The primary source for the accepted analysis is the Instituto Nacional de Estadística y Geografía (INEGI), Encuesta Nacional de Ocupación y Empleo (ENOE). The accepted analytical scope uses eight snapshots: 2024-Q3, 2024-Q4, 2025-Q1, 2025-Q2, 2025-Q3, 2025-Q4, 2026-Q1, and 2026-Q2. The recorded approval is for **acquisition** of these eight inputs. It does not authorize microdata publication, activate future editions, or turn the catalog into an automatic refresh order.

The snapshot registry field `publication_approved=false` preserves the microdata-publication prohibition explicitly required by the inventory reader. Aggregate authorization and validation are checked at the corresponding publication boundary; this flag is not changed to release a report.

ZIP files and person rows remain local. Public artifacts may contain validated aggregate results and the metadata required to explain them, but they do not redistribute microdata. Attribution must preserve the authority, metadata, URL, SHA-256, and transformation notice: Brújula Laboral MX performed the calculations and transformation; INEGI did not perform or endorse them.

### Register of the eight accepted inputs

The English register repeats the same immutable values; translation does not create a second source identity.

| Snapshot | Period | Exact URL | ZIP SHA-256 |
|---|---|---|---|
| `enoe_2024_q3` | 2024-Q3 | https://www.inegi.org.mx/contenidos/programas/enoe/15ymas/datosabiertos/2024/conjunto_de_datos_enoe_2024_3t_csv.zip | `f384a1b8872e051856ed2241289400302b13a8701489b1c596390452c183cd01` |
| `enoe_2024_q4` | 2024-Q4 | https://www.inegi.org.mx/contenidos/programas/enoe/15ymas/datosabiertos/2024/conjunto_de_datos_enoe_2024_4t_csv.zip | `bb6d958c9bca11672d367d2c051cd08bf1654c471c2f32c8e21992c126a3b426` |
| `enoe_2025_q1` | 2025-Q1 | https://www.inegi.org.mx/contenidos/programas/enoe/15ymas/datosabiertos/2025/conjunto_de_datos_enoe_2025_1t_csv.zip | `3931e7c9242147da6ebf9badb1e2b9a59d43d95a9811e077232be406c4ce6691` |
| `enoe_2025_q2` | 2025-Q2 | https://www.inegi.org.mx/contenidos/programas/enoe/15ymas/datosabiertos/2025/conjunto_de_datos_enoe_2025_2t_csv.zip | `9530a017e3defb0658418b73a47a6039eeb54abf11342fa10693374736515127` |
| `enoe_2025_q3` | 2025-Q3 | https://www.inegi.org.mx/contenidos/programas/enoe/15ymas/datosabiertos/2025/conjunto_de_datos_enoe_2025_3t_csv.zip | `7138b2bfabc740a9805b83b3fd0dae28287fc2aab3781a596a741b8fc7861566` |
| `enoe_2025_q4` | 2025-Q4 | https://www.inegi.org.mx/contenidos/programas/enoe/15ymas/datosabiertos/2025/conjunto_de_datos_enoe_2025_4t_csv.zip | `e4d4284cc9924a40c39544a5530715f320a5627cd81997214c0430827616d9d6` |
| `enoe_2026_q1` | 2026-Q1 | https://www.inegi.org.mx/contenidos/programas/enoe/15ymas/datosabiertos/2026/conjunto_de_datos_enoe_2026_1t_csv.zip | `429c288af46e408de743e5dfb92750f668df7e42789be5824f7cdf1c5ff56580` |
| `enoe_2026_q2` | 2026-Q2 | https://www.inegi.org.mx/contenidos/programas/enoe/15ymas/datosabiertos/2026/conjunto_de_datos_enoe_2026_2t_csv.zip | `9ef8877c363f6097da1a04b2077cbda96300cc474b38f835c4963d1dd8f953df` |

The versioned `data/catalog/enoe-snapshots.json` contains approved ZIP identities, and `docs/SOURCES.md` contains the public metadata inventory. Public Phase 2–4 acceptance receipts establish the validated scope; readers do not depend on `.cache` paths.

### What “accepted” means

Phase 2 acceptance covers aggregate calculations, numerical oracles, and reconciliation for the eight snapshots. Phase 3 acceptance covers the persisted analytical handoff. Phase 4 adds installed identity, exports, reports, sealing, `current` resolution, replay and integrated controls; its public receipt is `docs/evidence/phase-04-publication-acceptance.json`. Phase 5 audit and final publication remain separate gates.

### References and inactive sources

OLA, Data México, and IMCO are documentary references or benchmarks. They are not ingestion sources here, do not activate snapshots, and their figures are not redistributed. OLA retains a unit ambiguity; Data México combines cubes with different grains and terms; IMCO has its own methodology and rights. MOPRADEF is a comparability negative control and is outside the labor domain.

A source catalog may contain candidates or future editions. A URL, an agent proposal, or a manual comparison never activates a source automatically. A new edition requires approval, controlled acquisition, receipt, hash, terms review, and contract validation before it enters scope.

### Attribution / Atribución

Fuente: INEGI, Encuesta Nacional de Ocupación y Empleo (ENOE), cortes aprobados 2024-Q3 a 2026-Q2. Cálculos y transformación de Brújula Laboral MX, no realizados ni avalados por INEGI. Consulta documental: 2026-09-22.

Source: INEGI, Encuesta Nacional de Ocupación y Empleo (ENOE), approved snapshots 2024-Q3 through 2026-Q2. Calculations and transformation by Brújula Laboral MX; not performed or endorsed by INEGI. Documentary consultation: 2026-09-22.

[Programa / Program](https://www.inegi.org.mx/programas/enoe/15ymas/) · [Términos de libre uso / Terms of use](https://www.inegi.org.mx/inegi/terminos.html).

This source guide carries no v1.0.0 release PASS claim.
