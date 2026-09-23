<!-- refreshed: 2026-09-22 -->
# Architecture

**Analysis Date:** 2026-09-22

## System Overview

```text
Local research entry points
  brujula/__main__.py -> brujula/cli.py
       | build/demo            | report                | scout
       v                       v                       v
  brujula/pipeline.py     resolve_current()       brujula/scout.py
       |                 manifest/raw hashes      metadata only
       v
  brujula/data.py -> brujula/quality.py
       |             schema, relationships, comparability
       v
  brujula/agents.py -> brujula/insights.py
       |             deterministic evidence-bound packets
       v
  brujula/warehouse.py + brujula/export.py + brujula/report.py
       |             DuckDB, CSV/Parquet/JSON, Markdown/HTML, SVG/PNG
       v
  artifacts/runs/<run_id>/ -> sealed manifest and receipt
       |
       v
  artifacts/current.json  (atomic canonical publication pointer)

Separate ENOE components, without a publication connection:
  data/catalog/enoe-snapshots.json -> brujula/acquisition.py -> raw ZIP
  caller-supplied design arrays  -> brujula/survey.py      -> estimates
```

- The executable application is a local Python research pipeline, not a web service. Commands and output paths are defined in `brujula/cli.py`; the product boundary is enforced by `AGENTS.md` and `docs/CONTRACT.md`.
- The active v1 publication path accepts the synthetic fixture at `data/fixtures/pilot.json`. Although `contracts/dataset.schema.json` names `official_snapshot`, `brujula/quality.py` explicitly rejects that mode for publication.
- `brujula/acquisition.py` and `brujula/survey.py` are present as untracked implementation additions in this checkout. They are not imported by `brujula/cli.py` or `brujula/pipeline.py`; their existence does not establish an integrated ENOE report or validated numeric release.
- `docs/decisions/0006-real-research-scope-and-acquisition.md` authorizes acquisition separately from statistical publication. `docs/FINAL-RELEASE-PLAN.md` describes an in-progress delivery; it is not an implemented v2 interface. The active schemas in `contracts/` remain v1.

## Component Responsibilities

| Component | Responsibility | File |
|-----------|----------------|------|
| CLI | Parse commands, select input/output, return failure codes, run verification subprocesses | `brujula/cli.py` |
| Resource resolver | Locate contracts, catalog and fixture in checkout or installed wheel | `brujula/resources.py` |
| Dataset loader | Reject duplicate JSON keys, nonfinite numbers and schema violations | `brujula/data.py` |
| Quality gate | Validate relationships, grain, concepts, source approval, precision and freshness | `brujula/quality.py` |
| Build coordinator | Order gates, write provenance, seal artifacts, publish or invalidate current | `brujula/pipeline.py` |
| Build lock | Enforce one writer per output root using OS locks | `brujula/runlock.py` |
| Agent replay | Produce six bounded role records and validate publication authority | `brujula/agents.py` |
| Insight contracts | Generate and verify exact observation-bound descriptive claims | `brujula/insights.py` |
| Warehouse | Materialize validated dimensions, observations and evidence links transactionally | `brujula/warehouse.py` |
| Exports | Preserve nulls, metadata and evidence in CSV, Parquet and full dataset JSON | `brujula/export.py` |
| Static renderer | Render escaped Markdown/HTML and deterministic SVG/PNG charts | `brujula/report.py` |
| Metadata scout | Read an allowed official page, compare content hashes, record a review proposal | `brujula/scout.py` |
| ENOE acquisition component | Download or verify cached allowlisted ZIPs with attempt receipts | `brujula/acquisition.py` |
| Survey component | Compute design-based totals/ratios, variance, intervals and suppression fields | `brujula/survey.py` |

## Pattern Overview

**Overall:** A synchronous, function-oriented batch pipeline with schema-bound dictionaries, deterministic analytical gates and immutable run artifacts. `brujula/pipeline.py` owns orchestration; consumers resolve the canonical pointer before using an output.

**Key Characteristics:**
- Keep I/O and publication in `brujula/pipeline.py`; statistical and claim logic remain independently callable in `brujula/quality.py`, `brujula/insights.py` and `brujula/survey.py`.
- Treat the input JSON plus its SHA-256 as provenance. DuckDB is a per-run materialization, not the system of record (`brujula/pipeline.py`, `brujula/warehouse.py`).
- Deny publication on failed gates, preserve historical runs and expose only the current verified run (`brujula/pipeline.py:115`, `brujula/pipeline.py:152`).
- Use deterministic local role replay, not model inference or tool execution, for the agent artifact (`brujula/agents.py:64`).
- Keep metadata permission, raw acquisition permission and numeric publication authority distinct (`data/catalog/sources.json`, `data/catalog/enoe-snapshots.json`, `docs/decisions/0006-real-research-scope-and-acquisition.md`).

## Layers

**Command and resource layer:**
- Purpose: Adapt shell invocations and installed-package resources to local functions.
- Location: `brujula/cli.py`, `brujula/__main__.py`, `brujula/resources.py`.
- Contains: `argparse` subcommands, console output, subprocess verification, resource-path resolution.
- Depends on: `brujula/pipeline.py`; `scout` imports `brujula/scout.py` only when invoked.
- Used by: `python -m brujula`, the `brujula` console entry in `pyproject.toml`, and wrappers in `scripts/`.

**Contract and analytical layer:**
- Purpose: Establish valid data, comparison semantics and permitted claims before persistence or rendering.
- Location: `contracts/*.schema.json`, `brujula/data.py`, `brujula/quality.py`, `brujula/insights.py`, `brujula/agents.py`.
- Contains: Draft 2020-12 validation, relational checks, period comparisons and canonical insight templates.
- Depends on: Resolved schema resources, passed dictionaries and `jsonschema`/`referencing`; no paid API or network transport.
- Used by: `brujula/pipeline.py`, export revalidation in `brujula/export.py`, tests and `evals/run.py`.

**Artifact and publication layer:**
- Purpose: Turn accepted analytical state into recoverable local artifacts and publish a verified pointer.
- Location: `brujula/pipeline.py`, `brujula/runlock.py`, `brujula/warehouse.py`, `brujula/export.py`, `brujula/report.py`.
- Contains: Atomic JSON replacement, exclusive immutable writes, OS locking, DuckDB transaction, report rendering and manifest verification.
- Depends on: The contract/analytical layer, filesystem, DuckDB and Matplotlib.
- Used by: CLI `build`, `demo` and `report`; generated roots default to `artifacts/`.

**Optional source-access layer:**
- Purpose: Record external source evidence without implicitly activating numeric results.
- Location: `brujula/scout.py`, `brujula/acquisition.py`, `data/catalog/sources.json`, `data/catalog/enoe-snapshots.json`.
- Contains: Separate HTTPS allowlists, size limits, metadata receipts and raw ZIP acquisition receipts.
- Depends on: Python `urllib`; the scout reuses helpers from `brujula/pipeline.py`, while acquisition uses `brujula/runlock.py` and `brujula/resources.py`.
- Used by: CLI `scout` for metadata; direct Python callers and `tests/test_acquisition.py` for acquisition. No acquisition CLI command is registered in `brujula/cli.py`.

**Independent statistical component:**
- Purpose: Evaluate caller-supplied survey design arrays without deciding source or universe validity.
- Location: `brujula/survey.py`.
- Contains: `SurveyDesign`, full-frame stratum/PSU indexing, Taylor ultimate-cluster variance, totals, ratios, 90% intervals and precision suppression.
- Depends on: NumPy arrays and an explicit caller-defined domain; no dataset schema, source catalog or publication pointer.
- Used by: `tests/test_survey.py`; no production adapter connection exists in `brujula/pipeline.py`.

## Data Flow

### Primary Request Path

1. Parse `build` or `demo`, select optional `--input`, `--output`, and `--as-of`, then call `build(...)` (`brujula/cli.py:35`). Both commands use the same build function.
2. Resolve the default fixture, lock the output root, recover a RUNNING attempt, create a unique run directory and write a BLOCKED/RUNNING current pointer plus journal (`brujula/pipeline.py:187`, `brujula/runlock.py:9`).
3. Read at most 16 MB, hash the exact input, update the digest in current/journal, and exclusively preserve raw bytes at `raw/<sha256>.json` (`brujula/pipeline.py:214`).
4. Load strict JSON and schema, compute relational/semantic quality, persist `quality.json`, and stop if `publishable` is false (`brujula/data.py:15`, `brujula/quality.py:18`).
5. Group observations by concept type/id, geography and metric; compare adjacent chronological periods using an explicit period map (`brujula/pipeline.py:65`, `brujula/quality.py:147`).
6. Generate and validate six read-only roles plus exact-evidence insight packets; deny the run if semantic validation fails or publication is disallowed (`brujula/agents.py:64`, `brujula/agents.py:124`).
7. Create the transactional warehouse, revalidate exports and render static reports within the run directory (`brujula/warehouse.py:8`, `brujula/export.py:32`, `brujula/report.py:227`).
8. Finalize the receipt as SUCCEEDED, write immutable bundle/receipt, hash the run artifacts into a manifest, and atomically replace `current.json` with the publishable pointer (`brujula/pipeline.py:254`).
9. Update the mutable journal and derived human index; resolve current and verify manifest, every sealed file, receipt, raw digest and bundle before exposing a report path (`brujula/pipeline.py:115`, `brujula/cli.py:60`).

### Failure and Recovery Flow

1. An exception inside the build stage calls `_failure`, retaining diagnostics and replacing public data with a BLOCKED bundle without observations or insights (`brujula/pipeline.py:152`).
2. If a receipt is already sealed, write `publication-failure.json` instead of modifying it; publish a nonpublishable current pointer (`brujula/pipeline.py:152`).
3. The next build under the OS lock converts an interrupted RUNNING pointer into a failed attempt before starting its own run (`brujula/pipeline.py:175`).
4. Failure to write the convenience `report.md` after canonical commit does not revoke current; the CLI reads the canonical pointer rather than trusting that index (`brujula/pipeline.py:91`, `tests/test_pipeline.py`).

### Metadata Scout Flow

1. Select a candidate with `monitor_allowed` from `data/catalog/sources.json` (`brujula/scout.py:51`).
2. Check robots policy and fetch only the approved HTTPS INEGI origin within the 3 MB response limit (`brujula/scout.py:26`).
3. Save content-addressed bytes plus an immutable receipt and a per-source current receipt. Changed content yields REVIEW; unchanged content can yield MEASURED for metadata only. `activation_allowed` and `numeric_publication_allowed` remain false (`brujula/scout.py:51`).

### Separate ENOE Acquisition and Estimation Paths

1. `acquire_snapshot(...)` loads an approved exact-URL registry entry, uses a lock per snapshot, records RUNNING, and either downloads a bounded ZIP or verifies an offline cache (`brujula/acquisition.py:193`).
2. ZIP checks reject unsafe member paths, duplicate names, symlinks and excessive declared expanded size. Successful acquisition preserves `raw/<sha256>.zip`, an attempt receipt and the snapshot current pointer; `resolve_snapshot(...)` verifies cache and receipt without network (`brujula/acquisition.py:119`, `brujula/acquisition.py:267`).
3. `SurveyDesign(...)` separately accepts the complete responding/resident frame, weights, strata and PSU identifiers. Domain masks restrict contributions while retaining the full design frame (`brujula/survey.py:19`).
4. `total(...)` or `ratio(...)` returns an estimate, visible `value`, standard error, CV, confidence interval, sample support and suppression reasons. This result is not a v1 observation or a release artifact (`brujula/survey.py:101`, `contracts/dataset.schema.json`).

**State Management:**
- Run data is passed as dictionaries, lists and `Path` objects; there is no web session, service registry or shared server database (`brujula/pipeline.py`, `brujula/cli.py`).
- `current.json` is mutable publication state, `journal.json` is mutable attempt state, and sealed run/raw artifacts are retained as history (`brujula/pipeline.py`).
- Acquisition has its own `acquisitions/<snapshot_id>/current.json` and attempt history; it is not the research publication pointer (`brujula/acquisition.py`).
- Survey weights are copied and marked read-only; design indexes are held in a `SurveyDesign` instance (`brujula/survey.py:27`).

## Key Abstractions

**Dataset and observation:**
- Purpose: A normalized analytical contract separating field, occupation, industry, geography, period, metric, source and evidence.
- Examples: `contracts/dataset.schema.json`, `data/fixtures/pilot.json`, `brujula/quality.py`.
- Pattern: Schema-validated dictionary with observation grain `(concept_type, concept_id, geography_id, period_id, metric_id)`; use `(concept_type, concept_id)` for label lookup.

**Quality and comparison:**
- Purpose: State whether a dataset can be published and whether a pair permits deltas.
- Examples: `brujula/quality.py`, `brujula/pipeline.py:65`.
- Pattern: Return structured checks/reasons; UNKNOWN/BLOCKED or incompatible rows produce null deltas. Match source, universe, method, unit, price basis, concept, geography and synthetic status before calculating a change.

**Insight and agent run:**
- Purpose: Bind every generated statement to supplied evidence while preventing source/bridge activation.
- Examples: `contracts/insight.schema.json`, `contracts/agent-run.schema.json`, `brujula/insights.py`, `brujula/agents.py`.
- Pattern: Generate canonical observation prose and validate exact text, identifiers, source, status and evidence; proposals remain REVIEW. V1 comparison prose is not accepted.

**Receipt, manifest and current pointer:**
- Purpose: Distinguish execution state, evidence state, artifact integrity and publication authority.
- Examples: `contracts/run.schema.json`, `brujula/pipeline.py`.
- Pattern: Separate `status` (`MEASURED|REVIEW|UNKNOWN|BLOCKED`) from `build_status` (`RUNNING|SUCCEEDED|FAILED`); seal terminal receipts once and expose only a verified current run.

**Survey design:**
- Purpose: Keep domain estimation and design variance on a consistent full frame.
- Examples: `brujula/survey.py`, `tests/test_survey.py`.
- Pattern: Explicit immutable weights, nested stratum/PSU groups and Boolean masks. Singleton design strata raise errors; zero weights require explicit caller audit. Never infer missing outcomes as observed zero.

## Entry Points

**Research CLI:**
- Location: `brujula/__main__.py`, `brujula/cli.py`, `pyproject.toml`.
- Triggers: `python -m brujula` or installed `brujula` command.
- Responsibilities: `build`, `demo`, `report`, `verify`, `scout`; no ENOE estimate/refresh/PDF command exists in this parser.

**Library surface:**
- Location: `brujula/__init__.py`.
- Triggers: Python imports from tests or other local scripts.
- Responsibilities: Export `load_dataset`, `validate_dataset`, `compare_observations`, `write_warehouse`. Additional components use their explicit module imports.

**Verification and eval entry points:**
- Location: `brujula/cli.py:15`, `evals/run.py`, `scripts/check_docs.py`, `.github/workflows/verify.yml`.
- Triggers: CLI `verify`, `python -m evals.run`, documentation check, CI push/PR.
- Responsibilities: Offline documentation checks, deterministic negative-control evals, pytest and a synthetic demo on Linux/Windows. These checks do not constitute an ENOE statistical release.

## Architectural Constraints

- **Threading:** The pipeline is synchronous. `BuildLock` excludes overlapping writers per output root; acquisition uses separate per-snapshot locks (`brujula/runlock.py`, `brujula/acquisition.py`). No background scheduler or worker pool is detected in `brujula/`.
- **Global state:** `ROOT` is derived at import time from checkout or working directory; contract paths are module constants. The renderer selects Matplotlib Agg, sets `MPLCONFIGDIR` if absent and changes SVG `rcParams` (`brujula/pipeline.py`, `brujula/resources.py`, `brujula/data.py`, `brujula/agents.py`, `brujula/report.py`).
- **Circular imports:** No active circular dependency is detected in the inspected modules. `brujula/scout.py` imports pipeline helpers and `brujula/cli.py` imports scout lazily; keep source transport out of build orchestration's import-time execution.
- **Contract migration:** Read `docs/CONTRACT.md` before changing interfaces. V1 schema disallows extra properties, so survey interval/design/suppression fields cannot simply be appended to observations (`contracts/dataset.schema.json`, `brujula/survey.py`).
- **Source authority:** The candidate catalog is not a dataset's active source list, and raw acquisition approval is not numeric publication approval (`data/catalog/sources.json`, `data/catalog/enoe-snapshots.json`, `docs/decisions/0006-real-research-scope-and-acquisition.md`).
- **Data custody:** Keep raw ZIPs and individual records outside committed editorial outputs; only reviewed aggregates are candidates for the real research release (`AGENTS.md`, `docs/decisions/0006-real-research-scope-and-acquisition.md`, `.gitignore`).
- **Project rules:** No project skill directories are detected at `.codex/skills/` or `.agents/skills/`. Follow `AGENTS.md` and `docs/CONTRACT.md` for local constraints.

## Anti-Patterns

### Treating a source format enum as an enabled research path

**What happens:** `contracts/dataset.schema.json` permits the text `official_snapshot`, but `brujula/quality.py` rejects that mode unconditionally. Acquisition and survey components remain disconnected from `brujula/pipeline.py`.
**Why it's wrong:** A schema-valid payload or successful ZIP receipt can be mistaken for permission to publish real estimates.
**Do this instead:** Preserve the active source gate and use the explicit acquisition/estimation/publication distinction documented in `docs/decisions/0006-real-research-scope-and-acquisition.md`; treat the missing integrated contract as a concrete implementation boundary.

### Reusing the v1 renderer for real estimates without changing its contract

**What happens:** `brujula/report.py` applies `SYNTHETIC_WARNING` and illustrative-market disclaimers to every publishable payload, irrespective of its mode. `brujula/insights.py` accepts exact v1 observation prose only.
**Why it's wrong:** Real aggregates would carry incorrect synthetic labels, and freely composed research prose would fail the existing semantic gate.
**Do this instead:** Keep v1 output behavior intact until the report, claim contracts and tests are changed together under `docs/CONTRACT.md`. The ENOE plan in `docs/FINAL-RELEASE-PLAN.md` does not itself change those consumers.

## Error Handling

**Strategy:** Fail closed at validation/publication boundaries and retain structured evidence instead of inheriting a historical success (`brujula/pipeline.py`, `brujula/quality.py`).

**Patterns:**
- Loaders and integrity resolvers raise `ValueError`, schema errors or filesystem errors for invalid inputs; quality returns structured diagnostic checks (`brujula/data.py`, `brujula/quality.py`, `brujula/pipeline.py:115`).
- Stage failures inside the build body are converted into sanitized error type/stage receipts. Lock setup and recovery occur outside that inner handler and can raise to the CLI (`brujula/pipeline.py:187`, `brujula/runlock.py`).
- CLI catches `OSError`, `ValueError` and `RuntimeError`, writes an error to stderr and returns exit code 1 (`brujula/cli.py`).
- Metadata scout records blocked receipts; acquisition records operational SUCCEEDED/FAILED receipts using its separate receipt format. Registry lookup errors occur before the acquisition attempt handler (`brujula/scout.py`, `brujula/acquisition.py`).
- Missing and suppressed observations remain null; unavailable statuses prevent numerical display and comparisons (`brujula/quality.py`, `brujula/report.py`, `brujula/survey.py`).

## Cross-Cutting Concerns

**Logging:** JSON receipts, journals, quality diagnostics, manifests and CLI output are the observability surface; a centralized logging framework is not detected (`brujula/pipeline.py`, `brujula/scout.py`, `brujula/acquisition.py`, `brujula/cli.py`).
**Validation:** JSON schemas cover structure; Python gates cover references, grain, comparability, evidence and authority. HTML escaping, CSV formula neutralization, hashed chart names and safe manifest paths protect output consumers (`contracts/`, `brujula/quality.py`, `brujula/agents.py`, `brujula/report.py`, `brujula/export.py`, `brujula/pipeline.py`).
**Authentication:** None for the application; there is no application user model. Optional source reads use public INEGI endpoints and catalog policy rather than credentials (`brujula/scout.py`, `brujula/acquisition.py`, `AGENTS.md`).

---

*Architecture analysis: 2026-09-22*
