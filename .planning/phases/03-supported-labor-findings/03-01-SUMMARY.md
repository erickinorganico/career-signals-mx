---
phase: 03-supported-labor-findings
plan: 01
subsystem: public-aggregate-analysis
tags: [enoe, public-v2, profiles, coverage, suppression]
requires:
  - phase: 02-defensible-survey-estimates
    provides: accepted eight-quarter public v2 payloads, request/evaluation audits, pinned numerical content
provides:
  - canonical IDs for all 6739 accepted public records
  - complete eight-quarter national and latest-quarter field, state and sex profile grids
  - observed response and nonexclusive exclusion coverage with explicit denominators
  - sanitized downstream record_index carrying complementary redactions
affects: [03-02-comparisons, 03-03-claims, 04-offline-publication]
tech-stack:
  added: []
  patterns: [independent accepted-content pins, ten-key canonical identity, public-only profile assembly, downstream redaction continuity]
key-files:
  created:
    - brujula/analysis_v2.py
    - tests/test_analysis_v2.py
    - data/fixtures/analysis-v2-golden.json
    - tests/phase3_prohibitions_01.py
    - tests/phase3_prohibitions_01.test.cjs
    - tests/fixtures/phase3_prohibitions/01.clean.json
    - tests/fixtures/phase3_prohibitions/01-p1.bad.json
    - tests/fixtures/phase3_prohibitions/01-p2.bad.json
  modified: []
key-decisions:
  - "Require the exact approved Phase 1 source hashes, Phase 2 eleven-file code inventory and independent public golden pins in addition to the supplied acceptance manifest."
  - "Keep quarter-specific method catalog source_snapshot_ids despite a shared method ID."
  - "Use profiles['record_index'] as the only downstream record source; it carries public-v2-valid complementary redactions while the accepted source index remains private."
  - "Label exact-income response as an observed count over occupied eligible n, separate from the weighted public estimate."
patterns-established:
  - "Missing requested, evaluated or public grain blocks; only an evaluated suppressed public record yields a null profile cell."
  - "Stable v2r IDs hash canonical JSON of the full ten-key grain."
requirements-completed: [ANA-01, ANA-04, ANA-05]
coverage:
  - id: canonical-index
    description: Eight accepted public roots produce stable IDs with exact request/evaluation integrity and independent pins
    requirement: ANA-01
    verification:
      - kind: unit
        ref: tests/test_analysis_v2.py#test_synthetic_complete_grid_and_canonical_ids
        status: pass
      - kind: integration
        ref: offline accepted aggregate-only 6739-record profile build
        status: pass
    human_judgment: false
  - id: complete-slices
    description: Latest 118 named fields, 32 states and two recorded-sex slots retain actual null causes
    requirement: ANA-04
    verification:
      - kind: unit
        ref: tests/test_analysis_v2.py#test_synthetic_complete_grid_and_canonical_ids
        status: pass
      - kind: integration
        ref: tests/phase3_prohibitions_01.test.cjs
        status: pass
    human_judgment: false
  - id: observed-coverage
    description: Observed response and exclusion categories keep explicit, nonexclusive denominators
    requirement: ANA-05
    verification:
      - kind: unit
        ref: tests/test_analysis_v2.py#test_observed_exact_income_response_has_explicit_denominator_and_empty_state
        status: pass
    human_judgment: false
  - id: disclosure-continuity
    description: Complementary parent suppression propagates to the common downstream public record index
    requirement: ANA-04
    verification:
      - kind: unit
        ref: tests/test_analysis_v2.py#test_profile_redaction_flows_to_downstream_record_index
        status: pass
      - kind: integration
        ref: canonical GSD prohibition-enforcement p1 and p2
        status: pass
    human_judgment: false
duration: 32min
completed: 2026-09-23
status: complete
---

# Phase 3 Plan 01: Supported Public Profiles Summary

**Accepted ENOE public aggregates now yield complete, traceable eight-quarter profiles and visible sparse coverage without restoring suppressed estimates.**

## Performance

- **Duration:** approximately 32 minutes of execution, plus the full regression run
- **Completed:** 2026-09-23
- **Tasks:** 3/3
- **Files created:** 8 implementation, fixture and control files

## Accomplishments

- The real accepted input indexes **6,739 unique public records** from eight snapshots. The profile packet has 920 national cells, 2,714 latest named-field cells covering 118 actually observed official fields, 2,944 state cells (32 states × four cohorts/fields × 23 metrics), and 184 recorded-sex cells (two codes × four cohorts/fields × 23 metrics).
- These sections contain **6,762 appearances**. Sixty-nine latest focal cells intentionally appear in both national and named-field views; 46 benchmark-only national-context Baja California source cells are outside the profile sections. Sections are not a count of distinct source records.
- Every requested/evaluated/public grain is checked before construction. Snapshot hashes, exact eleven-file numerical code inventory, independent public golden pins, approved Phase 1 source hashes and URLs, metric manifest, per-quarter record digests and combined digest are verified. All public JSON is read as UTF-8 to preserve official labels and hashes.
- Coverage preserves observed n, eligible and responding denominators, exact-income responding n, named exclusions and their nonexclusive meaning. No weighted estimate is described as observed or effective sample size.
- The real packet redacts five unique parent records in its sanitized downstream `record_index` when a suppressed state or sex part could be isolated. They appear ten times across national and named-field sections. The original accepted source index remains unchanged and private; Phase 3 comparisons, claims and Phase 4 publication must consume `profiles['record_index']`.

## Validation Results

- Focused synthetic aggregate tests: **12 passed**. The fixture is explicitly synthetic and contains no person rows.
- Accepted real aggregate-only integration: **6,739 indexed records; 920 / 2,714 / 2,944 / 184 profile cells**; no ENOE ZIP, R or survey estimation rerun.
- Node prohibition controls: **2 passed**. Each known-bad fixture fails only its matching named test; the clean fixture passes both. Canonical GSD producer for both descriptors reports `status: green`, `located: true`, `failFirst: true`, `passed: true`, and `flagged: false`.
- Full Python regression: **378 passed**, one existing duplicate-ZIP-member warning from `tests/test_acquisition.py`, in 253.87 seconds.

## Task Commits

1. **Task 1 — accepted index:** `16d9f7e` RED, `8c8eede` GREEN.
2. **Task 2 — complete profiles and coverage:** `3a2f74a` RED, `e59dd21` RED, `4e8acdc` GREEN; `f3fb89a` RED and `dd27004` GREEN for accepted-input and downstream disclosure hardening.
3. **Task 3 — prohibitions:** `73fbad2` computed Python/Node checks, clean and targeted bad fixtures.

## Decisions Made

- `index_public_estimates` accepts `{'manifest': accepted_manifest, 'audits': aggregate_audits}`. The accepted manifest alone does not carry each complete audit, so the two are passed together and checked against independent source and golden resources.
- The same method ID is valid across quarters while its catalog entry binds only that quarter's source snapshot. Catalogs remain per snapshot.
- `build_profiles` returns `record_index` keyed by stable `v2r:` ID. Its `record` is a sanitized public-v2 record; a redacted entry also carries `redaction_reason: complementary_suppression`. This index is the common downstream input. The source `index_public_estimates` result must remain private.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing critical integrity] Independently bound accepted inputs**
- **Found during:** Task 1 and Task 2 review.
- **Issue:** A caller could coherently alter public, audit and manifest digests without checking the independently approved Phase 1 source catalog or Phase 2 public golden.
- **Fix:** Enforce exact code-file inventory, source IDs/hashes/URLs, public golden pins, per-quarter record digests and the combined digest; add repinning negative tests.
- **Files modified:** `brujula/analysis_v2.py`, `tests/test_analysis_v2.py`.
- **Committed in:** `dd27004`.

**2. [Rule 2 - Missing critical disclosure control] Propagated complementary redactions**
- **Found during:** Task 2 downstream interface readback.
- **Issue:** A redacted profile parent remained visible through the raw source index that later claims or exports might consume.
- **Fix:** Return a sanitized public-v2-compatible `record_index` from profiles; test that the same stable ID is null there while the accepted source stays unchanged.
- **Files modified:** `brujula/analysis_v2.py`, `tests/test_analysis_v2.py`.
- **Committed in:** `dd27004`.

## Known Stubs

None. Empty dictionaries and lists in the implementation and tests are accumulation structures filled before output; they are not placeholder findings.

## Next Phase Readiness

Plans 03-02 and 03-03 can consume `profiles['record_index']` for comparison and claims while retaining `redaction_reason`. The Phase 4 packaging pass should resolve the source-catalog, code-hash and golden-pin resource paths for an installed wheel; the current local checkout is verified.

## Integration correction — bound coverage references

After the initial wave summary, a targeted synthetic reproduction changed an aggregate responding count from 100 to 999,999,999 without changing accepted estimate hashes; the old index accepted it. RED commit `98e4f6e` captures that failure. The correction independently pins every population coverage map and every exact-grain metric coverage/exclusion map in the hash-only resource `data/fixtures/enoe-analysis-coverage-pins.json`, originating from the accepted final Phase 2 replay. The resource contains no person rows or diagnostic estimates. Published count values must also be nonnegative integers with valid eligible/observed denominators; exclusion categories remain nonexclusive.

The seven new negative cases cover changed population/responding/domain counts, negative or mistyped exclusions, NaN and booleans, including a coherently changed caller-supplied coverage hash. Focused tests: **19 passed**; current Node controls: **2 passed**. Real aggregate-only readback verifies all eight independent coverage pins and preserves 6,739 records, 920/2,714/2,944/184 section appearances and five unique redacted parents. Profile content digest: `6c4123296e3e50b0d02e1e88f34a702df4766725d37dfd776ea4aaad2b8d3139`. The Phase 2 numerical code, accepted values, golden and historical receipts remain unchanged. The next wave's full suite includes this correction; no duplicate survey or R execution is needed.

## Self-Check: PASSED

All eight planned implementation/control files and this SUMMARY exist. All eight listed task commits resolve to Git commits. Focused, canonical prohibition, accepted-real and full-suite evidence above was read back after the final code changes.

---
*Phase: 03-supported-labor-findings*  
*Completed: 2026-09-23*
