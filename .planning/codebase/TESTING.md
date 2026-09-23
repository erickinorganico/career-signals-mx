# Testing Patterns

**Analysis Date:** 2026-09-22

## Test Framework

**Runner:**
- Pytest `9.0.3`, pinned in `requirements.txt` and the test extra in `pyproject.toml`.
- Config: `pyproject.toml`, section `[tool.pytest.ini_options]`; test root is `tests`, default options are `-ra`, and the repository root is on `pythonpath`.
- Runtime target is Python 3.12+ in `pyproject.toml`; `.github/workflows/verify.yml` runs Python 3.12 on Windows and Ubuntu.

**Assertion Library:**
- Plain Python `assert`, `pytest.raises`, and `pytest.approx`; examples are `tests/test_quality.py`, `tests/test_runlock.py`, and `tests/test_survey.py`.
- DuckDB itself verifies persisted schema, values, counts, and Parquet round trips in `tests/test_data.py`, `tests/test_warehouse.py`, `tests/test_export.py`, and `tests/test_pipeline.py`.

**Run Commands:**

```bash
python -m pytest -q                           # All collected tests
python -m pytest -q tests/test_quality.py      # Affected module
python -m pytest -q tests/test_acquisition.py tests/test_survey.py
python -m pytest -q tests/test_pipeline.py -k failed_refresh
python -m evals.run                           # Deterministic claim/authority evals
python scripts/check_docs.py                  # Documentation and repository hygiene
python -m brujula verify                      # Docs + evals + pytest + receipts
```

- These commands correspond to `pyproject.toml`, `evals/run.py`, `scripts/check_docs.py`, and `verify()` in `brujula/cli.py`. Activate the local Python environment first, or use `.venv/Scripts/python.exe` on Windows as `scripts/verify.ps1` does.
- Watch mode: Not detected in `pyproject.toml` or `requirements.txt`.
- Coverage command: Not configured; neither pytest-cov nor coverage.py is declared in `pyproject.toml` or `requirements.txt`.
- This map is based on file inspection; no full suite is executed for the mapping task. Preserve the distinction between recorded evidence and fresh execution.

**Evidence Scope:**
- The synthetic release record in `docs/evidence/release-receipt.json` records 89 passing tests, 12 passing eval cases, and passing Windows/Ubuntu CI for its recorded source revision. This is evidence for the synthetic release scope recorded in that file.
- The mapping assignment reports isolated acquisition and survey checks of 15 and 24 passing cases respectively. Their source files are `tests/test_acquisition.py` and `tests/test_survey.py`; those reported results are not an integrated suite receipt, a current collection total, or an independent statistical oracle.
- The acquisition and survey modules are present in `brujula/acquisition.py` and `brujula/survey.py`, but the active orchestration in `brujula/cli.py` and `brujula/pipeline.py` does not connect them into a real ENOE analytical release.
- Independent implementation comparison, official-data reconciliation, and integrated acceptance are requirements in `docs/FINAL-RELEASE-PLAN.md`; do not infer them from passing unit examples or the synthetic release receipt.

## Test File Organization

**Location:**
- Tests are separate from implementation in `tests/`; production modules live in `brujula/`.
- Deterministic evaluation definitions and runner live in `evals/cases.json` and `evals/run.py`; `tests/test_evals.py` tests their contract and outcomes.
- Repository-wide fixture behavior lives in `tests/conftest.py`; most data factories are local to the test module that needs them.

**Naming:**
- Use `tests/test_<subject>.py` and descriptive `test_<behavior>` functions. No class-based test suites are detected in the inspected tests.
- Use `@pytest.mark.parametrize` for related invalid inputs and boundary conditions; see `tests/test_data.py`, `tests/test_quality.py`, `tests/test_acquisition.py`, and `tests/test_survey.py`.

**Structure:**

```text
tests/
  conftest.py          # Autouse socket denial
  test_data.py         # Strict JSON/schema and warehouse loading
  test_quality.py      # Semantic validation and comparability
  test_warehouse.py    # Normalized tables, provenance and nulls
  test_export.py       # CSV/Parquet/JSON and publication gate
  test_pipeline.py     # Analytical E2E, receipts, crashes and integrity
  test_runlock.py      # Interprocess exclusivity and crash release
  test_report.py       # Offline artifacts, escaping and chart semantics
  test_cli.py          # Resolver error exit paths
  test_agents.py       # Role authority and publication decisions
  test_insights.py     # Exact claims, evidence and concept namespaces
  test_evals.py        # Fixed evaluation contract and determinism
  test_scout.py        # Approved-source metadata with fake transports
  test_acquisition.py  # ZIP acquisition/cache and failure receipts
  test_survey.py       # Totals, ratios, variance and suppression
evals/
  cases.json
  run.py
data/fixtures/
  pilot.json          # Explicitly synthetic analytical fixture
```

## Test Structure

**Suite Organization:**

The representative pattern in `tests/test_quality.py` loads a valid fixture, changes a specific invariant, executes the public validator, and checks diagnostic identity:

```python
def test_quality_fails_duplicate_grain_and_unapproved_source():
    dataset = load_dataset(FIXTURE)
    dataset["observations"].append(copy.deepcopy(dataset["observations"][0]))
    dataset["sources"][0]["approved"] = False
    result = validate_dataset(dataset)
    assert result["publishable"] is False
    ids = {check["id"] for check in result["checks"] if check["status"] == "FAIL"}
    assert {"duplicate_grain", "approved_source"} <= ids
```

**Patterns:**
- Arrange/act/assert is expressed directly without special suite helpers; assertions target semantic outputs and artifact state in `tests/test_quality.py` and `tests/test_pipeline.py`.
- Use `tmp_path` for each filesystem scenario. Tests create local input JSON, output roots, DuckDB databases, and cache fixtures rather than reading a mutable working output directory; see `tests/test_data.py`, `tests/test_export.py`, and `tests/test_acquisition.py`.
- `tests/test_pipeline.py` uses a module-scoped `successful_run(tmp_path_factory)` to avoid rebuilding expensive reports for every invariant. Tests that mutate that run first use `shutil.copytree` into their own `tmp_path`.
- Use explicit evaluation dates such as `date(2026, 9, 22)` in `tests/test_pipeline.py` and `date(2026, 1, 15)` in `tests/test_quality.py` to make temporal assertions reproducible.
- Fixture lifecycle and `monkeypatch` restore changes automatically. No external cleanup service or shared database teardown is configured in `tests/conftest.py`.
- For immutable evidence, compare exact bytes before and after the attempted mutation; examples include preserved receipts, raw collisions, and sealed receipts across commit failures in `tests/test_pipeline.py`.

## Mocking

**Framework:** Pytest `monkeypatch` and simple Python callables; no separate mocking library is declared in `requirements.txt`.

**Patterns:**

Transport substitution in `tests/test_acquisition.py` returns an in-memory ZIP while preserving real hashing, archive inspection, and receipt writes:

```python
payload = _zip()
monkeypatch.setattr(acquisition, "_download", lambda *args: payload)
receipt = acquisition.acquire_snapshot(
    "s1", tmp_path, registry_path=_registry(tmp_path)
)
digest = hashlib.sha256(payload).hexdigest()
assert receipt["status"] == "SUCCEEDED"
assert (tmp_path / "raw" / f"{digest}.zip").read_bytes() == payload
```

`tests/conftest.py` imposes the offline rule for pytest's process:

```python
@pytest.fixture(autouse=True)
def prohibit_test_network(monkeypatch):
    def denied(*args, **kwargs):
        raise AssertionError("Network access is forbidden in the offline test suite")
    monkeypatch.setattr(socket, "create_connection", denied)
    monkeypatch.setattr(socket.socket, "connect", denied)
    monkeypatch.setattr(socket.socket, "connect_ex", denied)
```

**What to Mock:**
- Mock public HTTP at explicit boundaries. `tests/test_scout.py` passes `fake_page(...)` as the scout fetcher; `tests/test_acquisition.py` patches `_download` and provides a disposable registry.
- Inject failures at the stage being tested. `tests/test_pipeline.py` patches `brujula.report.render_report`, `pipeline.atomic_json`, and `pipeline.current_report` to test staging, commit, and index failures separately.
- Replace heavy rendering with the local `fast_renderer` only when testing pipeline state transitions rather than report behavior; see `tests/test_pipeline.py`.
- Capture output through `capsys` for direct CLI calls in `tests/test_cli.py`, and through `subprocess.run(..., capture_output=True)` for actual process failures in `tests/test_pipeline.py` and `tests/test_runlock.py`.

**What NOT to Mock:**
- Keep DuckDB, export serialization, schema validation, hashing, and filesystem atomicity real in their integration tests: `tests/test_data.py`, `tests/test_export.py`, `tests/test_pipeline.py`, and `tests/test_runlock.py`.
- Keep the real renderer for escaping, metadata, byte determinism, null gaps, and chart content tests in `tests/test_report.py`.
- Keep survey arithmetic real in `tests/test_survey.py`; examples and metamorphic transformations are intended to test estimates, uncertainty, and suppression together.
- Do not convert live-source availability into an offline test dependency. `AGENTS.md`, `CONTRIBUTING.md`, and `tests/conftest.py` establish disposable local tests with no production access.
- The socket monkeypatch is process-local. The CLI/lock subprocess tests in `tests/test_pipeline.py` and `tests/test_runlock.py` do not inherit Python monkeypatches; their invoked behaviors are local, but that is not an operating-system network sandbox.

## Fixtures and Factories

**Test Data:**

The canonical fixture is `data/fixtures/pilot.json`, used by `tests/test_data.py`, `tests/test_quality.py`, `tests/test_agents.py`, `tests/test_insights.py`, and `tests/test_pipeline.py`. It contains 54 synthetic combinations, explicit nulls, separate concept dimensions, evidence, and source metadata.

The ZIP factory in `tests/test_acquisition.py` creates a minimal controlled payload:

```python
def _zip(name="ok.csv", body=b"id,value\n1,2\n"):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr(name, body)
    return buffer.getvalue()
```

The calculation fixture in `tests/test_survey.py` is deliberately small enough to inspect:

```python
design = SurveyDesign([1] * 4, [1, 1, 2, 2], [1, 2, 3, 4])
result = design.total([10, 30, 20, 40])
assert result["estimate"] == 100
assert result["standard_error"] == pytest.approx(math.sqrt(800))
assert result["design_df"] == 2
assert result["value"] is None
```

**Location:**
- Shared authored analytical data: `data/fixtures/pilot.json`.
- Small factories and independent copies: `_registry`/`_zip` in `tests/test_acquisition.py`, `fake_page` in `tests/test_scout.py`, and `payload` in `tests/test_report.py`.
- Mutation cases for deterministic agent replay: `evals/cases.json`; mutations are implemented and allowlisted in `evals/run.py`.
- Temporary filesystem data: pytest-managed roots used by `tmp_path`/`tmp_path_factory`; do not substitute mutable `artifacts/` contents for isolated fixtures.

## Coverage

**Requirements:**
- No numeric line/branch coverage threshold is configured in `pyproject.toml` or `.github/workflows/verify.yml`.
- Behavioral acceptance is mapped to requirements in `docs/VALIDATION-PLAN.md`: null preservation, strict schema, reference integrity, comparability, receipts, publication authority, report semantics, and release evidence.
- Critical agent-evaluation violations must be empty; `tests/test_evals.py` asserts the 12-case receipt and required failure-mode set in `evals/cases.json`.
- `docs/FINAL-RELEASE-PLAN.md` separately requires independently checked statistical calculations and real ENOE acceptance; these are not discharged by synthetic E2E checks.

**View Coverage:**
- No generated code-coverage artifact is defined. The actual test outcome artifacts are `artifacts/verification/junit.xml` and `artifacts/verification/verify.json`, created by `brujula/cli.py`.
- JUnit and verifier output report execution outcomes, not line coverage. Inspect `docs/evidence/release-receipt.json` for the explicitly scoped synthetic release record.

**Visible Gaps:**
- Independent survey implementation comparison is not present in `tests/test_survey.py`; the file tests hand-calculable cases, policy thresholds, and invariants. Confidence intervals use `Z90` imported from the implementation, so those assertions do not independently validate the constant.
- `SurveyDesign` in `brujula/survey.py` rejects full-design singleton strata, and `tests/test_survey.py` asserts that rejection. An explicit conservative singleton adjustment is not implemented; an official snapshot containing singleton strata cannot pass this constructor without a separately defined treatment.
- `tests/test_acquisition.py` tests redirect/HTML failure propagation by replacing `_download` with an exception. These cases do not exercise the real `_download` response parsing or `_CheckedRedirects.redirect_request` in `brujula/acquisition.py`.
- Successful replay through `acquire_snapshot(..., offline=True)` is not asserted by `test_offline_replay_verifies_cache_and_resolve` in `tests/test_acquisition.py`; that case exercises `resolve_snapshot`. The pinned-cache failure case does exercise offline acquisition.
- Real ENOE source mapping, official benchmark reconciliation, and full integration into reports are not covered by `tests/test_pipeline.py`, whose analytical fixture is synthetic. The outstanding acceptance scope is specified in `docs/FINAL-RELEASE-PLAN.md`.
- `scripts/check_docs.py` does not enumerate `.planning/`; its PASS cannot certify these codebase-map documents.

## Test Types

**Unit Tests:**
- Strict input shape and nonfinite rejection: `tests/test_data.py`.
- Referential integrity, source approval, null/status consistency, future dates, and comparison compatibility: `tests/test_quality.py`.
- Agent authority, canonical claims, evidence congruence, prompt-like input, and concept namespace collisions: `tests/test_agents.py` and `tests/test_insights.py`.
- Statistical totals/ratios, retained zero-contribution PSUs, nested PSU IDs, row-order invariance, weight-scale metamorphism, invalid weights, denominator rules, precision thresholds, and boundary suppression: `tests/test_survey.py`.

**Integration Tests:**
- Real normalized DuckDB tables and export round trips: `tests/test_warehouse.py`, `tests/test_data.py`, and `tests/test_export.py`.
- Acquisition cache, receipts, archive-path rejection, duplicate members, expansion bounds, pinned hash mismatch, and current-failure semantics with fake transport: `tests/test_acquisition.py`.
- Actual subprocess lock contention and OS release after `os._exit`: `tests/test_runlock.py`.
- Static report generation with real Matplotlib output and semantic/byte assertions: `tests/test_report.py`.

**E2E Tests:**
- Analytical E2E is `tests/test_pipeline.py`: input -> strict load -> quality -> warehouse -> exports -> deterministic agents -> report -> receipt/manifest/current resolver.
- Its success test verifies 54 rows, raw SHA-256, Parquet row count, preserved nulls, manifest hashes, synthetic warnings, HTML images/tables, and absence of scripts.
- Failure E2E checks retain immutable history while invalidating current; separate cases cover missing input, renderer errors, interruption before receipt sealing, errors during pointer commit, and index failure after commit in `tests/test_pipeline.py`.
- Browser/UI E2E framework: Not used. `AGENTS.md` and `docs/VALIDATION-PLAN.md` scope this project to static research artifacts, not a navigable application.
- CI in `.github/workflows/verify.yml` installs pinned requirements, runs `python -m brujula verify`, builds the dated synthetic demo, and resolves its report on Ubuntu and Windows. The workflow definition itself is not evidence of a fresh CI result for unintegrated modules.

## Common Patterns

**Async Testing:**
- Not applicable to the inspected implementation: `brujula/pipeline.py`, `brujula/scout.py`, and `brujula/acquisition.py` are synchronous; no pytest-asyncio setup is declared in `pyproject.toml`.
- Test concurrency through independent processes as `tests/test_runlock.py` does, not by adding an async fixture around synchronous filesystem locks.

**Error Testing:**

`tests/test_pipeline.py` pairs an injected error with assertions on both retained diagnostics and publication denial:

```python
def broken_renderer(*args):
    raise ValueError("renderer failed")

monkeypatch.setattr("brujula.report.render_report", broken_renderer)
payload = build(output=tmp_path)
run = tmp_path / "runs" / payload["run_id"]
assert (run / "observations.parquet").exists()  # diagnostic staging only
assert payload["status"] == "BLOCKED" and payload["dataset"] is None
with pytest.raises(ValueError, match="BLOCKED"):
    resolve_current(tmp_path)
```

- Assert failure receipts and the current pointer, not only exceptions; `tests/test_pipeline.py`, `tests/test_scout.py`, and `tests/test_acquisition.py` all test failure replacing a successful current result.
- Use exception-message fragments for stable failure categories, as in `tests/test_data.py` and `tests/test_survey.py`, rather than complete path-bearing error strings.
- Use metamorphic invariants to complement hand examples: rescale all weights and compare totals, ratios, standard errors, and CV in `tests/test_survey.py`; permute rows without changing estimates.
- Test report determinism by comparing Markdown, HTML, PNG, and SVG bytes from the same payload in `tests/test_report.py`; timestamps and source metadata must be controlled in the fixture.
- For malicious or missing evidence, retain the valid baseline and mutate one policy-relevant field, as `tests/test_insights.py`, `tests/test_agents.py`, and `evals/run.py` do.

---

*Testing analysis: 2026-09-22*
