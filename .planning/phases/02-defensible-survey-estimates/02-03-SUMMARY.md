---
phase: 02-defensible-survey-estimates
plan: 03
subsystem: independent-numerical-acceptance
tags: [enoe, survey, R, official-reconciliation, reproducibility]
requires:
  - phase: 02-defensible-survey-estimates
    provides: verified full frames, metric vectors, complete-design estimates and strict public projection
provides:
  - independent real and analytic R survey oracle
  - pinned official national and Baja California reconciliation
  - complete eight-quarter acceptance and unchanged offline replay
  - full public and hash-only internal golden references
  - aggregate-only versioned acceptance evidence
affects: [phase-03-supported-labor-findings, phase-04-offline-publication]
tech-stack:
  added: []
  patterns: [independent expected inventory, immutable golden hashes, fail-closed current receipt]
key-files:
  created:
    - scripts/enoe_survey_oracle.R
    - scripts/official_reconciliation.py
    - scripts/accept_enoe_estimates.py
    - tests/test_survey_oracle.py
    - tests/test_official_reconciliation.py
    - tests/test_enoe_integration.py
    - tests/phase2_prohibitions_03.py
    - tests/phase2_prohibitions_03.test.cjs
    - data/fixtures/enoe-aggregate-golden.json
    - docs/evidence/phase-02-numerical-acceptance.json
  modified:
    - brujula/enoe_adapter.py
    - brujula/metrics.py
    - tests/test_enoe_adapter.py
    - tests/test_enoe_metrics.py
    - tests/phase2_prohibitions_01.py
    - tests/phase2_prohibitions_01.test.cjs
key-decisions:
  - Preserve rtol=1e-10 and atol=1e-8 for independent R points and standard errors.
  - Separate exact official counts and official rounding from untuned SE discrepancies.
  - Independently construct all required domains and compare exact requested/evaluated/record grain sets.
  - Pin complete public contents and hash-only internal diagnostics; initialization cannot replace an existing baseline.
  - Exclude acquisition clocks and harmless ordering from numerical identity while retaining exact custody digests.
requirements-completed: [STAT-01, STAT-02, STAT-03, STAT-04, STAT-05, STAT-06]
coverage:
  - id: independent-oracle
    description: Final-cohort R totals, ratios, positive-known income and age boundary controls
    requirement: STAT-04
    verification:
      - kind: integration
        ref: docs/evidence/phase-02-numerical-acceptance.json
        status: pass
      - kind: unit
        ref: tests/test_survey_oracle.py
        status: pass
    human_judgment: false
  - id: official-reconciliation
    description: Exact official counts, separately rounded rates and untuned SE differences
    requirement: STAT-05
    verification:
      - kind: integration
        ref: docs/evidence/phase-02-numerical-acceptance.json
        status: pass
      - kind: unit
        ref: tests/test_official_reconciliation.py
        status: pass
    human_judgment: false
  - id: complete-repeatable-acceptance
    description: Eight-quarter domain completeness, golden pins and unchanged replay
    requirement: STAT-01
    verification:
      - kind: integration
        ref: docs/evidence/phase-02-numerical-acceptance.json
        status: pass
      - kind: unit
        ref: tests/test_enoe_integration.py
        status: pass
    human_judgment: false
completed: 2026-09-23
status: complete
---

# Phase 2 Plan 03: Independent numerical acceptance

**All eight approved ENOE quarters pass 6,739 computed cells, independent R and official-source reconciliation, then reproduce the same content on an unchanged offline replay.**

## Accomplishments

The acceptance entry point verifies source/member/dictionary custody, independently required domains, keyed request/evaluation/internal/public grain equality, strict v2 roots, real support/suppression causes, metric identity and full public plus hash-only internal references. All 11 implementation hashes match at entry and exit. Failed attempts invalidate current and preserve an immutable receipt; no old success substitutes for a failed refresh.

The R oracle covers 26 real cases across national context, the three focal fields and Baja California, plus four analytic controls including known age 97 versus unknown age 98. It uses R 4.6.1 and survey 4.5, complete-design zero-domain PSUs and the explicit singleton adjustment. The original rtol=1e-10/atol=1e-8 remain fixed.

Official 2025-Q2 reconciliation matches six national/Baja California totals exactly and both four-decimal rate intervals. The national-population SE relative discrepancy remains -0.0037148696737544095; no precision correction is invented. Five 2026-Q2 national PDF totals also match. Every method retains official_precision=false and the documented REVIEW limitation.

## Validation Results

- Frozen implementation: `86406f6`; full regression: 366 passed, zero skipped in 115.25 seconds. The one warning is the expected duplicate-ZIP fixture. All 18 Node controls pass; all seven canonical Phase 2 prohibitions return green, located=true, flagged=false and violation-fixture proof.
- After initializing the internal hash map, all 30 affected oracle/official/integration fixture tests passed again in 1.58 seconds.
- Independent source review is clean after seven findings and bounded corrections. The goal verifier separately ran 30 focused Python and 12 Phase 2 Node cases successfully; final goal verdict is in 02-VERIFICATION.md.
- Real initialization attempt `05dd6471-58a8-474e-8202-2a4b2a57d9fc`: PASS in 795.094 seconds. Existing public/official/semantic pins stayed fixed; only previously absent internal hash references were initialized after all gates passed.
- Unchanged replay attempt `45fe0738-b981-4c9c-852b-28545bf4a9bf`: PASS in 31856.734 seconds. Every exact public payload digest, canonical public/internal hash, record digest and requested count matches initialization.
- Elapsed times record wall time, not a performance benchmark; the replay includes a prolonged interval observed during the 2025-Q2 step.
- Combined numerical digest: `8db575e9d664864d1513e3b9658bd9b060c4cb3bed8b51561f208adeb97b9a00`. Six quarters contain 115 cells, 2025-Q2 has 138 and 2026-Q2 has 5,911; the extra national Baja California domains support official checks.
- Durable aggregate-only evidence: `docs/evidence/phase-02-numerical-acceptance.json`. Complete local receipts and ledgers: `.cache/research/phase2-acceptance/final-initialization-pass.json`, `final-replay-pass.json` and immutable `attempts/` receipts. Individual source rows and temporary R frames are not tracked.

Commands: `.venv/Scripts/python.exe scripts/accept_enoe_estimates.py --output-root artifacts/enoe --audit-dir .cache/research/phase2-acceptance --generate-golden`, followed by the same command without `--generate-golden`; both exit 0. Fixture commands are `.venv/Scripts/python.exe -m pytest -q` and `node --test tests/phase*_prohibitions_*.test.cjs`.

## Task Commits

1. Independent R: RED `78a4f55`, GREEN `aef1515`.
2. Official reconciliation: RED `6e95dd8`, GREEN `d364960`.
3. All-quarter gate and prohibitions: RED `8799e06`, GREEN `deaab3a`.
4. Geographic dtype correction `c1973cc`; review fixes `d3b1437`, `eeaa8ee`, `2e96882`, `695f15c`, `7cc967c`, `f0d67c4`, `5662d8a`, `8e8ef43`, `86406f6`.

## Deviations and Resolution

The first real official comparison exposed text geography aliases being compared against integers. Canonical integer geography and loaded-ZIP regression fixed that integration defect. Independent review then exposed conflicting selectors, caller-mutated Frame/cache state, output scanner gaps, self-referential domain inventory, incomplete golden coverage and baseline initialization/canonicalization defects. Each was corrected and independently rechecked before the final freeze. Historical failure/review records remain; the earlier pre-core numerical pass is not represented as evidence for the revised source.

No external source or precision rule was activated or relaxed. This plan does not implement Phase 3 findings, Phase 4 reports or a final release.

## User Setup Required

None for the accepted local verification. Portable installed-wheel operation and documented R/PDF setup remain Phase 4/5 deliverables.

## Next Phase Readiness

Phase 3 may consume the accepted strict public estimates and aggregate coverage after independent 02-VERIFICATION and canonical phase closure. Read the actual final manifests and keep method catalogs scoped by snapshot; null values and reasons survive unchanged.

## Self-Check: PASSED

Implementation, tests, approved golden references and aggregate evidence exist. The final code, R, official, full-domain and unchanged-replay gates pass. Independent goal acceptance remains a separate phase-level artifact.
