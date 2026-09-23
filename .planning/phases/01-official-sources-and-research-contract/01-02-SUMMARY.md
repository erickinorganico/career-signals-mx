---
phase: 01-official-sources-and-research-contract
plan: 02
subsystem: population-rules
tags: [enoe, population, cmpe, denominators, income]
requires:
  - phase: 01-official-sources-and-research-contract
    provides: verified period-specific ENOE source metadata and catalog
provides:
  - Two immutable named ENOE population definitions and pure eligibility classifier
  - Explicit sample and weighted denominator summaries with reason counts
  - Strict CMPE catalog membership and income sentinel classification
affects: [phase-2-estimation, phase-3-research-records]
tech-stack:
  added: []
  patterns: [ASCII-only lexeme normalization, explicit unknown states, observed-versus-weighted denominator separation]
key-files:
  created: [brujula/populations.py, tests/test_population_rules.py]
  modified: []
key-decisions:
  - "An unknown study field remains inside the named professional population but blocks a named-field claim."
  - "Only ASCII U+0020 outer padding is removed from row codes; arbitrary numeric coercion is rejected."
  - "Employment uses known CLASE2 1–4 support; positive-known income requires occupied CLASE2=1, consistent ING7C and positive valid INGOCUP."
patterns-established:
  - "Return reason-specific exclusions and a separate unknown-field coverage count."
  - "Return null for an unavailable weighted denominator; reject invalid or overflowing weights."
requirements-completed: [CTR-02]
coverage:
  - id: D1
    description: National and completed-professional populations classify boundaries and exclusions deterministically.
    requirement: CTR-02
    verification:
      - kind: unit
        ref: tests/test_population_rules.py#test_age_boundaries_and_operational_unknown
        status: pass
      - kind: unit
        ref: tests/test_population_rules.py#test_professional_exclusions_are_distinct
        status: pass
    human_judgment: false
  - id: D2
    description: Population summaries separate observed support, response, exclusions and weighted denominator.
    requirement: CTR-02
    verification:
      - kind: unit
        ref: tests/test_population_rules.py#test_definition_and_summary_keep_counts_and_weights_separate
        status: pass
    human_judgment: false
  - id: D3
    description: Study codes require verified period catalog membership and unknown codes remain null.
    requirement: CTR-02
    verification:
      - kind: unit
        ref: tests/test_population_rules.py#test_cmpe_requires_supplied_period_catalog_and_ascii_digits
        status: pass
      - kind: unit
        ref: tests/test_population_rules.py#test_bad_catalog_rejected
        status: pass
    human_judgment: false
  - id: D4
    description: Income states and measure denominators distinguish positive known income from all occupied people.
    requirement: CTR-02
    verification:
      - kind: unit
        ref: tests/test_population_rules.py#test_measure_denominators_keep_employment_and_positive_income_distinct
        status: pass
      - kind: unit
        ref: tests/test_population_rules.py#test_weight_validation_and_finite_accumulation
        status: pass
    human_judgment: false
duration: 6min
completed: 2026-09-23
status: complete
---

# Phase 1 Plan 2: Population and Denominator Rules Summary

**Two named ENOE populations now have explicit eligibility, education and age exclusions, strict study-code mapping, and distinct observed and weighted measure denominators.**

## Performance

- **Duration:** 6 min
- **Started:** 2026-09-23T03:26:00Z
- **Completed:** 2026-09-23T03:32:14Z
- **Tasks:** 2 completed
- **Files modified:** 2

## Accomplishments

- `national_15_plus_context` accepts valid resident responses at operational EDA 15–98, marking 98 as unknown age. `completed_professional_known_age` accepts 15–97 and completed CS_P13_1=07 studies, while separating technical, postgraduate, incomplete and unknown reasons.
- `summarize_denominators` reports observed eligible n, valid-response n, reason counts, unknown study-field coverage and weighted eligible denominator under different names. Empty input has null weighted denominator.
- `normalize_cmpe_key` checks the caller-supplied period catalog, rejects malformed or duplicate normalized keys, and leaves missing and 999999 null. Income state and measure summaries retain no-income, unspecified and inconsistent values outside positive-known income support.
- The rules neither emit person records nor alter the existing survey estimator. They leave field of study, occupation, industry, geography, sex and period as separate dimensions for later stages.

## Task Commits

1. **Task 1 RED:** `2538087` — failing population boundary tests.
2. **Task 1 GREEN:** `0b0e743` — population definitions, eligibility and summaries.
3. **Task 2 RED:** `76bbf04` — failing catalog and income tests.
4. **Task 2 GREEN:** `3750714` — CMPE validation and measure denominators.

## Verification

- `.venv/Scripts/python.exe -m pytest tests/test_population_rules.py -q` after Task 1: **31 passed**.
- `.venv/Scripts/python.exe -m pytest tests/test_population_rules.py tests/test_survey.py -q` after Task 2: **93 passed**.
- The ignored eight-quarter audit was checked for R_DEF, EDA, CS_P13_1, CS_P16, ING7C and INGOCUP dictionary ranges in each period. No new package, external inference or network access was used.

## Decisions Made

- Unknown study fields stay in the named completed-professional population, with a separate count. A named-field estimate still requires a verified catalog match.
- Lexical normalization strips only outer ASCII spaces observed in the eight-quarter audit and accepts ASCII digits. Unicode lookalikes and numeric casts remain invalid.
- INGOCUP zero is not a wage claim; a positive-known income denominator requires a positive amount consistent with ING7C and occupied status.

## Deviations from Plan

None - plan executed as specified.

## Issues Encountered

None. The eight-quarter audit supplied the observed padding and code-range evidence before implementation.

## Known Stubs

None. Null weighted denominators and unknown classifications are deliberate contract states, not placeholder calculations.

## Next Phase Readiness

Phase 2 can construct domain masks and measure support from these pure helpers. Numeric estimation, variance, official concordance and publication precision remain Phase 2 gates.

## Self-Check: PASSED

Both owned files exist; the four task commits are present; population and survey fixture tests passed. No tracked files were deleted by the task commits.

---
*Phase: 01-official-sources-and-research-contract*
*Completed: 2026-09-23*
