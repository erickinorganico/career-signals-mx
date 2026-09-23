---
phase: 01-official-sources-and-research-contract
plan: 03
subsystem: research-contract
tags: [enoe, jsonschema, provenance, precision, suppression]
requires:
  - phase: 01-official-sources-and-research-contract
    provides: source inventory and named population rules from plans 01-01 and 01-02
provides:
  - Strict internal research v2 schema and semantic validator
  - Separate strict public v2 schema and fail-closed projection
  - Documented v2 grain, precision, provenance and suppression interface
affects: [phase-2-estimation, phase-3-findings, phase-4-publication]
tech-stack:
  added: []
  patterns: [Draft-2020-12 schemas, allowlist projection, deterministic semantic checks, visible-value precision gate]
key-files:
  created: [contracts/research-v2.schema.json, contracts/research-v2-public.schema.json, brujula/research_contract.py, tests/test_research_contract.py, docs/CONTRACT-V2.md]
  modified: []
key-decisions:
  - "Population IDs resolve only through POPULATION_DEFINITIONS; v2 never changes v1."
  - "A public null value clears all weighted totals and point-derived precision while retaining observed n and unweighted design/domain counts."
  - "Visible values must pass existing support and CV gates; supported REVIEW remains valid."
patterns-established:
  - "Validate internal schema and references before projecting from an explicit public allowlist, then validate public schema again."
  - "Use separate variance and interval method fields and full-design/domain support counts."
requirements-completed: [CTR-01, CTR-02]
coverage:
  - id: D1
    description: Strict v2 internal record and referential grain validation.
    requirement: CTR-01
    verification:
      - kind: unit
        ref: tests/test_research_contract.py#test_internal_rejects_invalid_or_orphan_records
        status: pass
      - kind: unit
        ref: tests/test_research_contract.py#test_adjacent_periods_are_valid_but_overlapping_periods_are_not
        status: pass
    human_judgment: false
  - id: D2
    description: Public projection removes suppressed diagnostics and validates a separate strict schema.
    requirement: CTR-01
    verification:
      - kind: unit
        ref: tests/test_research_contract.py#test_suppressed_projection_never_leaks_value_equivalent_sentinels
        status: pass
      - kind: unit
        ref: tests/test_research_contract.py#test_public_rejects_diagnostic_and_suppression_leaks
        status: pass
    human_judgment: false
  - id: D3
    description: Visible values obey observed support and CV gates while supported REVIEW remains representable.
    requirement: CTR-02
    verification:
      - kind: unit
        ref: tests/test_research_contract.py#test_unsupported_visible_values_fail_precision_gate
        status: pass
      - kind: unit
        ref: tests/test_research_contract.py#test_review_value_allows_cv_20_or_project_singleton_but_measured_does_not
        status: pass
    human_judgment: false
  - id: D4
    description: V2 contract and compatibility documentation.
    requirement: CTR-01
    verification:
      - kind: other
        ref: docs/CONTRACT-V2.md#contrato-de-investigacion-enoe-v2
        status: pass
      - kind: integration
        ref: uv build --offline --cache-dir .cache/uv --wheel --out-dir .cache/research/wheels
        status: pass
    human_judgment: true
    rationale: Editorial sufficiency and later consumer adoption require review.
duration: 13min
completed: 2026-09-23
status: complete
---

# Phase 1 Plan 3: Research v2 Contract Summary

**A separate validated research v2 contract now gates every public aggregate through an allowlist that removes suppressed estimates, weighted totals and precision diagnostics.**

## Performance

- **Duration:** 13 min
- **Started:** 2026-09-23T03:35:00Z
- **Completed:** 2026-09-23T03:48:45Z
- **Tasks:** 2 completed
- **Files modified:** 5

## Accomplishments

- Internal Draft 2020-12 schema requires all ten grain references, method/design/version, evidence, observed and weighted denominators, full-design and domain support, confidence metadata, diagnostic `estimate`, gated `value`, status, reason and synthetic marker. Semantic validation checks uniqueness, resolvable references, source/period/method compatibility, period overlap, numeric finiteness and state coherence.
- Public schema forbids diagnostic `estimate`. `public_research_projection` starts from a validated internal object, constructs each public object from an allowlist, clears weighted denominator/support and SE/CV/IC90 when value is null, and validates the result again. Observed n, UPM, strata, degrees of freedom, method and confidence level remain labeled.
- Supported `REVIEW` values remain allowed. Visible values must meet n≥30, at least two domain UPM, positive design degrees of freedom, positive weighted denominator and SE, CV<30, nondegenerate IC90 and non-boundary status. `MEASURED` also requires CV<15 and cannot use project singleton adjustment.
- The v2 interface documents population authority, `all`/`unknown` IDs, separate study/occupation/industry axes, four units including `hours/week`, INEGI attribution, v1 compatibility and later numerical review gates.

## Task Commits

1. **Task 1 RED:** `4a58b4f` — failing internal and projection tests.
2. **Task 1 GREEN:** `21bfbd7` — internal schema and semantic validator.
3. **Task 2 RED:** `3f140ce` — failing public schema and projection tests.
4. **Task 2 GREEN:** `f1ef460` — public schema, projection, precision gate, tests and documentation.

## Verification

- `.venv/Scripts/python.exe -m pytest tests/test_research_contract.py tests/test_quality.py tests/test_data.py -q`: **45 passed**.
- Offline wheel built successfully with `uv build --offline --cache-dir .cache/uv --wheel --out-dir .cache/research/wheels`; ZIP inspection confirmed both v2 schemas packaged. Existing `pyproject.toml` `*.json` mapping needed no change.
- `contracts/dataset.schema.json`, `brujula/quality.py` and `data/fixtures/pilot.json` are byte-unchanged against the reviewed baseline. No tracked file deletion occurred.

## Decisions Made

- Use `POPULATION_DEFINITIONS` as the only population-ID authority; source/period/method/evidence associations are validated within each bundle.
- Keep `value` exactly equal to the gated internal `estimate` when visible. Display rounding happens downstream.
- Validate known support/CV gates in v2 while leaving estimation, variance, R/INEGI concordance and source activation to later phases.

## Deviations from Plan

None - the existing package-data mapping already includes both schemas, so `pyproject.toml` did not require a change.

## Issues Encountered

The virtual environment has no `pip`, and the default `uv` cache was inaccessible in the sandbox. An offline wheel build succeeded with a workspace-local cache; no dependency was installed or downloaded.

## Known Stubs

None. Nullable diagnostics represent unavailable or suppressed values. Geography concept equivalence and full person-row encoding remain explicit later-phase review gates.

## Next Phase Readiness

Phase 2 can emit candidate v2 records for validation and public projection after its estimation and numerical concordance gates. This plan does not certify survey variance or approve an official numerical release.

## Self-Check: PASSED

All five created files exist, the four task commits are present, focused v2 and unchanged v1 checks pass, and both schemas are present in the offline wheel.

---
*Phase: 01-official-sources-and-research-contract*
*Completed: 2026-09-23*
