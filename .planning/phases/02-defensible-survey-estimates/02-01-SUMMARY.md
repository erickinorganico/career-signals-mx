---
phase: 02-defensible-survey-estimates
plan: 01
subsystem: survey-adapter-and-metrics
tags: [enoe, numpy, survey-frame, metrics, provenance]
requires:
  - phase: 01-official-sources-and-research-contract
    provides: verified eight-snapshot inventory, population rules, and source custody
provides:
  - complete in-memory response/resident SDEM frames for eight pinned ENOE quarters
  - 23 versioned labor metric vector definitions with content-hashed method identity
  - aggregate-only source and missing-value prohibition controls
affects: [02-02-survey-estimation, 02-03-independent-reconciliation, phase-03-findings]
tech-stack:
  added: [numpy==2.5.3 direct dependency]
  patterns: [single-pass column loading, one-domain bounded mask cache, content-dependent negative controls]
key-files:
  created:
    - brujula/enoe_adapter.py
    - brujula/metrics.py
    - data/catalog/enoe-metrics.json
    - tests/test_enoe_adapter.py
    - tests/test_enoe_metrics.py
    - tests/phase2_prohibitions_01.py
    - tests/phase2_prohibitions_01.test.cjs
    - tests/fixtures/phase2_prohibitions/01.clean.json
    - tests/fixtures/phase2_prohibitions/01-p1.bad.json
    - tests/fixtures/phase2_prohibitions/01-p2.bad.json
  modified:
    - pyproject.toml
key-decisions:
  - "Keep every valid responding/resident row and design PSU before domain restriction."
  - "Exclude unknown labor and SUB_O states from rate denominators with explicit counts."
  - "Keep known ING7C bands with unavailable amounts in income-state shares, but outside the positive-known income mean."
  - "Hash the canonical metric definitions into method_version; retain only one cached domain state per frame."
requirements-completed: [STAT-01, STAT-06]
coverage:
  - id: frame
    description: Complete verified in-memory survey frame and aggregate audit for eight quarters
    requirement: STAT-01
    verification:
      - kind: unit
        ref: tests/test_enoe_adapter.py
        status: pass
      - kind: integration
        ref: offline eight-quarter aggregate comparison against .cache/research/eight-quarter-audit.json
        status: pass
    human_judgment: false
  - id: metrics
    description: Twenty-three versioned labor metrics and full-frame vectors
    requirement: STAT-06
    verification:
      - kind: unit
        ref: tests/test_enoe_metrics.py
        status: pass
    human_judgment: false
  - id: prohibitions
    description: Content-sensitive source and missing-value controls with fail-first fixtures
    verification:
      - kind: integration
        ref: tests/phase2_prohibitions_01.test.cjs
        status: pass
    human_judgment: false
duration: 27min
completed: 2026-09-22
status: complete
---

# Phase 2 Plan 01: Complete ENOE Frame and Metric Semantics Summary

**All eight SHA-pinned SDEM packages load into complete response/resident column frames; 23 content-hashed metric definitions produce full-length vectors with explicit missing-state exclusions.**

## Performance

- **Duration:** approximately 27 minutes, including an interrupted first real audit before the catalog lookup was optimized.
- **Started:** 2026-09-22T21:48:48-07:00
- **Completed:** 2026-09-22T22:16:00-07:00
- **Tasks:** 3
- **Files modified:** 11 implementation, test, catalog and fixture files

## Accomplishments

- `load_snapshot_frame(snapshot_id, output_root, registry_path=None)` checks Phase 1 current/attempt/raw/member custody, verifies dictionary and period catalog, decodes the exact Latin-1 SDEM member once, and returns a `Frame` of read-only NumPy columns plus an aggregate-only audit. `audit_all_snapshots(output_root, registry_path=None)` repeats this for all eight approved periods.
- `load_metric_manifest()` validates the catalog's canonical SHA-256 and returns `method_version=enoe-metrics-2026-09-22:2ee87c8b7bfae9addcdf224ae93071023b918a5a22012e1355b9378b73e5827e`. `metric_vectors(frame, population_id, domain, metric_id)` returns `numerator`, `denominator`, `domain`, `coverage`, `exclusions`, and `method_version`. Arrays retain full-frame alignment; empty denominators have null weighted coverage and an explicit reason.
- Both Phase 2 prohibitions have portable Node/Python checks over current APIs. Synthetic bad subjects independently trigger the named failure, clean subjects pass, and the canonical GSD producer returned `status=green`, `located=true`, `flagged=false`, `failFirstProof=violation-fixture` for each.

## Validation Results

- Focused Python controls: 83 passed after the denominator/cache changes; 21 adapter/metric tests passed after the final catalog lookup optimization.
- Full Python regression at final implementation HEAD `b6c2fcc`, run by the integration owner: 275 passed, 0 skipped, with only the established duplicate-ZIP fixture warning.
- Node prohibition controls at final HEAD: 2 passed. Both bad subjects failed only their matching named test; clean/default subjects passed. Canonical producer proved both fail-first controls and returned green.
- All eight real cached ZIPs matched the Phase 1 aggregate audit on response/resident frame count, strata, PSUs, singleton strata and SDEM SHA-256:

| Quarter | Frame rows | Strata | PSUs | Singleton strata |
|---|---:|---:|---:|---:|
| 2024-Q3 | 415147 | 1203 | 20978 | 53 |
| 2024-Q4 | 413024 | 1210 | 21056 | 39 |
| 2025-Q1 | 412079 | 1205 | 21117 | 124 |
| 2025-Q2 | 413004 | 743 | 21192 | 7 |
| 2025-Q3 | 411562 | 744 | 21203 | 23 |
| 2025-Q4 | 408099 | 724 | 21194 | 11 |
| 2026-Q1 | 406740 | 723 | 21171 | 16 |
| 2026-Q2 | 407107 | 722 | 21215 | 13 |

## Task Commits

1. **Task 1 — complete frame:** `0616c21` RED, `ec721f5` GREEN, `8a64968` official sentinel correction.
2. **Task 2 — metric definitions:** `c279ad9` RED, `d7d8a9f` GREEN, `cb2d0b1` denominator/cache correction.
3. **Task 3 — prohibition controls:** `ae8cc8d` Node/fixture control, `4626a87` current API runner. The content scanner itself was corrected before the GREEN commit.
4. **Cross-task real-source performance:** `b6c2fcc` validates CMPE keys once and performs equivalent O(1) row lookup; focused parity test passed.

## Files Created and Modified

- `brujula/enoe_adapter.py` and `brujula/metrics.py` implement the frame and metric APIs.
- `data/catalog/enoe-metrics.json` records the 23 metric definitions and canonical content hash.
- `tests/test_enoe_adapter.py`, `tests/test_enoe_metrics.py`, `tests/phase2_prohibitions_01.py`, and `tests/phase2_prohibitions_01.test.cjs` hold the behavioral and negative controls.
- `pyproject.toml` pins the direct NumPy dependency. Three small JSON subjects live under `tests/fixtures/phase2_prohibitions/`.

## Deviations from Plan

### Auto-fixed Issues

1. **[Rule 1 - Bug] Official CMPE catalog includes the `999999` unknown sentinel.** The Phase 1 field normalizer rejects this as a valid field key. The adapter now removes it from eligible catalog keys while preserving unknown rows as null. Commit: `8a64968`.
2. **[Rule 2 - Correctness] Unknown CLASE1/CLASE2 and SUB_O states could appear as denominator zeros.** Rate denominators now include only known status codes, and exclusions report unsupported states. Commit: `cb2d0b1`.
3. **[Rule 1 - Bug] Known ING7C 1..5 bands with unknown exact amount were excluded from income-state share denominators.** They now remain in state shares and stay excluded from the positive-known amount mean. Commit: `cb2d0b1`.
4. **[Rule 3 - Blocking performance] Revalidating approximately 185 CMPE catalog keys per person made the first all-eight audit impractical.** The stopped run was replaced by one-time validation plus a parity-tested normalized lookup. The complete rerun matched all eight quarters. Commit: `b6c2fcc`.

## Known Limits

- This plan provides metric inputs and definitions, not estimates, standard errors, official precision claims or public release. The variance and reconciliation gates remain in later Phase 2 plans.
- Frame arrays remain local in memory. Only counts, design support and hashes enter audits; no person rows are committed or returned in aggregate artifacts.

## Self-Check: PASSED

All listed implementation, test and catalog files exist, and every listed task commit was found in local history. The eight-source aggregate comparison passed without a source mismatch.
