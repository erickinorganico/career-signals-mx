# Phase 2: Defensible Survey Estimates - Pattern Map

**Mapped:** 2026-09-22  
**Files analyzed:** 14 planned files (adapter, metric catalog, estimator, three acceptance scripts, aggregate fixture, and seven focused test boundaries)  
**Analogs found:** 12 / 14 (the versioned R and official scripts have research prototypes as their closest matches)

This map covers the Phase 2 boundary described in `02-CONTEXT.md`, `02-RESEARCH.md`, and `02-VALIDATION.md`: exact eight-period SDEM reading, full responding/resident frame construction, metric masks, Taylor estimates, strict v2 records/projection, R replay, and official reconciliation. It does not read raw ZIPs or treat the ignored research prototypes as shipped implementation.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `brujula/enoe_adapter.py` | service / adapter | file-I/O, transform | `brujula/source_inventory.py` + `brujula/acquisition.py` | role-match; exact custody seam exists, row adapter is new |
| `brujula/metrics.py` | utility / service | transform, request-response | `brujula/populations.py` + `brujula/survey.py` | role/data-flow match |
| `brujula/estimates.py` | service | request-response, batch | `brujula/survey.py` | exact estimator core; ENOE orchestration is new |
| `brujula/research_contract.py`, `contracts/research-v2.schema.json`, `contracts/research-v2-public.schema.json` | validator / config | transform, validation | `brujula/data.py`, `brujula/quality.py`, `tests/test_research_contract.py` | exact implemented v2 API |
| `tests/test_enoe_adapter.py` | test | file-I/O, transform | `tests/test_source_inventory.py`, `tests/test_population_rules.py` | role/data-flow match |
| `tests/test_enoe_metrics.py` | test | transform | `tests/test_population_rules.py`, `tests/test_survey.py` | role/data-flow match |
| `tests/test_survey_oracle.py` | test | request-response, batch | `tests/test_survey.py` plus `.cache/research/oracle-adjust.R` | role match; oracle harness new |
| `tests/test_official_reconciliation.py` | test | batch / transform | `.cache/research/official-precision-probe.py` | prototype match only |
| `scripts/enoe_survey_oracle.R` | oracle | batch, request-response | `.cache/research/oracle-adjust.R` | prototype promoted to versioned script |
| `scripts/official_reconciliation.py` | reconciliation | file-I/O, batch | `.cache/research/official-precision-probe.py` | prototype promoted with strict acceptance semantics |
| `scripts/accept_enoe_estimates.py` | acceptance runner | batch, request-response | `brujula/pipeline.py` | role-match; eight-snapshot gate is new |
| `tests/test_estimates.py` | test | request-response, transform | `tests/test_survey.py`, `tests/test_research_contract.py` | role/data-flow match |
| `tests/test_enoe_integration.py` | test | batch, file-I/O | `tests/test_source_inventory.py` | role-match; eight-period gate is new |
| `data/catalog/enoe-metrics.json` | config / manifest | request-response | `data/catalog/enoe-snapshots.json` | exact registry style; metric semantics are new |
| `data/fixtures/enoe-aggregate-golden.json` | fixture / evidence | batch | existing synthetic fixtures | role-match; aggregate oracle fixture is new |

The finalized plans fix the module and script names above. Preserve the signatures and boundaries below. The Phase 1 v2 contract is implemented; its validators return `list[dict]` failures and its projection returns a validated `dict` or raises `ValueError`.

## Pattern Assignments

### `brujula/enoe_adapter.py` (strict frame adapter, file-I/O/transform)

**Analog:** `brujula/source_inventory.py`, with custody delegated to `resolve_snapshot`.

**Required seam/signature:**

```python
def load_snapshot_frame(
    snapshot_id: str,
    output_root: Path,
    registry_path: Path | None = None,
) -> tuple[Frame, dict]:
    """Load one complete frame and return aggregate-only audit metadata."""
```

The implementation must check the actual Phase 1 signature at integration time. `inventory_snapshot(snapshot_id, output_root, registry_path=None)` is currently implemented at `brujula/source_inventory.py:261-266`; `inventory_all(output_root, registry_path=None)` is at `:269-275`. Call the resolver/inventory before opening the exact main SDEM member. Do not create a downloader or use a historical receipt.

**Imports and custody pattern** (`brujula/source_inventory.py:5-15, 175-206, 219-245`):

```python
import csv
import hashlib
import io
import json
import re
import zipfile
from pathlib import Path

from .acquisition import AcquisitionError, _default_registry, _read_registry, resolve_snapshot
```

```python
path, receipt = resolve_snapshot(snapshot_id, output_root, registry_path)
with zipfile.ZipFile(path) as archive:
    names = archive.namelist()
    if len(names) != len(set(names)):
        raise AcquisitionError("ZIP contains duplicate member names")
    # Select the period-derived canonical member, not a substring match.
    header = _header(archive, person)
```

Copy the source inventory's exact period path construction (`:56-65`), UTF-8 metadata decoding and duplicate-header rejection (`:88-102`), full SDEM member hashing without row export (`:68-85`), and receipt/current recheck (`:219-230`). The data CSV is read as Latin-1 after the exact member is selected, as the audited prototype does; the dictionary/catalog remain UTF-8. Preserve raw lexeme and typed value separately. The returned `Frame` is an in-memory full-length typed column representation; it must not serialize person rows.

**Strict row and frame rules:** build the complete valid-response/resident frame first, then derive all age, study, entity, sex, outcome, and metric masks. Accept only reviewed response aliases (`R_DEF="0"` and `"00"`) and `C_RES in {"1", "3"}`. Trim ASCII U+0020 only; blank remains null; require ASCII digits for numeric fields; reject new tokens, nonfinite/zero/negative `FAC_TRI`, missing `EST_D_TRI`/`UPM`, invalid nesting, unexpected geography alias, or wrong catalog key. Retain every original PSU/stratum even when a domain contribution is zero. Output audit counts, hashes, exclusions, and source references only; never emit person rows, raw CSV, or individual oracle records.

**Error pattern:** raise the existing `AcquisitionError` for custody/member failures and use stable structured diagnostics for row-code failures. `source_inventory.py:162-172` is the model for explicit quarter-specific revision gates; `tests/test_source_inventory.py` provides negative fixtures for ambiguity, malformed metadata, failed current, and publication leakage.

### `brujula/metrics.py` (metric definitions and masks, transform)

**Analog:** `brujula/populations.py:185-205, 208-234, 237-283`.

**Required signatures:**

```python
def load_metric_manifest() -> dict: ...
def metric_vectors(frame: Frame, population_id: str, domain: dict, metric_id: str) -> dict:
    # keys: numerator, denominator, domain, coverage, exclusions
```

Keep population, field, occupation, industry, geography, period, and metric separate. Reuse `POPULATION_DEFINITIONS`, `classify_eligibility`, and `normalize_cmpe_key` rather than duplicating eligibility logic. The population module explicitly rejects non-ASCII numeric forms and preserves unknown field values:

```python
def normalize_cmpe_key(raw: object, valid_catalog_keys: Collection[str]) -> str | None:
    # validate catalog, zero-fill only ASCII digits, return None for 999999/absent
```

Metric definitions should be versioned data containing ID, numerator/denominator masks, unit, price basis, sentinels, coverage counters, and dictionary evidence. Follow the existing employment/income denominator distinction:

```python
if measure_id == "positive_known_income":
    if not is_occupied:
        excluded["not_occupied"] += 1
        continue
    income = classify_income_state(row)
    if not income["positive_known"]:
        excluded[income["state"]] += 1
        continue
```

Use `CLASE1=1` only for PEA and `CLASE2=1` for occupied. Income requires occupied plus `ING7C in 1..5` and exact `INGOCUP in 1..999998`; retain no-income, unspecified, non-applicable, invalid, and conflicting states. Suboccupation/hours must remain blocked for the affected metric until all eight dictionaries are checked. Empty denominators return null/UNKNOWN; no missing or sentinel value becomes zero.

### `brujula/estimates.py` (full-frame v2 estimator, request-response/batch)

**Analog:** `brujula/survey.py:22-67, 83-121, 123-189, 191-230`.

**Required signature:**

```python
def estimate_snapshot(
    snapshot_id: str,
    output_root: Path,
    *,
    domains: list[dict] | None = None,
    registry_path: Path | None = None,
) -> dict:
    # keys: internal, public, audit
```

Construct `SurveyDesign` from full-frame arrays. The class copies and freezes weights, validates finite nonnegative values and IDs, computes full design PSU/stratum support, and defaults to `singleton_policy="fail"` (`:37-67`). Phase 2 must explicitly choose `singleton_policy="adjust"` for these cuts while retaining `official_precision=false`, `status="REVIEW"`, and the approximation note. Do not filter the design to a domain before construction.

```python
design = SurveyDesign(weights, strata, psu, singleton_policy="adjust")
population = design.total(population_indicator, domain=national_age_mask)
rate = design.ratio(unemployed_indicator, pea_indicator,
                    domain=national_age_mask, percent=True)
```

Use full-frame boolean vectors and NaN only outside an explicit domain; `_values` masks before multiplication (`:91-98`). Totals and ratios already compute support, weighted denominator, CV, 90% intervals, design degrees of freedom, and suppression (`:123-189`). Ratios enforce nonnegative denominators and percentage bounds (`:203-229`). Extend the result only to add contributing-stratum support (`n_strata_domain`); do not reinterpret `design_df` or label support as effective sample size. Public gates are already encoded: n<30, fewer than two domain PSUs, CV>=30%, zero denominator, boundary proportion, zero variance, and undefined CV suppress value while retaining diagnostic state. CV 15..<30 is REVIEW and visible when other gates pass.

### `brujula/research_contract.py` / `contracts/research-v2*.schema.json` (strict v2 record, validation)

**Implemented API:** `validate_research_v2(payload: Mapping[str, object]) -> list[dict]`, `validate_public_research_v2(payload: Mapping[str, object]) -> list[dict]`, and `public_research_projection(payload: Mapping[str, object]) -> dict` (raises `ValueError` on invalid internal input or projected output). Schemas resolve through `contract_path("research-v2.schema.json")` and `contract_path("research-v2-public.schema.json")` (`brujula/research_contract.py:30-35`).

**Analog:** `brujula/data.py:15-44` for strict JSON loading and `brujula/quality.py:18-30, 42-106, 118-144` for structured semantic checks.

**Strict loading pattern** (`brujula/data.py:15-38`): reject nonfinite numbers, duplicate JSON keys, malformed schema, and extra properties; resolve schema through `resources.contract_path`, never a checkout-relative path.

```python
with dataset_path.open("r", encoding="utf-8") as handle:
    dataset = json.load(handle, parse_constant=reject_non_finite,
                        parse_float=parse_float,
                        object_pairs_hook=reject_duplicate_keys)
schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
Draft202012Validator(schema, format_checker=FormatChecker()).validate(dataset)
```

V2 records must keep the exact 10-key `GRAIN` tuple (`source_snapshot_id`, `population_id`, `field_of_study_id`, `occupation_id`, `industry_id`, `geography_id`, `recorded_sex_id`, `period_id`, `metric_id`, `method_id`) from `brujula/research_contract.py:17-27`; records have no `id` property. Require evidence, support, metric unit/basis, method/design/version, sample n, weighted denominator, precision method/level, singleton policy, status/reason, and source snapshot. Keep internal `estimate`/SE/CI distinct from public `value`; a suppressed public record must null value-derived diagnostics and weighted support while retaining unweighted n, PSU/strata support, df, status, and reason. Semantic checks are accumulated as `{id, message}` pairs (`:38-45, 66-170`).

### `tests/test_enoe_adapter.py` (adapter test, file-I/O/transform)

**Analogs:** `tests/test_source_inventory.py` exact ZIP fixture/custody controls and `tests/test_population_rules.py` boundary/sentinel rows. Use `tests/conftest.py:6-12`'s autouse network prohibition. Create tiny synthetic frames, never person-level fixtures from official ZIPs, covering exact member selection, aliases, ASCII-space padding, blank/null, response aliases, invalid codes/weights, nesting, zero-domain PSUs, and aggregate-only audit output. Require negative fixtures for unexpected token, wrong alias, invalid weight, wrong CMPE catalog, and custody failure.

### `tests/test_enoe_metrics.py` (metric test, transform)

**Analogs:** `tests/test_population_rules.py:1-?` and `tests/test_survey.py:177-185` for explicit domains. Table-drive PEA versus occupied, income sentinels, EMP_PPAL, SEX, POS_OCU, SUB_O, DUR9C/HRSOCUP, unknown categories, empty denominators, age 98/99, and field boundaries. Assert exclusion and coverage counts separately from weighted denominators; do not assert inferred zeros.

### `tests/test_survey_oracle.py` (Python/R acceptance test, batch)

**Analog:** `tests/test_survey.py:9-70, 87-145` for analytic totals, ratios, singleton adjust, and logit CI. Invoke a pinned local R script only in an oracle-enabled run; ordinary fixture tests remain offline and fast. Predeclare `rtol=1e-10`, `atol=1e-8`; assert national, three focal fields, one entity, totals, rates, and positive-known income, with signed differences retained. Rebuild the final known-age cohort (`15..97`, catalog membership); the ignored prototype included EDA 98 and is not an acceptance fixture.

### `scripts/enoe_survey_oracle.R` (versioned R oracle, batch)

**Research prototype:** `.cache/research/oracle-adjust.R:1-10`. It supplies the correct independent options and output shape:

```r
options(survey.lonely.psu='adjust', survey.adjust.domain.lonely=FALSE)
d <- svydesign(ids=~psu, strata=~stratum, weights=~w,
               data=full_resident_respondent_frame, nest=TRUE)
pack <- function(x) list(estimate=as.numeric(coef(x)),
                         standard_error=as.numeric(SE(x)))
```

Version the script in the repository, pass an aggregate-safe input generated by the adapter or a local ignored frame, record R and `survey` versions, design df, cohort/masks, singleton policy, and all signed point/SE differences. Never commit or print individual rows. The script is an independent oracle, not a runtime dependency.

### `scripts/official_reconciliation.py` (official workbook reconciliation, file-I/O/batch)

**Research prototype:** `.cache/research/official-precision-probe.py:21-35, 44-101, 104-160, 163-203`. Reuse its content hash gates, ZIP resolver, bounded workbook parser, header assertions, finite numeric parser, national/Baja California selection, and aggregate output shape. Correct its acceptance semantics for Phase 2: exact six population/PEA/unemployed point totals; rates checked separately against the official four-decimal rounding interval; raw signed point/SE differences retained; no widened tolerance for SE mismatch; `official_precision=false` and REVIEW limitation preserved. The script must call the verified Phase 1 inventory/resolver and fail closed on snapshot/workbook hash mismatch.

### `tests/test_official_reconciliation.py` (reconciliation test, batch)

**Analog:** the same prototype plus `tests/test_source_inventory.py` hash-failure style. Use pinned aggregate fixture data only. Assert exact official counts, rate rounding membership, original raw discrepancies, and the documented nonzero SE difference. Assert no person rows, workbook payload, or suppressed estimate leaks into the result.

## Shared Patterns

### Source custody and exact members

**Sources:** `brujula/acquisition.py:291-324`; `brujula/source_inventory.py:175-246`; `tests/test_source_inventory.py`.

Always resolve the successful current receipt, immutable attempt, registry SHA, raw ZIP SHA, ZIP safety, and exact period-derived member. A failed current blocks; prior success cannot substitute. Inventory metadata is not approval to publish microdata or numeric findings.

### Full-frame design before domains

**Source:** `brujula/survey.py:1-9, 37-67, 83-98, 100-121`.

Construct one complete responding/resident design. Apply age, CMPE, geography, sex, employment, and metric masks to full-length arrays. Zero-contribution PSUs remain in variance; only positive domain contributions count as domain support.

### Nulls, suppression, and diagnostic/public split

**Sources:** `brujula/survey.py:123-189`; planned v2 tests in `tests/test_research_contract.py:95-136`; `brujula/quality.py:93-105`.

Keep `estimate` diagnostic and `value` public. Suppressed values are null with stable reasons. Do not leak SE, CI, CV, weighted denominator, or other value-equivalent diagnostics through v2 public projection. Missing values remain null and statuses remain explicit `UNKNOWN`, `BLOCKED`, or `REVIEW`.

### Resource resolution and package data

**Sources:** `brujula/resources.py:9-29`; `pyproject.toml` package-data section.

Use `contract_path`, `catalog_path`, or `_resource` for authored manifests and schemas so checkout and wheel behavior agree. Add any v2 schema/metric manifest through the existing package-data mapping. Keep specialized imports direct; do not expand `brujula/__init__.py` without a deliberate public API.

### Offline tests and aggregate-only evidence

**Sources:** `tests/conftest.py:6-12`; `tests/test_source_inventory.py`; `.cache/research/eight-quarter-audit.py:1-5`.

All ordinary tests prohibit network and use disposable synthetic rows/ZIPs. Real eight-quarter and R checks are separate offline integration gates. Logs, fixtures, committed JSON, and public artifacts contain hashes, counts, exclusions, and aggregates only; no person rows or raw ZIP bytes.

## No Analog Found

| File / boundary | Reason | Planner implication |
|---|---|---|
| Strict ENOE row decoder and full-frame adapter | Existing inventory stops at metadata and `SurveyDesign` accepts caller arrays; no product code parses SDEM rows. | Build a focused manifest-driven adapter from the custody seam and add negative lexical/frame fixtures. |
| Versioned R oracle | Only ignored `.cache/research/oracle-adjust.R` exists. | Promote the reviewed options/masks/output shape into a versioned script; do not make the prototype the sole implementation. |
| Official reconciliation product script | Only ignored `.cache/research/official-precision-probe.py` exists and uses a broader prototype tolerance. | Create a versioned aggregate-only script with separate exact totals, rate-rounding, and raw SE ledger gates. |
| Eight-period final acceptance runner | Existing `brujula/pipeline.py` is a v1 synthetic build pipeline and does not run ENOE estimates. | Use it only for orchestration/atomic-output style; keep `scripts/accept_enoe_estimates.py` offline, sequential, aggregate-only, and fail-closed. |

## Metadata

**Analog search scope:** `brujula/`, `contracts/`, `data/catalog/`, `tests/`, `scripts/`, `.cache/research/`, `docs/CONTRACT.md`, and Phase 1/2 planning files.  
**Files scanned:** 30 relevant source, test, contract, prototype, and planning files.  
**Pattern extraction date:** 2026-09-22.  
**Read-only note:** no source files, tests, fixtures, or prototypes were modified.
