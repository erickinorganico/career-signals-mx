---
phase: 01-official-sources-and-research-contract
reviewed: 2026-09-23T03:52:57Z
depth: standard
files_reviewed: 12
files_reviewed_list:
  - brujula/acquisition.py
  - brujula/source_inventory.py
  - brujula/populations.py
  - brujula/research_contract.py
  - contracts/research-v2.schema.json
  - contracts/research-v2-public.schema.json
  - tests/test_acquisition.py
  - tests/test_source_inventory.py
  - tests/test_population_rules.py
  - tests/test_research_contract.py
  - docs/SOURCES.md
  - docs/CONTRACT-V2.md
findings:
  critical: 4
  warning: 1
  info: 0
  total: 5
status: issues_found
---

# Phase 1: Code Review Report

**Reviewed:** 2026-09-23T03:52:57Z  
**Depth:** standard  
**Files Reviewed:** 12  
**Status:** issues_found

## Summary

The source custody and population rules were read alongside the v2 schemas, validators, tests, and contracts. Isolated synthetic probes show that the public precision gate accepts contradictory diagnostics and impossible design support, suppressed estimates can escape through a retained free-text reason, and a nonfinite Decimal crashes validation. A reviewed focus code also fails normalization when presented in its documented six-digit form. These probes do not assess or approve actual ENOE estimates.

## Narrative Findings (AI reviewer)

## Critical Issues

### CR-01: **BLOCKER** — Claimed CV can contradict the standard error and estimate

**File:** `brujula/research_contract.py:154-166` (also `contracts/research-v2.schema.json:82-89` and `contracts/research-v2-public.schema.json:82-89`)

**Issue:** The visible-value gate checks only that the supplied CV is below 30. It does not check that CV equals `100 * standard_error / estimate`. In the complete synthetic fixture, changing only `standard_error` from `3.0` to `1000.0` leaves CV at `2.5`; `validate_research_v2` returns no failures and the value remains public. The stated precision gate can therefore be bypassed by contradictory input.

**Fix:** For a visible positive estimate, compare the supplied CV with `100 * se / abs(estimate)` using a documented numeric tolerance, and reject material disagreement. Recompute or validate interval endpoints against the declared interval method in the Phase 2 numerical gate. Add a negative test that changes SE while leaving CV unchanged.

### CR-02: **BLOCKER** — Impossible support counts can satisfy the release gate

**File:** `brujula/research_contract.py:128-133` (also `contracts/research-v2.schema.json:72-80` and `contracts/research-v2-public.schema.json:72-80`)

**Issue:** The support checks compare domain PSU and strata counts with their full-design counterparts, but never compare contributing PSU count with observed `sample_size`. The fixture passes with `sample_size=30`, `n_psu_domain=31`, `n_psu_design=31`, `n_strata_domain=6`, `n_strata_design=8`, and `design_df=23`; one observed person per contributing PSU is the absolute minimum, so this support is impossible. A further probe passes with a visible value and `weighted_support_total=0` although the record's weighted denominator is positive. Invalid support metadata can thus accompany a released value.

**Fix:** Require `n_psu_domain <= sample_size`, positive contributing support where a value is visible, and explicit consistency rules between weighted support and the measure denominator. Add negative fixtures for PSU count exceeding n and zero weighted support with a visible positive denominator.

### CR-03: **BLOCKER** — Suppressed estimate leaks through public reason

**File:** `brujula/research_contract.py:209-220` (also `contracts/research-v2-public.schema.json:109`)

**Issue:** The projection clears numeric diagnostics when `value` is null but copies `reason` verbatim. A valid internal record with `status=BLOCKED`, `value=null`, `estimate=120.0`, and `reason="Suppressed estimate 120.0"` passes both validators; the resulting public record contains that exact suppressed estimate in `reason`. The documented suppression guarantee is therefore incomplete.

**Fix:** Make the public reason a controlled code or a template selected by the projection from a bounded internal reason category. Keep detailed diagnostic text internal. Test a reason containing the suppressed estimate and require that the serialized public payload does not contain it.

### CR-04: **BLOCKER** — Nonfinite Decimal crashes the validator

**File:** `brujula/research_contract.py:48-63` and `brujula/research_contract.py:122`

**Issue:** `_nonfinite_paths` checks only Python `float`, while the JSON Schema validator accepts `Decimal` as a number. Setting a fixture record's `value` to `Decimal("NaN")` makes `validate_research_v2` raise `decimal.InvalidOperation` at the subsequent range comparison, rather than returning a validation failure. A malformed input mapping can therefore terminate a validation or publication run outside the documented failure path.

**Fix:** Reject every nonfinite numeric type accepted by the API before schema and semantic comparisons (including `Decimal`), or normalize to strict JSON scalar types and reject unsupported Python numbers. Add a direct test for `Decimal("NaN")` and `Decimal("Infinity")` in visible and diagnostic numeric fields.

## Warnings

### WR-01: **WARNING** — Focus-code helper rejects its normalized form

**File:** `brujula/source_inventory.py:24-31`

**Issue:** `normalize_cmpe_code("31300", coding)` returns `"031300"`, but passing `"031300"` with the same verified coding returns null because lookup uses only the unpadded key. The inventory and source contract describe six-digit normalization, so a downstream caller that receives an already normalized SDEM lexeme can incorrectly classify a known focus field as unknown. This differs from `brujula/populations.py:185-205`, which accepts either spelling after normalization.

**Fix:** Normalize the ASCII input to six digits before matching it against normalized `focus_codes` values, while continuing to reject `999999`, malformed input, and codes outside the verified catalog. Test both `31300` and `031300` for each reviewed focus code.

---

_Reviewed: 2026-09-23T03:52:57Z_  
_Reviewer: the agent (gsd-code-reviewer)_  
_Depth: standard_
