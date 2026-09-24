---
phase: 04-offline-publication-and-reproducible-operation
plan: 05
subsystem: offline-publication
tags: [immutable-receipts, source-custody, publication, replay, installed-cli]
requires:
  - phase: 04-02
    provides: accepted eight-source numerical custody and immutable acceptance
  - phase: 04-03
    provides: guarded aggregate analysis and public table exporter
  - phase: 04-04
    provides: offline HTML, Markdown, PDF, figures and packaged fonts
provides:
  - sealed publication with exact model-derived artifact inventory and fail-closed current
  - live eight-source and immutable-acceptance verification on each open
  - installed real-data analysis, build, replay and open commands
affects: [04-06, release-acceptance]
tech-stack:
  added: []
  patterns: [immutable-operation-receipts, atomic-current-promotion, independent-logical-replay]
key-files:
  created:
    - brujula/pipeline_v2.py
    - contracts/publication-manifest-v2.schema.json
    - tests/test_pipeline_v2.py
    - tests/test_cli_v2.py
    - tests/test_installed_runtime.py
  modified:
    - brujula/cli.py
    - brujula/resources.py
key-decisions:
  - "The expected publication inventory is derived from the validated model: 67, 69, 71 or 73 files for zero through three opening claims."
  - "Replay compares ordered canonical CSV and typed full-row multisets in DuckDB and Parquet; container bytes and operational timestamps are excluded."
  - "An explicit R library remains required by the existing numerical acceptance contract."
patterns-established:
  - "Separate numerical acceptance, analysis operation, publication run and replay operation identities."
  - "Reject symlink and Windows junction ancestry before creating output or resolving current paths."
requirements-completed: [OPS-01, OPS-02, OPS-03]
duration: 1h00m
completed: 2026-09-23
---

# Phase 04 Plan 05: Offline Publication and Reproducible Operation Summary

**Sealed aggregate publications bind immutable numerical acceptance to eight live acquisitions and expose verified offline reports and exports through an installed CLI.**

## Performance

- **Started:** 2026-09-23T23:29:08Z (first task commit)
- **Completed:** 2026-09-24T00:29:01Z
- **Duration:** 1h00m
- **Tasks:** 3/3
- **Files modified:** 7 source, schema and test files

## Accomplishments

- Builds immutable publication runs with validated `analysis.json`, HTML, Markdown, PDF, exact figure set, 46 exports and five packaged font assets. A successful receipt and manifest precede atomic current promotion; failures leave a bounded immutable receipt, BLOCKED current and historical runs intact.
- Resolves current only after verifying the sealed receipt, manifest, exact artifact names and hashes, accepted packet binding and all eight live acquisition currents. It rechecks custody and content before returning report or export paths.
- Adds `research-analyze`, `research-build`, `research-replay`, `research-open` and the explicit ENOE refresh, accept and replay commands to the installed CLI. The analysis bridge writes a fresh packet from an immutable accepted numerical receipt; publication replay renders and exports again into an isolated audit without promoting current.
- Registers the publication manifest as the 24th authored resource without changing the eleven fixed numerical code files or seven fixed numerical resources.

## Task Commits

1. **Task 1: sealed run and failure state machine** — RED `44c1be0`, GREEN `a19b99c`.
2. **Task 2: verify current on every open** — RED `5b7d5ad`, GREEN `133da22`.
3. **Task 3: installed real workflow and replay** — RED `06036a1`, GREEN `5e1446c`.

Follow-up correctness commits: `9aced70`, `b778eee`, RED `9c8b3c4`, GREEN `84abac8`, and independent-negative test correction `26c9864`. Plan wording correction `5273a36` was committed by the orchestrator.

## Files Created or Modified

- `brujula/pipeline_v2.py` — accepted-packet bridge, sealed builder, verified current resolver and reconstructive replay.
- `brujula/cli.py` — installed real-data commands, explicit roots and bounded errors; v1 synthetic commands remain separate.
- `brujula/resources.py` and `contracts/publication-manifest-v2.schema.json` — strict publication resource registration and schema.
- `tests/test_pipeline_v2.py`, `tests/test_cli_v2.py`, `tests/test_installed_runtime.py` — receipt, source, artifact, fault, replay and CLI regressions.

## Decisions Made

- The accepted three-opening real model has exactly 73 artifact files. Supported models with fewer openings legitimately have 67, 69 or 71; code derives the exact set from the validated model and rejects extras or omissions.
- CSV replay equality is canonical ordered rows. DuckDB and Parquet replay equality is typed full-row multiset equality, so tied first-column values can reorder without a false mismatch and a changed value still fails.
- Numerical acceptance remains read-only to the publication builder; its audit and the analysis/replay operation audits are separate.
- `--r-lib` remains required because the accepted numerical runtime rejects implicit R libraries.

## Deviations from Plan

### Auto-fixed Issues

1. **[Rule 1 - Bug] Failure receipt for absent accepted receipt.** The analysis operation now records a bounded immutable failure at a valid destination. Commit `9aced70`.
2. **[Rule 1 - Security] Windows junction containment.** A disposable build reproduced an output `runs` junction writing outside the declared root. Ancestry and canonical containment checks now reject that and an analysis-output junction before any write. Commit `b778eee`; independent disposable negatives passed.
3. **[Rule 1 - Bug] Valid sparse opening claims.** A hardcoded 73-file check would reject valid zero-to-two-opening models. Schema and independent expected-name derivation now support 67/69/71/73 while preserving exactness. Commit `b778eee`.
4. **[Rule 1 - Bug] Logical export replay.** Comparing only DuckDB missed CSV and Parquet mutations. All formats are checked; DuckDB and Parquet use full-row typed multisets to avoid a reproduced tie-order false mismatch. Commits `b778eee`, `9c8b3c4`, `84abac8`, `26c9864`.

All corrections are within the planned custody, exact-inventory and replay contract.

## Test Results

- Focused suite: `38 passed in 37.42s` for pipeline v2, CLI v2, v1 CLI regression and installed-runtime resource tests at `26c9864`; `git diff --check` passed.
- Independent reviewer reproduced the junction and CSV negatives before correction, then reran the corrected disposable negatives successfully.
- An isolated installed wheel completed real `research-analyze` and `research-build` from the unchanged eight-source accepted receipt. The final wheel at `26c9864` has the same analyze/build functions, 24 resources and 36 installed dependency versions; the only source change from that wheel is replay logical-row comparison. `research-replay` on the final wheel passed with no network attempts in `.cache/research/phase4-installed-chain/final-replay-command.json`; its immutable receipt `.cache/research/phase4-final-installed-publication-replay/attempts/20260924T001001-c9ecddaaee71.json` preserves numerical `8db575e9…`, analysis `15f5bdc0…` and publication `ff4f7ef1…` digests. Installed HTML, Markdown, PDF and CSV opens passed; 22/22 table and 625-key container readbacks passed under `.cache/research/phase4-installed-readback-20260923/`.
- Four installed `research-open` formats (HTML, Markdown, PDF and CSV) passed, and direct readback passed all 22 tables across CSV, Parquet and DuckDB plus 625 declared container keys. In an isolated custody copy, deleting one required ZIP produced a FAILED offline acquisition receipt (`20260924T002741769026Z-1ee9bcb4edf2`) with no network attempt; the subsequent open exited nonzero with `AcquisitionError`. All 73 original sealed artifacts and the original source, numerical and publication anchors remained unchanged. Evidence: `.cache/research/phase4-installed-readback-20260923/copied-fault.json` and `open-copy-{before,after}.json`.

## Known Stubs

None in the Plan 04-05 runtime paths; final installed replay is a verification gate, not a substitute implementation.

## Next Phase Readiness

Plan 04-06 owns clean Windows and Ubuntu installed-wheel release gates, the 45 edge criteria, and public-safe release evidence. Its CI and edge implementation maps are prepared under ignored `.cache/research/`; they are planning aids rather than runtime dependencies. Plan 04-05's real installed chain and copied-source failure gate are complete; cross-platform release acceptance remains separate.

---
*Phase: 04-offline-publication-and-reproducible-operation*
*Completed: 2026-09-23*

## Self-Check: PASSED

All seven owned implementation/test files and all eleven listed task/correction commits exist. The final installed replay receipt, four CLI open readbacks and isolated source invalidation proof were inspected before completion.
