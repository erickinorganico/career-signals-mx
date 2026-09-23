---
phase: 02-defensible-survey-estimates
plan: 02
subsystem: survey-estimation-and-public-projection
tags: [enoe, taylor, survey-design, research-v2, suppression]
requires:
  - phase: 02-defensible-survey-estimates
    provides: verified full ENOE frame, quarter CMPE catalog labels, and 23 metric vectors from Plan 01
provides:
  - complete-frame Taylor estimates with separate full-design and contributing support
  - strict internal and public v2 estimate payloads with an exact-grain request/evaluation ledger
  - aggregate coverage, exclusion and source audit handoff for acceptance and analysis
  - computed singleton-precision and public-suppression prohibition controls
affects: [02-03-independent-reconciliation, phase-03-supported-labor-findings]
tech-stack:
  added: []
  patterns: [one design per verified frame, bounded domain vector reuse, strict public projection, aggregate-only ledgers]
key-files:
  created:
    - brujula/estimates.py
    - tests/test_estimates.py
    - tests/phase2_prohibitions_02.py
    - tests/phase2_prohibitions_02.test.cjs
    - tests/fixtures/phase2_prohibitions/02.clean.json
    - tests/fixtures/phase2_prohibitions/02-p3.bad.json
    - tests/fixtures/phase2_prohibitions/02-p4.bad.json
  modified:
    - brujula/survey.py
    - tests/test_survey.py
key-decisions:
  - "Use the complete FAC_TRI/EST_D_TRI/UPM frame for variance and a denominator-contributing mask for ratio support."
  - "Keep the explicit project singleton adjustment as REVIEW with official_precision=false."
  - "Reject missing or conflicting synthetic provenance and take professional field labels from the verified quarter catalog."
  - "Keep weighted diagnostics in validated internal records; public suppression uses the Phase 1 allowlist, while the aggregate audit carries unweighted coverage and exclusions."
requirements-completed: [STAT-01, STAT-02, STAT-03, STAT-06]
coverage:
  - id: survey-precision
    description: Full-frame design support, Taylor intervals and exact suppression boundaries
    requirement: STAT-02
    verification:
      - kind: unit
        ref: tests/test_survey.py
        status: pass
    human_judgment: false
  - id: estimate-boundary
    description: Exact-grain estimate assembly, provenance, aggregate audit and strict public projection
    requirement: STAT-01
    verification:
      - kind: unit
        ref: tests/test_estimates.py
        status: pass
      - kind: integration
        ref: .cache/research/02-02-real-smoke.json
        status: pass
    human_judgment: false
  - id: prohibition-controls
    description: Computed singleton and suppressed-number controls with bad/clean causal proof
    requirement: STAT-03
    verification:
      - kind: integration
        ref: tests/phase2_prohibitions_02.test.cjs
        status: pass
      - kind: integration
        ref: gsd-tools check prohibition-enforcement p3 and p4
        status: pass
    human_judgment: false
duration: 22min
completed: 2026-09-22
status: complete
---

# Phase 2 Plan 02: Defensible Survey Estimates Summary

**All 23 declared ENOE metrics now flow from one complete verified survey design into strict v2 records, with explicit support, precision, suppression, provenance and an aggregate-only coverage ledger.**

## Performance

- **Duration:** approximately 22 minutes, from 2026-09-22T22:21:45-07:00 to 2026-09-22T22:43:05-07:00.
- **Tasks:** 3.
- **Files modified or created:** 9 owned implementation, test and control files.

## Accomplishments

- `SurveyDesign` reports design PSU and strata, contributing PSU and strata, design degrees of freedom, observed denominator support, Taylor SE, CV and finite IC90. It retains zero-contribution PSUs in variance. It suppresses unsupported or unstable values at the specified n, PSU, CV, zero-variance and proportion boundaries. The explicit singleton adjustment never asserts official precision.
- `estimate_snapshot` evaluates every requested metric and domain using one verified frame and one survey design. The exact ten-key grain has a real request/evaluation entry, records contain no `id`, and the internal payload and Phase 1 public projection both pass their strict validators. The audit carries aggregate source lexemes, population exclusions, metric eligibility and reasons without weighted diagnostic figures.
- The p3/p4 controls exercise computed singleton and suppression results. The canonical GSD producer found each named Node test, proved the matching bad fixture red, the clean fixture green, and returned `status=green`, `located=true`, `flagged=false` for both.

## Validation Results

- Focused Python: 86 passed across survey, estimate and v2 contract tests after the final audit change; an additional request-inventory and CV-edge test run passed 47/47.
- Node: 2/2 Plan 02-02 prohibition tests passed. Both canonical producer requests reported `failFirstProof=violation-fixture`.
- Real 2026-Q2 aggregate-only smoke: three explicit domains × 23 metrics produced 69 requested and 69 evaluated records. Forty-six values were visible as REVIEW, 23 were suppressed, and all public suppressed rows had null weighted and precision diagnostics. The source reported `synthetic=false` and `approved_pinned_snapshot` provenance. The ignored receipt is `.cache/research/02-02-real-smoke.json`.
- The eight-snapshot inventory, independent R oracle and official reconciliation are Plan 02-03 acceptance gates; the three-domain smoke does not stand in for them.

## Task Commits

1. **Task 1 — survey support and suppression:** `68a457f` RED; `e17f6f3` GREEN; `cf13195` exact CV and design-df edge tests.
2. **Task 2 — estimate assembly and public boundary:** `e245e2c` RED; `8c290cc` GREEN; `030f6f6` denominator support and stable method identity; `9737646` explicit provenance and verified field labels; `fec0100` aggregate coverage/exclusion ledger.
3. **Task 3 — prohibition controls:** `02fb966` computed Python/Node pair and clean/bad fixtures.

## Deviations from Plan

### Auto-fixed Issues

1. **[Rule 1 - Bug] Ratio weighted support omitted known zero outcomes.** Found during Task 2 readback. The weighted support total now follows positive denominator contribution, matching observed n and domain PSU support. The synthetic employment-rate test includes known zero outcomes. Commit: `030f6f6`.
2. **[Rule 2 - Correctness] Platform line endings changed the adapter source digest without changing behavior.** The adapter source digest now normalizes CRLF to LF; genuine source changes still change the method version. Commit: `030f6f6`.
3. **[Rule 2 - Correctness] Synthetic provenance and official field labels needed verified handoff.** The assembler now checks explicit frame/audit provenance agreement and uses the verified quarter catalog labels; its aggregate audit preserves origin. This followed the Plan 01 adapter integration commit `2936905`. Commit: `9737646`.
4. **[Rule 2 - Correctness] Downstream coverage needed source and exclusion aggregates.** The exact-grain audit now carries unweighted metric coverage/exclusions plus separate nonexclusive population exclusion counts and the source-frame aggregate audit. It carries no weighted denominator diagnostics. Commit: `fec0100`.

## Known Limits

- The singleton-adjusted variance is a documented project approximation. The strict v2 records and public projection label supported visible values REVIEW with `official_precision=false`.
- The real smoke covers three selected domains in one quarter. Plan 02-03 owns all eight quarters, the R comparison and official reconciliation.

## Self-Check: PASSED

All nine owned implementation/control paths exist; all nine Plan 02-02 commit hashes listed above were found in local history. The focused Python, Node, canonical producer and three-domain real smoke checks passed.
