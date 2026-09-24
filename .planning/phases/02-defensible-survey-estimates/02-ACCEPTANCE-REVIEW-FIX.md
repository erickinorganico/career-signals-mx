---
phase: 02-defensible-survey-estimates
fixed_at: 2026-09-23T07:00:32Z
review_path: .planning/phases/02-defensible-survey-estimates/02-ACCEPTANCE-REVIEW.md
iteration: 1
findings_in_scope: 2
fixed: 2
skipped: 0
status: all_fixed
---

# Phase 2: Acceptance Review Fix Report

**Fixed at:** 2026-09-23T07:00:32Z  
**Source review:** `.planning/phases/02-defensible-survey-estimates/02-ACCEPTANCE-REVIEW.md`  
**Iteration:** 1

**Summary:** 2 findings in scope; 2 fixed; 0 skipped. The separate core WR-01 recheck was also corrected on this isolated branch.

## Fixed Issues

### CR-01: Full planned request inventory is not independently checked

**Files modified:** `scripts/accept_enoe_estimates.py`, `tests/test_enoe_integration.py`  
**Commit:** `695f15c`  
**Applied fix:** The acceptance entry point independently constructs required quarter domains from observed verified catalog fields, the focal fields, 32 entities, two recorded-sex slices, and the two explicit Baja California context additions. It checks generator output before estimation and checks requested, evaluated, internal, and public grains against the independent inventory. Custom partial estimator requests remain valid. Focused omitted field, entity, sex, and Baja California controls block. **Status:** fixed; requires human verification of the planned inventory logic.

### CR-02: Approved golden fixture does not pin most accepted numeric cells

**Files modified:** `scripts/accept_enoe_estimates.py`, `tests/test_enoe_integration.py`, `data/fixtures/enoe-aggregate-golden.json`  
**Commit:** `f0d67c4`  
**Applied fix:** The fixture pins complete canonical public content for each of eight quarters and the metric manifest. Canonicalization excludes only the adapter-source method version in records and its copy in the method catalog. All dimensions, values, support, precision, status, reason, and source IDs remain included. Internal diagnostic content gets a separate hash-only per-quarter pin through an explicit `--generate-golden` run; suppressed numeric diagnostics are never committed. The initialization refuses to change the public or official baseline. Non-oracle older-quarter public-value and suppressed internal-only mutation controls block. **Status:** fixed; requires human verification of numeric replay after the full eight-quarter run.

The public pins were derived solely from preserved aggregate public outputs under `.cache/research/phase2-acceptance`. Before derivation, `pre-core-review-pass.json` was confirmed `PASS`, its metric manifest digest matched the current catalog, all eight public payload digests and record digests matched the frozen manifest, and its combined numeric digest matched. No person rows or raw ZIP contents were read for seeding.

## Additional Core Recheck Correction

### WR-01: Caller-owned replacement arrays can still stale-cache masks

**Files modified:** `brujula/enoe_adapter.py`, `tests/test_enoe_adapter.py`, `tests/test_enoe_metrics.py`  
**Commit:** `7cc967c`  
**Applied fix:** `Frame` copies every input array and marks the owned copy read-only, so later writes through a caller-held array cannot change a primed frame. Constructor and `dataclasses.replace` mutation controls passed. This is ordinary in-process robustness, not a security boundary against deliberately changing NumPy flags.

**Follow-up commit:** `5662d8a`  
**Applied fix:** `metric_vectors` returns a copy of exclusion counts, so callers cannot mutate the cached domain state through a returned result. A same-domain replay regression passed.

## Verification and Next Gate

The combined affected Python suite passed (78 tests), and Node Phase 2 prohibition controls passed (3 tests). Python parse checks, JSON parse, and `git diff --check` passed. The real eight-quarter R run was intentionally left to the parent after consolidation.

From the main checkout, initialize the internal hash baseline with:

```powershell
& .\.venv\Scripts\python.exe scripts\accept_enoe_estimates.py --output-root artifacts\enoe --audit-dir .cache\research\phase2-acceptance --generate-golden
```

Then rerun the same command without `--generate-golden` and require unchanged replay. Any intentional future public baseline change requires an evidence-reviewed manual fixture update from verified aggregate-only public outputs; `--generate-golden` cannot change the public pin.

---

_Fixed: 2026-09-23T07:00:32Z_  
_Fixer: the agent (gsd-code-fixer)_  
_Iteration: 1_
