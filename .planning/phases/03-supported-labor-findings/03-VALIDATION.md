---
phase: 3
slug: supported-labor-findings
status: planned
nyquist_compliant: false
wave_0_complete: false
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

## Sign-off

- [ ] Phase 2 real numerical acceptance and all eight public v2 roots verified before Phase 3 execution.
- [ ] All new focused tests, full suite and real aggregate-only integration pass.
- [ ] Thirty-one edge checks have specific evidence; all seven test-tier prohibitions have canonical GSD producer `green`, `located:true`, bad red, clean green and `flagged:false` results. Missing or failing controls block completion.
- [ ] Independent reviewer checks all comparison signatures, geography evidence, canonical prose and full expected-cell counts.
- [ ] `nyquist_compliant: true` only after implementation evidence exists.
