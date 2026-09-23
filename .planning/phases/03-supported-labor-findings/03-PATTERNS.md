# Phase 3: Supported Labor Findings - Pattern Map

**Mapped:** 2026-09-22  
**Files analyzed:** 8 planned/inferred analysis and test files  
**Analogs found:** 8 / 8 (role/data-flow analogs; Phase 3 v2 analysis modules are new)

Phase 3 must consume only the accepted Phase 2 public v2 projection. Phase 2 is not implemented yet, so every Phase 2 interface below is provisional and must be rechecked against the completed modules and eight-period acceptance ledger before Phase 3 execution. Do not extend the v1 synthetic comparison or insight behavior to real v2 findings by assumption.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `brujula/analysis_v2.py` | analysis service / profile builder | transform, batch | `brujula/data.py`, `brujula/quality.py` | role-match; v2 grids are new |
| `brujula/comparisons_v2.py` | utility / comparison service | request-response, transform | `brujula/quality.py::compare_observations` | same flow; signature rules are stricter/new |
| `brujula/claims_v2.py` | validator / claim builder | transform, validation | `brujula/insights.py` | strong role match; v2 typed claims are new |
| `tests/test_analysis_v2.py` | test | batch / transform | `tests/test_data.py`, `tests/test_quality.py` | role/data-flow match |
| `tests/test_comparisons_v2.py` | test | request-response | `tests/test_quality.py` | exact flow analog |
| `tests/test_claims_v2.py` | test | validation | `tests/test_insights.py`, `tests/test_research_contract.py` | exact flow analog |
| `tests/test_analysis_integration.py` (or finalized equivalent) | test | batch | `tests/test_pipeline.py` | role-match; accepted v2 packet is new |
| `data/fixtures/analysis-v2-golden.json` (or finalized aggregate fixture) | fixture / evidence | batch | `data/fixtures/pilot.json` | role-match; public v2 aggregate fixture is new |

The research recommends the three module names above and focused tests; the exact integration fixture name remains discretionary until Phase 2 produces a stable public payload. Keep analysis independent from `brujula/report.py`, which belongs to the later publication phase.

## Pattern Assignments

### `brujula/analysis_v2.py` (profiles, coverage, expected cells, batch transform)

**Analogs:** `brujula/data.py:15-44` for strict loading and `brujula/quality.py:18-144` for structured semantic checks.

**Phase 2 dependency to recheck:** consume the finalized `estimate_snapshot(snapshot_id, output_root, *, domains=None, registry_path=None) -> dict` only through its `public` result after `validate_public_research_v2` succeeds. Do not call the planned adapter directly or decode ZIPs again. The public records have the 10-key v2 grain and no record `id`; derive a canonical, version-prefixed ID from canonical serialization of the complete grain and retain the grain alongside it.

**Strict input pattern:** validate the incoming public payload before building any index. `brujula/data.py:15-38` rejects nonfinite values and duplicate JSON keys, while `brujula/research_contract.py:222-240` exposes the v2 validator/projection seam. Reject any validator failures, duplicate canonical IDs, unknown references, mixed population definitions, or public diagnostics. Use deterministic sorted iteration for records, fields, periods, entities, and sexes.

**Expected-cell pattern:** materialize every required cell, including unsupported cells with `value=null` and an explicit reason. Build eight national periods for national context, cohort, and the three focal fields; latest-period all identifiable official fields; latest-period 32 entities; and latest-period two recorded sexes. Keep national 15+ context separate from the completed-professional known-age cohort and keep sex/entity slices separate. Join Phase 2 aggregate audit coverage/exclusion data by exact period, field, population, and metric; weighted support is an estimate, never sample size.

**Evidence pattern:** use official catalog labels for identifiable CMPE fields. Blank, absent, and `999999` remain an unknown-field coverage bucket. Preserve source snapshot IDs, hashes, method IDs/version, evidence references, precision status, universe, and exclusion notes in every profile/cell. No helper may recover internal `estimate`, SE, CI, or weighted denominator from the public projection.

### `brujula/comparisons_v2.py` (comparability signatures and descriptive deltas)

**Analog:** `brujula/quality.py:147-189`, especially `compare_observations(previous, current, periods_by_id=None)`. That implementation validates required fields, exact shared dimensions, non-null values/statuses, period order, and returns either a numeric delta or `BLOCKED` with null deltas and reasons.

Phase 3 must preserve that fail-closed shape while using a richer signature: source family and edition/revision evidence; population ID and definition version; normalized geography concept/key; sex; field/occupation/industry IDs and classification versions; metric plus numerator/denominator definition version; unit; price basis; estimator/design/method version; singleton/precision policy; and suppression-rule version. Snapshot IDs and SHA-256 values remain provenance, not equality requirements. If Phase 2 does not expose definition versions, block deltas until its method/metric manifest is joined and verified.

```python
# Shape to preserve from brujula.quality.py:183-189
return {
    "status": "REVIEW" if ... else "MEASURED",
    "comparable": True,
    "absolute_change": absolute,
    "relative_change_pct": relative,
    "reasons": [],
    "evidence_refs": sorted(...),
}
# Incompatible or unavailable endpoints return BLOCKED and null changes.
```

Generate only ordered q→q+1 and q→q+4 pairs within the eight-quarter window. Normalize old `ENT` and new `CVE_ENT` to the verified two-digit geography key while retaining native alias provenance; key/name mismatch blocks. Require both public endpoints supported and non-null, exact compatible signatures, and valid quarter order. Changes are descriptive only: percentage points for rates, display-unit changes for other metrics, nominal wording for income, and seasonality caveat for adjacent quarters. Never derive change SE, significance, or independent sample size.

### `brujula/claims_v2.py` (canonical findings and claim gate)

**Analogs:** `brujula/insights.py:53-62, 89-118, 127-183` and `tests/test_insights.py`.

`observation_claim` shows the project’s exact-template approach: labels and units come from validated maps, evidence/source/population/method are bound to the row, and no free numeric prose is accepted. `validate_insights` rebuilds the sanctioned text and rejects unbound numbers, causal/significance/vacancy language, instruction-like content, incongruent evidence, and concept identity substitution (`:147-182`). Reuse this architecture for v2 typed claims, but index by canonical grain ID rather than v1 observation `id`.

Each claim should contain a typed template ID, exact record/comparison IDs, source snapshot IDs, method/version, evidence refs, population/universe, precision limitations, and any seasonality or nominal-income qualifier. Regenerate canonical Spanish text from the typed payload during validation; compare exact text and typed quantities. Reject suppressed or incompatible endpoints, altered labels, extra numbers, causal phrasing, personal advice, and claims that bridge field of study to occupation. Select up to three opening findings only after the data pass using a deterministic supported-relevance/coverage rule; fewer is valid.

### `tests/test_analysis_v2.py` (profiles/coverage test)

**Analogs:** `tests/test_data.py:8-42` and `tests/test_quality.py` semantic and null-preservation tests. Use a small validated public v2 fixture with all required dimensions. Assert stable canonical IDs under input reorder, complete expected-cell grids, national-context/cohort separation, official labels, unknown-field handling, explicit unsupported reasons, coverage/exclusion joins, and absence of diagnostic fields. Do not use raw or person-level fixtures.

### `tests/test_comparisons_v2.py` (comparability test)

**Analog:** `tests/test_quality.py` comparison tests and `brujula/quality.py:147-189`. Table-drive equal and changed signatures, geography alias normalization, source hash provenance, metric/population version changes, null/suppressed endpoints, adjacent and year-over-year pair generation, zero prior values, and deterministic reason order. Assert incompatible entries have null deltas and never become zero.

### `tests/test_claims_v2.py` (claim validation test)

**Analogs:** `tests/test_insights.py:30-183` and `tests/test_research_contract.py` public suppression tests. Assert exact template regeneration, canonical ID/evidence binding, no extra numerals, no causal/advice/significance language, no field/occupation substitution, no suppressed-value leak through coverage or prose, stable selection under reorder, and acceptance of fewer than three opening claims.

### `tests/test_analysis_integration.py` and aggregate fixture (batch gate)

**Analog:** `tests/test_pipeline.py` for blocked/publicable orchestration and `data/fixtures/pilot.json` for local fixture loading. The fixture must contain only validated public aggregates and synthetic labels where applicable. The integration gate should fail closed when Phase 2 acceptance is absent, a public validator fails, a required cell is missing, or a comparison signature is incomplete. It must never run ZIP decoding, use internal v2 diagnostics, or promote a report artifact.

## Shared Patterns

### Validate before analysis

Use `validate_public_research_v2` after `public_research_projection`; reject the packet before indexing. The v2 contract returns deterministic `{id, message}` failures and the projection raises `ValueError` for invalid internal or projected payloads. Preserve nulls and explicit unavailable reasons.

### Evidence and concept identity

`brujula/insights.py:_maps` (`:34-44`) keys concepts by `(concept_type, id)`, preventing a shared identifier from silently changing field-of-study meaning. Phase 3 must retain separate field, occupation, industry, geography, period, sex, source, and evidence namespaces and never infer bridges.

### Deterministic structured checks

Follow `brujula/quality.py`’s `_check`/`fail` pattern (`:14-45`): collect stable check IDs/messages, sort where order matters, and return blocked/null results rather than partial numeric claims. Use `pipeline.py:65-87` only as an orchestration shape; its v1 synthetic comparison path is not a Phase 3 implementation.

### Public boundary and no leakage

The v2 projection allowlist is the only numeric input to profiles, comparisons, coverage, and claims. Suppressed values remain null, and complementary totals or weighted support must not reconstruct them. Rendering, exports, CLI/current promotion, and release auditing are Phase 4 responsibilities.

## No Analog Found

| Boundary | Reason | Planner implication |
|---|---|---|
| v2 profile/coverage grid | Existing `brujula/report.py` renders v1 observations and does not create expected cells. | Add a focused deterministic analysis module and preserve unsupported cells with reasons. |
| v2 comparability signature | `compare_observations` only compares the narrower v1 fields and intentionally requires exact shared metadata. | Implement a separate v2 module; do not widen the v1 function in place. |
| v2 canonical claim registry | `brujula/insights.py` validates v1 observation prose and explicitly rejects comparison prose. | Implement typed v2 templates and validation separately. |

## Phase 2 Recheck Gate

Before Phase 3 execution, inspect the implemented `brujula/enoe_adapter.py`, `brujula/metrics.py`, and `brujula/estimates.py`, confirm `estimate_snapshot(...)` and public/internal payload keys, verify the eight-period acceptance ledger, and confirm that metric/population/geography definition versions needed by comparison signatures are present. If any are absent, keep the affected profile/comparison/claim output blocked and update the plan before coding.

## Metadata

**Analog search scope:** `brujula/{data,quality,insights,agents,pipeline,report,research_contract,populations}.py`, `tests/`, v2 schemas, Phase 2 plans, and Phase 3 context/research.  
**Files scanned:** 18 relevant source, test, schema, and planning files.  
**Pattern extraction date:** 2026-09-22.  
**Read-only note:** no source files or tests were modified.
