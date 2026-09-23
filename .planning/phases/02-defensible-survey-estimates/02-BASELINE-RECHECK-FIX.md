---
phase: 02-defensible-survey-estimates
fixed_at: 2026-09-23T07:11:50Z
review_path: .planning/phases/02-defensible-survey-estimates/02-REVIEW.md
iteration: 2
findings_in_scope: 2
fixed: 2
skipped: 0
status: all_fixed
---

# Phase 2: Baseline Recheck Fix Report

**Fixed at:** 2026-09-23T07:11:50Z  
**Source review:** consolidated baseline recheck  
**Iteration:** 2

**Summary:** 2 findings in scope; 2 fixed; 0 skipped.

## Fixed Issues

### WR-01: Reinitialization can replace an approved internal hash baseline

**Files modified:** `scripts/accept_enoe_estimates.py`, `tests/test_enoe_integration.py`  
**Commit:** `8e8ef43`  
**Applied fix:** `--generate-golden` can add an absent internal hash map or replay an identical one, but it rejects any change to an existing map. The focused idempotent and changed-map controls passed. **Status:** fixed; requires human verification of the baseline update policy.

### WR-02: Acquisition time and payload ordering cause false numeric drift

**Files modified:** `scripts/accept_enoe_estimates.py`, `tests/test_enoe_integration.py`, `data/fixtures/enoe-aggregate-golden.json`  
**Commit:** `86406f6`  
**Applied fix:** Canonical content excludes `sources[*].acquired_at` as an operational receipt clock, as well as the existing method-version fields. It sorts records by the ten-field grain and root catalogs by ID. Source IDs, hashes, URLs, terms, dimensions, values, support, precision, status, and reasons remain pinned. The separate full public payload digest still records exact custody bytes and ordering. Timestamp/order-only controls pass; source hash and value mutations block. **Status:** fixed; requires human verification of canonical replay semantics.

The eight public canonical hashes were repinned solely from preserved aggregate public payloads under `.cache/research/phase2-acceptance`. The frozen `pre-core-review-pass.json` was verified as `PASS`; its metric manifest, each full public payload digest, each public record digest, and its combined numeric digest matched before derivation. No raw ZIP or person rows were read.

## Verification

Focused acceptance, reconciliation, and survey oracle Python tests passed (30 tests). Phase 2 Node prohibition controls passed (3 tests). Python parse, fixture JSON parse, and `git diff --check` passed. The real eight-quarter R run was not performed in this fix worktree.

---

_Fixed: 2026-09-23T07:11:50Z_  
_Fixer: the agent (gsd-code-fixer)_  
_Iteration: 2_
