---
phase: 02-defensible-survey-estimates
reviewed: 2026-09-22
depth: standard
files_reviewed: 9
files_reviewed_list:
  - scripts/accept_enoe_estimates.py
  - scripts/official_reconciliation.py
  - scripts/enoe_survey_oracle.R
  - data/fixtures/enoe-aggregate-golden.json
  - tests/test_survey_oracle.py
  - tests/test_official_reconciliation.py
  - tests/test_enoe_integration.py
  - tests/phase2_prohibitions_03.py
  - tests/phase2_prohibitions_03.test.cjs
findings:
  critical: 2
  warning: 0
  info: 0
  total: 2
status: issues_found
---

# Plan 02-03: Acceptance Review

The acceptance code and its focused tests were reviewed against Plan 02-03 and the v2 research contract. The existing pre-core real pass reports 6,739 evaluated cells, 26 real R cases, four analytic R cases and passing 2025/2026 official comparisons; that pass predates the parallel core fixes and is not a final acceptance result. The focused Python tests passed (19 tests), as did the three Node prohibition controls. These results do not close the two acceptance gaps below.

## Narrative Findings (AI reviewer)

### CR-01 — BLOCKER: Full planned request inventory is not independently checked

**File:** `scripts/accept_enoe_estimates.py:402-410,270-279`

**Issue:** Acceptance obtains `domains` from `required_estimation_domains`, gives exactly that list to `estimate_snapshot`, and then derives its `expected` grains from that same list. If the domain generator omits any required latest-quarter field, entity, or recorded-sex slice, all four compared sets remain equal and the gate passes a partial inventory. The helper's support for custom partial domains is intentional; the complete eight-snapshot gate must assert its own Plan 02-03 inventory. A focused disposable check removed the Derecho/32 domain from a 141-domain latest-quarter request and `compare_inventory` still returned `PASS` for the resulting 140-domain request/evaluation/record sets.

**Fix:** Build an independent expected domain/grain set in the acceptance entry point from the pinned quarter catalog, national context/cohort/focal fields, verified latest-quarter field IDs, entities `01`–`32`, and recorded sexes `1` and `2`, including the two explicit Baja California context additions. Compare the generated `domains` and all requested, evaluated, internal, and public grains against it. Add a regression that removes one required entity or sex domain from the generator and requires acceptance to block.

### CR-02 — BLOCKER: The approved golden fixture does not pin most accepted numeric cells

**File:** `scripts/accept_enoe_estimates.py:437-480,495`

**Issue:** `golden_cases` includes only two 2026-Q2 population totals. The golden equality check therefore leaves the remaining requested public cells unpinned. Per-quarter and combined numeric digests are written into the new run's ledgers and manifest but are never compared with approved expected digests. A changed value outside those two cells, the 26 R oracle cases, and compatible official cells can pass with no explicit golden evidence update. This contradicts Plan 02-03's requirement that golden aggregate changes require an explicit evidence update and weakens replay detection across runs.

**Fix:** Pin an aggregate-only expected digest for every quarter's canonical public numeric content (or a complete keyed aggregate value ledger) in the approved fixture. Compare each current digest with its pinned value before returning `PASS`; update the fixture only through the explicit golden-evidence workflow. Add a regression that changes one non-oracle, non-official metric in a disposable result and requires acceptance to block.

## Verification

- `.venv/Scripts/python.exe -m pytest tests/test_survey_oracle.py tests/test_official_reconciliation.py tests/test_enoe_integration.py -q`: 19 passed.
- `node --test tests/phase2_prohibitions_03.test.cjs`: 3 passed.
- Focused partial-inventory proof: 141 planned latest-quarter domains, 140 submitted after omitting Derecho/32, `compare_inventory(...)=PASS`.
- No real eight-snapshot rerun was performed during this review; the core implementation is being changed in parallel.
