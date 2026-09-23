# External Integrations

**Analysis Date:** 2026-09-22

## APIs & External Services

**INEGI metadata monitoring:**
- Service: public INEGI ENOE program page on `https://www.inegi.org.mx`, selected by source ID from `data/catalog/sources.json`; the default source is `inegi_enoe_2025_q2` in `brujula/cli.py`.
  - SDK/Client: Python standard-library `urllib.request`, `urllib.robotparser`, and a restricted `HTTPRedirectHandler` in `brujula/scout.py`.
  - Auth: none; public HTTPS reads with a descriptive user agent in `brujula/scout.py`.
  - Entry point: `python -m brujula scout --source inegi_enoe_2025_q2 --output <directory>` from `brujula/cli.py`.
  - Policy: require `monitor_allowed=true`, inspect INEGI `robots.txt`, restrict origin/redirects, cap responses at 3,000,000 bytes, allow specific text/JSON content types, and use 20-second HTTP timeouts in `brujula/scout.py`.
  - Result: raw response digest, HTTP metadata, immutable receipt, changed-content recommendation, and mutable source-current pointer in `brujula/scout.py`. `MEASURED` here means unchanged metadata, not a verified statistical estimate.
  - Authority: receipts always set `activation_allowed=false` and `numeric_publication_allowed=false` in `brujula/scout.py`; monitoring does not activate a source.

**INEGI snapshot acquisition — in-progress local module:**
- Service: eight enumerated official ENOE CSV ZIPs, covering 2024-Q3 through 2026-Q2, in `data/catalog/enoe-snapshots.json`.
  - SDK/Client: standard-library `urllib.request`, `zipfile`, `hashlib`, and filesystem operations in `brujula/acquisition.py`; no INEGI SDK or paid API is used.
  - Auth: none; exact public HTTPS URLs on the registry's `allowed_host`, currently `www.inegi.org.mx`, in `data/catalog/enoe-snapshots.json`.
  - Callable interface: `acquire_snapshot(snapshot_id, output_root, offline=False, registry_path=None)` and `resolve_snapshot(snapshot_id, output_root, registry_path=None)` in `brujula/acquisition.py`.
  - Integration state: `brujula/cli.py` and `brujula/pipeline.py` do not import or dispatch this module; it is an in-progress local addition with isolated tests in `tests/test_acquisition.py`.
  - Access boundary: each snapshot has `acquisition_approved=true`; the registry has `publication_approved=false`. `docs/decisions/0006-real-research-scope-and-acquisition.md` authorizes acquisition separately from validated aggregate publication.
  - Limits: registry caps compressed downloads at 100,000,000 bytes and listed expanded contents at 1,500,000,000 bytes; network timeout is 60 seconds in `brujula/acquisition.py`.
  - Validation: HTTPS/host/redirect checks, size checks, HTML rejection, ZIP member/path/symlink checks, content hashes, and optional expected digest in `brujula/acquisition.py`. All current `expected_sha256` entries in `data/catalog/enoe-snapshots.json` are null, so first-fetch identity comes from the approved URL plus captured digest rather than a pre-pinned digest.
  - Scope: acquisition writes raw ZIPs and receipts; extraction, field mapping, source-universe verification, and analytical publication are separate responsibilities under `docs/decisions/0006-real-research-scope-and-acquisition.md`.
  - Observed compatibility defect: `brujula/acquisition.py` sends `Accept: application/zip`; the local attempt `artifacts/enoe/acquisitions/enoe_2026_q2/attempts/20260923T020515431345Z-156eeebc73cf.json` records HTTP 406 and a null digest. This failed request does not establish that the official source is unavailable. The integrator reports success for the same URL using `Accept: */*`, but that diagnostic is not a sealed acquisition receipt. Require a successful verified attempt before claiming snapshot acquisition.

**Catalogued reference sources — no automated numeric integration:**
- OLA/STPS - Benchmark reference with `monitor_allowed=false` and `numeric_ingestion_allowed=false`; reuse terms are not recorded as an explicit redistribution license in `data/catalog/sources.json`.
- Data México / Secretaría de Economía - API information and legal URLs are catalog metadata only; monitoring and numeric ingestion are disabled in `data/catalog/sources.json`.
- IMCO Compara Carreras - Methodology reference only; the catalog records no reusable data license and disables monitoring and numeric ingestion in `data/catalog/sources.json`.
- INEGI MOPRADEF - Methodology-break negative control; not enabled for monitoring or ingestion in `data/catalog/sources.json`.
- Keep catalog flags distinct from dataset-level active sources: `docs/CONTRACT.md` and `brujula/data.py` define the latter within each validated dataset. The synthetic fixture's source approval in `data/fixtures/pilot.json` is fixture-specific.

**Model services:**
- None in the application runtime. `brujula/agents.py` implements six deterministic read-only roles and `brujula/insights.py` implements evidence-bound claim generation; `pyproject.toml` and `requirements.txt` declare no inference SDK.
- `AGENTS.md` excludes paid APIs, external inference, credentials, and third-party messages; preserve this boundary when extending the project.

## Data Storage

**Databases:**
- DuckDB 1.4.4, embedded local file per run in `brujula/warehouse.py`.
  - Connection: explicit filesystem path; no connection-string environment variable. The JSON pipeline writes `<output>/runs/<run_id>/warehouse.duckdb` in `brujula/pipeline.py`.
  - Client: `duckdb.connect(...)`; direct SQL, with no ORM, in `brujula/warehouse.py` and `brujula/export.py`.
  - Schema: field, occupation, industry, geography, period, metric, source, evidence, bridge, observation, and evidence-link tables in `brujula/warehouse.py`.
  - Write pattern: new database file, explicit transaction, bound insert values, primary/foreign keys, and observation grain uniqueness in `brujula/warehouse.py`.
  - Read/export pattern: read-only connection and DuckDB `COPY ... FORMAT PARQUET` in `brujula/export.py`; JSON retains the full dataset contract, while CSV neutralizes formula prefixes.

**File Storage:**
- Local filesystem only; no object-storage client is declared in `pyproject.toml` or `requirements.txt`.
- JSON builds: `<output>/raw/<sha256>.json`, immutable `<output>/runs/<run_id>/`, and atomic `<output>/current.json` in `brujula/pipeline.py`; each run seals receipt, bundle, manifest, database, exports, and reports.
- Metadata scout: `<output>/raw/<sha256>.bin`, `<output>/runs/<uuid>.json`, and `<output>/current/<hash-of-source-id>.json` in `brujula/scout.py`.
- ENOE acquisition: `<output_root>/raw/<sha256>.zip`, `<output_root>/acquisitions/<snapshot_id>/attempts/<run_id>.json`, and a snapshot-specific `current.json` in `brujula/acquisition.py`.
- `artifacts/`, DuckDB files, environments, and generated build/cache directories are ignored in `.gitignore`; maintain raw microdata exclusion required by `docs/decisions/0006-real-research-scope-and-acquisition.md`.

**Caching:**
- Content-addressed filesystem artifacts replace a cache service in `brujula/pipeline.py`, `brujula/scout.py`, and `brujula/acquisition.py`.
- `acquire_snapshot(..., offline=True)` only reuses locally verified digest-addressed ZIPs; `resolve_snapshot(...)` verifies the successful current receipt, catalog URL, raw digest, and ZIP safety in `brujula/acquisition.py`.
- The acquisition module downloads again when `offline=False`; do not describe its normal path as an unconditional cache-first client. See `brujula/acquisition.py`.
- Matplotlib configuration cache defaults to a temporary `brujula-matplotlib` directory through `MPLCONFIGDIR` in `brujula/report.py`.
- GitHub Actions caches pip dependencies through setup-python in `.github/workflows/verify.yml`; no Redis or remote result cache is configured.

## Authentication & Identity

**Auth Provider:**
- None. Local CLI/file access is the application boundary in `brujula/cli.py`; INEGI source reads are unauthenticated in `brujula/scout.py` and `brujula/acquisition.py`.
- Source identity is recorded as source/snapshot IDs, authority, approved URLs, and evidence references in `data/catalog/sources.json`, `data/catalog/enoe-snapshots.json`, and `contracts/dataset.schema.json`.
- Operational approval is represented by repository policy and registry flags, not user accounts or OAuth scopes: consult `AGENTS.md` and `docs/decisions/0006-real-research-scope-and-acquisition.md`.
- Dataset claims must resolve evidence references; `brujula/agents.py` validates deterministic role output and blocks activation by proposals. Keep this evidence gate separate from filesystem access.

## Monitoring & Observability

**Error Tracking:**
- No hosted error tracker or telemetry agent is declared in `pyproject.toml` or `requirements.txt`.
- Build failures emit local final receipts and a blocked current pointer through `brujula/pipeline.py`; previous successful runs remain historical artifacts.
- Source metadata failures are represented as `BLOCKED` receipts in `brujula/scout.py`; snapshot attempt execution uses `RUNNING`, `SUCCEEDED`, and `FAILED` in `brujula/acquisition.py`. These execution states differ from analytical evidence states in `docs/CONTRACT.md`.

**Logs:**
- JSON receipts on stdout, errors on stderr, and explicit exit codes in `brujula/cli.py`; detailed machine-readable evidence is persisted in `brujula/pipeline.py`.
- Build journal, content hashes, final `receipt.json`, manifest, quality checks, deterministic role output in the bundle, and publication pointer provide the local audit trail in `brujula/pipeline.py`.
- Source capture retains status/content type/URL, ETag, Last-Modified, and digest in `brujula/scout.py`; these are capture metadata, not proof of unchanged statistical methodology.
- Verification emits JSON and JUnit artifacts via `brujula/cli.py`; deterministic evaluation results come from `evals/run.py`.

## CI/CD & Deployment

**Hosting:**
- No application hosting target. `brujula/report.py` generates static Markdown/HTML and SVG/PNG files; `AGENTS.md` excludes a frontend, backend service, or navigable application.
- The designated public repository is `erickinorganico/career-signals-mx` in `README.md` and `AGENTS.md`; publication authorization does not make every local artifact releasable.
- Wheel packaging is configured in `pyproject.toml`; resource lookup supports both a source checkout and installed wheel in `brujula/resources.py`.

**CI Pipeline:**
- GitHub Actions workflow `.github/workflows/verify.yml` runs on pull requests and pushes to `main` or `codex/**` branches.
- Matrix: `ubuntu-latest` and `windows-latest`, Python 3.12, read-only repository permission, 15-minute job timeout in `.github/workflows/verify.yml`.
- Steps: install `requirements.txt`, run `python -m brujula verify`, build the dated synthetic demo, and resolve the verified report pointer in `.github/workflows/verify.yml`.
- No scheduled acquisition, deployment, artifact upload, or release-publication job is configured in `.github/workflows/verify.yml`; do not infer current remote CI success from workflow configuration.

## Environment Configuration

**Required env vars:**
- None detected for application operation in `brujula/`; use explicit CLI paths/arguments in `brujula/cli.py` and local catalogs/contracts via `brujula/resources.py`.
- Optional `MPLCONFIGDIR` controls Matplotlib configuration storage; `brujula/report.py` supplies a temporary-directory default.
- Source connection/limit configuration lives in `data/catalog/sources.json` and `data/catalog/enoe-snapshots.json`, not credentials or environment files.

**Secrets location:**
- No application secrets store is configured in `brujula/` or `.github/workflows/verify.yml`; `AGENTS.md` excludes credentials from the authorized project workflow.
- `.gitignore` excludes environment files. No root environment file was detected during filename-only inspection; no secret-file contents are needed for this mapping.
- Use `scripts/check_docs.py` for the repository's existing publication-hygiene checks, while observing `AGENTS.md` and `THIRD_PARTY_NOTICES.md` for source/license review requirements.

## Webhooks & Callbacks

**Incoming:**
- None in the research runtime; `brujula/cli.py` exposes local subcommands and no HTTP listener. GitHub push/PR events trigger CI through `.github/workflows/verify.yml`.

**Outgoing:**
- No application webhooks, mail, chat messages, or callbacks are implemented in `brujula/`; public-source HTTP reads are confined to `brujula/scout.py` and the in-progress `brujula/acquisition.py`.
- Research output is local files from `brujula/pipeline.py` and `brujula/report.py`. Metadata discovery and acquisition do not automatically publish, activate sources, or notify third parties.

---

*Integration audit: 2026-09-22*
