---
phase: 01-official-sources-and-research-contract
verified: 2026-09-23T04:31:47Z
status: passed
score: 27/27 must-haves verified
overrides_applied: 0
re_verification:
  previous_status: human_needed
  previous_score: 23/23
  prohibition_flags_closed: 6
  new_plan_truths_verified: 4
  gaps_remaining: []
  regressions: []
---

# Phase 1: Official Sources and Research Contract Verification Report

**Phase goal:** Analysts can verify the eight official inputs and apply unambiguous research definitions before estimating any result.

**Verified:** 2026-09-23T04:31:47Z at `80194ce`  
**Status:** `passed`  
**Mode:** Re-verification after Plan 01-04 closed the six prohibition flags.  
**Scope:** Phase 1 source custody, metadata, population definitions and v2 interface. This is not acceptance of real ENOE estimates, temporal comparisons, public outputs or release.

## Goal achievement

The four roadmap success criteria, 19 original plan truths and four Plan 01-04 truths have implementation and behavioral evidence. Six previously descriptor-less prohibitions now have test-tier descriptors and executable fail-first controls. I independently reran the canonical enforcement producer for all six; each returned `status=green`, `located=true`, `flagged=false`, and `failFirstProof=violation-fixture` in its evidence. No Phase 1 human verification item remains. This does not accept Phase 2 numerical results or publication.

### Observable truths

| # | Source | Truth checked | Status | Code and behavioral evidence |
|---|---|---|---|---|
| R1 | Roadmap SC1 | Eight approved quarters resolve to pinned local ZIPs, immutable attempts and fail-closed current | VERIFIED | `data/catalog/enoe-snapshots.json` has exactly 2024-Q3–2026-Q2, eight SHA-256 pins. `resolve_snapshot` in `brujula/acquisition.py:291` checks registry URL/hash, current versus immutable attempt, raw hash and ZIP safety. `inventory_all` in `brujula/source_inventory.py:272` checks every latest attempt. Real offline inventory test ran with no skip. |
| R2 | Roadmap SC2 | Per-quarter members, dictionary, catalog, revision, coding, geographic aliases and provenance are inspectable without person rows | VERIFIED | `source_inventory.py:59-249` selects exact paths, hashes full members, validates dictionary and study catalog, checks 2024 revisions and geography headers, and emits metadata only. `docs/SOURCES.md:80-130` records all eight hashes, corrections, terms and transformation. Real offline test asserts eight SDEM member hashes, headers, revisions and metadata-only output. |
| R3 | Roadmap SC3 | National and completed-professional populations, exclusions and denominators are exact | VERIFIED | `brujula/populations.py:19-282` defines distinct masks, EDA 98 unknown in national context, 15–97 professional cohort, education/completion exclusions, unknown-field indicator, observed and weighted denominators, and income sentinels. `tests/test_population_rules.py` passed. |
| R4 | Roadmap SC4 | Separate strict v2 internal/public research records validate dimensions, evidence and precision while v1 regression remains intact | VERIFIED | Both `contracts/research-v2*.schema.json` reject extra fields and require distinct dimensions and precision fields. `brujula/research_contract.py:98-272` checks references, grain, source/method compatibility, support/CV and suppression, then validates the public projection. The focused v2 and existing v1 suite passed. |
| P1 | 01-01 | Exactly eight approved ZIPs resolve offline through current and immutable attempts | VERIFIED | Exact registry period/ID/order checks at `source_inventory.py:37-56`; resolver and live eight-package test. |
| P2 | 01-01 | Absent, failed, malformed, mismatched or concurrent attempts block inventory | VERIFIED | `acquisition.py:201-324` writes attempt/current receipts and rejects failed current; `source_inventory.py:222-285` rejects missing/mismatched/newer attempts. Synthetic corruption and concurrency tests passed. |
| P3 | 01-01 | Exact SDEM, dictionary, catalog and revision selection resists similar filenames | VERIFIED | `_paths`, `_member`, `_inventory` in `source_inventory.py:59-208`; tests add similarly named CSV and reject absent/ambiguous exact members. |
| P4 | 01-01 | 2024 corrections, 2025-Q3 header transition and per-quarter coding are visible | VERIFIED | `_validate_revisions` expects Q3 four and Q4 nine 2024 corrections; geography check requires ENT then CVE_ENT. Eight real package assertions passed; conceptual equivalence remains REVIEW. |
| P5 | 01-01 | Only metadata, terms, acquisition date and transformation notes leave the raw area | VERIFIED | `_inventory` returns selected metadata and hashes, retains no SDEM payload, and marks `microdata_publication_approved=False`; `docs/SOURCES.md:125-130` names attribution and local-only records. |
| P6 | 01-01 | SRC edge cases have negative and determinism checks | VERIFIED | `tests/test_acquisition.py` and `tests/test_source_inventory.py` cover empty/adjacent IDs, duplicate members, malformed encoding, ordering, corruption and newer attempts; both ran. |
| P7 | 01-02 | National operational ages 15–98 preserve 98 as unknown | VERIFIED | `classify_eligibility` in `populations.py:57-113`; parameterized age tests passed. |
| P8 | 01-02 | Professional cohort requires age 15–97, CS_P13_1=07 and CS_P16=1 | VERIFIED | `populations.py:80-105`; education, response, residence and age tests passed. |
| P9 | 01-02 | Technical, incomplete, postgraduate and unknown states stay separate | VERIFIED | Reason-specific branches in `populations.py:85-105`; `summarize_denominators` counts each reason and eligible unknown field separately. |
| P10 | 01-02 | Period catalog constrains six-digit CMPE keys and separate concepts | VERIFIED | `normalize_cmpe_key` in `populations.py:185-205` requires caller-supplied catalog; `source_inventory.py:122-144` verifies dictionary/catalog codes. V2 grain keeps field, occupation and industry separate. |
| P11 | 01-02 | Income zero/sentinels do not imply zero wage or all-occupied coverage | VERIFIED | `classify_income_state` and `summarize_measure_denominator` in `populations.py:208-282` distinguish positive-known, no-income, unspecified, not applicable and conflicts; sentinel tests passed. |
| P12 | 01-02 | Observed, response, excluded and weighted denominators are distinct | VERIFIED | `summarize_denominators` returns separately named counts and weighted denominator; `_weight`/`_sum_weights` reject invalid weights and overflow. |
| P13 | 01-02 | Boundary, empty, encoding and precision edge tests exist | VERIFIED | `tests/test_population_rules.py` covers 15/97/98/99, empty rows, malformed ASCII codes, income sentinels and weighted sums; ran in focused suite. |
| P14 | 01-03 | V2 separates all ten grain dimensions and resolves references | VERIFIED | `GRAIN`, `CATALOG_REFS` and semantic checks in `research_contract.py:17-159`; both strict schemas and duplicate/orphan tests passed. |
| P15 | 01-03 | Records carry design, support, precision, state and evidence | VERIFIED | Schema required fields and semantic checks at `research_contract.py:144-197`; malformed support/CV and source/evidence mismatch tests passed. This validates declared metadata, not correctness of future computed errors. |
| P16 | 01-03 | Internal estimate and public record use separate strict schemas | VERIFIED | `_validator(public)` selects packaged schema; `public_research_projection` validates internal before allowlisting and public after. |
| P17 | 01-03 | Suppressed public cells hide estimate-equivalent diagnostics and retain labeled support | VERIFIED | `research_contract.py:232-272` removes estimate and nulls weighted denominator, weighted support, SE, CV and intervals. Controlled public reason codes prevent the reviewed free-text leak. Negative serialized-sentinel tests passed. |
| P18 | 01-03 | V2 preserves v1 synthetic contract | VERIFIED | No v1 schema/fixture edits in Phase 1; the root full suite at this HEAD was reported as 254 passed, 0 skipped, and the focused run included existing v1 acquisition tests. V2 tests explicitly keep synthetic records in REVIEW. |
| P19 | 01-03 | CTR edge cases have negative and determinism checks | VERIFIED | `tests/test_research_contract.py` tests duplicate grain, empty refs/catalogs, adjacent periods, ordering, nonfinite numbers, rounding, contradictory CV and impossible support; ran in focused suite. |
| P20 | 01-04 | Six existing must-NOT statements have named executable checks over current Phase 1 APIs | VERIFIED | Six Node targets call `tests/phase1_prohibitions_common.cjs`, which invokes `tests/phase1_prohibitions.py`; each Python case calls source inventory, population or v2 validation APIs with synthetic inputs. |
| P21 | 01-04 | Each check passes current and clean behavior but fails its known-bad subject | VERIFIED | Direct `node --test` ran six clean passes. The canonical producer ran every target with its bad and clean JSON fixture; all six evidence entries include `failFirst=true`, `passed=true`, `failFirstProof=violation-fixture`. Mutations alter freshly computed API outputs before behavioral assertions. |
| P22 | 01-04 | Original plans project four flat check descriptors without changing prohibition statements | VERIFIED | Inspected 01-01/02/03 frontmatter: each of the six unchanged statements carries `verification: test`, `check_kind`, `check_target`, `check_violation_fixture` and `check_clean_fixture`. All paths resolve. |
| P23 | 01-04 | Canonical enforcement producer proves all six checks green | VERIFIED | Parsed the six descriptor blocks from plan frontmatter and independently called `gsd-tools.cjs check prohibition-enforcement` for each: six green, six located, zero flagged, six violation-fixture proofs. |

**Score:** 27/27 positive truths verified; six negative prohibitions mechanically enforced.

### Required artifacts and links

| Artifact or link | Existence / substance / wiring | Assessment |
|---|---|---|
| Registry, `brujula/acquisition.py`, local `artifacts/enoe` cache | Eight exact entries with SHA pins; resolver checks current/attempt/raw bytes; real offline inventory test passed | VERIFIED |
| `brujula/source_inventory.py` → acquisition resolver and approved registry | Imported resolver and registry; exact member selection, full hashes, revisions and metadata projection exercised by fixture and eight-cache tests | VERIFIED |
| `docs/SOURCES.md` and ignored local inventory | Eight-period hash table, correction details, aliases, attribution, terms, transformation and local-only boundary documented | VERIFIED |
| `brujula/populations.py` → period study catalog | Pure eligibility/denominator functions require supplied verified catalog keys; Phase 2 estimator consumption is explicitly future work, so no Phase 1 runtime estimate is asserted | VERIFIED for Phase 1 contract; Phase 2 consumer deferred |
| Both `research-v2` schemas → `brujula/research_contract.py` → `brujula.populations` | Schemas loaded through `contract_path`; validator imports population definitions, checks references and validates public projection; package data maps both JSON resources | VERIFIED |
| `docs/CONTRACT-V2.md`, source/population/v2 tests | Substantive interface, limits and negative cases; all affected tests passed | VERIFIED |
| `tests/phase1_prohibitions.py` → Node bridge → six named targets → 12 fixtures | Current API outputs are checked against prohibited outcomes; bad fixtures modify those outputs and fail the same assertions; clean fixtures pass. No production data or network dependency. | VERIFIED |
| 01-01/02/03 plan descriptors → canonical producer | Six plan-authored node-test targets and bad/clean subjects were parsed and accepted by the enforcement command with machine-proven fail-first evidence | VERIFIED |

### Data flow and behavioral checks

`inventory_all(Path('artifacts/enoe'))` flows from eight registry entries through the current receipt, immutable attempt, SHA-verified raw ZIP and exact internal members to a metadata-only list. No source inventory field is populated from a static empty fallback. Population rules consume caller-supplied SDEM mappings and period catalog keys; they do not claim numerical estimates. V2 validation consumes a caller-supplied research payload; projection derives the public payload solely from validated input, with controlled reason codes and null suppression. The actual Phase 2 producer and Phase 4 public consumer do not exist yet and are not represented as Phase 1 evidence.

| Behavior | Command/evidence | Result |
|---|---|---|
| Affected source, acquisition, population and v2 contract tests, including eight real cached ZIPs | `.venv/Scripts/python.exe -m pytest tests/test_source_inventory.py tests/test_population_rules.py tests/test_research_contract.py tests/test_acquisition.py -q` | PASS: 135 passed, no skips, one expected duplicate-ZIP fixture warning, 8.26 s |
| Full Python regression after Plan 01-04 | Root orchestration result: `.venv/Scripts/python.exe -m pytest -q` | 254 passed, 0 skipped, 54.11 s; reused rather than rerun |
| Reviewed CV/support, reason leak, nonfinite Decimal and six-digit code fixes | Actual `research_contract.py` and `source_inventory.py` branches and focused tests; independent `01-REVIEW-RECHECK.md` separately probes all five | PASS for the five original findings; no numerical estimate approval |
| Six named prohibition controls | `node --test tests/phase1_prohibitions_1.test.cjs ... tests/phase1_prohibitions_6.test.cjs` | PASS: six passed, zero failed/skipped |
| Six fail-first and clean controls | For each plan descriptor, canonical `gsd-tools.cjs check prohibition-enforcement <request.json>` with descriptor-sourced target and fixtures | PASS: six green/located, zero flagged; each evidence entry proves bad subject failed and clean/current passed |
| Probe scripts | No phase-declared `probe-*.sh` or conventional `scripts/*/tests/probe-*.sh` found | SKIPPED: no declared probe |

### Requirements coverage

| Requirement | Plan | Status | Evidence |
|---|---|---|---|
| SRC-01 | 01-01 | SATISFIED | Registry exact eight SHA pins, resolver and real eight-cache integration test |
| SRC-02 | 01-01 | SATISFIED | Immutable attempt receipts, failed/RUNNING current rejection, newer-attempt and concurrent fixture tests |
| SRC-03 | 01-01 | SATISFIED | Exact SDEM/dictionary/catalog hashes, 2024 revisions, CMPE and geography header checks |
| SRC-04 | 01-01 | SATISFIED | Inventory terms, authority, acquisition timestamp, transformation and local-only person bytes |
| CTR-01 | 01-03 | SATISFIED | Strict separate v2 schemas, semantic validator, safe projection and v1 regression |
| CTR-02 | 01-02, 01-03 | SATISFIED | Population masks, exclusions, unknown states and separate denominator summaries |

Plan 01-04 reinforces all six requirements with executable negative controls; it does not add a new roadmap requirement.

All six roadmap-assigned Phase 1 requirements appear in plan frontmatter. No Phase 1 requirement is orphaned. The repository requirements checklist remains unmarked pending integrator bookkeeping; this report records independent Phase 1 evidence, not a mutation of that checklist.

### Anti-patterns and disconfirmation

No unreferenced `TBD`, `FIXME` or `XXX` marker or user-visible placeholder was found in the Phase 1 implementation or new prohibition-control files. `return []` in `_json_input_checks` is a legitimate acceptance result for a valid scalar, not a stub. A passing synthetic contract test alone would be weak evidence for official source custody; the non-skipped real eight-ZIP inventory test directly checks pinned bytes and member hashes. The new bad fixtures are deliberately injected into freshly computed API results, so they prove the assertions detect violations; they do not simulate changing the production implementation itself. A passing real inventory or prohibition control does not prove survey estimates, person-row encoding, ENT/CVE_ENT conceptual equivalence or future publisher wiring. These are explicitly assigned to Phases 2–4 in the roadmap and docs, so they are not Phase 1 failures.

## Prohibition re-verification

The prior `human_needed` report identified six descriptor-less judgment-tier prohibitions. Plan 01-04 added test-tier descriptors, current-API controls and synthetic bad/clean subjects without changing their statements. The independently invoked canonical producer now returns green for each:

| Plan | Prohibition | Executable result |
|---|---|---|
| 01-01 | Acquisition metadata cannot approve microdata/numerical findings | P1 green: `inventory_all` output and current receipt checked; synthetic bad subject asserts a false approval and fails. |
| 01-01 | Preserve 2024 corrections; ENT/CVE_ENT alias cannot imply equivalence | P2 green: inventory correction counts, headers and REVIEW field checked; bad subject erases correction and approves alias, then fails. |
| 01-02 | Professional cohort excludes postgraduate/unknown education and avoids overbroad label | P3 green: eligibility and population label checked; bad subject folds those groups and fails. |
| 01-02 | Missing income/age/field cannot become zero or a field finding | P4 green: eligibility, denominators and income state checked; bad subject imputes values and fails. |
| 01-03 | Project singleton/diagnostic estimate cannot confer official precision | P5 green: v2 validator errors and public REVIEW projection checked; bad subject removes errors and flips precision flag, then fails. |
| 01-03 | Unknown/synthetic/suppressed cells cannot become measured claims | P6 green: v2 internal/public validators and projection checked; bad subject promotes and leaks values, then fails. |

Each result had `located=true`, `flagged=false`, and an evidence record with `failFirstProof=violation-fixture`. No original or Plan 01-04 `<human-check>` was deferred.

### Prior status retained

The initial report at `0eec8c6` on 2026-09-23T04:14:08Z had `status: human_needed`, `score: 23/23`, and six **unverified-prohibition — human review recommended** flags because the original plans lacked descriptors. Those flags were valid at that revision. Plan 01-04 and this independent re-verification close all six; they are not carried as current human-verification items.

## Gaps summary

No Phase 1 blocker or human-verification item remains. The Phase 2 numerical oracle, person-row decoding, official precision reconciliation, and Phase 3 conceptual comparability are specifically later-phase gates; Phase 4 owns final public-output wiring. An actual user-facing report or service is outside this phase.

---

_Verified: 2026-09-23T04:31:47Z_  
_Verifier: the agent (gsd-verifier)_
