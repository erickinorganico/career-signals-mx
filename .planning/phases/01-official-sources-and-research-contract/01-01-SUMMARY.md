---
phase: 01-official-sources-and-research-contract
plan: 01
subsystem: source-inventory
tags: [enoe, inegi, zip, provenance, metadata]
requires: []
provides:
  - Offline inventory of eight current, SHA-pinned ENOE packages
  - Exact member, revision, coding, geography and source provenance metadata
affects: [phase-2-ingestion, phase-3-analysis, release-evidence]
tech-stack:
  added: []
  patterns: [resolver-backed offline custody, exact ZIP member selection, metadata-only projection]
key-files:
  created: [brujula/source_inventory.py, tests/test_source_inventory.py]
  modified: [docs/SOURCES.md]
key-decisions:
  - "SDEM headers preserve original spelling; validation compares case-insensitive names."
  - "The two 2024 SDEM revision logs are required exactly; later missing logs are reported as absence in the package."
  - "Any newer acquisition attempt blocks inventory until a successful current receipt supersedes it."
patterns-established:
  - "Resolve each approved current attempt before inspecting exact period-derived members."
  - "Stream the full person member into SHA-256 while decoding only its header."
requirements-completed: [SRC-01, SRC-02, SRC-03, SRC-04]
coverage:
  - id: D1
    description: Eight current ENOE packages resolve offline with exact member hashes and fail-closed custody.
    requirement: SRC-01
    verification:
      - kind: integration
        ref: tests/test_source_inventory.py#test_all_eight_cached_offline_when_present
        status: pass
      - kind: unit
        ref: tests/test_source_inventory.py#test_failed_or_running_current_and_missing_attempt_block
        status: pass
    human_judgment: false
  - id: D2
    description: Metadata exposes source, revisions, coding and geography without person rows.
    requirement: SRC-03
    verification:
      - kind: integration
        ref: tests/test_source_inventory.py#test_all_eight_cached_offline_when_present
        status: pass
      - kind: unit
        ref: tests/test_source_inventory.py#test_catalog_encoding_alias_and_provenance_fail_closed
        status: pass
    human_judgment: false
  - id: D3
    description: Eight-period source and license account in Spanish.
    requirement: SRC-04
    verification:
      - kind: other
        ref: docs/SOURCES.md#inventario-local-verificado-de-ocho-paquetes-enoe
        status: pass
    human_judgment: true
    rationale: Editorial adequacy and legal attribution require reviewer judgment.
duration: 14min
completed: 2026-09-23
status: complete
---

# Phase 1 Plan 1: Official Source Inventory Summary

**Eight current official ENOE ZIPs now have a deterministic offline inventory of full member hashes, revision logs, coding and provenance without exporting person rows.**

## Performance

- **Duration:** 14 min
- **Started:** 2026-09-23T03:09:00Z
- **Completed:** 2026-09-23T03:23:40Z
- **Tasks:** 2 completed
- **Files modified:** 3

## Accomplishments

- `inventory_snapshot` and `inventory_all` accept only the eight approved periods in registry order, resolve current plus immutable attempts, reject newer failed attempts, and select exact ZIP members.
- Full SDEM streams are SHA-256 hashed; only headers and bounded UTF-8 dictionary, catalog and bitácora metadata are decoded. The output contains no person observations or ZIP payload.
- The 2024-Q3 and Q4 logs are validated as 4 and 9 changes dated 2025-05-27. The 2025-Q3 geography shift and three reviewed CMPE codes are explicit; conceptual equivalence and person-row encoding remain unresolved.
- `docs/SOURCES.md` records eight source fichas, complete raw and SDEM hashes, dictionary editions, revision hashes, INEGI terms and transformation attribution.

## Task Commits

1. **Task 1 RED:** `d67f734` — failing custody and exact-member tests.
2. **Task 1 GREEN:** `89df59f` — resolver-backed inventory.
3. **Task 2 RED:** `f56fb78` — failing revision and provenance tests.
4. **Task 2 GREEN:** `da78a8e` — revision, coding, source documentation and controls.

## Verification

- `.venv/Scripts/python.exe -m pytest tests/test_acquisition.py tests/test_source_inventory.py -q`: **28 passed**, one expected duplicate-ZIP fixture warning.
- `.venv/Scripts/python.exe -m pytest tests/test_source_inventory.py -q`: **9 passed**, including the eight real cached ZIPs.
- Two consecutive `inventory_all(Path('artifacts/enoe'))` reads returned identical eight-record metadata. The ignored `.cache/research/enoe-source-inventory.json` is available for local review. The integration test fails if the downloader is invoked.

## Decisions Made

- Preserve source header spelling while checking aliases case-insensitively because the official CSV uses lowercase names.
- Require the known 2024 revision logs and reject an unexpected later log until its implications are reviewed.
- Treat a newer failed acquisition attempt as blocking even when current still points at an older success.

## Deviations from Plan

None - plan executed as specified. Case-insensitive header comparison and latest-attempt validation implement the planned real-package and concurrency gates.

## Issues Encountered

The first real ZIP check revealed lowercase source headers. Validation was adjusted without changing the emitted header. No packages, network access or new dependencies were needed.

## Known Stubs

None. `person_row_encoding: UNRESOLVED` and `concept_equivalence_review: REVIEW` are explicit evidence limitations, not placeholders for silently computed values.

## Next Phase Readiness

Phase 2 can consume the current snapshot metadata and exact member paths. It must determine person-row encoding and numeric lexical rules before parsing or publishing rows; this plan does not approve numerical findings or microdata release.

## Self-Check: PASSED

All three owned files exist; four task commits are present; focused and eight-package integration checks passed. No tracked file deletion occurred in either implementation commit.

---
*Phase: 01-official-sources-and-research-contract*
*Completed: 2026-09-23*
