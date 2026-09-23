# Plan de validación y release analítico

> **Validación histórica del piloto sintético 0.1.0.** La validación de ENOE real sigue los planes `VALIDATION.md` de cada fase del [roadmap activo](../.planning/ROADMAP.md), con aceptación registrada en [STATE](../.planning/STATE.md). Los gates históricos siguientes no certifican el release 1.0.0.

Este plan cubre pipelines, tablas, gráficas y reportes locales. No incluye una
aplicación web, navegador, servidor HTTP ni APIs pagadas. Los estados de cada
gate son `DOCUMENTED`, `IMPLEMENTED`, `PARTIAL`, `VERIFIED` o `BLOCKED`; una
decisión de release necesita evidencia reproducible, no solo código presente.

El resultado ejecutado está en [RELEASE](RELEASE.md) y su
[recibo](evidence/release-receipt.json); este archivo conserva los criterios.

## Hitos

| Hito | Propósito | Salida de aceptación |
|---|---|---|
| M0 | Planeación y alcance | Requisitos REQ-001..REQ-018 trazados a contrato y estado |
| M1 | Datos y contratos | Fixture y schemas verificados con negativos estructurales |
| M2 | Pipeline y almacén | Replay local, DuckDB, raw inmutable y receipts |
| M3 | Reportes | Markdown/HTML y gráficas deterministas con metadata |
| M4 | Agentes | Refs, claims, injection y publication gate validados |
| M5 | Release | Clean setup, licencia, secretos, docs y receipt de publicación |
| M6 | ENOE real | Solo después del MVP: snapshot, hash, CMPE, ponderación y varianza |

## Requisitos trazables

El significado de cada ID proviene de [PRD](PRD.md); los casos siguientes
no redefinen los requisitos. ENOE real pertenece a M6 y no condiciona el cierre
del MVP sintético.

| ID | Hito | Validación y evidencia requerida |
|---|---|---|
| REQ-001 | M0 | Catálogo separa candidato, metadata autorizada e ingesta numérica; registra autoridad, URL, términos, acceso, población, periodicidad y fecha |
| REQ-002 | M1 | Schemas estrictos para dataset e insights; campos inesperados, estructura y enums inválidos se rechazan. Las referencias entre entidades se comprueban además en validación semántica |
| REQ-003 | M1 | 54 combinaciones explícitas de 3 campos × 2 geografías × 3 periodos × 3 métricas; al menos dos UNKNOWN/null y todo valor sintético etiquetado |
| REQ-004 | M1 | Dimensiones y bridges separados; no tratar un mapeo editorial en REVIEW como equivalencia de campo/ocupación ni como vacante |
| REQ-005 | M1 | Null no es cero; UNKNOWN con número bloquea; BLOCKED no produce valor publicable; real sin precisión evaluada no obtiene MEASURED automáticamente |
| REQ-006 | M2 | Negativos NaN/Infinity, rangos, IDs duplicados en todas las entidades, duplicate grain, referencias huérfanas, inconsistencia source/evidence/unit/basis y mezcla real/sintética. Probar conjunto vacío, all UNKNOWN, REVIEW + UNKNOWN y cualquier BLOCKED contra la tabla de reducción de SPEC; UNKNOWN sin valor nunca habilita publicación numérica |
| REQ-007 | M2 | Freshness usa periodos referenciados por filas; periodo o checked_at futuro no se acepta como fresco; cobertura incompleta explícita y reloj de captura separado. Probar stale agregado con valores disponibles y all UNKNOWN con warning de freshness: el warning no convierte ausencia de datos en REVIEW publicable |
| REQ-008 | M2 | Rechazar pares nulos, UNKNOWN/BLOCKED, refs ausentes, periodos invertidos/solapados y mismatch de fuente, universo, método, concepto, geografía, medida, unidad, base o modo. Con base cero, delta relativo null; delta absoluto solo si las demás reglas permiten |
| REQ-009 | M2 | Input hash y raw inmutable, receipt final write-once por intento, versión/parámetros/timestamps/error; refresh fallido invalida current sin reutilizar éxito histórico y sin destruirlo. Inyectar fallo de renderer después de staging y crash antes/después del reemplazo atómico de current.json, incluso antes de actualizar report.md; solo current.json y hashes validados autorizan artefactos |
| REQ-010 | M2 | Tablas DuckDB, recuentos, claves, dimensiones/observaciones/bridges; ningún total se calcula a través de un bridge editorial |
| REQ-011 | M2 | CSV/Parquet/JSON preservan source/period/unit/status/synthetic/evidence; falla de gate retiene exportación; texto que parece fórmula CSV se neutraliza |
| REQ-012 | M3 | Reportes Markdown/HTML y SVG/PNG con fuente, periodo, geografía, unidad, universo y precisión; tabla alternativa; HTML realmente renderiza figuras y no ejecuta contenido externo |
| REQ-013 | M3 | Null/UNKNOWN son gaps o sin dato, BLOCKED no tiene cifra, no se unen periodos incompatibles; cada imagen exportada mantiene la etiqueta sintética |
| REQ-014 | M3 | Packet separa observación, interpretación, recomendación y unknowns; cada cifra tiene refs que resuelven y respaldan exactamente la afirmación |
| REQ-015 | M4 | Seis roles read-only, propuestas sin activar fuentes/bridges, sin escritura canónica ni publicación por inferencia; gate determinista controla artifacts |
| REQ-016 | M4 | Dataset de evals cubre falso cero, confusión campo/ocupación/vacante, evidencia inventada/incongruente, causalidad, instrucciones dentro de datos y series incompatibles |
| REQ-017 | M5 | Entorno limpio con dependencias fijadas; demo y verify completos offline después de instalación, unit/integration/E2E verdes; distinguir instalación online de ejecución offline |
| REQ-018 | M5 | Auditoría de secretos/licencias, revisión Astra del software integrado, trazabilidad de REQ, receipt con SHA y artefactos verificables antes de etiquetar el release analítico |

## Secuencia de validación

1. **Unit data/quality (M1–M2).** Ejecutar colección específica y casos
   parametrizados para estructura, null/zero, NaN/Infinity, duplicate IDs,
   duplicate grain, referencias, precision, mixed synthetic, future period,
   source/evidence y comparabilidad. Registrar comando, versión Python,
   exit code y log en el run.
2. **Integration pipeline/warehouse (M2).** Cargar el fixture local, validar,
   escribir DuckDB, construir comparaciones y comprobar que el recuento y el
   hash del raw son estables. Forzar input ausente, refresh fallido y colisión
   de raw; verificar receipts y que `current` queda `BLOCKED` sin fallback.
   Inyectar una interrupción en cada límite de staging, receipt final,
   reemplazo de `current.json` y actualización del índice humano `report.md`.
   Antes del commit validado, ningún artefacto en staging es publicable;
   después del commit, los consumidores resuelven el run autorizado desde
   `current.json` aunque el índice humano quede atrasado. Un renderer fallido
   después de staging conserva el diagnóstico sin publicar sus exports.
   Un proceso interrumpido con estado de ejecución RUNNING no permite usar
   un éxito histórico como resultado actual. No sobrescribir receipts finales.
3. **E2E analítico (M2-M4).** Ejecutar el replay desde un directorio limpio,
   comprobar bundle, agent run, claims y reportes. Validar refs de evidencia,
   injection en textos/CSV, separación campo/ocupación y que ningún insight
   se publica sin evidence.
4. **Reportes y charts (M3).** Comprobar Markdown/HTML, PNG/SVG, tabla
   alternativa, etiquetas sintéticas persistentes, metadata de fuente/periodo/
   unidad/población/precision, licencias y ausencia de secretos o recursos
   remotos. Repetir con null, `UNKNOWN`, `BLOCKED` y series incompatibles.
5. **Release (M5).** Reinstalar en clean setup sin red numérica, ejecutar
   secret scan, license scan y enlaces de docs, guardar receipt con SHA y
   revisar el árbol Git. Etiquetar el release analítico solo cuando todos los gates estén
   `VERIFIED`; registrar URL y commit exactos. Los avances de documentación y
   checkpoints incompletos pueden publicarse antes con su estado explícito,
   revisión de secretos/licencias y autorización ya existente.
6. **ENOE real (M6).** Requiere aprobación metodológica posterior: snapshot
   inmutable, hash, licencia, resolución CMPE, población, factor de expansión,
   estrato/UPM, denominadores y varianza. Hasta entonces, cualquier valor real
   queda `REVIEW` o `BLOCKED` según el fallo.

## Artefactos mínimos por run

Cada run exitoso debe conservar, con rutas concretas dentro del directorio de salida:

```text
raw/<sha256>.json
runs/<run_id>/receipt.json
runs/<run_id>/bundle.json
runs/<run_id>/report/report.md
runs/<run_id>/report/report.html
runs/<run_id>/report/charts/*
current.json
report.md
```

Un intento fallido conserva el journal y su receipt final; `input_sha256` es
null si no pudo leer el input. Raw y diagnósticos se conservan solo si llegaron
a crearse. No se exigen reportes ni gráficas de un renderer fallido, y el puntero
actual queda `BLOCKED`. Una interrupción abrupta puede dejar el journal en
RUNNING y el receipt aún ausente; la recuperación debe cerrarlo como fallo
sin habilitar resultados históricos.

El journal/puntero registra la ejecución iniciada; el receipt final inmutable
registra su resultado. El estado de ejecución, el estado de evidencia, la
publicabilidad y la publicación remota son campos distintos. `current.json`
es la única autoridad para resolver el run actual: un fallo lo invalida, y
`report.md` es un índice humano que exige consultar ese puntero. Los históricos
permanecen identificados como históricos. Estos comportamientos son criterios
de aceptación pendientes de implementar y verificar, no resultados del
checkpoint actual.
