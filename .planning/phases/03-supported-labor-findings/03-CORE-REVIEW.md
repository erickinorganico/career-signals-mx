---
phase: 03-supported-labor-findings
reviewed: 2026-09-23T17:57:08Z
depth: deep
files_reviewed: 16
files_reviewed_list:
  - brujula/analysis_v2.py
  - brujula/comparisons_v2.py
  - data/fixtures/enoe-analysis-coverage-pins.json
  - data/catalog/enoe-geography-equivalence.json
  - tests/test_analysis_v2.py
  - tests/test_comparisons_v2.py
  - tests/phase3_prohibitions_01.py
  - tests/phase3_prohibitions_01.test.cjs
  - tests/phase3_prohibitions_02.py
  - tests/phase3_prohibitions_02.test.cjs
  - tests/fixtures/phase3_prohibitions/01.clean.json
  - tests/fixtures/phase3_prohibitions/01-p1.bad.json
  - tests/fixtures/phase3_prohibitions/01-p2.bad.json
  - tests/fixtures/phase3_prohibitions/02.clean.json
  - tests/fixtures/phase3_prohibitions/02-p3.bad.json
  - tests/fixtures/phase3_prohibitions/02-p4.bad.json
findings:
  critical: 0
  warning: 0
  info: 0
  total: 0
status: clean
scope: completed_phase3_core_only
---

# Phase 3: Core Code Review Report

**Reviewed:** 2026-09-23T17:57:08Z  
**Depth:** deep  
**Status:** clean

## Summary

Reviewed the completed Phase 3 profile index, observed coverage, geography registry, descriptive comparisons, focused tests and Node prohibition controls against the accepted Phase 2 and Phase 3 contracts. The one reproducible comparison integrity blocker was fixed and independently rechecked. No open finding remains in this scoped core review. Claims, findings, schema and final Phase 3 acceptance are outside this report. The accepted 403-test suite, four prohibition controls, and 6,739-record / 4,209-slot readbacks are recorded in the 03-01 and 03-02 summaries; unchanged inputs did not warrant another full run.

## Narrative Findings (AI reviewer)

All reviewed core files meet the scoped quality gate after the CR-01 correction. No open issues found.

## Resolved Finding

### CR-01 — BLOCKER, closed: A coherently changed native geography alias was accepted as an approved state comparison

**Original file:** `brujula/comparisons_v2.py:205-221, 308-317`  
**Fixed at:** `brujula/comparisons_v2.py:60-69, 185-192`  
**Related control:** `tests/test_comparisons_v2.py:61-86`  
**Issue:** `_signature` selected the expected state-catalog hash *from the mutable registry's native alias* without independently checking that a specific quarter used `ENT` before 2025-Q3 or `CVE_ENT` afterward. `_result` excluded both `native_geography_field` and `state_catalog_sha256` from pair equality. A coherent alias-plus-catalog change could therefore yield a supported cross-edition state delta.

**Original reproduction:** Using synthetic 2025-Q2 and 2025-Q3 state `02` records, changing Q2's `native_geography_field` to `CVE_ENT` and its `state_catalog_sha256` to the Q3 CVE hash returned `comparable=True`, `reasons=[]` and a non-null delta. Q2's reviewed native field is `ENT`.

**Impact before fix:** An incorrectly assembled or transformed registry could falsely certify a cross-edition state delta.

**Fix and verification:** Commits `7569f83` (RED) and `79dbd25` (GREEN) add an independent eight-snapshot period/native-field/catalog-hash map and reject a disagreement as `geography_snapshot_identity`; `24eed1d` records the execution evidence. The same synthetic reproduction now returns `comparable=False`, `reasons=['geography_snapshot_identity']`, `absolute_change=None`. The new regression covers coherent mutation in both directions and national metadata. Independently reran `tests/test_comparisons_v2.py`: **21 passed**, and `tests/phase3_prohibitions_02.test.cjs`: **2 passed**. No ZIP, R, network or person-row access was used.

---

_Reviewer: gsd-code-reviewer (scoped core review)_  
_No source files modified._
