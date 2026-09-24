---
phase: 03-supported-labor-findings
verified: 2026-09-23T18:45:13Z
status: passed
score: 42/42 must-haves verified
overrides_applied: 0
---

# Phase 3: Supported Labor Findings Verification Report

**Phase goal:** Readers can explore field and labor patterns across periods and geographies without unsupported differences or claims.
**Verified:** 2026-09-23T18:45:13Z
**Status:** passed
**Re-verification:** No; no prior `03-VERIFICATION.md` existed.

## Goal achievement

The Phase 3 deliverable is a validated, aggregate-only analytical packet for local inspection and Phase 4 consumption. Directly reloading `.cache/research/phase3-analysis/analysis.json` and invoking `validate_analysis_packet` returned **zero errors**. Its file SHA-256 is `9bbb5af3091c4cb02bec98d499ac522d77715f3a1316a30f906364fcc4c6537d`, matching the durable acceptance record. The packet has eight ordered national quarters, 6,739 sanitized public records, 4,209 comparison slots, 38 canonical claims and three supported openings. This verification does not imply that Phase 4 HTML/PDF publication or Phase 5 release exists.

### Roadmap success criteria

| # | Contract | Status | Direct evidence |
| --- | --- | --- | --- |
| 1 | Focal field profiles, total professional cohort, and other identifiable fields | VERIFIED | `build_profiles` constructs eight-quarter national/cohort/focal cells and latest official field slots; persisted packet has 920 national cells, 2,714 latest field cells and 118 named fields. |
| 2 | Eight quarters and descriptive changes only when all comparability and precision conditions permit | VERIFIED | `comparison_signature` and `_result` check pinned source, population, geography, sex, classification, metric, unit, basis, method, suppression and chronology; persisted packet has 805 adjacent and 460 annual slots. All 2,089 blocked pairs have null absolute and relative deltas. |
| 3 | Supported sex/entity differences with visible missingness, response and exclusions | VERIFIED | Packet has 184 recorded-sex cells, 2,944 entity cells, 92 sex contrasts and 2,852 entity contrasts; 3,586 profile appearances are null with reasons. `analysis_v2._coverage` preserves observed denominators and nonexclusive exclusions. |
| 4 | Exact finding lineage and gate against unsupported prose/quantities/advice | VERIFIED | All 38 claims reference present public records; `validate_claim` regenerates every field from typed evidence, and `validate_analysis_packet` rebuilds comparisons, claims, openings and limitations. Seven current prohibition controls pass. |

### Observable truths: Plan 03-01 (18/18)

| # | Must-have truth | Status | Evidence |
| --- | --- | --- | --- |
| 01-01 | Eight quarters provide national 15+, completed professional and three focal profiles with accepted metrics | VERIFIED | `analysis_v2._required_grains`, `build_profiles`; persisted 920 national cells across eight periods. |
| 01-02 | Latest fields, 32 states and two sex slots remain complete with null/reason for unsupported cells | VERIFIED | `build_profiles`; persisted 2,714/2,944/184 cells and 3,586 reasoned null appearances. |
| 01-03 | Missing requested/evaluated Phase 2 computation blocks; actual suppression can be sparse | VERIFIED | `index_public_estimates` compares exact requested, evaluated and public grains, then checks evaluation reason; missing-computation regression in `test_analysis_v2.py`. |
| 01-04 | Support, response, age/field exclusions and income coverage join by explicit keys; weighted values labeled estimates | VERIFIED | `analysis_v2._coverage`, `_cell`, `_observed_response`; edge tests distinguish observed counts from weighted estimates. |
| 01-05 | Shared field/occupation/industry code retains field-of-study identity | VERIFIED | Ten-key `GRAIN` ID and profile selector; `test_same_catalog_code_keeps_field_occupation_and_industry_separate`. |
| 01-06 | Computed suppressed field remains a null; absent computation blocks | VERIFIED | `_cell` requires record; `index_public_estimates` requires evaluation; `test_missing_computation_blocks_instead_of_becoming_sparse`. |
| 01-07 | Official six-digit CMPE labels remain linked; blank/999999 unknown | VERIFIED | Six-digit and sentinel checks in `index_public_estimates`; `test_unknown_cmpe_key_cannot_become_a_named_field`. |
| 01-08 | Record/catalog permutation leaves IDs and grid unchanged | VERIFIED | Canonical grain digest and sorted cells; `test_reordering_public_records_and_catalog_preserves_entire_profile_grid`. |
| 01-09 | Exactly 32 state and two sex selections for each cohort/focal field | VERIFIED | `STATE_CODES`, `SEX_CODES`, partition length checks; current p1 control and persisted sections. |
| 01-10 | State and sex slices stay separate | VERIFIED | Separate `latest_states`/`latest_recorded_sexes` output; one-axis comparator tests. |
| 01-11 | Sparse entity/sex cells keep null, precision state and reason | VERIFIED | `_cell` rejects leaked suppressed diagnostics; current p1 control. |
| 01-12 | State and sex slots sort by canonical codes | VERIFIED | `build_profiles` loops sorted codes; reorder edge test. |
| 01-13 | Visible support retained; sparse cells reveal no hidden denominator/CI | VERIFIED | `_cell` preserves public support, enforces null diagnostics; complementary parent test. |
| 01-14 | Observed and income-response counts use named denominators at zero/full/partial | VERIFIED | `_observed_response` names `occupied_eligible_n`; zero/50%/100% test. |
| 01-15 | Overlapping exclusion categories stay distinct | VERIFIED | `_coverage` copies keyed `counts_nonexclusive`; overlapping-exclusions edge test. |
| 01-16 | Missing audit bucket or zero denominator gives null and reason | VERIFIED | `_coverage` rejects absent accepted bucket; `_observed_response` returns null/`empty_denominator`; focused tests. |
| 01-17 | Exclusion/coverage output stable under audit permutation | VERIFIED | Key sorting in `_coverage`; audit-permutation edge test. |
| 01-18 | Weighted estimates never become observed n; complementary totals do not disclose a suppressed part | VERIFIED | Distinct output fields, `_redact_parent_if_complementary`, sanitized `record_index`; five redacted parent records in saved packet. |

### Observable truths: Plan 03-02 (15/15)

| # | Must-have truth | Status | Evidence |
| --- | --- | --- | --- |
| 02-01 | Eight-quarter series have seven adjacent and four annual slots | VERIFIED | `build_comparison_ledger` iterates offsets 1/4 over authoritative `PERIODS`; 805/460 persisted slots. |
| 02-02 | Only compatible supported endpoints have deltas; blocked pairs retain null/reasons | VERIFIED | `_result` computes delta only if no reasons; direct packet check covers all 2,089 blocked pairs. |
| 02-03 | Reviewed ENT/CVE_ENT cross-boundary comparison can pass, other mismatches block | VERIFIED | Pinned `load_definition_registry`, `_signature`; cross-boundary and coherent-tamper tests. |
| 02-04 | Pair generator uses only q→q+1 and q→q+4 | VERIFIED | Fixed offset loop and `PERIODS`; reversed-window mutation test. |
| 02-05 | Adjacent pairs warn seasonality; annual pairs identify like quarter; no independent-sample claim | VERIFIED | `_result.limitations`, claim `_extra_limit`; temporal caveat tests and p4. |
| 02-06 | Missing quarter keeps a blocked expected pair slot | VERIFIED | `by_key.get` endpoints and stable slot IDs; fully-missing-series test. |
| 02-07 | Shuffled periods/records preserve chronological pair order and IDs | VERIFIED | Authoritative `PERIODS`, sorted series; ledger-order test. |
| 02-08 | Rate changes use points, income nominal, zero prior has null relative percent | VERIFIED | `_result.display_unit` and zero denominator guard; zero-prior/income test and p3. |
| 02-09 | All required signature differences block with null deltas | VERIFIED | `_signature`/`_result` compare pinned source, population, geography, sex, concept, metric, basis, method and policy; mismatch matrix test. |
| 02-10 | ENT/CVE_ENT match requires code, name and reviewed evidence | VERIFIED | Exact catalog/hash/concept pins and name check; coherent alias/catalog mutation test. |
| 02-11 | Missing definition/revision or suppressed endpoint blocks | VERIFIED | `_signature` reasons and `_result` support gate; missing-version/suppression tests. |
| 02-12 | Longitudinal selectors match; cross-slice allows only one declared axis | VERIFIED | `_result(axis)` compares all other signature fields and exact same-period snapshot; one-axis test. |
| 02-13 | Old/new codes normalize to two ASCII digits with provenance retained | VERIFIED | Reviewed 32-row equivalence catalog and native alias fields in `load_definition_registry`; cross-boundary test. |
| 02-14 | Mismatch reasons and endpoint IDs remain deterministic | VERIFIED | Sorted reason set and content-derived IDs; reason/ID-order test. |
| 02-15 | Marginal intervals do not create comparison SE, CI, p-value or significance | VERIFIED | Comparison schema/output only descriptive deltas and limitations; p4 bad fixture rejected. |

### Observable truths: Plan 03-03 (9/9)

| # | Must-have truth | Status | Evidence |
| --- | --- | --- | --- |
| 03-01 | Deterministic packet includes profiles, coverage, ledger, typed claims and ≤3 openings | VERIFIED | `_assemble` followed by `validate_analysis_packet`; saved packet counts 6,739/4,209/38/3. |
| 03-02 | Every claim resolves exact estimates/comparison, snapshots, evidence, method, universe and precision | VERIFIED | `make_claim` stores exact IDs/metadata; `validate_claim` regenerates full equality; saved packet zero errors. |
| 03-03 | No claim uses suppressed/incompatible endpoint, hidden diagnostics, unsupported quantity, causal/significance/advice prose | VERIFIED | `_record` and `make_claim` reject unsupported endpoints; typed prose equality; p5–p7 controls pass. |
| 03-04 | Opening selection accepts 0–3, rejects fourth | VERIFIED | `select_opening_claims` validates `limit`; boundary and 1–2 opening tests. |
| 03-05 | Equal displayed numbers from other grains/units cannot substitute evidence | VERIFIED | Exact ID, grain and source checks; equal-value swapped-field test. |
| 03-06 | No eligible finding yields empty opening and visible limitation | VERIFIED | `_claims` returns empty; `_limitations` appends empty limitation; synthetic packet test. |
| 03-07 | Canonical Spanish labels, accents and units reject altered Unicode/injection | VERIFIED | `make_claim` uses pinned display metadata and `validate_claim` exact equality; lookalike test. |
| 03-08 | Input permutation leaves claim IDs, text and opening choices unchanged | VERIFIED | Digest IDs, sorted candidates and stable selection; ordering tests. |
| 03-09 | Extra numerals, altered precision or false certainty fail | VERIFIED | Full canonical regeneration and schema validation; altered quantity/metadata tests and p6. |

**Score:** 42/42 plan truths verified; 4/4 roadmap criteria verified. No override used.

## Required artifacts and wiring

| Artifact | Level 1/2 | Level 3/4 connection | Verdict |
| --- | --- | --- | --- |
| `brujula/analysis_v2.py` and accepted aggregate fixture/pins | Substantive exact Phase 2 hash, ledger and expected-grain checks | `findings_v2._assemble` calls index then `build_profiles`; saved real packet has complete sections | VERIFIED |
| `brujula/comparisons_v2.py` and `data/catalog/enoe-geography-equivalence.json` | Substantive pinned registry and comparison signatures | `_assemble` passes sanitized profile `record_index` to ledger; validator recomputes all pairs from saved JSON | VERIFIED |
| `brujula/claims_v2.py` | Substantive typed templates and strict equality validator | `_claims` consumes sanitized records and passing ledger IDs; packet validator regenerates all claims | VERIFIED |
| `brujula/findings_v2.py`, `contracts/analysis-v2.schema.json`, `data/fixtures/enoe-analysis-reference.json` | Strict shape and independent hash-only reference | Build validates before return; separate saved JSON reload also validates with zero errors | VERIFIED |
| Tests, golden/reference fixtures and seven bad/clean prohibition subjects from all three plans | Present and substantive; current Node controls directly exercise bad and clean subjects | 7/7 Node controls and 8/8 edge tests passed independently; full-suite JUnit shows 443/443 pass, zero skip | VERIFIED |

The essential data path is **accepted Phase 2 public aggregates → exact grain index → complete profiles and sanitized record index → pinned comparison registry/ledger → typed claims → strict packet validator → persisted JSON**. The Phase 3 packet contains real public aggregates (`synthetic: false`), not static placeholder arrays. `index_public_estimates` checks all eight approved snapshot hashes, requested/evaluated/public grain equality, metric manifest and audit pins before any profile is built. A missing computation cannot masquerade as a null cell. `build_profiles` then carries complementary redaction into the common downstream record index so neither comparisons nor claims can recover five hidden parent values. The packet validator checks schema, content digest, independent source/profile/coverage pins and recalculates comparison and claim output after JSON reload.

## Behavioral spot-checks and probes

| Check | Observed result | Status |
| --- | --- | --- |
| Reload saved `analysis.json`; run `validate_analysis_packet` | 0 errors; file SHA-256 matches durable Phase 3 acceptance; 6,739 records, 4,209 comparisons, 38 claims, 3 openings | PASS |
| Independently inspect every blocked comparison in saved packet | 2,089 blocked; all absolute and relative deltas null | PASS |
| `node --test` across three Phase 3 prohibition files | 7 passed, 0 failed, 0 skipped; direct current execution | PASS |
| `.venv/Scripts/python.exe -m pytest tests/test_phase3_edge_acceptance.py -q` | 8 passed in 3.44 s; direct current execution | PASS |
| Saved full-suite `.cache/research/phase3-final-controls/junit.xml` | 443 tests, 0 failures/errors/skips; one subsequently added edge case passed in focused run | PASS (prior unchanged source run) |
| Seven canonical `p1-proof.json`–`p7-proof.json` | Each `green`, `located:true`, `flagged:false`, bad fixture red and clean fixture green | PASS |

No Phase 3 plan declares a shell `probe-*.sh`, and no conventional `scripts/*/tests/probe-*.sh` exists. The seven explicit test-tier prohibitions are the phase probes and were executed above, rather than inferred from summary claims.

## Requirements coverage

| Requirement | Plans | Status | Evidence |
| --- | --- | --- | --- |
| ANA-01 | 01, 03 | SATISFIED | Eight-quarter index, three focal profiles, total cohort, 118 official named fields; exact public records. |
| ANA-02 | 02, 03 | SATISFIED | 805 adjacent and 460 annual ordered slots; overlap/seasonality limits and no invented significance. |
| ANA-03 | 02, 03 | SATISFIED | Pinned comparison signatures and conditional reviewed state equivalence; incompatible/sparse endpoints yield null deltas. |
| ANA-04 | 01, 02, 03 | SATISFIED | Full latest state/recorded-sex grids and separate one-axis contrasts, with visible nulls. |
| ANA-05 | 01, 03 | SATISFIED | Observed support and exact-income denominators, nonexclusive exclusions, precision and complementary disclosure guard. |
| ANA-06 | 03 | SATISFIED | Exact evidence-bound canonical claims, strict schema/reference validation and seven prohibition checks. |

All six requirements mapped to Phase 3 in `REQUIREMENTS.md` appear in plan frontmatter. No orphaned Phase 3 requirement was found.

## Anti-patterns, human checks and scope

No unreferenced `TBD`, `FIXME` or `XXX` marker was found in the Phase 3 implementation files, schema or plans. The one `return []` in `claims_v2.validate_claim` is the normal successful validation result after exact equality, not a stub. The full suite JUnit, clean independent `03-REVIEW.md`, `03-SECURITY.md` (15 closed, zero open), and Nyquist map (31/31) corroborate the direct source/packet checks; they were not used as substitutes for them.

No Phase 3 analytical truth remains uncertain or requires human verification. Visual design, printable output, public exports, replay/current promotion and release are explicitly Phase 4/5 success criteria, so their absence is outside this phase goal. The stored analytical packet is a validated local handoff, not a claim of public release.

## Gaps summary

None. The previously reported coherent geography tamper and persisted JSON tuple/list defects are closed in current source and exercised by affected tests and saved-packet readback. No override, deferral or human decision is needed for Phase 3 analytical acceptance.

---

_Verified: 2026-09-23T18:45:13Z_  
_Verifier: gsd-verifier goal-backward check_ 
