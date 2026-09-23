---
phase: 04-offline-publication-and-reproducible-operation
plan: 02
subsystem: installed numerical acceptance
tags: [wheel, enoe, survey, R, acceptance, replay, reproducibility]
requires:
  - phase: 02
    provides: accepted eight-snapshot numerical digest, public rows, and official benchmarks
  - phase: 03
    provides: analytical reference and guarded production packet builder
  - phase: 04-01
    provides: bundled resources and clean-wheel installation path
provides:
  - installed eight-ZIP numerical acceptance and full offline numerical replay with immutable receipts
  - explicit package code, golden, R-library, source, workbook, and PDF authority
  - independently justified analytical reference rebind and validated installed production packet
affects: [04-04 offline reports, 04-05 sealed publication, 04-06 release verification]
tech-stack:
  added: []
  patterns: [package-owned numerical authority, attempt-specific immutable receipts, clock-free analytical content identity]
key-files:
  created:
    - brujula/enoe_acceptance.py
    - brujula/official_reconciliation.py
    - tests/test_installed_acceptance.py
  modified:
    - scripts/accept_enoe_estimates.py
    - scripts/official_reconciliation.py
    - brujula/analysis_v2.py
    - brujula/findings_v2.py
    - brujula/resources.py
    - brujula/oracle/enoe_survey_oracle.R
    - scripts/enoe_survey_oracle.R
    - contracts/analysis-v2.schema.json
    - contracts/publication-v2.schema.json
    - data/fixtures/enoe-analysis-reference.json
    - tests/test_official_reconciliation.py
    - tests/test_analysis_integration.py
    - tests/test_publication_v2.py
    - tests/test_export_v2.py
key-decisions:
  - Separate seven fixed numerical resources from downstream analysis and publication resources so a reviewed reference rebind does not silently repin numerical trust.
  - Verify raw public packet digests operationally while binding analytical trust to canonical content rather than acquisition timestamps.
  - Require explicit survey and jsonlite package loading from the configured R library at actual oracle execution.
patterns-established:
  - Public acceptance and replay calls create failed or successful current and immutable attempt receipts; unsafe roots fail before filesystem mutation.
  - A replay recomputes all eight snapshots into unique output and audit paths and compares exact public records with its immutable accepted seal.
requirements-completed: []
requirements-addressed: [OPS-01]
duration: approximately 1h from first task commit through final affected tests
completed: 2026-09-23
---

# Phase 4 Plan 02: Installed Numerical Acceptance and Replay Summary

**A fresh wheel executed the approved eight ENOE ZIPs twice, reproduced the accepted digest and public rows exactly, and built the 6,739-record analytical packet only after a guarded reference rebind.** The method remains nonofficial and its precision status remains `REVIEW`.

## Performance

- First task commit: 2026-09-23 13:56 PDT; final affected regression: 2026-09-23 14:55 PDT.
- Tasks: 2/2. The installed numerical acceptance and replay were each run once after the source freeze.
- Final affected Python suite: 114 passed, zero skipped, in 271.26 seconds. It covered installed acceptance/runtime, official reconciliation, ENOE/R, analysis/integration, publication/export, and Phase 3 edge controls. Root separately ran 25 unchanged Node Phase 1–3 controls, all passed.

## Task commits

| Task | Commits | Result |
| --- | --- | --- |
| 1. Move acceptance and official reconciliation into the package | `a0d0364` | Real numerical and official implementations now live under `brujula`; script entry points are thin compatibility wrappers. |
| 2. Establish installed numerical and analytical trust | `c2c2940` RED, `981ce6f` GREEN, `ab01b14` pre-run correctness fix, `244bfe2` post-proof reference rebind | Explicit installed identity, fresh acceptance/replay, guarded historical-reference rejection, and final validated production packet. |

## Installed numerical proof

- Source freeze: `ab01b14`. The first fresh wheel SHA-256 was `933d770d13b2a1af647d1462c2719840aeb17e6fb0b5dab26383d2e39f2230e1`; it was installed under `C:\Users\erick\AppData\Local\Temp\brujula-0402-installed` and invoked outside the checkout. It resolved 11 fixed package code/oracle paths, seven fixed numerical resources, eight current acquisition receipts, R 4.6.1, and survey 4.5 from the explicit `.cache/R-library`. No checkout resource fallback was accepted.
- Fresh acceptance immutable receipt: `.cache/research/phase4-acceptance/audit/attempts/ee11f305-8113-4ff4-855c-bb8727fe89ab.json`, SHA-256 `14f615e7e9dad2aef91e22e270f8d3184be58db10f5051abec15433f3e9d8b9f`. Its numeric digest is the required `8db575e9d664864d1513e3b9658bd9b060c4cb3bed8b51561f208adeb97b9a00`; all eight public record sets equal the historical Phase 2 canonical rows. The 26-case R survey oracle, four analytical R cases, workbook and PDF gates passed.
- Fresh full offline replay immutable receipt: `.cache/research/phase4-replay/audit/attempts/b6ee089e-a08d-4919-ab7d-f1903d2201b4.json`, SHA-256 `2f2821a3f39f22edd037ac0dc47430eb439a40eaa7488e6378d28abc762952fa`. It recomputed all eight source ZIPs into unique attempt paths, preserved the sealed acceptance and source artifacts, and matched exact public documents, numeric digest, source IDs, R cases, workbook and PDF gates. Acceptance/replay attempt IDs and output paths differ.
- Approved workbook SHA-256: `21b45fb76a3f2df336529c3c9ac5cf7543c7d1ded477cc21f77bcc2db8ba267c`; approved PDF SHA-256: `74cfc4f19f98ea25ba20d0e0dc70557855050cc3399bbdc25dd46e066a0b8fca`. Both were checked at entry and immediately before a PASS receipt. Historical Phase 2 and Phase 3 receipts and accepted acquisition current files were not rewritten.

## Analytical guard and reference rebind

- Before any reference change, installed guarded indexing produced 6,739 records. The test-only candidate contained 6,739 records, 4,209 comparisons and 38 claims; validation returned exactly `trusted_reference`, and the production builder rejected it. Evidence: `.cache/research/phase4-analysis/pre-rebind-proof.json`.
- The reference update in `244bfe2` changed only `source_manifest_sha256` after the numerical proof. The old reference SHA-256 was `2ecaf5808db2ec26c38f4d28138dc0af50ca191f5fb0fdb498240f650862a520`; the new one is `56ed548f90a2fc5bea44f051198ca75e414231690cb8509e09e34bf6069a4abe`. The old bytes remain in Git history and `.cache/research/phase4-analysis/old-reference.json`; rebind evidence is `.cache/research/phase4-analysis/reference-rebind.json`.
- The final wheel SHA-256 was `8692850c568d38ae6c74e64f8beabdaa1ccecc0cc55337c2ff8c6621407a782d`. Its installed production builder wrote `.cache/research/phase4-analysis/analysis.json` (SHA-256 `71d9fb7d6ceb20cff39a1a10f8428bcb239629e2e723b6e001816bd6d564bce3`). Reloading that persisted JSON yielded zero validation errors, 6,739 records, 4,209 comparisons, 38 claims, unchanged three opening IDs and content digest `15f5bdc0fb366f9b3ae75c1c0b096aed1f7b1f4e7f8b71b514f62133ea8dddca`. Machine receipt: `.cache/research/phase4-analysis/receipt.json`.

## Decisions and deviations

**[Rule 2 - Missing critical functionality]** Public `accept()` and `replay()` now own successful and failed attempt receipts and invalidate `current` on failure. Immutable complete receipts preserve prior PASS manifests; distinct attempt output roots and ancestry checks prevent a replay or failed run from altering source or historical evidence. The fixed seven-resource numerical authority excludes downstream analytical/publication schemas and the reference, while a final resource check catches drift during a long run. Verified by negative and replay tests; committed in `981ce6f` and `ab01b14`.

**[Rule 1 - Bug]** The R oracle previously allowed `survey` or `jsonlite` to load from another library despite an explicit configured path. Both compatibility and package oracle now load with `lib.loc=lib`; preflight records the actual Rscript SHA/version and package paths/versions, and the end gate rechecks benchmark hashes. The explicit-library RED test in `c2c2940` failed before the fix and passed after `981ce6f`; benchmark drift was fixed in `ab01b14`.

**[Rule 1 - Bug]** Acquisition `acquired_at` changed raw `public_v2_digest` on identical ZIP bytes. The raw digest remains verified in the numerical/index receipts; the analytical source manifest and its two strict schemas now use canonical public content and source/method identities without that clock. A synthetic clock-only regression confirms identical valid analytical packets, while changed value/source/method still rejects. Committed in `981ce6f`.

**[Rule 2 - Missing critical functionality]** Package resource resolution and golden/code checks were tightened to reject checkout fallback, old script inventories, altered executing modules/oracle and caller repinning. The independently pinned package golden and LF-canonical 11-path code manifest remain active through indexing and production validation. Committed in `981ce6f`.

The independent static pre-run review reported no remaining material source blocker at `ab01b14`. Its separate review note is maintained by the reviewer. No external service configuration or paid inference was required.

## Next phase readiness

The immutable numerical receipts and validated real packet are ready for offline publication and sealed replay. This plan establishes the numerical part of OPS-01; publication-level run/current invalidation and end-to-end release verification remain with later Phase 4 plans. The real report may cite these artifacts while preserving nonofficial `REVIEW` and visible precision limitations.

## Self-Check: PASSED

The named source, proof, packet, and receipt files exist; task commits `a0d0364`, `c2c2940`, `981ce6f`, `ab01b14` and `244bfe2` resolve in Git. The final affected suite passed with zero skips, and no source code changed after the numerical freeze.
