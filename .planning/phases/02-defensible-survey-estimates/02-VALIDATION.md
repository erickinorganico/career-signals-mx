---
phase: 2
slug: defensible-survey-estimates
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-09-22
---

# Phase 2 — Validation Strategy

## Test Infrastructure

pytest 9.0.3 on Python 3.12.13; configuration in `pyproject.toml`.
Quick command: `.venv/Scripts/python.exe -m pytest tests/test_survey.py -q`.
Full command: `.venv/Scripts/python.exe -m pytest -q`.
Real integration runs offline against eight cached pinned ZIPs; R is a separate numerical oracle, not a requirement for ordinary Python fixture tests.

## Sampling Rate

Run affected tests after each task, full suite after each wave, then the real adapter/R/official phase gate. Keep focused synthetic feedback under 60 seconds. Capture actual integration durations separately; do not replace a real acceptance check with a fixture.

## Per-Task Verification Map

Each group is assigned to an executable plan/task. Phase 2 execution begins only after Phase 1 verification, including the completed v2 projection.

| Verification group | Requirements | Automated command or evidence | Initial state |
|---|---|---|---|
| Strict frame, aliases, lexical states and full design | STAT-01, STAT-06 | 02-01 Task 1: `pytest tests/test_enoe_adapter.py -q`; eight offline snapshots with source/member hashes and aggregate-only row/code counts | tests to create |
| Metric numerators, denominators and sentinels | STAT-06 | 02-01 Task 2: `pytest tests/test_enoe_metrics.py -q`; CLASE1 PEA versus CLASE2 occupied, SUB_O/occupied, and DUR9C/HRSOCUP regression | tests to create |
| Support, suppression and strict v2 projection | STAT-02, STAT-03 | 02-02 Tasks 1–2: `pytest tests/test_survey.py tests/test_estimates.py tests/test_research_contract.py -q`; serialized suppression sentinels | survey exists; additions pending |
| Independent numerical oracle | STAT-04 | 02-03 Task 1: `pytest tests/test_survey_oracle.py -q`; explicit offline R replay with pinned versions/options and signed point/SE ledger | tests/script to create |
| Official point and precision reconciliation | STAT-05 | 02-03 Task 2: `pytest tests/test_official_reconciliation.py -q`; six exact counts, separate rate rounding intervals and raw precision differences | tests/script to create |
| Complete eight-period accepted estimates | STAT-01–06 | 02-03 Task 3: `pytest tests/test_enoe_integration.py -q`; then `.venv/Scripts/python.exe scripts/accept_enoe_estimates.py --output-root artifacts/enoe --audit-dir .cache/research/phase2-acceptance` against the approved local acquisition root | to create |
| Complete Phase 3 request coverage | STAT-01–06 | 02-02 Task 2 and 02-03 Task 3: compare requested/evaluated/record grain sets for every metric in eight-quarter national context/cohort/focal three; latest national catalog-verified identifiable fields; latest 32 entities and two recorded-sex slices for cohort and each focal field separately. An absent computation or fabricated n<30 null fails. | tests and acceptance gate to create |
| Phase 2 operational prohibitions | STAT-01–06 | 02-01 T3, 02-02 T3 and 02-03 T3: `node --test tests/phase2_prohibitions_01.test.cjs`, `_02.test.cjs`, `_03.test.cjs`; canonical `check prohibition-enforcement` for each of seven projected descriptors with bad and clean subjects | tests/fixtures to create; not yet green |

## Wave 0 Requirements

- Create reusable synthetic frame fixtures with adequate n, two or more contributing PSUs, zero-domain PSUs, singleton handling, unknown/sentinel codes, PEA versus occupied distinction and explicit source metadata.
- Preserve the completed raw lexeme audit. Only ASCII-space normalization is permitted. The occupied/PEA audit correction passed all eight snapshots; encode that regression in the adapter. Hours zero with DUR9C=1 and DUR9C=9 must take different eligibility paths.
- Inspect the verified Phase 1 public projection before execution. The signatures are `validate_research_v2(payload)`, `validate_public_research_v2(payload)`, and `public_research_projection(payload)`; Phase 1's own prohibition controls are separate evidence, not Phase 2 numerical acceptance.
- Version the oracle/reconciliation code and aggregate expected values; ignored prototype files alone do not satisfy reproducibility.

## Acceptance Rules

- Python/R tolerance declared in advance: rtol=1e-10 and atol=1e-8 for point estimates and standard errors. Cover national controls, all three focal fields and an entity, including totals, rates and positive-known nominal income.
- Official exact totals and official source rounding are different checks. Keep the original raw discrepancies; never widen tolerance to hide differences in standard errors.
- The singleton adjustment remains a project approximation, not official precision. A supported REVIEW value is allowed; unavailable precision and suppressed values remain visibly unavailable.
- No effective-n claim, person-level output, independent-quarter significance claim or suppressed-number fallback is permitted. Capture stdout/stderr/loggers and content-scan tracked/packaged data artifacts for person-record structures, using disposable synthetic bad-surface controls rather than source-text keyword matching.
- Reviewer checks metric meanings and independent calculation setup, including denominator coverage, official edition identity and raw/cohort exclusions.

## Security and Negative Controls

Malformed required codes/weights, unexpected aliases, duplicate/missing headers and source custody failures must stop ingestion. Strict v2 refs must reject inconsistent sources, periods and methods. Public projection must remove all value-derived precision and weighted totals for suppressed cells while retaining unweighted coverage. Fixtures never access production.

## Validation Sign-Off

- [ ] Every implemented task has a concrete automated check and traced requirement.
- [ ] No three consecutive tasks lack verification.
- [ ] All referenced tests exist and pass.
- [ ] Eight pinned snapshots pass the real adapter audit.
- [ ] Every Phase 3 requested metric/cell has a real evaluated estimate or computed support/suppression metadata; exact request/evaluation/record sets agree, and a missing computation never appears as a fabricated sparse null.
- [ ] Final-cohort R replay passes with original tolerances.
- [ ] Official counts reconcile; rate rounding and precision discrepancies remain explicit.
- [ ] Full regression and strict v2 public validation pass.
- [ ] Independent review confirms metric and design semantics.
- [ ] Seven Phase 2 test-tier prohibitions are located and green under the canonical GSD producer, each with non-vacuous current pass, machine-proven bad-fixture red and clean-fixture green. Missing or failing planned controls block canonical completion.
- [ ] `nyquist_compliant: true` set only after evidence exists.

## Edge Candidate Acceptance Map

The 30 applicable probes in `02-EDGE-PROBE.json` are lifted into explicit flat-string `must_haves.truths`: 11 in 02-01, 9 in 02-02, and 10 in 02-03. The table maps each truth to its required test. No probe is considered satisfied merely by appearing in a plan.

| Requirement | Boundary | Adjacency | Empty | Ordering | Encoding | Precision |
|---|---|---|---|---|---|---|
| STAT-01 | 02-01/T1: R_DEF 0/00, EDA 14/15/97/98/99, positive FAC_TRI | 02-01/T1: same PSU in same stratum merges; PSU ID shared across strata remains distinct | 02-01/T1: zero/one valid design row fails | 02-01/T1: reordered rows preserve frame counts/support | — | 02-01/T1: ASCII-space trim only; weight overflow/nonfinite fails |
| STAT-02 | 02-02/T1: n 29/30, PSU 1/2, CV 15/30 | 02-02/T1: exactly 15 enters REVIEW; exactly 30 suppresses | 02-02/T1: null estimate/SE and zero-support design | 02-02/T1: stable reason order | — | 02-02/T1: IC90 normal versus logit delta; finite endpoints |
| STAT-03 | 02-02/T1–2: 0/100 proportion and SE zero suppress | — | 02-02/T2: null value with reason; no diagnostic fallback | — | 02-02/T2: nested serialized JSON sentinel cannot bypass allowlist | 02-02/T2: estimate/denominator/SE/CI sentinels absent publicly |
| STAT-04 | 02-03/T1: rtol=1e-10, atol=1e-8 pass/fail neighbors | 02-03/T1: 2026-Q2 known-age 97/98 cohort split | 02-03/T1: missing oracle case fails | 02-03/T1: reordered oracle cases preserve IDs/verdict | — | 02-03/T1: signed point and SE errors recorded before tolerance test |
| STAT-05 | 02-03/T2: six counts exact and four-decimal rate half-unit interval | 02-03/T2: exact rounding endpoints versus just outside | 02-03/T2: absent official cell/hash fails | 02-03/T2: reordered workbook rows match by key | — | 02-03/T2: untuned raw signed/relative official SE discrepancy |
| STAT-06 | 02-01/T2: INGOCUP 0/1/999998/999999, HRSOCUP 0/1/168/169 | 02-01/T2: SUB_O=1 occupied-only; DUR9C 1 versus 9 at hours zero | 02-01/T2: no known income/hours denominator yields null | 02-01/T2: metric records and category counts order stable | 02-01/T2: only ASCII digits/U+0020, six-digit CMPE catalog membership | 02-01/T2: no zero imputation; stable weighted numerator/denominator values |

## Four-Source Coverage Audit

| Source | Item | Plan | Status |
|---|---|---|---|
| GOAL | Supported estimates distinguished from imprecise/unverified cells | 02-01–03 | COVERED |
| REQ | STAT-01 full design and totals/ratios/means | 02-01–03 | COVERED |
| REQ | STAT-02 support, SE, IC90, CV and singleton state | 02-02–03 | COVERED |
| REQ | STAT-03 suppression and null reason | 02-02–03 | COVERED |
| REQ | STAT-04 independent R survey point/SE | 02-03 | COVERED |
| REQ | STAT-05 official national/entity points and precision | 02-03 | COVERED |
| REQ | STAT-06 all named labor metrics and sentinel rules | 02-01–03 | COVERED |
| RESEARCH | Exact member/hash, full frame, U+0020 lexemes, period codes | 02-01 | COVERED |
| RESEARCH | NumPy direct dependency; installed local runtime | 02-01 | COVERED |
| RESEARCH | Taylor singleton adjust, support and suppression | 02-02 | COVERED |
| RESEARCH | Final known-age R oracle, official ledger, eight-quarter gate | 02-03 | COVERED |
| CONTEXT | Full-frame/resident design, population/CMPE rules, local person rows | 02-01 | COVERED |
| CONTEXT | All metric denominators, including SUB_O and DUR9C exceptions | 02-01 | COVERED |
| CONTEXT | Project approximate precision, review and central projection | 02-02 | COVERED |
| CONTEXT | Original Python/R tolerance and official discrepancies | 02-03 | COVERED |

`02-CONTEXT.md` has no D-NN IDs; its implementation decisions are mapped by subject above. Deferred Phase 3 findings and Phase 4 publication/CLI are excluded as specified, with no feature loss inside STAT-01–06.

The three plans carry seven operational prohibitions under `must_haves.prohibitions` as flat `statement`, `status: resolved`, `verification: test`, `check_kind: node-test`, `check_target`, `check_violation_fixture`, and `check_clean_fixture` scalars. The targets and JSON subjects are explicitly owned by executable tasks and will exercise current API outputs; they are **planned paths**, not present or green checks. The shared `projectProhibitions`/`descriptorFromProjection` contract makes the canonical producer locate them deterministically. Until implementation proves current/clean green and the known-bad subject red, `dispositionForProhibition` remains flagged-unverified and canonical phase completion is blocked. No descriptor merely attests success. Each plan names its output functions, fields, flags and artifact paths in `<artifacts_created>`.
