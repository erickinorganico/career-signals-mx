---
phase: 03-supported-labor-findings
plan: 02
subsystem: public-aggregate-analysis
tags: [enoe, comparability, public-v2, descriptive-deltas, geography]
requires:
  - phase: 03-supported-labor-findings
    plan: 01
    provides: sanitized public record_index, complete eight-quarter profile cells
  - phase: 02-defensible-survey-estimates
    provides: accepted public-v2 snapshots and approved source/metric/revision evidence
provides:
  - pinned comparison definition registry and conditional ENT/CVE_ENT state concept mapping
  - fail-closed quarterly, annual, recorded-sex and fixed-reference entity comparison ledger
  - nominal-income and rotating-sample prohibition controls with bad and clean subjects
affects: [03-03-claims, 04-offline-publication]
tech-stack:
  added: []
  patterns: [packaged approved-source pins, versioned comparison signatures, stable missing-slot IDs, descriptive-only deltas]
key-files:
  created:
    - brujula/comparisons_v2.py
    - data/catalog/enoe-geography-equivalence.json
    - tests/test_comparisons_v2.py
    - tests/phase3_prohibitions_02.py
    - tests/phase3_prohibitions_02.test.cjs
    - tests/fixtures/phase3_prohibitions/02.clean.json
    - tests/fixtures/phase3_prohibitions/02-p3.bad.json
    - tests/fixtures/phase3_prohibitions/02-p4.bad.json
  modified: []
key-decisions:
  - "Load the reviewed registry through packaged catalog resources and check an independent digest of all eight exact source/revision pins."
  - "Fix the entity comparison reference to reviewed Baja California code 02; an absent reference emits blocked slots."
  - "Use only profiles['record_index'] for endpoint values, retaining complementary redaction as an explicit blocking reason."
  - "Keep snapshot IDs and raw SHA-256s as longitudinal endpoint provenance, while same-period slices require exact equality."
patterns-established:
  - "Every expected q-to-q+1 and q-to-q+4 slot has a stable unique ID even when both endpoints are missing."
  - "Unknown edition dates are limitations on otherwise approved signatures, never invented evidence or automatic blocks."
requirements-completed: [ANA-02, ANA-03, ANA-04]
coverage:
  - id: temporal-slots
    description: Eight-quarter series retain seven adjacent and four like-quarter annual slots, null endpoints and chronological order
    requirement: ANA-02
    verification:
      - kind: unit
        ref: tests/test_comparisons_v2.py#test_ledger_has_all_slots_in_stable_order
        status: pass
      - kind: unit
        ref: tests/test_comparisons_v2.py#test_fully_missing_pair_ids_remain_unique_across_series_and_slots
        status: pass
      - kind: integration
        ref: accepted eight-quarter aggregate-only comparison readback
        status: pass
    human_judgment: false
  - id: strict-signatures
    description: Approved source, edition, geography, population, concept, metric and method versions block incompatible or suppressed endpoints
    requirement: ANA-03
    verification:
      - kind: unit
        ref: tests/test_comparisons_v2.py#test_signature_mismatch_blocks
        status: pass
      - kind: unit
        ref: tests/test_comparisons_v2.py#test_missing_version_and_wrong_native_alias_are_blocked
        status: pass
    human_judgment: false
  - id: one-axis-slices
    description: Same-period sex and entity contrasts require one declared axis, exact snapshot identity and reviewed reference 02
    requirement: ANA-04
    verification:
      - kind: unit
        ref: tests/test_comparisons_v2.py#test_one_axis_slices_require_same_snapshot_and_reference
        status: pass
      - kind: unit
        ref: tests/test_comparisons_v2.py#test_missing_reference_emits_blocked_entity_slots
        status: pass
    human_judgment: false
  - id: prohibited-interpretations
    description: Computed income and time ledgers reject purchasing-power wording, independent person sums and change significance
    requirement: ANA-03
    verification:
      - kind: integration
        ref: tests/phase3_prohibitions_02.test.cjs
        status: pass
      - kind: integration
        ref: canonical GSD prohibition-enforcement p3 and p4
        status: pass
    human_judgment: false
duration: 30min
completed: 2026-09-23
status: complete
---

# Phase 3 Plan 02: Strict Descriptive Comparisons Summary

**Pinned ENOE definitions now permit only compatible descriptive deltas, while sparse and suppressed pairs remain visible with null changes and stable reasons.**

## Performance

- **Duration:** approximately 30 minutes
- **Completed:** 2026-09-23
- **Tasks:** 3/3
- **Files created:** 8

## Accomplishments

- `load_definition_registry(entity_reference_code="02")` reads packaged metric and geography catalogs. Its geography resource pins all eight approved source ZIP hashes, period titles and URLs, dictionary and CMPE catalog hashes, native `ENT`/`CVE_ENT` fields, revision status/hash, and the exact 32 code/name mappings. It validates those pins against independent constants. The fixed reference is Baja California `02`; loading `01` fails.
- `comparison_signature(record, provenance, definition_registry)`, `compare_public_records(previous, current, *, registry=...)`, `compare_public_slices(left, right, *, axis=..., registry=...)`, and `build_comparison_ledger(profiles, *, registry=...)` consume sanitized `profiles["record_index"]` items. A parent marked `redaction_reason: complementary_suppression` cannot regain a delta. Native geography alias and source hashes stay in signatures/provenance; an unknown edition date appears in `limitations`.
- Time comparisons emit only q→q+1 and q→q+4 slots. Same-period sex contrasts compare recorded `1` and `2` at national geography; entity contrasts hold recorded sex fixed and use the reviewed `02` reference. All other signature dimensions must agree. A pair with unsupported endpoints is `BLOCKED`, has all reasons, and keeps both change fields null.
- The accepted aggregate-only readback produced **4,209 unique comparison slots**: 805 adjacent (692 comparable), 460 like-quarter annual (393 comparable), 92 recorded-sex (66 comparable), and 2,852 entity (969 comparable). The national 2025-Q2→Q3 boundary has 115 candidates, 99 with supported descriptive deltas and the unknown-edition-date caveat. Earlier state/sex endpoints absent from accepted public snapshots remain blocked; no state cross-boundary finding is inferred from the synthetic bridge test.
- Each ledger entry carries a stable comparison ID, ordered endpoint IDs and source hashes, `status`, `comparable`, nullable absolute/relative deltas, `display_unit`, reasons, limitations and evidence refs. Percent rates use percentage points, positive-known income uses nominal MXN/month, and zero prior values produce null relative percent. No change SE, CI, p-value, significance or combined quarterly person count is produced.

## Validation Results

- Focused Python comparison tests: **18 passed**. Tests cover mismatch dimensions, cross-boundary ENT/CVE_ENT candidate, one-axis slices, fixed/missing reference, changed nonempty policy versions, changed official state name, identity tampering, missing-slot ID uniqueness, nominal income and reason order.
- Node comparison prohibitions: **2 passed**. The p3 bad fixture fails only the nominal-income named test; p4 fails only the rotating-sample named test; clean passes both. The canonical GSD producer for both reports `status=green`, `located=true`, `flagged=false`, `failFirst=true` and `passed=true` with violation-fixture proof.
- Accepted real aggregate-only integration: **4,209 unique IDs from 4,209 slots**, using the existing eight public-v2 files and accepted audits. No ZIP, R or numerical survey rerun was performed.
- Full Python regression, including the concurrent 03-01 coverage-integrity fix: **403 passed**, one existing duplicate-ZIP-member warning in `tests/test_acquisition.py`, in 190.20 seconds.

## Task Commits

1. **Task 1 — geography and signatures:** `b49c9a6` RED, `66d7483` GREEN.
2. **Task 2 — descriptive ledger:** `6198712` RED, `8f43139` GREEN.
3. **Task 3 — executable prohibitions and integrity hardening:** `eae5bac` RED, `9ed3244` GREEN.

## Decisions Made

- The reviewed geography catalog is a conditional comparison input, not a source activation or universal bridge. It records official cross-boundary references and exact catalog/member hashes; every other signature member still gates a delta.
- The registry loader does not require the ignored local `.cache` source inventory in a clean checkout or installed wheel. The approved metadata copied from that inventory is packaged and independently digest-pinned.
- The reference entity is fixed to `02` by the Phase 3 gate note. Missing reference metadata causes blocked entity slots; the code never chooses another state opportunistically.
- Comparison IDs include series and period slot identity so distinct fully missing slots cannot collide. Endpoint IDs remain canonical `v2r:` hashes of the full ten-key grain.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing critical integrity] Made approved registry portable and immutable by content**
- **Found during:** Task 3 review.
- **Issue:** Reading the ignored source inventory would fail in a clean checkout; mutable nonempty policy versions or state names could agree across endpoints and falsely pass.
- **Fix:** Package the eight exact source/revision pins in the owned geography catalog, validate its independent digest and exact state list, and require fixed policy versions in every signature.
- **Files modified:** `brujula/comparisons_v2.py`, `data/catalog/enoe-geography-equivalence.json`, `tests/test_comparisons_v2.py`.
- **Verification:** Focused tests, Node controls, real readback and full regression passed.
- **Committed in:** `9ed3244`.

**2. [Rule 1 - Bug] Prevented duplicate IDs for fully missing pair slots**
- **Found during:** Task 3 review.
- **Issue:** An endpoint-only ID would hash `[null, null]` identically for multiple absent pairs.
- **Fix:** Include comparison type, full series and periods in each ledger ID; retain nullable endpoint IDs.
- **Files modified:** `brujula/comparisons_v2.py`, `tests/test_comparisons_v2.py`.
- **Verification:** Two sparse series produce 22 distinct blocked time slots; real packet has 4,209 distinct IDs.
- **Committed in:** `9ed3244`.

**3. [Rule 2 - Missing critical governance] Enforced the reviewed entity anchor**
- **Found during:** Task 3 review.
- **Issue:** A caller could select any state as reference or omit the reference and silently lose all entity contrasts.
- **Fix:** Require `02` and emit blocked, reasoned entity slots when the reference is absent.
- **Files modified:** `brujula/comparisons_v2.py`, `tests/test_comparisons_v2.py`.
- **Verification:** Focused fixed-reference and missing-reference tests passed.
- **Committed in:** `9ed3244`.

## Known Stubs

None. Null endpoint values and absent relative percentages are contracted findings, not placeholders.

## Next Phase Readiness

Plan 03-03 can call `load_definition_registry(entity_reference_code="02")`, pass the result and `profiles` to `build_comparison_ledger`, and use `profiles["record_index"]` for canonical public endpoints. Direct comparator results contain `comparison_id`, `previous_record_id`, `current_record_id`, `status`, `comparable`, `absolute_change`, `relative_change_pct`, `display_unit`, `reasons`, `limitations`, `evidence_refs`, `source_snapshot_ids`, `source_sha256s`, `signature_previous`, and `signature_current`; ledger entries additionally contain `comparison_type` and `slot_periods`. Claims must not infer significance from these descriptive differences.

## Self-Check: PASSED

All eight implementation/control files and this summary exist. All six task hashes resolve to commits; the listed focused, real aggregate-only, canonical prohibition and full-suite results were read back after the final code change.

---
*Phase: 03-supported-labor-findings*  
*Completed: 2026-09-23*
