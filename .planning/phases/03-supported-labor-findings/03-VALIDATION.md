---
phase: 3
slug: supported-labor-findings
status: validated
nyquist_compliant: true
wave_0_complete: true
created: 2026-09-22
---

# Phase 3 — Validation Strategy

Phase 3 execution starts only after Phase 1 verification and Phase 2's real eight-snapshot numerical acceptance. Before 03-01 Task 1, inspect the implemented `brujula/enoe_adapter.py`, `brujula/metrics.py`, `brujula/estimates.py`, `estimate_snapshot` return shape, accepted metric/population/geography definition versions, public v2 validator/projection signatures, and aggregate acceptance ledger. If any required version/field or numerical gate is absent, keep affected analysis blocked and revise the plan against the actual interface; synthetic fixtures cannot stand in for accepted real estimates.

## Test Infrastructure and Sampling

Python 3.12 and pytest 9.0.3 are available locally. Focused tests use synthetic, validated public aggregate fixtures with no network or person rows. Run the affected test after each task, the full `.venv/Scripts/python.exe -m pytest -q` suite after each wave, and an offline real eight-snapshot integration at the Phase 3 gate. The real integration consumes accepted Phase 2 public aggregates; it must not reopen ZIPs or recompute survey estimates.

| Plan/task | Requirements | Automated gate and evidence |
|---|---|---|
| 03-01 T1 | ANA-01, ANA-05 | `.venv/Scripts/python.exe -m pytest tests/test_analysis_v2.py -q`; Phase 2 acceptance manifest, strict public v2 validation, ten-key canonical IDs, reorder/collision negatives |
| 03-01 T2 | ANA-01, ANA-04, ANA-05 | Same focused test; exact Phase 2 requested/evaluated/public grain equality, eight national periods, complete three-focus metrics, latest official other fields, 32 states/two sex slots, genuinely computed sparse nulls, response/exclusion denominator and suppression sentinels; absent computation blocks |
| 03-02 T1 | ANA-03 | `.venv/Scripts/python.exe -m pytest tests/test_comparisons_v2.py -q`; longitudinal equality mismatch matrix; separate same-period sex/entity one-axis supported and blocked controls, mandatory entity reference, source edition and metric-version negatives, reviewed ENT/CVE_ENT code/name/definition evidence |
| 03-02 T2 | ANA-02, ANA-04 | Same focused test; seven q→q+1 and four q→q+4 slots per full series, sparse blocked slots, percentage-point/nominal units, no change precision |
| 03-03 T1 | ANA-06 | `.venv/Scripts/python.exe -m pytest tests/test_claims_v2.py -q`; exact Spanish template regeneration, source/method/evidence refs, zero-to-three openings, altered-number/causal/advice negatives |
| 03-03 T2 | ANA-01–06 | `.venv/Scripts/python.exe -m pytest tests/test_analysis_integration.py tests/test_claims_v2.py -q`; then real accepted Phase 2 public aggregates through `build_analysis_packet`, strict schema, complete scope, nested and complementary suppression sentinel scan |
| 03-01 T3, 03-02 T3, 03-03 T3 | ANA-01–06 | `node --test tests/phase3_prohibitions_01.test.cjs`, `_02.test.cjs`, `_03.test.cjs`; canonical `check prohibition-enforcement` for all seven projected descriptors with known-bad and known-clean subjects |

## Edge Candidate Acceptance Map

`03-EDGE-PROBE.json` is produced by the shared GSD edge engine from the six Spanish requirements with explicit semantic shape overrides. It has **31 applicable and explicitly resolved plan criteria**: ANA-01 four, ANA-02 five, ANA-03 six, ANA-04 five, ANA-05 five, ANA-06 six. Each resolution string is the exact matching flat-string `must_haves.truths` entry; the table gives the test owner. Resolution here means the criterion is specified, not that implementation has passed.

| Requirement | Edge categories and plan/task owner | Concrete acceptance |
|---|---|---|
| ANA-01 | adjacency, empty, encoding, ordering → 03-01 T1–2 | Separate field/occupation/industry IDs; explicit null cell; official CMPE key/label; stable index/grid under reorder |
| ANA-02 | boundary, adjacency, empty, ordering, precision → 03-02 T2 | Exactly seven adjacent/four like-quarter pairs; seasonality caveat; missing pair blocked; chronological stability; pp/nominal units and zero-prior relative null |
| ANA-03 | boundary, adjacency, empty, encoding, ordering, precision → 03-02 T1 | Every signature mismatch blocks; conditional cross-alias equivalence; missing version/suppressed endpoint blocks; exact 2-digit state key with native provenance; stable reasons; no delta SE/CI/significance |
| ANA-04 | boundary, adjacency, empty, ordering, precision → 03-01 T2 and 03-02 T2 | All 32 state/two sex slots; separate slices; sparse null/reason; stable code order; no hidden weighted precision |
| ANA-05 | boundary, adjacency, empty, ordering, precision → 03-01 T2 | Correct named coverage denominator; distinct exclusion categories; null zero-denominator; stable counts; no weighted-as-sample-n or complementary disclosure |
| ANA-06 | boundary, adjacency, empty, encoding, ordering, precision → 03-03 T1 | Zero-to-three openings; grain-bound numbers; empty opening limitation; exact accented labels/units; stable IDs; no extra numerals or false certainty |

## Prohibition and Security Review

The plans carry seven operational prohibitions in structured `must_haves.prohibitions` with flat `statement`, `status: resolved`, `verification: test`, `check_kind: node-test`, `check_target`, `check_violation_fixture`, and `check_clean_fixture` fields. Planned Node/Python targets exercise actual profile, comparison, claim and packet APIs. Bad JSON subjects mutate computed output; clean subjects leave it unchanged. The canonical GSD producer must locate each target and prove a non-vacuous current pass, targeted bad-fixture red, clean-fixture green and content causation. These controls are **not implemented or green at planning time**; absent or failing checks remain flagged-unverified and block canonical completion. ASVS L1 focus here is the private-record/public-aggregate boundary, strict input and output validation, source identity, and prevention of suppressed-number or unsupported-claim disclosure; V2 authentication and V3 sessions do not apply to local batch analysis.

## Four-Source Coverage Audit

| Source | Item | Plans | Status |
|---|---|---|---|
| GOAL | Supported field, time, sex and territorial findings with visible limits | 03-01–03 | COVERED |
| REQ | ANA-01 focal, cohort and other official field profiles | 03-01, 03-03 | COVERED |
| REQ | ANA-02 eight-quarter descriptive changes | 03-02, 03-03 | COVERED |
| REQ | ANA-03 fail-closed comparable deltas | 03-02, 03-03 | COVERED |
| REQ | ANA-04 recorded-sex and all-entity coverage | 03-01–03 | COVERED |
| REQ | ANA-05 support, response and exclusions | 03-01, 03-03 | COVERED |
| REQ | ANA-06 exact evidence-bound claims | 03-03 | COVERED |
| RESEARCH | Ten-key canonical public index, no record ID, full expected cells | 03-01 | COVERED |
| RESEARCH | Phase 2 accepted-public preflight and definition versions | 03-01–03 | COVERED |
| RESEARCH | Versioned source/population/geo/metric/method comparison signature and cross-alias evidence | 03-02 | COVERED |
| RESEARCH | q→q+1/q→q+4, descriptive units and rotating-sample limits | 03-02 | COVERED |
| RESEARCH | Typed claims, exact templates, strict packet schema and public-only boundary | 03-03 | COVERED |
| CONTEXT | All eight national/cohort/focal periods and full metric profiles | 03-01 | COVERED |
| CONTEXT | Latest official other fields, 32 entities/two sex slices, sparse nulls | 03-01 | COVERED |
| CONTEXT | ENT/CVE_ENT conditional equivalence, strict comparability, nominal/seasonal wording | 03-02 | COVERED |
| CONTEXT | Coverage/exclusions and sample versus weighted distinction | 03-01 | COVERED |
| CONTEXT | Canonical claims, up-to-three evidence-based openings, public-only input | 03-03 | COVERED |

`03-CONTEXT.md` contains locked decisions without D-NN IDs, so the audit maps each decision group by subject. Deferred Phase 4 formatting/exports/current and out-of-scope causal modeling, personal advice and deflation are excluded as specified. No ANA requirement or research feature is silently omitted.

## Executed Nyquist audit — 2026-09-23

The following map uses the 31 exact categories in `03-EDGE-PROBE.json`. Each reference names an executable assertion over a constructed public aggregate, comparator result, claim, or saved packet. The eight tests in `tests/test_phase3_edge_acceptance.py` were added by this audit; all other listed tests were created during Plans 03-01–03. A prior green test does not substitute for the final run after the JSON serialization correction.

| Requirement / edge | Observable behavior | Behavioral test evidence |
|---|---|---|
| ANA-01 adjacency | A matching field, occupation and industry code retains separate ten-key identities and field-only profiles | `test_phase3_edge_acceptance.py::test_same_catalog_code_keeps_field_occupation_and_industry_separate` |
| ANA-01 empty | A computed null remains visible; deleting its evaluation blocks construction | `test_analysis_v2.py::test_synthetic_complete_grid_and_canonical_ids`; `::test_missing_computation_blocks_instead_of_becoming_sparse` |
| ANA-01 encoding | Blank and `999999` cannot become named CMPE fields; accepted catalog labels remain attached to field cells | `test_phase3_edge_acceptance.py::test_unknown_cmpe_key_cannot_become_a_named_field`; `test_analysis_v2.py::test_synthetic_complete_grid_and_canonical_ids` |
| ANA-01 ordering | Record and field-catalog permutation preserves every profile cell and public record ID | `test_phase3_edge_acceptance.py::test_reordering_public_records_and_catalog_preserves_entire_profile_grid` |
| ANA-02 boundary | An eight-period series yields seven adjacent and four annual slots; a forged period window cannot authorize reverse time | `test_comparisons_v2.py::test_ledger_has_all_slots_in_stable_order`; `::test_mutated_period_registry_cannot_authorize_a_different_window` |
| ANA-02 adjacency | Adjacent pairs carry seasonality/overlap; annual pairs carry like-quarter/overlap | `test_comparisons_v2.py::test_temporal_pairs_keep_specific_seasonality_and_overlap_limits` |
| ANA-02 empty | Missing quarter endpoints still yield all 11 blocked slots with unique IDs and null deltas | `test_comparisons_v2.py::test_fully_missing_pair_ids_remain_unique_across_series_and_slots` |
| ANA-02 ordering | Reversed input periods and records produce the same chronological slot sequence | `test_comparisons_v2.py::test_ledger_has_all_slots_in_stable_order` |
| ANA-02 precision | Rate change uses percentage points; income uses nominal MXN; zero prior has null relative percent | `test_comparisons_v2.py::test_approved_signatures_and_cross_boundary`; `::test_zero_prior_has_no_relative_percent_and_income_is_nominal` |
| ANA-03 boundary | Changed source, population, sex, concept, metric, unit, basis, method or policy blocks with null deltas | `test_comparisons_v2.py::test_signature_mismatch_blocks`; `::test_missing_version_and_wrong_native_alias_are_blocked`; `::test_geography_concept_cannot_be_coherently_replaced` |
| ANA-03 adjacency | Reviewed `ENT`→`CVE_ENT` code `02` passes; coherent native-alias/catalog tampering blocks | `test_comparisons_v2.py::test_approved_signatures_and_cross_boundary`; `::test_coherent_native_alias_and_catalog_tamper_is_blocked` |
| ANA-03 empty | Suppressed endpoint, missing version or absent fixed entity reference produces blocked reason and null deltas | `test_comparisons_v2.py::test_suppression_and_missing_policy_block`; `::test_missing_reference_emits_blocked_entity_slots` |
| ANA-03 encoding | Old native `ENT` and new `CVE_ENT` retain approved snapshot provenance while normalizing to `02`; a wrong alias is rejected | `test_comparisons_v2.py::test_approved_signatures_and_cross_boundary`; `::test_missing_version_and_wrong_native_alias_are_blocked` |
| ANA-03 ordering | Metadata-key permutation leaves comparison ID and sorted reason set unchanged | `test_comparisons_v2.py::test_reason_and_id_order_are_stable` |
| ANA-03 precision | Ledger omits change SE/p-value and the rotating-sample control rejects invented delta precision | `test_comparisons_v2.py::test_ledger_has_all_slots_in_stable_order`; `phase3_prohibitions_02.test.cjs` p4 |
| ANA-04 boundary | Latest profiles contain every `01`–`32` state and both recorded-sex slots for cohort and three focal fields | `test_analysis_v2.py::test_synthetic_complete_grid_and_canonical_ids`; `phase3_prohibitions_01.test.cjs` p1 |
| ANA-04 adjacency | State and sex sections remain separate; one-axis same-period contrasts pass and second-axis changes block | `test_analysis_v2.py::test_synthetic_complete_grid_and_canonical_ids`; `test_comparisons_v2.py::test_one_axis_slices_require_same_snapshot_and_reference` |
| ANA-04 empty | Sparse state/sex cells stay present, null, reasoned and without weighted/precision diagnostics | `phase3_prohibitions_01.test.cjs` p1; `test_analysis_v2.py::test_profile_redaction_flows_to_downstream_record_index` |
| ANA-04 ordering | Each field has ordered state codes and sex codes, independent of source order | `phase3_prohibitions_01.test.cjs` p1; `test_phase3_edge_acceptance.py::test_reordering_public_records_and_catalog_preserves_entire_profile_grid` |
| ANA-04 precision | A visible cell retains support; complementary suppression clears parent value and uncertainty in the downstream index | `test_phase3_edge_acceptance.py::test_observed_support_is_not_replaced_by_a_weighted_population_estimate`; `test_analysis_v2.py::test_profile_redaction_flows_to_downstream_record_index` |
| ANA-05 boundary | Exact-income response gives null at denominator zero, 50% at partial, 100% at full, and rejects over-response | `test_analysis_v2.py::test_observed_exact_income_response_has_explicit_denominator_and_empty_state` |
| ANA-05 adjacency | Overlapping age/field exclusions remain distinct keyed nonexclusive counts, even when their sum exceeds the responding count | `test_phase3_edge_acceptance.py::test_overlapping_exclusions_survive_audit_permutation_without_additive_total` |
| ANA-05 empty | Zero denominator yields null and `empty_denominator`; missing accepted coverage blocks | `test_analysis_v2.py::test_observed_exact_income_response_has_explicit_denominator_and_empty_state`; `::test_coverage_cannot_change_independently_of_accepted_inputs` |
| ANA-05 ordering | Reordered aggregate-audit entries and exclusion keys leave displayed profile coverage unchanged | `test_phase3_edge_acceptance.py::test_overlapping_exclusions_survive_audit_permutation_without_additive_total` |
| ANA-05 precision | Observed n remains separate from weighted population; complementary totals cannot reveal a suppressed part | `test_phase3_edge_acceptance.py::test_observed_support_is_not_replaced_by_a_weighted_population_estimate`; `test_analysis_v2.py::test_complementary_parent_cannot_reveal_one_suppressed_state` |
| ANA-06 boundary | Zero, one, two and three supported openings succeed; a fourth is rejected | `test_claims_v2.py::test_suppressed_record_and_boundary_selection`; `test_phase3_edge_acceptance.py::test_one_or_two_supported_opening_claims_are_retained` |
| ANA-06 adjacency | Equal displayed values from different fields cannot swap evidence IDs | `test_claims_v2.py::test_equal_values_from_different_fields_are_not_interchangeable` |
| ANA-06 empty | No eligible synthetic claim yields no opening IDs and an explicit empty-finding limitation | `test_analysis_integration.py::test_synthetic_packet_has_complete_public_only_shape` |
| ANA-06 encoding | Exact accented Spanish label and a Cyrillic lookalike substitution are checked; altered prose is rejected | `test_claims_v2.py::test_observation_has_exact_evidence_and_canonical_spanish`; `::test_equal_values_from_different_fields_are_not_interchangeable` |
| ANA-06 ordering | Candidate permutation keeps opening IDs and relevance order; repeated packet assembly is identical | `test_claims_v2.py::test_opening_selection_is_stable_under_reorder_and_uses_distinct_themes`; `test_analysis_integration.py::test_synthetic_packet_has_complete_public_only_shape` |
| ANA-06 precision | Changed typed amount, source/method metadata, invented significance and unsupported prose fail validation | `test_claims_v2.py::test_supported_descriptive_templates_and_exact_metadata`; `::test_observation_has_exact_evidence_and_canonical_spanish`; `phase3_prohibitions_03.test.cjs` p6 |

The six requirement gates are: **ANA-01** accepted eight-snapshot index and expected profiles (`test_analysis_v2.py`, real `test_analysis_integration.py`); **ANA-02** complete descriptive time ledger (`test_comparisons_v2.py`, real packet); **ANA-03** strict signature and reviewed geography controls (`test_comparisons_v2.py`); **ANA-04** full state/sex grids and one-axis contrasts (`test_analysis_v2.py`, `test_comparisons_v2.py`, p1); **ANA-05** denominator, exclusions and disclosure continuity (`test_analysis_v2.py`, new edge tests); **ANA-06** exact claim regeneration, opening selection and strict packet validation (`test_claims_v2.py`, `test_analysis_integration.py`, p5–p7). The real integration must execute, not skip, and must read only accepted aggregate JSON.

The new edge suite ran with `.venv/Scripts/python.exe -m pytest tests/test_phase3_edge_acceptance.py -q`: **8 passed in 4.19 s**. A strengthened collision fixture initially failed its independent coverage pin after two additional evaluated rows; correcting that test fixture yielded the passing run. This was fixture setup, not an implementation assertion failure.

The final `.venv/Scripts/python.exe -m pytest -q` run after the JSON-native comparison-signature correction recorded **443 passed, 0 skipped in 151.46 s** in `.cache/research/phase3-final-controls/junit.xml`. The additional observed-support edge test was added after that run's collection and passed in the focused eight-test run; therefore this is **443 whole-suite passes plus a separate passing focused check**, representing 444 distinct current tests, not a claim of 444 passes in one run. The real accepted-aggregate integration executed in the whole suite. All seven refreshed `.cache/research/phase3-final-controls/p1-proof.json` through `p7-proof.json` have `status: green`, `located: true`, `flagged: false`, and evidence entries with `failFirst: true`, `passed: true`, `failFirstProof: violation-fixture`. The persisted `.cache/research/phase3-analysis/analysis.json` was reloaded and accepted by `validate_analysis_packet` with zero errors; its SHA-256 and content digest stayed unchanged. The direct readback is recorded in `.cache/research/phase3-analysis/persisted-validation.json`. The packet contains 6,739 sanitized records, 4,209 comparison slots, 38 exact claims and three opening IDs, with content digest `d2f28f26f993d052fb5f246db3262ad00b776081a663d608e0427962745a0c79`. No raw ZIP or R estimation was rerun. Independent review in `03-REVIEW.md` closed **CLEAN with zero open findings** after checking comparison signatures, geography evidence, Spanish claims, packet scope and final controls.

## Sign-off

- [x] Phase 2 real numerical acceptance and all eight public v2 roots verified before Phase 3 execution.
- [x] All new focused tests, full suite and real aggregate-only integration pass.
- [x] Thirty-one edge checks have specific evidence; all seven test-tier prohibitions have canonical GSD producer `green`, `located:true`, bad red, clean green and `flagged:false` results.
- [x] Independent reviewer checks all comparison signatures, geography evidence, canonical prose and full expected-cell counts (`03-REVIEW.md`: CLEAN, zero open findings).
- [x] `nyquist_compliant: true` set only after executed behavioral, persisted-readback and prohibition evidence existed.
