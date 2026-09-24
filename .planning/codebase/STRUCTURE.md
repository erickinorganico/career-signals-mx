---
last_mapped_commit: 20b935e
last_mapped_at: 2026-09-22
---
# Codebase Structure

**Analysis Date:** 2026-09-22

## Directory Layout

Root-file inventory refreshed for the GSD drift advisory: `.gitattributes` controls LF/binary handling and preserves published example bytes; `CHANGELOG.md` records historical releases; `LICENSE` is MIT; `PROJECT-EFFICIENCY.md` documents deterministic runtime and Laya non-applicability; `README.en.md` is the English entry; `CONTRIBUTING.md` governs local verification; `THIRD_PARTY_NOTICES.md` records source/dependency attribution. These are files already present at the mapping baseline, not new directories.

```text
Observatorio/
├── brujula/                    # Python research package and CLI
│   ├── __main__.py             # python -m brujula entry
│   ├── cli.py                  # build/demo/report/verify/scout commands
│   ├── pipeline.py             # Gates, runs, receipts, current publication
│   ├── resources.py            # Checkout/wheel resource resolution
│   ├── data.py                 # Strict JSON/schema loading
│   ├── quality.py              # Semantic quality and comparisons
│   ├── agents.py               # Six deterministic read-only roles
│   ├── insights.py             # Canonical evidence-bound prose
│   ├── warehouse.py            # Per-run normalized DuckDB
│   ├── export.py               # CSV, Parquet and dataset JSON
│   ├── report.py               # Static Markdown/HTML and SVG/PNG
│   ├── runlock.py              # Cross-platform single-writer lock
│   ├── scout.py                # Opt-in public metadata monitor
│   ├── acquisition.py          # ENOE ZIP acquisition; separate from build
│   └── survey.py               # Survey estimates; separate from build
├── contracts/                  # v1 JSON Schema resources
├── data/
│   ├── catalog/                # Source policy and ENOE snapshot registry
│   └── fixtures/               # Authored synthetic pilot
├── tests/                      # Offline pytest suites by module
├── evals/                      # Deterministic analytical negative controls
├── scripts/                    # Shell wrappers and documentation checks
├── docs/                       # Project contracts, plans and methodology
│   ├── decisions/              # Numbered architectural decisions
│   ├── evidence/               # Authored/preserved verification receipts
│   └── research/               # ENOE method and product research
├── examples/synthetic/         # Reviewed synthetic report and chart example
├── .github/workflows/          # Verification CI
├── .planning/codebase/         # GSD implementation maps
├── artifacts/                  # Ignored local run/acquisition outputs
├── .cache/                     # Ignored local cache
├── .venv/                      # Ignored Python environment
├── build/                      # Ignored package build output
├── career_signals_mx.egg-info/  # Ignored package metadata
├── AGENTS.md                   # Repository execution and evidence rules
├── pyproject.toml              # Package, entry point, resources, pytest config
├── requirements.txt            # Pinned environment requirements
├── README.md / README.en.md    # Spanish and English entry documentation
└── CONTRIBUTING.md            # Contribution and validation process
```

The tree describes the inspected checkout. `brujula/acquisition.py`, `brujula/survey.py`, their tests, `data/catalog/enoe-snapshots.json` and the ENOE research/decision documents are untracked additions; they are not evidence of an integrated publication command. `brujula/cli.py` and the schemas in `contracts/` still expose v1.

## Directory Purposes

**`brujula/`:**

- Purpose: Keep the small research pipeline in one Python package, partitioned by responsibility rather than web/application layers.
- Contains: Functional loaders, gates, artifact writers, renderer, optional source transports and the `SurveyDesign` class.
- Key files: `brujula/pipeline.py`, `brujula/quality.py`, `brujula/cli.py`, `brujula/report.py`.
- Put source access in `brujula/scout.py` or `brujula/acquisition.py`, statistical estimation in `brujula/survey.py`, and publication state management in `brujula/pipeline.py`. These boundaries are visible in the imports and call sites.

**`contracts/`:**

- Purpose: Define machine-checkable v1 public structures.
- Contains: Strict Draft 2020-12 JSON schemas, not business calculations or activation decisions.
- Key files: `contracts/dataset.schema.json`, `contracts/insight.schema.json`, `contracts/agent-run.schema.json`, `contracts/run.schema.json`.
- Packaging maps this directory to `brujula.contracts`; access it through `brujula/resources.py`, not a hardcoded working-directory path (`pyproject.toml`).

**`data/catalog/`:**

- Purpose: Preserve source policy and explicit acquisition registries separately from observations.
- Contains: `data/catalog/sources.json` for candidate sources and metadata permissions; `data/catalog/enoe-snapshots.json` for eight approved raw acquisition entries.
- Key rule: A candidate, metadata success or acquisition receipt does not activate numeric publication (`docs/decisions/0006-real-research-scope-and-acquisition.md`).
- Packaging maps these JSON files to `brujula.catalog` (`pyproject.toml`, `brujula/resources.py`).

**`data/fixtures/`:**

- Purpose: Ship deterministic, explicitly synthetic input for the offline demonstration and tests.
- Contains: `data/fixtures/pilot.json` with dimensions, sources, metrics, evidence and observations.
- Key rule: Keep this fixture synthetic; do not replace its rows with real survey records (`AGENTS.md`, `brujula/quality.py`).
- Packaging maps JSON fixtures to `brujula.fixtures` (`pyproject.toml`).

**`tests/` and `evals/`:**

- Purpose: Separate module/flow regression tests from declared analytical and authority-negative controls.
- Contains: `tests/test_<module>.py`, the autouse network prohibition in `tests/conftest.py`, `evals/cases.json`, and `evals/run.py`.
- Key files: `tests/test_pipeline.py`, `tests/test_quality.py`, `tests/test_insights.py`, `tests/test_report.py`, `tests/test_acquisition.py`, `tests/test_survey.py`.
- Use disposable paths and fake transports; real source access does not belong in the offline test suite (`tests/conftest.py`).

**`docs/`:**

- Purpose: Maintain the repository-owned product, statistical and interface contracts alongside evidence.
- Contains: Scope, specification, methodology, plans, risks, source policy and release status.
- Key files: `docs/CONTRACT.md`, `docs/ARCHITECTURE.md`, `docs/METHODOLOGY.md`, `docs/STATUS.md`, `docs/FINAL-RELEASE-PLAN.md`.
- Keep an implemented interface map distinct from a target plan. `docs/ARCHITECTURE.md` includes an implementation-status table, while the actual module behavior is authoritative for this codebase map.

**`docs/decisions/`, `docs/research/`, `docs/evidence/`:**

- Purpose: Separate decisions, research findings and verification artifacts.
- Contains: Numbered ADRs; ENOE method/product research; release and dependency review receipts.
- Key files: `docs/decisions/0006-real-research-scope-and-acquisition.md`, `docs/research/ENOE-METHOD-REVIEW.md`, `docs/research/PRODUCT-GAP-AUDIT.md`, `docs/evidence/release-receipt.json`.
- Record a source/publication authority change in the decision layer; an agent research finding is not itself activation (`AGENTS.md`).

**`scripts/` and `.github/workflows/`:**

- Purpose: Offer thin command wrappers and automate verification.
- Contains: PowerShell/shell demo wrappers, `scripts/check_docs.py`, and `.github/workflows/verify.yml`.
- Key behavior: CI installs pinned dependencies, runs `python -m brujula verify`, then builds and resolves a synthetic demo on Linux and Windows.

**`examples/synthetic/`:**

- Purpose: Provide a reviewed, shareable static illustration without installing the repository.
- Contains: `examples/synthetic/report.md`, `examples/synthetic/report.html`, paired SVG/PNG charts, and `examples/synthetic/README.md`.
- Key rule: Preserve visible synthetic status; this directory is not the active publication pointer (`README.md`, `brujula/pipeline.py`).

## Key File Locations

**Entry Points:**

- `brujula/__main__.py`: Module executable.
- `brujula/cli.py`: Argument parser and command dispatch.
- `brujula/__init__.py`: Small public import surface for data, quality, comparison and warehouse functions.
- `evals/run.py`: Deterministic eval command.
- `scripts/check_docs.py`: Offline links, required documentation, JSON and heuristic secret/path checks.

**Configuration:**

- `pyproject.toml`: Setuptools build, Python version, dependencies, console entry, package resource mapping, pytest options.
- `requirements.txt`: Pinned install requirements.
- `.python-version`: Local Python version selection.
- `.gitignore`: Runtime artifacts, caches, environments and build outputs excluded from Git.
- `.github/workflows/verify.yml`: Linux/Windows CI verification.
- `AGENTS.md`: Local authorization, conceptual boundaries and data handling rules.
- `docs/CONTRACT.md`: Interface and artifact contracts to read before changing consumers or producers.

**Core Logic:**

- `brujula/pipeline.py`: `build`, `resolve_current`, receipts, immutable/atomic writes, failed-run recovery.
- `brujula/quality.py`: `validate_dataset`, `compare_observations` and publication status reduction.
- `brujula/warehouse.py`: Dimensions, metric/source/evidence tables, observations and evidence link tables.
- `brujula/agents.py`, `brujula/insights.py`: Role output and exact claim/evidence validation.
- `brujula/export.py`, `brujula/report.py`: Structured exports and static outputs.
- `brujula/acquisition.py`, `brujula/survey.py`: Standalone acquisition and estimation components without a v1 build connection.

**Testing:**

- `tests/conftest.py`: Global test network prohibition.
- `tests/test_pipeline.py`, `tests/test_runlock.py`, `tests/test_cli.py`: Execution, failure, integrity, concurrency and CLI contracts.
- `tests/test_data.py`, `tests/test_quality.py`, `tests/test_warehouse.py`, `tests/test_export.py`: Analytical and persistence contracts.
- `tests/test_agents.py`, `tests/test_insights.py`, `tests/test_evals.py`: Evidence and role-authority controls.
- `tests/test_report.py`: Escaping, synthetic labels, null gaps, path safety and determinism.
- `tests/test_scout.py`, `tests/test_acquisition.py`, `tests/test_survey.py`: Optional source transports and statistical component checks.
- `evals/cases.json`: Declared mutation cases for false zero, fabricated claims, conceptual confusion and related failures.

## Naming Conventions

**Files:**

- Use short lowercase Python module names by responsibility, such as `brujula/quality.py` and `brujula/warehouse.py`.
- Mirror module names with `tests/test_<module>.py`, such as `tests/test_survey.py`.
- Use `<artifact>.schema.json` for public contracts, such as `contracts/run.schema.json`.
- Use uppercase descriptive filenames for main documentation and GSD maps, such as `docs/CONTRACT.md` and `.planning/codebase/ARCHITECTURE.md`.
- Use numbered, hyphenated ADR filenames, such as `docs/decisions/0005-current-failure-wins-over-historical-success.md`.
- Use source/purpose catalog names such as `data/catalog/sources.json` and `data/catalog/enoe-snapshots.json`.

**Directories:**

- Group authored data by purpose under `data/catalog/` and `data/fixtures/`; keep generated data under ignored output roots (`.gitignore`, `brujula/pipeline.py`).
- Group documentation by decision, research or evidence under `docs/decisions/`, `docs/research/`, `docs/evidence/`.
- Preserve `raw/<sha256>.<extension>` and `runs/<run_id>/` for generated provenance; use the path builders in `brujula/pipeline.py` and `brujula/acquisition.py`.

## Where to Add New Code

**New Feature:**

- Primary code: Add a focused module under `brujula/`; wire shell-facing behavior through `brujula/cli.py` and artifact ordering through `brujula/pipeline.py`.
- Tests: Add or extend `tests/test_<module>.py`; exercise publication/failure interactions in `tests/test_pipeline.py` and CLI behavior in `tests/test_cli.py`.
- Interface: Change `contracts/` and `docs/CONTRACT.md` together when a public payload changes. Strict v1 observations do not accept survey design/interval/suppression fields from `brujula/survey.py`.
- Scope: ENOE adaptation, v2 publication and a real editorial report are not existing directories or commands. Use the owned tasks in `docs/FINAL-RELEASE-PLAN.md` rather than assuming these interfaces are implemented.

**New Component/Module:**

- Source metadata: Follow `brujula/scout.py` and candidate permission records in `data/catalog/sources.json`.
- Raw snapshot acquisition: Extend `brujula/acquisition.py` and `data/catalog/enoe-snapshots.json` within the explicit decision in `docs/decisions/0006-real-research-scope-and-acquisition.md`.
- Statistical estimation: Keep design calculations in `brujula/survey.py`; verify with analytical examples and independent oracles in `tests/test_survey.py`.
- Data validation/comparability: Add checks to `brujula/quality.py`, preserving explicit concept/source/method boundaries and null semantics.
- Evidence-bound claims: Use `brujula/insights.py` and `brujula/agents.py`; define corresponding contract and eval cases before allowing a new claim shape.
- Report/chart output: Use `brujula/report.py` and `tests/test_report.py`; preserve table alternatives, escaped content and integrity sealing by `brujula/pipeline.py`.

**Utilities:**

- Shared resource lookup: `brujula/resources.py`; add packaged JSON resources via `pyproject.toml`.
- Publication filesystem helpers: `brujula/pipeline.py` provides `atomic_json`, `immutable_bytes`, `json_bytes` and receipt sealing. `brujula/runlock.py` owns locking.
- Development wrappers/checks: `scripts/`; keep analytical business logic in `brujula/`, as shown by `scripts/demo.ps1` and `scripts/demo.sh`.
- There is no general `utils/` package; keep new helpers with the module that owns their invariants (`brujula/`).

## Special Directories

**`artifacts/`:**

- Purpose: Local generated output, including `current.json`, raw content-addressed inputs, immutable run directories, reports, verification and optional acquisition/scout output (`brujula/pipeline.py`, `brujula/cli.py`, `brujula/acquisition.py`).
- Generated: Yes.
- Committed: No; excluded by `.gitignore`.
- Layout is scoped by `--output`: `artifacts/demo/` or any caller-selected output root has its own `current.json`, `raw/` and `runs/` (`brujula/cli.py`).

**`examples/synthetic/`:**

- Purpose: Curated exported report/chart artifacts with synthetic warnings (`examples/synthetic/README.md`).
- Generated: Report and charts are generated; the directory is deliberately curated for sharing.
- Committed: Yes; tracked separately from ignored `artifacts/`.

**`.planning/codebase/`:**

- Purpose: GSD navigation and implementation reference maps.
- Generated: Authored analysis from code inspection.
- Committed: No tracked files in this directory at inspection; the assigned maps are new local output. It is not excluded by `.gitignore`.
- Do not treat these maps as source activation or release receipts; authority remains in `AGENTS.md`, `docs/CONTRACT.md` and relevant ADRs.

**`.venv/`, `.cache/`, `.pytest_cache/`, `brujula/__pycache__/`:**

- Purpose: Local interpreter/dependencies, caches and test/runtime state (`.gitignore`).
- Generated: Yes.
- Committed: No.
- Do not map application structure from installed dependencies or caches; authored modules are in `brujula/`.

**`build/`, `dist/`, `career_signals_mx.egg-info/`:**

- Purpose: Setuptools distribution output and metadata (`pyproject.toml`, `.gitignore`).
- Generated: Yes; `build/` and package metadata are present in the checkout, while `dist/` is a configured ignored output location.
- Committed: No.
- Package resource mappings may create an installed layout different from the source tree; use `brujula/resources.py` to resolve either form.

**`.codex/skills/`, `.agents/skills/`:**

- Purpose: Project-local skill instructions, if present.
- Generated: Not applicable.
- Committed: Not detected; neither project skill directory exists in this checkout. Repository rules are in `AGENTS.md`.

---

*Structure analysis: 2026-09-22*
