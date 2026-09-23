---
phase: 02-defensible-survey-estimates
fixed_at: 2026-09-23T06:46:54Z
review_path: .planning/phases/02-defensible-survey-estimates/02-CORE-REVIEW.md
iteration: 1
findings_in_scope: 3
fixed: 3
skipped: 0
status: all_fixed
---

# Phase 2: Core Code Review Fix Report

**Fixed at:** 2026-09-23T06:46:54Z  
**Source review:** `.planning/phases/02-defensible-survey-estimates/02-CORE-REVIEW.md`  
**Iteration:** 1

**Summary:** 3 findings in scope; 3 fixed; 0 skipped.

## Fixed Issues

### CR-01: Conflicting geography selectors silently choose one geography

**Files modified:** `brujula/metrics.py`, `tests/test_enoe_metrics.py`  
**Commit:** `d3b1437`  
**Applied fix:** Normalize each supplied official entity code and reject conflicting `entity` and `geography` values before constructing vectors. Numeric and zero-padded equivalent aliases are accepted. **Status:** fixed; requires human verification of selector semantics because this is a logic finding.

### WR-01: Frame mutation leaves cached metric masks stale

**Files modified:** `brujula/enoe_adapter.py`, `brujula/metrics.py`, `tests/test_enoe_adapter.py`, `tests/test_enoe_metrics.py`, `tests/test_estimates.py`  
**Commit:** `eeaa8ee`  
**Applied fix:** Copy and freeze frame column, catalog-label, and nested custody mappings; keep the mask cache private per frame. A frame created with `dataclasses.replace` starts with an empty cache. The internal estimate, public projection, and audit remain JSON serializable.

### WR-02: Person-row prohibition check misses common logged and packaged forms

**Files modified:** `tests/phase2_prohibitions_01.py`, `tests/phase2_prohibitions_01.test.cjs`, five `tests/fixtures/phase2_prohibitions/01-p1-*.bad.json` files  
**Commit:** `2e96882`  
**Applied fix:** Inspect prefixed and multiline JSON, Python repr, and CSV streams. Inspect tracked data artifacts plus aggregate audit, metric coverage, report, and ZIP outputs created in a disposable staging directory. Five independent negative controls fail on injected synthetic rows, including an untracked package.

## Verification

The affected adapter, metric, and estimate tests passed (49 tests). The Phase 2 P1/P2 Node control passed (7 tests, including five negative controls). Python syntax checks and `git diff --check` passed.

---

_Fixed: 2026-09-23T06:46:54Z_  
_Fixer: the agent (gsd-code-fixer)_  
_Iteration: 1_
