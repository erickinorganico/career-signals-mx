# Brújula Laboral MX — Operación / Operations

> Phase 4 operation interfaces, installed real publication and clean Windows/Ubuntu fixture/PDF checks have recorded evidence. Final v1.0.0 release audit remains a Phase 5 gate. Statistical `REVIEW` is distinct from an operation that completes with `SUCCEEDED` or `PASS`.

## ES-01 — Estado y boundary operativo

La operación real usa una rueda instalada y raíces explícitas. La adquisición y la aceptación numérica conservan custodia y auditorías inmutables; el análisis crea un paquete nuevo; la construcción sella una publicación agregada; replay reconstruye en raíces nuevas; `research-open` solo devuelve rutas cuando el `current` de publicación, su manifest, sus artefactos, la aceptación y las ocho fuentes vivas pasan las comprobaciones. No existe fallback sintético para una operación real fallida o ausente. Una recepción estadística puede quedar en `REVIEW` por precisión no oficial aunque la operación haya terminado correctamente.

## ES-02 — Instalación limpia y prerrequisitos

`pyproject.toml` requiere Python 3.12 o posterior. La instalación de prueba necesita el extra `[test]`, que incluye `pytest==9.0.3` y `pypdf==6.19.0`; la ruta completa de informes PDF usa el cierre fijado en `requirements-pdf.txt` (incluye `weasyprint==70.0` y `fonttools==4.65.0`). La instalación de dependencias y la adquisición de fuentes requieren red o artefactos previamente entregados; el análisis, replay y apertura de insumos ya custodiados deben ejecutarse sin red. Una rueda limpia debe instalarse fuera del checkout y resolver recursos empaquetados, no depender de caches ignorados.

En Windows, el asset oficial `weasyprint-windows-onedir.zip` tiene URL `https://github.com/Kozea/WeasyPrint/releases/download/v70.0/weasyprint-windows-onedir.zip` y SHA-256 `ab1151f210b4e6bb7aa7a79e91a67e8ddb760094c107bfda55241b6aaefe7d53`. Descárgalo solo en una carpeta temporal, verifica el hash antes de extraer y define `WEASYPRINT_DLL_DIRECTORIES` para `onedir/weasyprint/_internal` bajo el directorio extraído; no modifiques el PATH global. En Ubuntu, instala y registra versiones de `libpango-1.0-0`, `libharfbuzz0b`, `libpangoft2-1.0-0` y `libharfbuzz-subset0`. El run 36050222714 confirmó ambas instalaciones y un PDF español legible.

## ES-03 — Raíces, guardas y separación

`source-root` contiene la custodia de los ocho ZIP, sus recibos `current` y sus intentos; `output-root` contiene salidas dependientes; `audit-dir` contiene evidencia de la operación. Son raíces distintas y no pueden solaparse entre sí, con un run sellado, ni mediante symlink/junction/reparse point. `research-analyze` también exige un `analysis-output` nuevo, fuera de fuente, auditorías, aceptación y publicación aceptada. `research-build` recibe el paquete analítico desde una ruta separada y usa `audit-dir` como auditoría numérica de solo lectura. Un error de configuración, destino inválido o solapamiento bloquea antes de prometer un recibo de éxito; los destinos seguros sí conservan el recibo inmutable de fallo.

## ES-04 — Comandos exactos y sus resultados

Las formas implementadas por la CLI instalada son:

```text
python -m brujula enoe-refresh --source-root SOURCE_ROOT --output-root OUTPUT_ROOT
python -m brujula enoe-accept --source-root SOURCE_ROOT --output-root OUTPUT_ROOT --audit-dir AUDIT_DIR --workbook WORKBOOK --pdf PDF --rscript RSCRIPT --r-home R_HOME --r-lib R_LIB
python -m brujula research-analyze --source-root SOURCE_ROOT --acceptance-receipt ACCEPTANCE_RECEIPT --analysis-output ANALYSIS_OUTPUT --audit-dir AUDIT_DIR
python -m brujula research-build --source-root SOURCE_ROOT --output-root OUTPUT_ROOT --audit-dir AUDIT_DIR --analysis-packet ANALYSIS_PACKET
python -m brujula research-replay --source-root SOURCE_ROOT --run SEALED_RUN --audit-dir AUDIT_DIR
python -m brujula research-open --source-root SOURCE_ROOT --output-root OUTPUT_ROOT --format html|markdown|pdf|csv|parquet|duckdb
```

`enoe-refresh` refresca los ocho cortes en orden y devuelve `PASS` solo si cada adquisición queda `SUCCEEDED`; cualquier fallo devuelve `BLOCKED` y deja la publicación dependiente bloqueada. `enoe-accept` exige workbook y PDF oficiales, `Rscript`/`R_HOME` explícitos y una biblioteca R explícita con `survey` y `jsonlite`; valida el diseño, las referencias oficiales, el PDF y el oráculo R, y produce aceptación numérica y auditoría separada. `research-analyze` consume una aceptación inmutable y escribe un análisis nuevo. `research-build` consume ese paquete y sella agregados, informes y exports; su recibo operativo puede tener `build_status=SUCCEEDED` y `status=REVIEW` por la precisión estadística no oficial. `research-replay` reconstruye en auditoría y outputs nuevos sin promover `current`. `research-open` es de solo lectura y falla cerrado si no puede demostrar un `current` vivo y verificado.

La interfaz numérica adicional es `enoe-replay --source-root SOURCE_ROOT --run SEALED_ACCEPTANCE --audit-dir AUDIT_DIR --rscript RSCRIPT --r-home R_HOME --r-lib R_LIB`; recalcula la aceptación en un audit nuevo y exige identidad de runtime, fuentes y benchmark. Se documenta para reproducibilidad, pero no convierte su resultado en publicación ni reemplaza la auditoría original.

## ES-05 — Aceptación, auditorías y contenido canónico

La aceptación numérica, el análisis y la publicación tienen receipts, roots y límites de evidencia separados. La aceptación es la autoridad de los agregados numéricos; el paquete nuevo de `research-analyze` es la autoridad del análisis de esa ejecución; el run sellado es la autoridad de informes y exports. Replay compara contenido canónico: registros tipados, filas lógicas y orden definido, excluyendo bytes accidentales de PDF, timestamps y journals operativos. La equivalencia de un PDF no se decide comparando bytes del archivo.

El lector debe obtener el workbook oficial y el PDF oficial 2026-Q2 desde las rutas del catálogo aprobado y proporcionar sus archivos a `enoe-accept`; este documento no inventa rutas personales ni depende de helpers ignorados. Los hashes y referencias que recibe la aceptación son evidencia de esos archivos concretos. No se debe tratar un enlace, un archivo histórico o una ruta local personal como fuente viva sin la comprobación del receipt y del catálogo.

## ES-06 — Current, fallos y recuperación

Durante cada operación el `current` dependiente se invalida o permanece bloqueado hasta que el nuevo resultado esté validado. Un receipt `RUNNING` no es evidencia. `SUCCEEDED` describe la ejecución completa de esa operación; `PASS` describe una aceptación/replay o un refresco completamente exitoso; `REVIEW` describe una publicación estadísticamente revisable pero operativamente sellada; `BLOCKED`/`FAILED` retiene acceso. Un `current` faltante, stale o con hashes que no coinciden bloquea la apertura, no significa cero ni salud.

Una adquisición requerida posterior que falla invalida la publicación dependiente aunque exista un run sellado anterior. El run histórico y sus receipts permanecen inmutables; no se sobrescriben ni se vuelven actuales por antigüedad. La recuperación aísla el intento, conserva su fallo, corrige o refresca solo la dependencia afectada y ejecuta un nuevo intento identificado.

## ES-07 — Recuperación y límites de evidencia

Una interrupción durante `research-build` se recupera bajo el lock exclusivo del sistema operativo. El journal mutable y el `current` pueden conservar `RUNNING`; no son receipts inmutables ni prueba de éxito. La siguiente construcción valida el run, escribe un fallo `BLOCKED` de recuperación o reusa el fallo válido, conserva el run sellado histórico y no reemplaza sus seals. La prueba instalada real de `os._exit(17)`, recuperación, construcción y apertura está en `04-INTEGRATED-OPERATION.md`. La validación de hashes puede consumir tiempo según el número y tamaño de archivos; no se documenta un tiempo garantizado. Windows y Ubuntu pasaron sus instalaciones limpias, helper y PDF en el run 36050222714.

## EN-01 — Operational status and boundary

The real workflow uses an installed wheel and explicit roots. Acquisition and numerical acceptance retain immutable custody and audit evidence; analysis creates a new packet; build seals an aggregate publication; replay reconstructs into new roots; `research-open` returns paths only when publication `current`, manifest, artifacts, acceptance, and all eight live sources pass validation. There is no synthetic fallback for a failed or missing real operation. A statistical result may remain `REVIEW` because project precision is nonofficial even when the operation completes successfully.

## EN-02 — Clean installation and prerequisites

`pyproject.toml` requires Python 3.12 or later. Test installation needs `[test]`, which includes `pytest==9.0.3` and `pypdf==6.19.0`; the complete PDF report path uses the pinned closure in `requirements-pdf.txt` (including `weasyprint==70.0` and `fonttools==4.65.0`). Dependency installation and source acquisition require network access or pre-delivered artifacts; analysis, replay, and opening of already-custodied inputs must run offline. A clean wheel must be installed outside the checkout and resolve packaged resources without relying on ignored caches.

On Windows, the official `weasyprint-windows-onedir.zip` asset is at `https://github.com/Kozea/WeasyPrint/releases/download/v70.0/weasyprint-windows-onedir.zip`, SHA-256 `ab1151f210b4e6bb7aa7a79e91a67e8ddb760094c107bfda55241b6aaefe7d53`. Download into a temporary directory, verify the hash before extraction, and set `WEASYPRINT_DLL_DIRECTORIES` to `onedir/weasyprint/_internal` under that directory; do not mutate global PATH. On Ubuntu, install and record versions of `libpango-1.0-0`, `libharfbuzz0b`, `libpangoft2-1.0-0`, and `libharfbuzz-subset0`. Run 36050222714 confirmed both clean installations and searchable Spanish PDFs.

## EN-03 — Roots, guards, and separation

`source-root` holds the eight ZIP files, their `current` receipts, and attempts; `output-root` holds dependent outputs; `audit-dir` holds operation evidence. These roots must be separate and cannot overlap each other, a sealed run, or any symlink/junction/reparse path. `research-analyze` also requires a new `analysis-output` outside source, audits, acceptance, and accepted publication. `research-build` receives the analysis packet from a separate path and treats `audit-dir` as a read-only numerical acceptance audit. A configuration error, invalid destination, or overlap blocks before promising a success receipt; safe destinations preserve an immutable failure receipt.

## EN-04 — Exact commands and outcomes

The installed CLI implements these forms:

```text
python -m brujula enoe-refresh --source-root SOURCE_ROOT --output-root OUTPUT_ROOT
python -m brujula enoe-accept --source-root SOURCE_ROOT --output-root OUTPUT_ROOT --audit-dir AUDIT_DIR --workbook WORKBOOK --pdf PDF --rscript RSCRIPT --r-home R_HOME --r-lib R_LIB
python -m brujula research-analyze --source-root SOURCE_ROOT --acceptance-receipt ACCEPTANCE_RECEIPT --analysis-output ANALYSIS_OUTPUT --audit-dir AUDIT_DIR
python -m brujula research-build --source-root SOURCE_ROOT --output-root OUTPUT_ROOT --audit-dir AUDIT_DIR --analysis-packet ANALYSIS_PACKET
python -m brujula research-replay --source-root SOURCE_ROOT --run SEALED_RUN --audit-dir AUDIT_DIR
python -m brujula research-open --source-root SOURCE_ROOT --output-root OUTPUT_ROOT --format html|markdown|pdf|csv|parquet|duckdb
```

`enoe-refresh` refreshes all eight snapshots in order and returns `PASS` only when each acquisition is `SUCCEEDED`; any failure returns `BLOCKED` and leaves dependent publication blocked. `enoe-accept` requires official workbook and PDF files, explicit `Rscript`/`R_HOME`, and an explicit R library containing `survey` and `jsonlite`; it validates design, official references, PDF, and the R oracle, producing numerical acceptance and a separate audit. `research-analyze` consumes immutable acceptance and writes a new analysis. `research-build` consumes that packet and seals aggregates, reports, and exports; its operational receipt may have `build_status=SUCCEEDED` and `status=REVIEW` because statistical precision is nonofficial. `research-replay` reconstructs into new audit and output roots without promoting `current`. `research-open` is read-only and fails closed unless it can prove a live verified `current`.

The additional numerical interface is `enoe-replay --source-root SOURCE_ROOT --run SEALED_ACCEPTANCE --audit-dir AUDIT_DIR --rscript RSCRIPT --r-home R_HOME --r-lib R_LIB`; it recomputes acceptance in a new audit and requires runtime, source, and benchmark identity. It is documented for reproducibility, but does not make its result a publication or replace the original audit.

## EN-05 — Acceptance, audits, and canonical content

Numerical acceptance, analysis, and publication have separate receipts, roots, and evidence boundaries. Acceptance is authoritative for numerical aggregates; the new `research-analyze` packet is authoritative for that operation's analysis; the sealed run is authoritative for reports and exports. Replay compares canonical content: typed records, logical rows, and defined ordering, excluding accidental PDF bytes, timestamps, and operational journals. PDF equivalence is not decided by comparing file bytes.

The reader must obtain the official workbook and official 2026-Q2 PDF from the approved catalog routes and provide those files to `enoe-accept`; this document invents no personal paths and depends on no ignored helper. Hashes and references recorded by acceptance identify those concrete files. A link, historical file, or personal local path is not a live source without receipt and catalog validation.

## EN-06 — Current, failures, and recovery

During each operation, dependent `current` remains invalid or blocked until the new result is validated. A `RUNNING` receipt is not evidence. `SUCCEEDED` describes completion of that operation; `PASS` describes a fully successful acceptance/replay or refresh; `REVIEW` describes a statistically reviewable but operationally sealed publication; `BLOCKED`/`FAILED` withholds access. A missing, stale, or hash-mismatched `current` blocks opening; it does not mean zero or healthy.

A later failed required acquisition invalidates dependent publication even when an earlier sealed run exists. Historical runs and receipts remain immutable; age does not make them current. Recovery isolates the attempt, preserves its failure, repairs or refreshes only the affected dependency, and starts a newly identified attempt.

## EN-07 — Recovery and evidence limits

An interruption during `research-build` is recovered under the exclusive operating-system lock. Mutable journal and `current` may retain `RUNNING`; they are not immutable receipts or success evidence. The next build validates the run, writes a `BLOCKED` recovery failure or reuses a valid failure, preserves the historical sealed run, and does not replace its seals. Actual installed `os._exit(17)` recovery, build and open evidence is in `04-INTEGRATED-OPERATION.md`. Hash validation may take time depending on file count and size; no guaranteed duration is documented. Windows and Ubuntu clean installations, helpers and PDFs passed in run 36050222714.

## Authority and integration notes

- Runtime authority: `brujula/cli.py`, `brujula/pipeline_v2.py`, `brujula/enoe_acceptance.py`, `brujula/resources.py`, and `pyproject.toml`.
- Accepted operation evidence: `04-05-SUMMARY.md` and `04-WAVE3-CHECKS.md`.
- Cross-platform evidence: [hosted CI run 36050222714](https://github.com/erickinorganico/career-signals-mx/actions/runs/36050222714) and `docs/evidence/phase-04-publication-acceptance.json`.
- Phase 5 status: version 1.0 remains planned until public readback and final acceptance.
