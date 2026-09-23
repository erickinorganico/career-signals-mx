---
phase: 1
slug: official-sources-and-research-contract
status: validated
nyquist_compliant: true
wave_0_complete: true
created: 2026-09-22
---

# Phase 1 — Validation Strategy

## Test Infrastructure

| Property | Value |
|---|---|
| Framework | pytest 9.0.3, Python 3.12.13 |
| Config | pyproject.toml |
| Quick command | `.venv/Scripts/python.exe -m pytest tests/test_acquisition.py tests/test_quality.py -q` |
| Full suite | `.venv/Scripts/python.exe -m pytest -q` |
| Expected latency | Focused fixtures <60 seconds; offline ZIP inventory measured separately |

## Sampling Rate

After each task run its affected tests. After each plan wave and before phase verification run the full suite. Tests use disposable synthetic fixtures; actual ZIP inventory is a separate offline integration check and never enters CI as person data.

## Per-Task Verification Map

All listed files now exist. All six task checks are COVERED and pass in the final full regression at `0eec8c6`: 254 tests passed in 54.84 seconds, with no skip. The rows below preserve the original plan-time existence/status record; the final audit table supersedes those pending labels.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---|---|---|---|---|---|---|---|---|---|
| 01-01-T1 | 01-01 | 1 | SRC-01, SRC-02, SRC-03 | T-01-01, T-01-03, T-01-04 | Tampered/failed current, ambiguous members and concurrent attempts cannot resolve | unit + offline integration | `.venv/Scripts/python.exe -m pytest tests/test_acquisition.py tests/test_source_inventory.py -q` | acquisition yes; inventory no | pending |
| 01-01-T2 | 01-01 | 1 | SRC-03, SRC-04 | T-01-02 | Exact revisions/provenance; only metadata public | unit + offline integration | `.venv/Scripts/python.exe -m pytest tests/test_source_inventory.py -q` | no | pending |
| 01-02-T1 | 01-02 | 1 | CTR-02 | T-02-01, T-02-03 | Response, residence, age and education exclusions stay distinct | unit | `.venv/Scripts/python.exe -m pytest tests/test_population_rules.py -q` | no | pending |
| 01-02-T2 | 01-02 | 1 | CTR-02 | T-02-02, T-02-04 | Unknown field/income and weighted denominator do not become false zero | unit + survey regression | `.venv/Scripts/python.exe -m pytest tests/test_population_rules.py tests/test_survey.py -q` | survey yes; population no | pending |
| 01-03-T1 | 01-03 | 2 | CTR-01, CTR-02 | T-03-01, T-03-03 | Strict internal refs/grain and imported population definitions | unit + v1 regression | `.venv/Scripts/python.exe -m pytest tests/test_research_contract.py tests/test_quality.py tests/test_data.py -q` | v1 yes; v2 no | pending |
| 01-03-T2 | 01-03 | 2 | CTR-01 | T-03-02, T-03-04 | Separate strict public schema; suppressed diagnostics and equivalent weighted/support totals absent | unit + v1 regression | `.venv/Scripts/python.exe -m pytest tests/test_research_contract.py tests/test_quality.py tests/test_data.py -q` | v1 yes; v2 no | pending |

## Wave 0 Requirements

- Create meaningful synthetic fixtures and assertions in `tests/test_source_inventory.py`, `tests/test_research_contract.py`, `tests/test_population_rules.py` with the implementation tasks. Do not create placeholder tests merely to fill the checklist.
- Existing pytest infrastructure requires no installation.

## Manual-Only Verifications

Review the eight generated inventories against package paths, aliases and 2024 revision metadata in `01-RESEARCH.md`; automated integration must call `inventory_all(Path('artifacts/enoe'))` and verify full member hashes and counts. Review semantic rules against the cited INEGI dictionaries. Numerical estimates and precision acceptance are Phase 2 gates. `01-03` runs in wave 2 after `01-02`, because its validator imports the population definitions.

## Validation Sign-Off

- [x] Every task has an automated verification command.
- [x] No three consecutive tasks lack verification.
- [x] New test references exist and pass after execution.
- [x] No watch flags; focused fixture feedback <60 seconds.
- [x] Actual eight-package inventory passed offline.
- [x] Full v1/v2 regression suite passed.
- [x] `nyquist_compliant: true` set only after verification.

Approval: validation coverage verified 2026-09-22; independent phase-goal acceptance remains separate.

## Validation Audit 2026-09-22

| Task | Requirement | Final status | Behavioral evidence |
|---|---|---|---|
| 01-01-T1 | SRC-01/02/03 | COVERED | acquisition/inventory corruption, failure, latest-attempt, exact member and eight-cache tests |
| 01-01-T2 | SRC-03/04 | COVERED | revision log, catalog/dictionary hashes, provenance and metadata-only inventory fixtures |
| 01-02-T1 | CTR-02 | COVERED | response/resident/age/education/field exclusion parameterized tests |
| 01-02-T2 | CTR-02 | COVERED | separate observed/weighted denominators; income sentinel, overflow and invalid-weight tests |
| 01-03-T1 | CTR-01/02 | COVERED | schema/ref/grain/period/nonfinite/support/CV negative tests plus v1 regression |
| 01-03-T2 | CTR-01 | COVERED | public-schema suppression and serialized reason/sentinel negative tests |

Coverage review found no missing automated task checks after the five independent code-review fixes; zero gaps require a Nyquist test-generation agent. Full command: `.venv/Scripts/python.exe -m pytest -q`; **254 passed, 0 skipped, 1 expected duplicate-ZIP fixture warning** in 54.84 seconds. The eight real pinned source inventories ran offline within that suite. The existing semantic research/dictionary review supports definitions, not numerical inference; numerical and final public-output acceptance remain later-phase gates.

## Gap-plan validation

01-04 adds two tasks: executable controls and canonical descriptor enforcement. Both are COVERED: `node --test tests/phase1_prohibitions_*.test.cjs` passes six tests; all six named bad subjects fail, all clean controls pass, and the GSD producer returns six green, located, unflagged results with machine-proven violation fixtures. Full Python regression after this addition remains **254 passed, 0 skipped, 54.11 seconds**; the six Node controls are additional checks, not included in the 254 count. They are now included in the Windows/Ubuntu CI workflow. The harness selects a local platform-appropriate venv, an explicit `BRUJULA_TEST_PYTHON`, or CI's `python` on PATH. Linux execution remains independently observable in CI after push.

## Planning Source Audit

| Source | Required item | Plan | Status |
|---|---|---|---|
| GOAL | Eight verifiable official inputs and unambiguous definitions before estimation | 01-01, 01-02, 01-03 | COVERED |
| REQ | SRC-01 exact eight pinned offline ZIPs | 01-01 | COVERED |
| REQ | SRC-02 every attempt receipted; failed current wins | 01-01 | COVERED |
| REQ | SRC-03 package members, revision, coding, geography | 01-01 | COVERED |
| REQ | SRC-04 terms, attribution, dates, transformation, local rows | 01-01 | COVERED |
| REQ | CTR-01 strict v2 dimensions, evidence and precision with v1 regression | 01-03 | COVERED |
| REQ | CTR-02 two explicit populations, denominators, age and sentinel rules | 01-02, 01-03 | COVERED |
| RESEARCH | Resolver/current authority, exact ZIP members and eight-period offline check | 01-01 | COVERED |
| RESEARCH | 2024 corrections, CMPE normalization, ENT/CVE_ENT and edition uncertainty | 01-01 | COVERED |
| RESEARCH | Population masks, unknown age, income and observed versus weighted denominators | 01-02 | COVERED |
| RESEARCH | Strict internal/public schemas, grain, singleton representation, semantic refs and suppression of diagnostic and equivalent weighted totals | 01-03 | COVERED |
| RESEARCH | Package resource and v1 compatibility | 01-03 | COVERED |
| CONTEXT | All source/reproduction, universe/concept and contract/public-value locked decisions in `01-CONTEXT.md` | 01-01, 01-02, 01-03 | COVERED |
| CONTEXT | Deferred numeric estimates, findings, reports, release and frontend | later phases / out of scope | EXCLUDED |

The 22 `01-EDGE-PROBE.json` candidates are assigned explicitly in `must_haves.truths` and task actions: SRC-01 five, SRC-02 two, SRC-03 four and SRC-04 two in 01-01; CTR-02 four in 01-02; CTR-01 five in 01-03. The plan-specific `prohibitions` are descriptor-less and flagged for independent verification; no check descriptor is fabricated. Existing project prohibitions remain binding regardless of the probe.
