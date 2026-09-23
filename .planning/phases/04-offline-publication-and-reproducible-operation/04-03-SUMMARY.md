---
phase: 04-offline-publication-and-reproducible-operation
plan: 03
subsystem: publication
tags: [public-model, csv, parquet, duckdb, suppression, provenance]
requires:
  - phase: 03-analysis-and-claims
    provides: Independently pinned Phase 3 sanitized record index, accepted comparisons and claims
provides:
  - Closed public publication model with exact v2r/v2c/v2k joins and declared figure references
  - Typed joined CSV, Parquet and DuckDB exports with a complete data dictionary
affects: [04-04-editorial-report, 04-05-sealed-operation, 04-06-acceptance]
tech-stack:
  added: []
  patterns:
    - Validate independently pinned Phase 3 packet before model projection
    - Reconstruct and revalidate accepted packet from every public model before export
    - Stage typed relational files and atomically expose the completed export directory
key-files:
  created:
    - brujula/publication_v2.py
    - brujula/export_v2.py
    - contracts/publication-v2.schema.json
    - tests/test_publication_v2.py
    - tests/test_export_v2.py
    - tests/publication_v2_support.py
  modified:
    - brujula/resources.py
    - tests/test_installed_runtime.py
key-decisions:
  - Figure links select a declared editorial subset while all 6,739 sanitized records remain in exports.
  - CSV escapes formula prefixes and original leading apostrophes with one reversible apostrophe; DuckDB and Parquet preserve original text.
  - Typed DuckDB COPY loads transient UTF-8 rows inside a transaction before atomic directory promotion.
patterns-established:
  - All report and export values resolve to the same independently validated sanitized record index.
requirements-completed: [PUB-04, PUB-05]
duration: 49min
completed: 2026-09-23
---

# Phase 4 Plan 03: Public Model and Joined Exports Summary

**A pinned Phase 3 packet now yields one strict 6,739-row public model and joined typed CSV, Parquet and DuckDB exports, with suppression and provenance preserved.**

## Performance

- **Duration:** approximately 49 minutes including independent review corrections
- **Started:** 2026-09-23T19:43:00Z
- **Completed:** 2026-09-23T20:32:00Z
- **Tasks:** 2 completed
- **Files modified:** 8 implementation, schema and test files

## Accomplishments

- `build_publication_model` accepts only a `validate_analysis_packet`-accepted input and copies its sanitized `record_index`. `validate_publication_model` checks the closed schema, content digest, figure references and reconstructed packet against the independent Phase 3 pins. It rejects changed values, diagnostic roots, nonfinite numbers and orphan links.
- Nine declared figure/table links cover national context, the three focal fields, eight-quarter trends, recorded-sex contrasts, all 32 state availability rows, other identifiable fields and three accepted opening claims. Full detail stays in the exports.
- `export_public_tables` creates typed record, comparison, claim, figure, evidence, join and dimension tables. It writes CSV and Parquet for every table and one DuckDB database, plus a column-by-column dictionary. Exports are staged and promoted only after all files finish.

## Validation Evidence

- The persisted `.cache/research/phase3-analysis/analysis.json` passed the installed `validate_analysis_packet` gate. The public model retained **6,739 exact v2r record IDs**, **23 metric IDs**, **4,209 v2c comparisons**, **38 v2k claims**, and **3 opening claim IDs**.
- `tests/test_publication_v2.py`: 4 passed against the real packet, including altered input/model, nested suppressed precision, nonfinite values, unknown roots and orphan links.
- `tests/test_export_v2.py`: The original real-packet readback verified every public record column across DuckDB and Parquet, and CSV matched its documented representation. It also verified 23 metrics, 4,209 comparisons, 38 claims, leading-zero codes, SQL nulls, status, reason, provenance and interrupted-write cleanup. Final review corrections added portable field-level comparison parity for both signatures and all other fields.
- `tests/test_installed_runtime.py`: 12 passed with 23 mandatory authored resource digests, including the new public schema. `git diff --check` passed.
- Post-review compact tests: **18 passed, 2 optional real integrations deselected** against an independently pinned synthetic packet. The same modules ran in a disposable clean `git archive HEAD` source copy with no ignored cache: **18 passed, 2 explicitly skipped** because the real packet was absent. No boundary assertion was skipped.
- The two optional real integration tests passed against the persisted 6,739-row packet before the final comparison-array serialization change. The final real-packet and full-suite recheck is assigned to the phase integrator after source freeze; it is not counted as complete here.

## Task Commits

1. **Task 1 RED:** `fda8550` — failing public model boundary tests.
2. **Task 1 GREEN:** `53c9a6d` — pinned model, closed schema, figure joins and resource inventory.
3. **Task 2 RED:** `972cc30` — failing cross-format readback tests.
4. **Task 2 GREEN:** `34afcd4` — typed aggregate exports and dictionary.
5. **Task 2 edge verification:** `5930797` — full-column parity and reversible CSV text checks.
6. **Review RED:** `a23150e` — failing clean-runner and blocked-figure tests.
7. **Review GREEN:** `a89b782` — portable pinned fixture, lossless comparison export and supported-only figure links.

## Decisions Made

- The model retains the exact upstream v2r keys and reconstructs the upstream packet on validation. This keeps an altered caller-produced projection from becoming trusted through a newly computed public digest.
- Figure membership is a deterministic subset of accepted public records and comparisons. Its IDs are stable and readable for the later editorial renderer.
- DuckDB loads temporary typed CSV through `COPY` in one transaction; the public CSV uses a separate reversible spreadsheet-safe representation. The final export directory appears only after all outputs succeed.
- Sparse valid packets omit figure groups without matching rows. Unsupported endpoints remain in public records and the full comparison ledger, while figure comparison links contain only comparable `REVIEW` rows.
- Comparison signatures and other array fields use canonical UTF-8 JSON text in every container; the dictionary documents how to parse them without losing nested keys or array boundaries.

## Independent Review Corrections

- **CR-01, portable tests:** Added `tests/publication_v2_support.py` to build a compact synthetic Phase 3 packet and freeze an independent test reference. All mandatory boundary and export assertions run without `.cache`; only the separate persisted real-packet integrations skip when that artifact is absent. A disposable clean source copy proved 18 passed and 2 optional skips.
- **CR-02, comparison signatures:** Both complete endpoint signatures, plus reasons, limitations, source IDs/hashes and period arrays, now serialize as canonical JSON text. The compact export test parses and compares every comparison field across DuckDB, Parquet and CSV and checks evidence links.
- **WR-01, blocked figure comparisons:** Figure links require canonical `comparable=true` and `status=REVIEW`. A focused test includes a blocked comparison with both endpoints selected and proves it is omitted while the endpoint record keys remain visible.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Replaced slow row-wise DuckDB insertion**
- **Found during:** Task 2 real-packet readback.
- **Issue:** Per-row insertion of 6,739 wide records did not complete in a practical test window.
- **Fix:** Typed DuckDB `COPY` from transient CSV inside the same transaction, retaining full-value readback and atomic directory promotion.
- **Files modified:** `brujula/export_v2.py`
- **Verification:** Real 6,739-row CSV/Parquet/DuckDB parity test passed.
- **Committed in:** `34afcd4`

**2. [Rule 2 - Missing critical] Added the new schema to the installed resource inventory**
- **Found during:** Task 1 package boundary review.
- **Issue:** The model validator requires the schema to exist in an installed wheel, while the authored resource digest inventory did not yet require it.
- **Fix:** Registered `publication-v2.schema.json` as mandatory and updated the expected count to 23.
- **Files modified:** `brujula/resources.py`, `tests/test_installed_runtime.py`
- **Verification:** 12 installed resource tests passed.
- **Committed in:** `53c9a6d`

## Known Stubs

None. The empty list and null initializers in implementation are transient builders, not rendered placeholder data.

## Issues Encountered

The accepted real packet takes roughly 28 seconds for each full independent validation. The compact test fixture preserves independent pins for mandatory CI assertions; no production validation cache or pin bypass was added.

## Next Phase Readiness

Plan 04-04 can consume `build_publication_model`, `validate_publication_model` and declared `figure_links`; Plan 04-05 can seal the exact inventory returned by `export_public_tables`. The final report, rendered PDF, installed numerical refresh and phase-level acceptance remain separate downstream gates.

## Self-Check: PASSED

All eight listed source/schema/test files and this summary exist. All seven task and review commit IDs resolve to commits. The clean-copy result and reported test outcomes were checked against execution output.
