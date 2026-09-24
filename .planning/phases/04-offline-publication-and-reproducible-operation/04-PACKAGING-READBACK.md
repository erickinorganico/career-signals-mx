# Phase 4 packaging readback

**Scope and status:** read-only packaging handoff at the Phase 2 source freeze
`86406f6`. This file records current evidence and a proposed implementation
boundary. No code, fixture, source row, or publication artifact was changed.

## Current installed-wheel evidence

The existing **historical** offline wheel is
`.cache/research/wheels/career_signals_mx-0.1.0-py3-none-any.whl`.
Its ZIP contains the older v1 runtime and a partial v2 surface. It does **not**
contain the then-current acceptance modules `brujula/enoe_adapter.py`,
`brujula/estimates.py`, or `brujula/metrics.py`, and contains no `scripts/`
tree. This is stale-wheel evidence, not a defect in today's package
declarations; it cannot establish current installed real-data behavior.

The recorded wheel readback is `.cache/final-wheel-outside/wheel-check.json`
(status `PASS`, `installed_without_checkout: true`, Python 3.12.13). That PASS
only covers the synthetic v1 demo: 54 rows, 7 nulls, 8 charts and a verified
manifest. The recorded wheel SHA-256 is
`1117e9b788271c1ef3ad855104520be4afdbf1f8d67d8ea8331da1586fe68410`.
It is evidence of v1 installation behavior, not evidence of real-data
acceptance/replay.

A fresh offline build using `uv --cache-dir .cache/uv build --wheel --offline
--python .venv/Scripts/python.exe --out-dir
.cache/research/phase2-wheel-readback` succeeded. Its build log shows the
current `pyproject.toml` includes all current `brujula/*.py` modules and the
JSON globs include `enoe-metrics.json`, `enoe-snapshots.json`, and
`enoe-aggregate-golden.json`. This is a packaging-content check only; the
wheel has still not run installed real-data acceptance.

## Exact gaps that block installed real-data replay

1. `brujula/cli.py` exposes only `build`/`demo`, `verify`, `report`, and
   `scout`. There is no installed entry point for the Phase 2 acceptance,
   replay, or official reconciliation. `verify()` also intentionally requires
   `CHECKOUT_ROOT`, so it cannot be the installed acceptance command.
2. `scripts/accept_enoe_estimates.py` derives `ROOT` from the script location,
   opens `data/catalog/enoe-snapshots.json` and
   `data/fixtures/enoe-aggregate-golden.json`, and hashes checkout scripts and
   modules. The script is absent from the wheel and these checkout-relative
   inputs are not all package resources.
3. The current package declarations already ship the estimator imports
   `brujula.enoe_adapter`, `brujula.estimates`, and `brujula.metrics`, and the
   catalog/fixture JSON globs already ship the metric catalog and golden
   baseline. Accepted ENOE ZIPs and receipts remain user-supplied offline
   source roots and must not be embedded. The remaining gap is that the
   acceptance implementation itself is still checkout-only.
4. `_execute_r()` currently resolves `BRUJULA_RSCRIPT`, then a checkout-local
   `.cache/R-4.6.1/bin/Rscript.exe`, then literal `Rscript`; it also passes a
   checkout-local library path and script path. Those defaults cannot work from
   an installed wheel.
5. The current `pyproject.toml` pins DuckDB, jsonschema, Matplotlib and NumPy,
   but does not declare the Phase 4 PDF dependency (`weasyprint==70.0`). A
   clean PDF acceptance therefore needs an explicit PDF extra/configuration
   check; native Pango/Fontconfig remains an OS prerequisite rather than a
   Python wheel resource.

## Minimal proposed ownership and compatibility seam

The following is a recommendation, not implemented behavior.

* `brujula/enoe_acceptance.py` should own the moved implementation from
  `scripts/accept_enoe_estimates.py`, with the existing public callable
  `accept(output_root: Path, audit_dir: Path, *, generate_golden=False)` and
  `main(argv=None)` retained. The current callable accepts only
  `output_root` and `audit_dir`; a future CLI may map an explicit
  `--source-root` into the acquisition/output-root contract, but a compatibility
  wrapper must preserve the current callable signature. It should resolve
  package catalogs and the R oracle through `importlib.resources`.
* `brujula/official_reconciliation.py` should own the moved reconciliation
  implementation and retain the exact current signatures
  `reconcile(output_root: Path, workbook: Path, records: list[dict])`,
  `check_2026_pdf_benchmark(pdf: Path, records: list[dict])`,
  `workbook_cells(path: Path)`, and `main(argv=None)`. The existing
  `scripts/official_reconciliation.py` should become a compatibility wrapper
  that imports and calls that module's `main`, preserving checkout users.
* `scripts/accept_enoe_estimates.py` should likewise become a thin compatibility
  wrapper. The wrapper signatures preserve existing automation while the
  installed command uses the package module. No acceptance logic should hash a
  wrapper in place of the implementation; code identity should name the
  package modules and oracle resource explicitly.
* `brujula/oracle/enoe_survey_oracle.R` (or an equivalent package-data location)
  should ship the R script. `brujula.resources` should expose typed accessors
  for `enoe-snapshots.json`, `enoe-metrics.json`, the golden baseline, and the
  oracle script. `importlib.resources.files("brujula").joinpath(...)` is the
  installed-wheel path; checkout fallback can remain only for compatibility.
* R discovery should be deterministic and fail closed: use an explicit
  `BRUJULA_RSCRIPT` file path first; otherwise `shutil.which("Rscript")`; on
  Windows also probe the documented project-local runtime only when an explicit
  `--r-home`/config path is supplied. Validate that the resolved executable is
  a file, run `Rscript --version`, set `BRUJULA_R_LIB` only when configured,
  and include executable/version/library identity in the acceptance receipt.
  Do not mutate PATH or silently depend on a checkout cache.
* Add explicit `enoe-accept` and `enoe-replay` subcommands to `brujula` (or
  equivalent package entry points) with source/output/audit roots and a
  read-only replay mode. Keep v1 `build`/`demo` behavior intact. The CLI must
  reject missing catalogs, missing source receipts, missing R, or a missing
  PDF extra with exit 1 and a receipt rather than falling back to synthetic
  data.

## Catalog, dependency, and configuration validation

The installed command should validate at startup that all expected package
resources exist, each catalog parses against its schema, the eight snapshot IDs
are unique and ordered, the metric catalog digest matches the acceptance
baseline, and the project Python version is `>=3.12`. It should report the
resolved package version, catalog digests, source root, output root, R identity,
and optional PDF capability in the run receipt. `enoe-aggregate-golden.json`
is a diagnostic acceptance baseline and may be packaged only if its license and
synthetic/aggregate status remain acceptable; it must never be treated as a
source snapshot.

For PDF-enabled environments, the minimal declared option is a `pdf` extra
containing `weasyprint==70.0`, plus a runtime check for Pango/Fontconfig. The
Windows check should use the documented `WEASYPRINT_DLL_DIRECTORIES` or an
explicit official MSYS2/onedir installation. Ubuntu should install the local
Pango packages through its environment procedure. Both checks must render a
small offline Spanish PDF and record the exit code, WeasyPrint version and
native-library result. No network URL or machine-wide PATH mutation belongs in
the acceptance path.

## Proposed clean-install acceptance commands

These commands are a future acceptance recipe, not commands run by this
readback. They assume a wheelhouse containing the built project wheel and its
already-approved dependency wheels; `--no-index` keeps the run offline.

Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --no-index --find-links wheelhouse career-signals-mx[pdf]
$env:BRUJULA_RSCRIPT = 'C:\path\to\Rscript.exe'
.\.venv\Scripts\python.exe -m brujula enoe-accept --source-root C:\enoe\snapshots --output-root artifacts\enoe --audit-dir artifacts\acceptance
.\.venv\Scripts\python.exe -m brujula enoe-replay --source-root C:\enoe\snapshots --run artifacts\enoe\runs\<run_id>
```

Ubuntu:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install --no-index --find-links wheelhouse 'career-signals-mx[pdf]'
export BRUJULA_RSCRIPT=/usr/bin/Rscript
.venv/bin/python -m brujula enoe-accept --source-root /srv/enoe/snapshots --output-root artifacts/enoe --audit-dir artifacts/acceptance
.venv/bin/python -m brujula enoe-replay --source-root /srv/enoe/snapshots --run artifacts/enoe/runs/<run_id>
```

Acceptance is complete only when the installed command resolves every required
snapshot receipt, reproduces the frozen numerical digest and row values, passes
the R oracle and official ledgers, and emits a sealed replay receipt. The
current evidence reaches only the synthetic wheel PASS; the real-data installed
acceptance remains pending the proposed packaging work and the full acceptance
run.
