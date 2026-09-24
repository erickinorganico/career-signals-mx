---
phase: 02-defensible-survey-estimates
reviewed: 2026-09-23
depth: standard
scope: consolidated-core-and-acceptance-recheck-at-86406f6
files_reviewed: 9
files_reviewed_list:
  - scripts/accept_enoe_estimates.py
  - scripts/official_reconciliation.py
  - scripts/enoe_survey_oracle.R
  - brujula/enoe_adapter.py
  - brujula/metrics.py
  - brujula/estimates.py
  - brujula/source_inventory.py
  - tests/test_enoe_integration.py
  - data/fixtures/enoe-aggregate-golden.json
findings:
  critical: 0
  warning: 0
  info: 0
  total: 0
status: clean
---

# Phase 2: Consolidated Code Review

The historical reviews are preserved in `02-CORE-REVIEW.md`, `02-CORE-RECHECK.md`, and `02-ACCEPTANCE-REVIEW.md`. This report consolidates their seven findings with a targeted recheck of the final baseline fixes on main `86406f6`. All seven are resolved at the source-code and focused-test level. The internal diagnostic pins are intentionally absent until the explicit first initialization, and a new real eight-snapshot R/official run and unchanged replay remain pending. This report does not claim numerical acceptance or publication readiness.

## Narrative Findings (AI reviewer)

No open source-code findings in this reviewed scope. The baseline and custody fixes were verified directly; the remaining gate is the real numerical run.

## Resolved Historical Findings

| Original finding | Recheck evidence |
|---|---|
| Core CR-01, conflicting geography aliases | `2` and `"02"` equivalent; `2` versus `3`, `0`, `33`, and bool rejected on a loaded disposable frame. |
| Core WR-01, stale frame masks | Mapping and nested custody immutable; `Frame` copies and freezes caller arrays; `dataclasses.replace` gets a fresh cache; returned exclusions are copied. Caller-array and exclusion-mutation regressions pass. |
| Core WR-02, person-row scanner gaps | Seven Node P1/P2 controls pass, including prefixed logger, multiline JSON, Python repr, CSV, and untracked staged ZIP/report bad subjects. |
| Acceptance CR-01, incomplete domain inventory | Independent expected domains include eight-quarter national/cohort/focal sets and latest observed fields, 32 entities, two sexes, and explicit Baja California context; omission tests block. |
| Acceptance CR-02, sparse golden fixture | Eight committed public-content pins match the preserved pre-core PASS outputs; non-oracle older-quarter public-value and suppressed internal-only mutation tests block. Internal hash initialization/replay is still a pending numerical gate. |
| Baseline CR-01, internal hash overwrite | `initialize_internal_golden` adds a missing map, accepts an identical existing map, and rejects a changed existing map. Disposable idempotence and changed-map probes, plus the focused test, passed. |
| Baseline CR-02, clock/order false drift | Numeric canonicalization excludes `acquired_at`, sorts records by `GRAIN` and catalogs by ID, while retaining source SHA-256 and numeric content. Saved public pins match all eight quarters; clock/order-only tests pass and source-hash/value mutations block. The separate exact payload digest remains order/time sensitive for custody. |

## Verification Boundary

Final targeted recheck: 30 affected Python tests and three Node Plan 02-03 controls passed. The previous broader run reported 363 Python tests passing with no skips and all 18 Node tests passing before the two final baseline commits; no unrelated source files changed in those commits. The eight saved public payloads matched their repinned canonical digests. No real R/eight-snapshot run was performed for this review; initialization and unchanged replay must be reported separately from source review.
