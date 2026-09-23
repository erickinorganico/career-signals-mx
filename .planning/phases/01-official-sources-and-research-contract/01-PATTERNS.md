# Phase 1: Official Sources and Research Contract - Pattern Map

**Mapped:** 2026-09-22
**Files analyzed:** 8 planned/inferred files (3 focused test files, source inventory, v2 schema/validator, population rules, catalog/packaging touchpoints)
**Analogs found:** 7 / 8 (one exact role match for acquisition; role matches for the remaining new boundaries)

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `brujula/inventory.py` (or equivalent focused module) | service / adapter | file-I/O, request-response | `brujula/acquisition.py` (`resolve_snapshot`) | role-match; inventory is new |
| `contracts/research.schema.json` (name discretionary) | config / contract | transform / validation | `contracts/dataset.schema.json` | exact contract style; v2 fields are new |
| `brujula/research.py` (or validator in `brujula/quality.py`) | utility / quality gate | request-response | `brujula/data.py` + `brujula/quality.py` | role-match |
| `brujula/populations.py` (or contract-owned pure helpers) | utility | transform / request-response | `brujula/survey.py` domain and denominator rules | role-match; eligibility is new |
| `data/catalog/enoe-snapshots.json` | config / source registry | request-response | existing registry consumed by `acquisition.py` | exact |
| `tests/test_source_inventory.py` | test | file-I/O | `tests/test_acquisition.py` | exact test style |
| `tests/test_research_contract.py` | test | validation / transform | `tests/test_data.py`, `tests/test_quality.py` | exact test style |
| `tests/test_population_rules.py` | test | transform | `tests/test_survey.py` | role/data-flow match |

Names for the new Python modules are discretionary in CONTEXT/RESEARCH. Keep each responsibility in a focused `brujula/` module and mirror it with `tests/test_<module>.py`; do not put v2 logic into the active v1 schema or silently wire real ENOE data into the v1 pipeline.

## Pattern Assignments

### `brujula/inventory.py` (source package inventory, file-I/O)

**Analog:** `brujula/acquisition.py`, especially `resolve_snapshot` (lines 291-324), `_zip_safety` (123-145), and `_read_registry`/`_snapshot` (50-89).

**Imports and resource lookup** (lines 7-22, 92-94):

```python
import hashlib
import json
import zipfile
from pathlib import Path

from .acquisition import AcquisitionError, resolve_snapshot
from .resources import _resource
```

Use `resources.py` to find authored catalog/schema files (9-17, 20-29), rather than relying on the working directory. Read the exact ZIP returned by `resolve_snapshot(snapshot_id, output_root, registry_path)`; it is read-only and performs no network request (291-324). Do not add a second downloader or fallback to a prior `current` receipt.

**Core inventory pattern** (adapt from acquisition's explicit registry and ZIP checks, 50-89 and 291-324):

```python
raw_zip, receipt = resolve_snapshot(snapshot_id, output_root, registry_path)
with zipfile.ZipFile(raw_zip) as archive:
    members = archive.namelist()
    # Require one exact canonical SDEM member, dictionary and cs_p14_c catalog.
    # Reject duplicate/ambiguous matches and record full member path.
    member_bytes = archive.read(expected_path)
    member_sha256 = hashlib.sha256(member_bytes).hexdigest()
return {
    "snapshot_id": snapshot_id,
    "period": registry_item["period"],
    "raw_sha256": receipt["sha256"],
    "receipt_run_id": receipt["run_id"],
    "members": ..., "dictionary_sha256": ..., "catalog_sha256": ...,
    "header": ..., "geography_alias": ...,
    "corrections": ..., "terms_url": registry["terms_url"],
}
```

The exact canonical paths are period-specific and must be selected by a manifest, never by the first filename containing `sdem`. Keep ZIP/person rows local; publish only metadata, hashes, headers, revisions, aliases, terms, transformation notes, and aggregate-ready contract data. Validate UTF-8 only for metadata members; preserve raw bytes when person-row encoding is not established.

**Error and custody pattern:** mirror `AcquisitionError` (29-31) and fail closed on missing/failed current, receipt/hash mismatch, absent or duplicate members, unknown codes, conflicting aliases, and unresolved joins. Preserve each inventory failure as a structured diagnostic result or receipt; a prior successful quarter cannot mask a failed current attempt. `tests/test_acquisition.py:38-54, 57-76, 116-136, 198-207` are the negative controls to reuse unchanged.

### `contracts/research.schema.json` (strict v2 contract, config)

**Analog:** `contracts/dataset.schema.json` (1-79) and `contracts/run.schema.json` (1-27).

**Schema pattern:** use Draft 2020-12, a distinct `$id`, `schema_version` constant for v2, object roots with `additionalProperties: false`, explicit `required`, and `$defs` for repeated dimensions. The v1 schema's strict root and nested objects (dataset 5-18, observation 70-78) are the model. The run schema's conditional `allOf` (24-26) is the model for status-dependent required fields.

The v2 record must keep the proposed unique grain:

```text
(source_snapshot_id, population_id, field_of_study_id, occupation_id,
 industry_id, geography_id, recorded_sex_id, period_id, metric_id, method_id)
```

Represent aggregate dimensions explicitly with `all` and `unknown` IDs; reserve JSON `null` for unavailable values. Require source snapshot, population, method/design/version, metric unit and price basis, observed `sample_size`, weighted denominator, support fields, precision method/level, singleton policy, status/reason, and nonempty evidence references. Keep `field_of_study`, `occupation`, `industry`, geography, sex, period, source, and evidence as separate references. Do not create automatic bridges.

**Diagnostic/public split:** internal candidate state may contain `estimate`, standard error, intervals, and suppression details. The public schema/projection must omit diagnostic `estimate` and any suppressed interval/SE that could reveal a value. This extends the architecture in `.planning/research/ARCHITECTURE.md:54-56`; it must not append fields to `contracts/dataset.schema.json`.

### `brujula/research.py` (v2 loader/semantic validator/public projection)

**Analogs:** `brujula/data.py` (15-44) for strict loading and `brujula/quality.py` (18-144) for semantic checks.

**Strict load pattern** (adapt `load_dataset`, 15-44):

```python
def load_research_record(path: Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        record = json.load(
            handle,
            parse_constant=reject_non_finite,
            parse_float=parse_float,
            object_pairs_hook=reject_duplicate_keys,
        )
    schema = json.loads(contract_path("research.schema.json").read_text(encoding="utf-8"))
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(record)
    return record
```

Retain duplicate-key, NaN/Infinity, and schema rejection. Resolve the schema through `contract_path`/`resources.py`, not a checkout-relative path.

**Semantic checks:** follow `validate_dataset`'s structured return (`quality.py:18-30, 70-144`): accumulate checks with stable IDs/messages, return public status plus `publishable`, row statuses, and reasons, and fail closed for duplicate grain, orphan references, empty evidence, invalid units/statuses, unresolved source snapshot, or suppressed values exposed as public values. Preserve nulls and explicit `UNKNOWN`/`BLOCKED`; never coerce unavailable values to zero. Keep v1 `load_dataset`/`validate_dataset` and `tests/test_quality.py` unchanged as regression gates.

**Public projection pattern:** implement one allowlist-based projection adjacent to validation. It should copy identity, public `value`, status, suppression reason, precision summary, source/method/population IDs, and evidence references; delete `estimate`, `standard_error`, `ci_lower`, `ci_upper`, and other revealing diagnostics when the value is suppressed. Every later export/warehouse/report consumer must receive this projection, never the internal candidate.

### `brujula/populations.py` (population and denominator rules, transform)

**Analog:** `brujula/survey.py`, `SurveyDesign._mask`/`_values` (73-88), `_result` (113-179), `total` (181-191), and `ratio` (193-220).

Eligibility helpers should be pure, explicit, and period-aware. Build the complete responding/resident frame first, then return boolean masks and exclusion counts. Encode the two locked populations:

```python
def national_15_plus_context(row) -> bool:
    return row["R_DEF"] == "0" and row["C_RES"] in {"1", "3"} and 15 <= row["EDA"] <= 98

def completed_professional_known_age(row) -> bool:
    return (row["R_DEF"] == "0" and row["C_RES"] in {"1", "3"}
            and 15 <= row["EDA"] <= 97 and row["CS_P13_1"] == "07" and row["CS_P16"] == "1")
```

Make sentinel semantics visible: `EDA=98` is age unspecified for the national context and is excluded from the main cohort; `EDA=99` is unknown. `CS_P13_1` 07/08/09 and postgraduate/incomplete/technical exclusions must have named counts. Normalize `CS_P14_C` only after catalog membership validation, with `raw.isascii()`, `raw.isdigit()`, length 1-6, and `zfill(6)`; `999999` and absent codes remain unknown.

Keep denominator fields separate: observed eligible `n`, valid-response `n`, excluded/unknown counts by reason, and weighted denominator. `sample_size` is observed n, never `sum(FAC_TRI)` or effective n. Income states follow the dictionary: `ING7C=6` no income, `ING7C=7` unspecified; `INGOCUP=0` alone does not establish a zero wage. Positive-known income denominators describe only their eligible known-income universe.

Use the survey result shape as the downstream contract seam: `_result` records `estimate`, public `value`, support, `weighted_denominator`, precision, status, and `suppression_reason` (158-179). The Phase 1 rules must not perform numerical estimation or label singleton adjustment as official precision; Phase 2 owns acceptance.

### `data/catalog/enoe-snapshots.json` (source registry, config)

**Analog:** existing registry consumed by `acquisition._validate_registry`/`_snapshot` (50-89) and `tests/test_acquisition._registry` (12-17).

Keep one exact URL, expected SHA-256, period, catalog ID, acquisition approval, size limits, allowed host, terms URL, license, and attribution at registry level. Add or reference period manifests for exact member paths, dictionary/catalog hashes, header geography alias, corrections/edition, and transformation metadata; do not duplicate raw URLs in Python. Registry validation must reject unsafe or duplicate IDs and unapproved snapshots. `publication_approved=false` remains distinct from `acquisition_approved=true` (see lines 5-12 of the registry and `docs/CONTRACT.md` source policy).

### `tests/test_source_inventory.py` (test, file-I/O)

**Analog:** `tests/test_acquisition.py` (12-17 fixture registry, 20-24 ZIP helper, 27-54 success/offline replay, 57-76 ZIP safety, 116-136 pinned cache/current failures) and `tests/conftest.py:6-12` network prohibition.

Build tiny in-memory ZIP fixtures with exact canonical members and assert the returned inventory contains full paths, member hashes/sizes, header, dictionary/catalog hashes, corrections, aliases, terms, acquisition date, and receipt run ID. Add negative fixtures for two SDEM-like CSVs, duplicate canonical members, missing dictionary/catalog, invalid CMPE key, conflicting ENT/CVE_ENT alias, failed current, and person-row publication. Resolve all eight snapshots offline in an integration test only when the cached artifact root is explicitly supplied; do not download in tests.

### `tests/test_research_contract.py` (test, validation)

**Analogs:** `tests/test_data.py:23-41` (strict properties, duplicate JSON keys, nonfinite numbers), `tests/test_quality.py:33-83` (duplicate grain, orphan refs, blocked evidence, official mode gate), and `tests/test_survey.py:63-97` (precision/public suppression).

Assert v2 rejects extra fields, duplicate grain, missing/unknown evidence, unresolved source/population/method references, dimension collapse, and invalid null/status combinations. Assert `estimate` remains in internal validation state but is absent from the public projection, including when `value is None`; preserve v1 fixture/schema tests as an unchanged separate test invocation.

### `tests/test_population_rules.py` (test, transform)

**Analog:** `tests/test_survey.py:20-41, 81-117` for denominator/support and zero-domain cases, plus the sentinel assertions described in RESEARCH validation table.

Use small row dictionaries covering `R_DEF`, `C_RES`, `EDA` 15/97/98/99, `CS_P13_1` 07/08/09, `CS_P16`, raw/normalized `CS_P14_C` including `999999` and absent, and `ING7C`/`INGOCUP` states. Assert eligibility masks, reason-specific exclusions, observed versus weighted denominators, and null/unknown results for empty or sentinel-only domains. Never assert an income-zero interpretation from `INGOCUP=0` alone.

## Shared Patterns

### Immutable source custody

**Sources:** `brujula/acquisition.py:96-120, 201-279, 291-324`; `tests/test_acquisition.py:38-54`.

Raw bytes are content-addressed (`raw/<sha256>.zip`), attempt receipts are write-once, and `current.json` is the only atomic mutable pointer. A failed refresh replaces current with `FAILED`; it cannot fall back to historical success. `resolve_snapshot` verifies registry URL/SHA, immutable attempt equality, raw hash, and ZIP safety before inventory.

### Strict JSON and semantic gates

**Sources:** `brujula/data.py:15-44`; `brujula/quality.py:18-30, 70-144`; `contracts/dataset.schema.json:5-18, 70-78`.

Separate syntax/schema validation from semantic checks. Reject duplicate keys, nonfinite values, extra properties, duplicate grain, orphan references, empty evidence, and status/value contradictions. Return structured check IDs and messages; preserve null and fail closed.

### Evidence and authority separation

**Sources:** `brujula/scout.py:51-79`; `brujula/agents.py:64-112`; `docs/CONTRACT.md` source/bridge rules.

Metadata discovery and acquisition do not activate numerical publication. Keep `approved`, `acquisition_approved`, `monitor_allowed`, and `publication_allowed` distinct. Source terms, hashes, receipt IDs, method versions, and transformation records must be resolvable evidence. No automatic field/occupation/industry bridges.

### Full-frame design and explicit public suppression

**Sources:** `brujula/survey.py:19-27, 73-88, 113-179, 193-220`; `.planning/research/ARCHITECTURE.md:54-56`.

Construct the full responding/resident design before domain masks. Preserve diagnostic estimates internally while exposing only gated public values. Record support, weighted denominator, precision, singleton policy, and suppression reason. A suppressed value is `null` with a reason; no consumer may recover it from an internal estimate.

### Packaging and resource resolution

**Sources:** `brujula/resources.py:9-29`; `pyproject.toml:20-31`; `.planning/codebase/CONVENTIONS.md:56-59, 123-125`.

Schemas and catalogs are packaged as JSON resources and resolved through `contract_path`, `catalog_path`, or `_resource`, supporting both checkout and wheel. Add the v2 schema/period manifests to the corresponding `pyproject.toml` package-data mapping. Keep specialized modules imported directly; do not expand `brujula/__init__.py` unless a deliberate public API is required.

## No Analog Found

| File/role | Reason | Planner implication |
|---|---|---|
| Period-aware ENOE inventory/adapter | No existing code selects exact SDEM/dictionary/catalog members or records ENOE revisions/aliases. | Extend `resolve_snapshot`; create a focused manifest-driven reader with exact-member and ambiguity tests. |
| Strict v2 research record | Existing contracts are v1 synthetic and explicitly reject `official_snapshot` activation in `quality.py:130-133`. | Create a separate v2 schema/reader/projection and preserve v1 gates. |
| ENOE population eligibility/crosswalk | `survey.py` accepts caller-supplied arrays and does not establish source/universe validity (module docstring lines 1-6). | Keep eligibility and CMPE normalization in a separate pure adapter/contract layer; Phase 2 owns estimates. |

## Metadata

**Analog search scope:** `brujula/`, `contracts/`, `data/catalog/`, `tests/`, `docs/CONTRACT.md`, `.planning/codebase/`, `.planning/research/`.
**Files scanned:** 18 source/test/contract files plus project maps and Phase 1 context/research.
**Pattern extraction date:** 2026-09-22.
