---
phase: 02-defensible-survey-estimates
verified: 2026-09-23T16:23:42Z
status: passed
score: 43/43 must-haves verified
overrides_applied: 0
---

# Phase 2: Defensible Survey Estimates Verification Report

**Phase goal:** Analysts can distinguish supported real-data survey estimates from imprecise or unverified cells.
**Status:** passed. **Re-verification:** No; no prior `02-VERIFICATION.md` existed.

## Goal achievement

The four non-negotiable ROADMAP success criteria are verified against implementation and current, sealed numerical evidence. The 43 additional PLAN truths are individually accounted for below; the roadmap wording governs where the plans elaborate the same outcome. No override, deferred item, or human-only test was needed. The Phase 2 output is local aggregate research evidence, not a Phase 4 publication or an official INEGI precision claim.

| Roadmap criterion | Status | Direct evidence |
|---|---|---|
| Complete-design national and domain totals, proportions, means, with explicit metric eligibility | VERIFIED | `brujula/enoe_adapter.py:154` binds approved ZIP/member/dictionary and builds all response/resident rows before domains. `brujula/metrics.py:157` constructs 23 full-length metric vectors; `brujula/estimates.py:228` evaluates each domain/metric on one `SurveyDesign`. Eight current quarter ledgers contain 6,739 evaluated cells with exact requested/evaluated/record sets. |
| Observed support, Taylor precision, singleton policy, and nonofficial provenance are exposed | VERIFIED | `brujula/survey.py:37` retains full stratum/PSU design and computes design df, domain support, SE, CV, and IC90; `brujula/estimates.py:177` maps them to strict v2 fields. All 6,739 public records have `official_precision=false`; official ledger retains a national-population SE relative difference of `-0.0037148696737544095`. |
| Unsupported or imprecise values are null with a reason, never a fabricated zero or effective-n claim | VERIFIED | `brujula/survey.py:124` gates n<30, fewer than two contributing UPM, zero design df/denominator/SE, degenerate CI, boundary proportions and CV>=30. `brujula/research_contract.py:232` allowlists public fields and clears suppressed diagnostics. Direct strict-schema inspection of all saved public files found 3,560 suppressed rows with reasons and null numeric diagnostics; 3,179 visible rows passed the precision contract. |
| Independent R and compatible official comparisons are inspectable with untuned differences | VERIFIED | `scripts/enoe_survey_oracle.R:16` builds a separate `survey::svydesign`; `scripts/accept_enoe_estimates.py:467` executes 26 real cases and four analytic controls at `rtol=1e-10`, `atol=1e-8`. `scripts/official_reconciliation.py:104` retains signed/relative official SE discrepancies. Both sealed attempts, official workbook and 2026-Q2 PDF checks are PASS. |

### PLAN truth ledger

Each row resolves one PLAN frontmatter truth. Test names and source paths are evidence pointers, not SUMMARY claims.

| Plan / truth | Status | Evidence |
|---|---|---|
| 01/1 complete responding, resident frame before restrictions | VERIFIED | `load_snapshot_frame` retains full design; `test_enoe_adapter.py`; eight real aggregate frame audits. |
| 01/2 versioned numerators, denominators, units, nonresponse, sentinels | VERIFIED | `data/catalog/enoe-metrics.json`, `metric_vectors`, `test_enoe_metrics.py`. |
| 01/3 failed current/member/hash/code blocks with aggregate diagnostics | VERIFIED | `inventory_snapshot` + `resolve_snapshot` at adapter lines 156–182 and 256; malformed-source tests. |
| 01/4 R_DEF, EDA and positive FAC_TRI boundaries | VERIFIED | Adapter lexing and weight checks; boundary tests in `test_enoe_adapter.py`. |
| 01/5 PSU label nesting by stratum | VERIFIED | Pair-based design clusters in adapter and `SurveyDesign`; adjacency tests. |
| 01/6 empty/single-row frame fails | VERIFIED | Adapter lines 238–255 and empty-frame tests. |
| 01/7 row permutation preserves frame counts/support | VERIFIED | Aggregate counts and pair sets; ordering tests. |
| 01/8 ASCII-space lexical rule and finite weights | VERIFIED | `_lex` and FAC_TRI checks; precision/overflow tests. |
| 01/9 income and hours boundary codes | VERIFIED | `_states`/`metric_vectors`; INGOCUP and HRSOCUP tests. |
| 01/10 SUB_O occupied-only and DUR9C hours-zero distinction | VERIFIED | Metric states; corrected semantic baseline checked for all eight snapshots. |
| 01/11 empty income/hours denominator stays unavailable | VERIFIED | `metric_vectors` coverage and `SurveyDesign.ratio`; empty-denominator tests. |
| 01/12 ASCII numeric and catalog-bound CMPE normalization | VERIFIED | Adapter `_lex`/`_cmpe_key`, dictionary binding, code tests. |
| 01/13 row ordering preserves metric/category identities | VERIFIED | ID-sorted manifest and grain records; ordering tests. |
| 01/14 sentinels never impute zero; finite reproducible vectors | VERIFIED | `metric_vectors` finite checks and sentinel tests. |
| 01/15 no person rows in audits, streams, or packaged artifacts | VERIFIED | Node p1 current and five injected bad-surface tests; aggregate-only audit shape. |
| 02/1 full-design estimate and every support/precision field | VERIFIED | `SurveyDesign` full-frame construction and `_record`; `test_survey.py`, `test_estimates.py`. |
| 02/2 singleton adjustment remains REVIEW and nonofficial | VERIFIED | `SurveyDesign._result`; p3 Node negative control and public readback. |
| 02/3 unsupported public null; diagnostic confined internally | VERIFIED | Strict projection allowlist; p4 Node negative and direct 6,739-row public validation. |
| 02/4 n=29/30, PSU=1/2 and CV=15/30 boundaries | VERIFIED | `SurveyDesign._result`; threshold tests. |
| 02/5 adjacent CV thresholds | VERIFIED | CV branch and boundary-neighbor tests in `test_survey.py`. |
| 02/6 absent estimate/SE or zero support remains null | VERIFIED | Zero-denominator and missing-SE paths; empty-support tests. |
| 02/7 deterministic concurrent reason order | VERIFIED | Ordered reason collection in `_result`; reason-order tests. |
| 02/8 finite normal/logit-delta IC90 | VERIFIED | `SurveyDesign._result` interval branches; interval tests. |
| 02/9 0/100 proportions and zero SE suppress | VERIFIED | Boundary/zero-variance branches; boundary tests. |
| 02/10 null public value has cause, no diagnostic fallback | VERIFIED | `_record`, strict projection and direct suppressed-row inspection. |
| 02/11 nested/serialized sentinels cannot bypass projection | VERIFIED | Allowlisted projection and sentinel tests/p4 negative control. |
| 02/12 suppressed weighted and precision diagnostics null | VERIFIED | Projection lines 259–267; direct check of all 3,560 suppressed public rows. |
| 02/13 complete eight-quarter plus latest entity/sex request inventory | VERIFIED | `required_estimation_domains`, independent `expected_acceptance_domains`; latest 5,911 cells. |
| 02/14 every request genuinely evaluated or suppressed | VERIFIED | `requested_cells`, `evaluated_cells`, strict grain comparison and mutation tests. |
| 03/1 independent R real and analytic points/SE at declared tolerance | VERIFIED | 26 real + four analytic PASS in both current manifests; versioned R code. |
| 03/2 compatible 2025-Q2 national/BC official cells and raw SE | VERIFIED | Pinned workbook SHA, eight keyed cells, official ledger PASS/precision REVIEW. |
| 03/3 eight strict internal/public aggregates and aggregate evidence | VERIFIED | Eight saved public files independently validated; 6,739 records. |
| 03/4 tolerance boundary/neighbor verdicts | VERIFIED | `compare_oracle_cases`; `test_survey_oracle.py`. |
| 03/5 age 97 included/98 excluded in final cohort | VERIFIED | R oracle population branch, Python population selector, final focal cases and tests. |
| 03/6 absent/duplicate R case fails | VERIFIED | Keyed comparison and missing/duplicate tests. |
| 03/7 case permutation preserves verdict | VERIFIED | Keyed oracle ledger and ordering test. |
| 03/8 signed point/SE errors precede tolerance; nonfinite fails | VERIFIED | Oracle comparison ledger and nonfinite tests. |
| 03/9 exact six official counts, rate rounding interval | VERIFIED | `compare_official_cells`, workbook ledger and official tests. |
| 03/10 rounding endpoint/neighbor verdicts | VERIFIED | `test_official_reconciliation.py` boundary tests. |
| 03/11 absent official cell/hash fails | VERIFIED | Workbook/source guards and missing-cell tests. |
| 03/12 keyed comparison stable under workbook row permutation | VERIFIED | Keyed workbook parser and ordering test. |
| 03/13 every official SE retains untuned signed/relative difference | VERIFIED | Eight official cells expose both differences; national population discrepancy remains nonzero. |
| 03/14 complete real request/evaluation/domain grain inventory | VERIFIED | Independent domain inventory, exact grain comparison, eight PASS ledgers; 6,739 cells. |

**Score:** 43/43 plan truths verified; all four roadmap success criteria verified.

## Required artifacts and wiring

| Artifact or link | Level 1/2/3 result | Evidence |
|---|---|---|
| `brujula/enoe_adapter.py` → `brujula/source_inventory.py` | VERIFIED | Substantive frame loader calls inventory and resolve before/after ZIP stream; source/member hashes and current receipt are checked. |
| `brujula/metrics.py` → `brujula/populations.py` and `data/catalog/enoe-metrics.json` | VERIFIED | Population IDs/selectors, period dictionary binding and all 23 metric operations are used in evaluated cells. |
| `brujula/survey.py` → `brujula/estimates.py` | VERIFIED | One full-frame design per snapshot; metric vectors feed total/ratio, result fields populate each v2 record. |
| `brujula/estimates.py` → `brujula/research_contract.py` | VERIFIED | Internal validation, central public projection and public validation are all invoked before return. |
| `scripts/accept_enoe_estimates.py` → adapter/estimates/R/official modules | VERIFIED | Eight approved snapshots load once each; exact domain/grain checks, R and official comparisons gate PASS. |
| `scripts/enoe_survey_oracle.R` | VERIFIED | Independent `survey` implementation runs from aggregate-only case specification and ignored local frame, returns point/SE ledger. |
| `scripts/official_reconciliation.py` → pinned golden/source/workbook/PDF | VERIFIED | Source/workbook/PDF hashes and period/universe/method checks precede keyed comparisons. |
| `data/fixtures/enoe-aggregate-golden.json` | VERIFIED | Eight public and eight internal canonical hashes; initialization cannot overwrite an existing pin. |
| Three Node prohibition suites and fixture subjects | VERIFIED | Seven canonical proof JSONs show `green`, `flagged=false`, `located=true`, bad-fixture fail-first; independent run 12/12 PASS. |
| Python adapter/metric/survey/estimate/oracle/official/integration tests | VERIFIED | Substantive boundary and negative tests are used; independently rerun oracle/official/integration slice 30/30 PASS. |

### Data-flow and numerical custody

The flow is pinned ENOE ZIP/member → complete in-memory frame → catalog-bound full-length metric vectors → full-design Taylor estimate → strict internal v2 → allowlisted public v2 → saved aggregate ledger. The public files are dynamic outputs of the eight source snapshots, not static placeholders. `current.json` equals the final replay manifest and points to attempt `45fe0738-b981-4c9c-852b-28545bf4a9bf`; the initialization receipt is a distinct PASS attempt `05dd6471-58a8-474e-8202-2a4b2a57d9fc`.

An independent readback asserted both PASS manifests have the same combined numerical digest `8db575e9d664864d1513e3b9658bd9b060c4cb3bed8b51561f208adeb97b9a00`, the same 11 code SHA-256 values as live files, and matching metric manifest, eight quarter counts, numeric digests, public-content hashes, internal-content hashes and exact public-file digests. Every saved public file's canonical content matches its golden pin. Quarter counts are 115, 115, 115, 138, 115, 115, 115 and 5,911, totaling 6,739. The replay duration includes an extended 2025-Q2 clock interval and is not a performance benchmark.

## Behavioral checks and probes

| Check | Observed result |
|---|---|
| `pytest tests/test_survey_oracle.py tests/test_official_reconciliation.py tests/test_enoe_integration.py -q` | 30 passed, exit 0. |
| `node --test tests/phase2_prohibitions_01.test.cjs tests/phase2_prohibitions_02.test.cjs tests/phase2_prohibitions_03.test.cjs` | 12 passed, exit 0. |
| Direct strict public-schema validation of eight saved files | 6,739 valid records; 3,179 visible; 3,560 suppressed with reason and null weighted/precision diagnostics; no `estimate` key. |
| Seven canonical GSD prohibition proof files | All `green`, located, unflagged, with violation-fixture fail-first evidence. |
| Final initialization and unchanged replay | Both PASS, distinct attempt IDs, identical numeric content and source hashes. R real 26/26, analytic 4/4, official workbook and PDF PASS. |

No `probe-*.sh` path is declared by these plans or present under this phase's scripts; the declared runnable gates are the R/official acceptance command and canonical GSD prohibition producer, whose current receipts and proof files were checked. The root full regression had 366 Python tests with no skips and 18 Node tests passing; this verifier independently reran only the focused slice above. No server or service was started.

## Requirements coverage

| Requirement | Status | Evidence |
|---|---|---|
| STAT-01 complete FAC_TRI/EST_D_TRI/UPM design, totals/ratios/means | SATISFIED | Adapter, `SurveyDesign`, eight real ledgers and R comparison. |
| STAT-02 support/precision/singleton provenance | SATISFIED | `_result`, v2 records, threshold tests and public readback. |
| STAT-03 suppression and no effective-n claim | SATISFIED | Precision gate, strict projection, 3,560 null public rows and p4 negative control. |
| STAT-04 independent R point/SE, analytic controls | SATISFIED | Both current manifests: 26 real and four analytic cases PASS at declared tolerance. |
| STAT-05 compatible official national/entity points and precision | SATISFIED | 2025-Q2 pinned workbook eight keyed cells including Baja California; six counts exact, two rates within original interval, raw SE differences retained; 2026-Q2 PDF counts PASS. |
| STAT-06 named labor metrics and sentinel rules | SATISFIED | 23-definition metric catalog, vector operations, unit/denominator/sentinel tests and eight-quarter semantic baseline. |

All six requirement IDs appear in PLAN frontmatter and ROADMAP Phase 2 mapping. No orphaned Phase 2 requirement was found. Later Phase 3 findings and Phase 4 publication are separate roadmap outcomes; none is needed to excuse a Phase 2 gap.

## Anti-pattern and human review disposition

No `TBD`, `FIXME`, `XXX`, disabled requirement test, placeholder implementation, empty handler, or hardcoded empty public data source was found in Phase 2 source and test files. Seven test-tier prohibitions have non-vacuous current, bad-fixture and clean-fixture evidence. The implementation explicitly labels singleton-adjusted precision as a project approximation; matching R does not certify official INEGI SE. The compatible official ledger's nonzero SE discrepancies remain visible under `precision_status=REVIEW`.

No human verification item remains for this local, nonvisual batch phase: source identity, metric semantics, suppression, numerical reproduction and official differences have executable or directly inspectable evidence. This status does not assert the separate Phase 3 report, Phase 4 release surface, or Phase 5 publication gates.

---

_Verified: 2026-09-23T16:23:42Z_
_Verifier: gsd-verifier_
