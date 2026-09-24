---
phase: 03-supported-labor-findings
reviewed: 2026-09-23T18:39:30Z
depth: deep
files_reviewed: 29
files_reviewed_list:
  - brujula/analysis_v2.py
  - brujula/comparisons_v2.py
  - brujula/claims_v2.py
  - brujula/findings_v2.py
  - contracts/analysis-v2.schema.json
  - data/fixtures/enoe-analysis-coverage-pins.json
  - data/fixtures/enoe-analysis-reference.json
  - data/catalog/enoe-geography-equivalence.json
  - tests/test_analysis_v2.py
  - tests/test_comparisons_v2.py
  - tests/test_claims_v2.py
  - tests/test_analysis_integration.py
  - tests/test_phase3_edge_acceptance.py
  - tests/phase3_prohibitions_01.py
  - tests/phase3_prohibitions_01.test.cjs
  - tests/phase3_prohibitions_02.py
  - tests/phase3_prohibitions_02.test.cjs
  - tests/phase3_prohibitions_03.py
  - tests/phase3_prohibitions_03.test.cjs
  - tests/fixtures/phase3_prohibitions/01.clean.json
  - tests/fixtures/phase3_prohibitions/01-p1.bad.json
  - tests/fixtures/phase3_prohibitions/01-p2.bad.json
  - tests/fixtures/phase3_prohibitions/02.clean.json
  - tests/fixtures/phase3_prohibitions/02-p3.bad.json
  - tests/fixtures/phase3_prohibitions/02-p4.bad.json
  - tests/fixtures/phase3_prohibitions/03.clean.json
  - tests/fixtures/phase3_prohibitions/03-p5.bad.json
  - tests/fixtures/phase3_prohibitions/03-p6.bad.json
  - tests/fixtures/phase3_prohibitions/03-p7.bad.json
findings:
  critical: 0
  warning: 0
  info: 0
  total: 0
status: clean
---

# Phase 3: Code Review Report

**Reviewed:** 2026-09-23T18:39:30Z  
**Depth:** deep  
**Status:** clean; no open review findings

## Summary

Reviewed the final profile, comparison, claims and packet code through source freeze `a6696a1`, including the strict schema, independent hash references, tests and seven prohibition controls. The original geography-alias blocker is closed in [03-CORE-REVIEW.md](03-CORE-REVIEW.md). Additional adversarial findings below were fixed and rechecked. No open defect remains in this review. This is a code-review verdict for Phase 3, not a claim that Phase 4 publication has occurred.

## Narrative Findings (AI reviewer)

No open finding remains. These resolved defects and controls are retained for the audit:

| Classification | Evidence and impact before fix | Fix checked |
| --- | --- | --- |
| **BLOCKER**, resolved — chronology | `brujula/comparisons_v2.py` used caller-supplied `registry['periods']` for adjacency. Reversing that list made a Q3→Q2 pair comparable with a non-null delta and no reasons. | `11ae33b` uses authoritative `PERIODS` and rejects altered registry order. Independent reproduction now returns `period_adjacency` and `period_registry`, null delta. |
| **BLOCKER**, resolved — geography concept | `brujula/comparisons_v2.py` accepted any nonempty `geography_concept` string while preserving the reviewed assertion. A changed concept still produced a supported state pair. | `11ae33b` pins exact reviewed concept text. Independent reproduction now returns `geography_concept_review` and null delta. |
| **BLOCKER**, resolved — professional age universe | `brujula/claims_v2.py:41` initially described the known-age cohort as ages 15–97, omitting that EDA code 97 means 97 years **or more** (`brujula/populations.py:34`). Every professional claim repeated the inaccurate bound. | The frozen Spanish label states the 97 top code explicitly. The national label also calls 98 a code for operationally unknown age. Focused claim tests and saved opening text confirm both. |
| **WARNING**, resolved — same-period wording | `brujula/claims_v2.py` called same-quarter sex/entity differences `cambio` and applied rotating-quarter overlap limits to them; `brujula/comparisons_v2.py` did likewise. This misdescribed the comparison axis. | `d1515e6` gives slices `descriptive_difference_only`; claim interpretation and limitation distinguish same-quarter groups from qoq/yoy. Independently reran 24 comparison tests and 2 Node controls, then 28 comparison tests and 2 Node controls after later core hardening. Positive claim-kind tests now cover all four comparison kinds. |
| **WARNING**, resolved — cyclic validator input | `brujula/findings_v2.py:183-201` previously raised uncaught `RecursionError` on a self-referential Python dict instead of returning a validation error. | Direct reproduction now returns a `json_scalars` error after cycle tracking was added. |
| **WARNING**, resolved — p7 control isolation | The first p7 bad fixture combined source activation and a suppressed claim, failing at the first assertion without separately proving validator rejection of each. | `tests/phase3_prohibitions_03.py:72-83` now checks source-only and suppression-only mutated packets against `validate_analysis_packet` before the combined bad-fixture assertion. |
| **WARNING**, resolved — canonical grammar | `brujula/claims_v2.py` initially prefixed every metric with Spanish `la`, making income and plural-person observations grammatically wrong. The national label also called code 98 an age rather than an unknown-age code. | `67fa85f` uses `el valor de «…»` for every metric and states `código 98: edad operativamente desconocida`. Regression tests and the saved opening findings confirm the final wording. |
| **BLOCKER**, resolved — persisted JSON validation | The first saved `analysis.json` failed `validate_analysis_packet` with `comparisons: ledger differs from recomputed public pairs`. `brujula/comparisons_v2.py` emitted `metric_dictionary_refs` as tuples, which JSON reload converted to lists; the in-memory gate missed it. Phase 4 could not validate the saved handoff. | RED `159cbcb` and GREEN `a6696a1` emit JSON-native lists. The synthetic round-trip regression passes; independently reloaded the unchanged saved artifact and obtained `errors 0 []`. The file SHA-256 remains `9bbb5af3091c4cb02bec98d499ac522d77715f3a1316a30f906364fcc4c6537d`; its content digest remains `d2f28f26f993d052fb5f246db3262ad00b776081a663d608e0427962745a0c79`. |

The original CR-01 coherent native-alias/catalog mutation now returns `geography_snapshot_identity`, `comparable=False`, and null delta. The focused comparison suite passed **28 tests** and Node comparison prohibitions passed **2** after the chronology and concept fixes.

## Final verification

The saved non-synthetic packet contains **6,739** sanitized records, **4,209** comparison slots, **38** canonical claims and **three** opening claims. Direct validation of the loaded JSON returned no errors; the trusted reference, five null redacted parents, source manifest and opening IDs were checked in the persisted readback. No estimate key, person row or private diagnostic was found in the public packet. The seven canonical prohibition proofs each report `green`, `located=true`, `flagged=false`, `failFirst=true` and `passed=true`.

JUnit records **443 passed, 0 failed, 0 skipped** in the full Python run (151.46 seconds reported by the runner). An eighth parametrized edge case was added after that run's collection; the final edge file was then run separately with **8 passed** (independently repeated here: 8 passed). Thus the full run and final focused check cover **444 unique test cases** without claiming a second full run. The Phase 3 security register has **0 open threats**; final code review now supplies its remaining independent-review input. The local cache packet is a validated analytical handoff, not a public release.

---

_Reviewer: gsd-code-reviewer_  
_No source files modified by this review._
