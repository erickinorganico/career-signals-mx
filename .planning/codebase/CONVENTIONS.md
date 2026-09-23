# Coding Conventions

**Analysis Date:** 2026-09-22

## Naming Patterns

**Files:**
- Use lowercase Python module names under `brujula/`, such as `brujula/quality.py`, `brujula/runlock.py`, and `brujula/acquisition.py`.
- Place corresponding tests in `tests/test_<module>.py`; examples are `tests/test_pipeline.py`, `tests/test_survey.py`, and `tests/test_acquisition.py`.
- Name JSON interface definitions `<artifact>.schema.json`, as in `contracts/dataset.schema.json` and `contracts/run.schema.json`.
- Use uppercase documentation topic names and numbered, descriptive ADR filenames; see `docs/CONTRACT.md` and `docs/decisions/0005-current-failure-wins-over-historical-success.md`.
- Repository-local skill directories are not detected at `.codex/skills/` or `.agents/skills/`. The project constraints are in `AGENTS.md`, `CONTRIBUTING.md`, and `docs/CONTRACT.md`.

**Functions:**
- Use `snake_case` and verb-led public functions: `load_dataset` in `brujula/data.py`, `validate_dataset` and `compare_observations` in `brujula/quality.py`, and `resolve_current` in `brujula/pipeline.py`.
- Prefix implementation helpers with `_`: `_schema_errors` in `brujula/agents.py`, `_safe_chart_name` in `brujula/report.py`, and `_zip_safety` in `brujula/acquisition.py`.
- Use `test_<behavior>` names that state the invariant or rejected condition; `tests/test_pipeline.py` includes `test_failed_refresh_replaces_current_without_destroying_history`.

**Variables:**
- Use `snake_case` for local variables and serialized fields. The JSON naming contract is explicit in `docs/CONTRACT.md`.
- Use uppercase module constants: `ADAPTER_VERSION` in `brujula/pipeline.py`, `FIELDS` in `brujula/export.py`, and `VARIANCE_METHOD` in `brujula/survey.py`.
- Preserve domain names such as `concept_type`, `geography_id`, `population`, `methodology_id`, `price_basis`, and `evidence_refs`; do not substitute convenient aliases that collapse dimensions. See `contracts/dataset.schema.json` and `brujula/warehouse.py`.
- Keep identity typed: use `(concept_type, concept_id)` for concept lookups, as implemented in `brujula/insights.py` and `brujula/report.py`.

**Types:**
- Use `PascalCase` for the few stateful abstractions and exceptions: `BuildLock` in `brujula/runlock.py`, `SurveyDesign` in `brujula/survey.py`, and `AcquisitionError` in `brujula/acquisition.py`.
- Use built-in generic annotations and unions where the module already has annotations: `dict[str, Any]`, `list[dict[str, Any]]`, and `Path | str | None`; see `brujula/data.py`, `brujula/agents.py`, and `brujula/pipeline.py`.
- Most data interfaces are plain dictionaries constrained by JSON Schema and semantic checks, not model classes. See `contracts/`, `brujula/data.py`, and `brujula/quality.py`.
- Annotation coverage is mixed: `brujula/survey.py` methods and several nested helpers in `brujula/warehouse.py` are unannotated. No enforced static typing policy is present in `pyproject.toml`.

## Code Style

**Formatting:**
- Python uses four-space indentation, predominantly double-quoted strings, and blank lines between top-level definitions; follow the surrounding style in `brujula/data.py` and `brujula/export.py`.
- No formatter or formatting configuration is detected in `pyproject.toml`, `requirements.txt`, or the repository file inventory. Do not assume Black, Ruff format, or a fixed line-length gate.
- Long dictionary literals and compact one-line guard statements exist in `brujula/quality.py`; compact fixture dictionaries exist in `tests/test_report.py`. Avoid unrelated reformatting while editing a focused behavior.
- Use UTF-8 for authored text and JSON. `brujula/export.py` deliberately writes CSV as UTF-8 with BOM for spreadsheet interoperability; its JSON exports use UTF-8 without that CSV convention.
- Preserve LF text normalization and generated-byte exceptions in `.gitattributes`: `examples/synthetic/**` is excluded from text conversion because published hashes depend on exact bytes.
- Serialize pipeline JSON through `json_bytes` in `brujula/pipeline.py`; it preserves insertion order, rejects nonfinite values, preserves Unicode, and terminates with a newline. It does not sort object keys.

**Linting:**
- No Ruff, Flake8, Pylint, isort, mypy, or dedicated pre-commit configuration is detected in `pyproject.toml`, `requirements.txt`, or `.github/workflows/verify.yml`.
- `scripts/check_docs.py` checks local Markdown targets, required deliverables, JSON syntax, likely credential patterns, and machine-specific personal paths. It is a repository hygiene check, not a Python style checker or complete security audit.
- Run affected checks and the documentation check under the contributor process in `CONTRIBUTING.md`; the integrated command is implemented by `verify()` in `brujula/cli.py`.
- `scripts/check_docs.py` explicitly enumerates checked roots and does not include `.planning/`; inspect generated codebase maps directly instead of treating that check as validation of these files.

## Import Organization

**Order:**
1. Module docstring, then `from __future__ import annotations` when used; see `brujula/pipeline.py` and `brujula/report.py`.
2. Standard library imports, then third-party packages, then relative application imports; `brujula/data.py` is a representative example.
3. Tests import public behavior through `brujula.<module>`; see `tests/test_quality.py`. They also import selected private rendering helpers for focused edge cases in `tests/test_report.py`.

Import ordering is a convention, not an enforced sorter rule: `tests/test_scout.py` and `brujula/quality.py` contain mixed ordering. Preserve special initialization order in `brujula/report.py`: configure `MPLCONFIGDIR` and the `Agg` backend before importing `pyplot`.

**Path Aliases:**
- No application path alias system is detected. Pytest includes the repository root via `pythonpath = ["."]` in `pyproject.toml`.
- Resolve shipped schemas, catalog, and fixture through `brujula/resources.py`; its helpers support both source checkout and installed package resource locations.
- `brujula/pipeline.py` uses function-local imports for pipeline stages, and `brujula/cli.py` imports the optional scout at dispatch. Preserve those boundaries when changing initialization or monkeypatch targets.

## Error Handling

**Patterns:**
- Reject malformed input at the load boundary. `load_dataset` in `brujula/data.py` rejects duplicate JSON keys, NaN/Infinity and overflowed floats, then validates Draft 2020-12 schema and date formats.
- Return structured diagnostic data for semantic validation: `validate_dataset` in `brujula/quality.py` returns `status`, `publishable`, `checks`, `row_statuses`, and `freshness`; checks carry an `id`, diagnostic `status`, and `message`.
- Keep statistical state, diagnostic outcome, and execution state separate. The distinction is specified in `docs/CONTRACT.md`; `brujula/pipeline.py` uses public `status` plus execution `build_status`, while `brujula/quality.py` uses `PASS|FAIL` inside checks.
- Preserve null for unavailable values. `compare_observations` in `brujula/quality.py` returns null deltas plus explicit reasons when source, universe, geography, measure, method, price basis, concept, evidence, or period checks fail.
- Raise exceptions for invalid operations at library boundaries: `FileExistsError` for overwriting a warehouse/export in `brujula/warehouse.py` and `brujula/export.py`, and `ValueError` for invalid survey design or nonfinite contributions in `brujula/survey.py`.
- At orchestration boundaries, write a failed receipt and invalidate the current pointer. `_failure` and `_recover_interrupted` in `brujula/pipeline.py` preserve immutable history while preventing a failed refresh from serving a successful historical run.
- Treat the human report index as derived. Resolve authoritative output using `resolve_current` in `brujula/pipeline.py`, which validates state and hashes; file existence alone does not authorize publication.
- CLI errors use stderr and nonzero return codes. `main` in `brujula/cli.py` catches `OSError`, `ValueError`, and `RuntimeError` and returns `1`.
- Acquisition is a separate interface: `brujula/acquisition.py` records `SUCCEEDED|FAILED` acquisition status and exposes `AcquisitionError`. Do not treat that receipt as the schema-defined analytical run receipt in `contracts/run.schema.json`.

## Logging

**Framework:** Structured JSON receipts and direct CLI output; no logging framework is detected in `brujula/cli.py`, `brujula/pipeline.py`, or `brujula/acquisition.py`.

**Patterns:**
- Emit machine-readable summaries with `json.dumps(..., ensure_ascii=False, indent=2)` in `brujula/cli.py`, `evals/run.py`, and `scripts/check_docs.py`.
- Persist build evidence in immutable per-run receipts and manifests; journal and current pointer are mutable execution state. See `brujula/pipeline.py` and `docs/CONTRACT.md`.
- Include error type and appropriate message while excluding headers, credentials, and secrets. `brujula/acquisition.py` includes `_clean_error`; the receipt boundary is specified in `docs/CONTRACT.md`.
- Keep public CLI and report text primarily Spanish, with English identifiers and many internal diagnostic messages; see `brujula/cli.py`, `brujula/report.py`, and `brujula/quality.py`.

## Comments

**When to Comment:**
- Explain authority and analytical assumptions rather than narrating statements: `brujula/scout.py` documents that discovery cannot activate sources, and `brujula/warehouse.py` states that callers validate before materialization.
- Explain the invariant behind unusual mechanics: `brujula/scout.py` hashes source IDs so they cannot become paths; `tests/test_pipeline.py` labels retained exports as diagnostic staging after renderer failure.
- Keep statistical assumptions near implementation. The `brujula/survey.py` module docstring requires the full design frame and states that final weights are fixed; it does not establish source or universe validity.
- Keep architecture decisions and interface changes in `docs/decisions/` and `docs/CONTRACT.md`, following `CONTRIBUTING.md`.

**JSDoc/TSDoc:**
- Not applicable: implementation is Python. Use Python docstrings following `brujula/data.py`, `brujula/export.py`, and `brujula/survey.py`; no uniform parameter-docstring format is enforced.

## Function Design

**Size:**
- No enforced function-size limit is detected in `pyproject.toml`. Small pure formatting, validation, and filesystem helpers sit beside longer orchestration functions in `brujula/report.py`, `brujula/quality.py`, and `brujula/pipeline.py`.
- Keep numerical computation in `brujula/survey.py`, publication orchestration in `brujula/pipeline.py`, transport and cache verification in `brujula/acquisition.py`, and formatting in `brujula/report.py`.

**Parameters:**
- Accept explicit input/output paths and dates instead of embedding personal paths; see `build(input_path, output, as_of)` in `brujula/pipeline.py`.
- Inject the source transport through `scout_source(..., fetcher=fetch_public_page)` in `brujula/scout.py`; acquisition tests patch `_download` and inject `registry_path` in `tests/test_acquisition.py`.
- Use keyword-only policy controls where accidental positional selection is risky: `offline` and `registry_path` in `brujula/acquisition.py`, and `allow_zero_weights` in `brujula/survey.py`.
- Supply the full survey design before passing a domain mask. `SurveyDesign` in `brujula/survey.py` copies weights, makes them read-only, nests PSU IDs within strata, and rejects true singleton strata.
- Pass period context explicitly into comparisons through `periods_by_id`; `brujula/quality.py` does not infer chronological order from period labels.

**Return Values:**
- Prefer explicit JSON-shaped results containing status, evidence, limitations, and reasons; examples are `brujula/quality.py`, `brujula/agents.py`, and `brujula/survey.py`.
- Separate an internal estimate from its publishable value: `SurveyDesign._result` in `brujula/survey.py` can preserve `estimate` while setting `value` to null and recording `suppression_reason`.
- The survey result is not directly compatible with the active dataset contract: `brujula/survey.py` can return suppressed `REVIEW` values, while `brujula/quality.py` requires null observations to be `UNKNOWN|BLOCKED`. Treat schema/consumer integration as an explicit contract change under `docs/FINAL-RELEASE-PLAN.md`.
- Return report filenames relative to the run directory, as `render_report` does in `brujula/report.py`, rather than embedding machine-specific absolute paths in distributable metadata.

## Module Design

**Exports:**
- `brujula/__init__.py` exposes only `load_dataset`, `validate_dataset`, `compare_observations`, and `write_warehouse` through `__all__`.
- Import specialized features directly from their modules, as in `tests/test_survey.py`, `tests/test_pipeline.py`, and `tests/test_acquisition.py`.
- Keep external effects at explicit command or adapter boundaries. `brujula/agents.py` is deterministic replay with exactly six read-only roles; proposals do not activate sources, bridges, or publication.
- Keep untrusted text literal. `brujula/report.py` escapes HTML and Markdown, hashes chart identifiers, and suppresses unavailable-status values; `brujula/export.py` neutralizes spreadsheet formula prefixes.
- Persist canonical data with exclusive creation and publish the current pointer atomically, following `immutable_bytes` and `atomic_json` in `brujula/pipeline.py` and the locking rules in `brujula/runlock.py`.

**Barrel Files:**
- The small re-export surface in `brujula/__init__.py` is the only package-level barrel detected. Do not assume every module belongs in that public interface.
- Resource packages for schemas, catalog, and fixtures are configured in `pyproject.toml`; route authored resource access through `brujula/resources.py` rather than relying on the working directory.

---

*Convention analysis: 2026-09-22*
