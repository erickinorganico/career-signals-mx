---
phase: 04-offline-publication-and-reproducible-operation
verified: 2026-09-24T20:47:38Z
status: human_needed
score: 5/5 must-haves verified
overrides_applied: 0
human_verification:
  - test: "Inspect the sealed offline report at desktop, mobile width, 200% zoom and A4 print size"
    expected: "Spanish prose, semantic tables and figure labels remain readable without clipping; source and uncertainty context remain visible"
    why_human: "The existing agent visual inspection is documented, but the GSD verification gate reserves visual appearance for a human decision"
---

# Phase 4: Offline Publication and Reproducible Operation Verification

**Phase goal:** Readers receive consistent, evidence-bound offline research outputs from a sealed run that can be replayed and whose current status fails closed.
**Status:** human_needed. All five codebase truths are verified; visual appearance still needs the developer's decision under the GSD verification gate. The separate Phase 5 release gate is outside this verdict.
**Mode:** Initial verification. No earlier `04-VERIFICATION.md` or overrides existed.

## Goal achievement

The five roadmap criteria are the governing truths. The 45 detailed Phase 4 edge criteria and additional PLAN truths were checked as refinements of these five outcomes; their individual assertion mapping and results are in `04-VALIDATION.md`. This verdict is based on implementation and observed artifacts, not SUMMARY claims.

| # | Roadmap truth | Status | Direct evidence and bounded observed result |
|---|---|---|---|
| 1 | Spanish question-led offline HTML, equivalent Markdown, printable PDF, supported claims and complete editorial sections | VERIFIED | `brujula/report_v2.py` builds one editorial document and emits HTML/Markdown, figures and semantic tables; `brujula/pipeline_v2.py:229-254` renders PDF from those staged local assets. The sealed run has nonempty HTML/Markdown and a 1,048,093-byte PDF. `docs/visual/phase-04-visual-review.md` records direct page/browser inspection and 625 shared record/comparison/claim keys. |
| 2 | SVG/PNG and semantic tables legible at print, mobile and 200% zoom with units, uncertainty, universe, source and state | VERIFIED | Renderer emits paired SVG/PNG and print tables from the same figure points; source/uncertainty text and responsive/print CSS are in `brujula/report_v2.py`. The visual review records 1440 px, 390 px, 200% zoom and A4 inspection, including corrected print tables and figure clipping. This is a bounded visual review, not PDF/UA certification. |
| 3 | Joinable CSV, Parquet and DuckDB aggregates preserve dimensions, nulls, precision and provenance | VERIFIED | `brujula/export_v2.py:179-232` validates the public model, creates typed DuckDB tables, exports 22 CSV and 22 Parquet tables and a column/key dictionary, then atomically exposes the directory. Actual sealed run has 6,739 record rows plus header and 249 nonempty figure-record links. `04-INTEGRATED-OPERATION.md` records independent all-table typed readback and nonempty figure/claim links; the real record-order permutation retained 22 byte-identical CSV tables. |
| 4 | Suppressed internal cell and diagnostics absent in every public representation | VERIFIED | `brujula/publication_v2.py:78-135` accepts only a validated Phase 3 packet and validates record/claim/figure references; render/export validate the resulting public model. `tests/phase4_prohibitions.py` drives the same suppressed-record canary through emitted HTML, Markdown, PDF text, SVG/PNG metadata, CSV, Parquet and DuckDB. The four deliberate bad fixtures failed before clean controls passed (`04-VALIDATION.md`); no internal numeric fallback is present in the inspected render/export path. |
| 5 | Documented offline CLI refresh/replay, sealed manifest before current promotion, failure receipts and live invalidation | VERIFIED | `brujula/cli.py` exposes refresh, acceptance, analysis, build, replay and verified open commands. `brujula/pipeline_v2.py:277-430` journals under `BuildLock`, writes immutable receipt and manifest before current; `:433-510` verifies exact inventory, hashes, acceptance and all eight live acquisitions twice on each open. Actual installed interruption exited 17, recovered an immutable BLOCKED receipt, then built and opened a fresh run (`04-INTEGRATED-OPERATION.md`). A later failed required acquisition blocked installed open while historical artifacts remained unchanged (`04-WAVE3-CHECKS.md`). Installed reconstruction on unchanged replay implementation passed with receipt SHA-256 `825d9d1122b953578b49ce40a9b7cf1b179444149aa69798b701106fcddaa2e8`. |

**Score: 5/5 roadmap truths verified.** No override or deferred Phase 4 failure was used.

## Required artifacts and wiring

| Artifact | Existence and substance | Wiring / data flow |
|---|---|---|
| `brujula/resources.py`, `pyproject.toml`, authored oracle/fonts | Present; typed installed resources, wheel package data and PDF dependency are substantive. | Installed acceptance, renderer and PDF use packaged resources. Outside-checkout helper checks 24 authored resources and installed font/PDF behavior on Windows and Ubuntu; `docs/evidence/phase-04-publication-acceptance.json` records both hosted results. |
| `brujula/enoe_acceptance.py`, `brujula/analysis_v2.py`, `brujula/findings_v2.py` | Present; code hashes, source/benchmark checks, numerical replay and guarded analysis are implemented. | `pipeline_v2.analyze_acceptance` consumes immutable acceptance and accepted public/audit payloads to build a validated packet. Installed real eight-source acceptance and replay receipts are in `04-WAVE3-CHECKS.md`; unchanged numerical identities were reused under their recorded hashes. |
| `brujula/publication_v2.py`, `contracts/publication-v2.schema.json` | Present; model is derived from and revalidated against a guarded analysis packet, with checked reference sets. | `pipeline_v2.build_publication` calls `build_publication_model`; both `report_v2` and `export_v2` consume the model. Actual run has nonempty records, comparisons, claims and figure joins. |
| `brujula/report_v2.py`, `brujula/pdf_v2.py` | Present; question-led content, semantic tables, figures, print CSS and local-only asset fetcher are implemented. | `pipeline_v2._render` calls both, checks declared figure/font inventory, then hashes staged output. Actual HTML/Markdown/PDF and nine figure pairs exist; human visual review is recorded separately. |
| `brujula/export_v2.py`, `contracts/publication-manifest-v2.schema.json` | Present; typed 22-table export, dictionary, exact manifest schema and null/precision rules are substantive. | `pipeline_v2._render` invokes exporter; `_expected` and `_inventory` enforce complete artifacts before seal and on open. Actual 73 content hashes were recomputed in this verification with zero mismatches. |
| `brujula/pipeline_v2.py`, `brujula/cli.py`, `tests/test_phase4_edge_acceptance.py`, `tests/phase4_prohibitions.test.cjs` | Present; operational functions and CLI dispatch are substantive; controls map the 45 edge criteria and four prohibitions. | CLI build/open/replay paths invoke pipeline; phase controls run in repository verification and hosted CI. No orphaned Phase 4 product artifact or key link was found. |

The current installed publication is run `20260924T010247-81cfb71ea5f1`. I directly read its `current.json`, recomputed `manifest.json` SHA-256 `38c3dfc21d816f32d7e4a21d7efd89418fc198fd80e94577783706f00d7fb023`, checked all **73** declared content SHA-256 values (zero mismatches), and matched the immutable receipt hash `1b2e2c228700c8491ea7ee2c1d489fb7af5cc603e1da40ba610d7144dcf5cbe1`. It records eight source dependencies and public digest `ff4f7ef1c34927812c15488d46220edd2cebb55378c264827c15b378970a385e`. The status `REVIEW` is the truthful nonofficial statistical designation; build status is `SUCCEEDED`.

## PLAN detail and requirements coverage

| Requirement | Plans | Resolution | Evidence |
|---|---|---|---|
| PUB-01 | 04-04, 04-06 | SATISFIED | Report/editorial source, actual three supported opening claims, eight-quarter sections and reviewed HTML/MD/PDF. All six PUB-01 edge assertions passed in the 46-test exact map. |
| PUB-02 | 04-01, 04-04, 04-06 | SATISFIED | One model renders three offline formats; local fetcher rejects remote/unsafe assets; installed native Spanish searchable PDF passed on both hosted OS jobs. Five PUB-02 edge assertions passed. |
| PUB-03 | 04-04, 04-06 | SATISFIED | Paired figures, semantic tables, responsive/print layout and actual browser/A4 review; six PUB-03 edge assertions passed. |
| PUB-04 | 04-03, 04-06 | SATISFIED | 22 typed public tables in all three containers, dictionary and nonempty keys; seven PUB-04 edge assertions and real permutation/readback passed. |
| PUB-05 | 04-03, 04-04, 04-06 | SATISFIED | Validated projection feeds renderer/exporter; six PUB-05 edge assertions and all-format nested suppression canary passed, with fail-first bad fixtures. |
| OPS-01 | 04-01, 04-02, 04-05, 04-06 | SATISFIED | Installed CLI, separate source/acceptance/analysis/run identities, real acceptance/replay and documented canonical digests; five OPS-01 edge assertions passed. |
| OPS-02 | 04-05, 04-06 | SATISFIED | Receipt/manifest before pointer, exact 73-artifact seal, crash recovery and immutable history; five OPS-02 edge assertions passed. |
| OPS-03 | 04-05, 04-06 | SATISFIED | Live eight-source and hash check on open, installed later-acquisition failure and preserved history; five OPS-03 edge assertions passed. |

All eight Phase 4 requirement IDs are claimed by plans and represented in the roadmap. No Phase 4 orphaned requirement was found. The 45 individual boundary, adjacency, empty, encoding, ordering, precision, idempotency and concurrency PLAN truths resolve to VERIFIED within the exact behavior map in `04-VALIDATION.md`; the additional plan truths resolve through the artifact/link evidence above, the installed real chain and the cross-platform fixture lane. The synthetic edge fixtures alone do not prove the real eight-quarter output; the installed real run and real permutation checks supply that separate evidence.

## Behavioral spot checks, probes and anti-patterns

| Check | Result |
|---|---|
| `.venv/Scripts/python.exe -m brujula --help` | Exit 0; refresh, acceptance, analysis, build, replay and verified open commands are exposed. |
| Direct sealed-run inventory/hash check | 73/73 content files match manifest, receipt hash matches manifest, eight source dependencies; PDF nonempty. |
| Direct public join check | `public-records.csv` has 6,739 data rows; `figure-record-links.csv` has 249 data rows. |
| Hosted Windows/Ubuntu installed fixture/PDF lane | Public acceptance receipt records both PASS on run 36050222714. A direct `gh run view` from this sandbox was denied socket access; this report does not claim an independent GitHub API requery. From that CI commit to current HEAD, `git diff --name-only` shows documentation/planning changes and no Phase 4 implementation or CI/helper source changes. |

No Phase 4 plan declared a `probe-*.sh` path, and none was found for this phase; Step 7c does not apply. An anti-pattern scan of Phase 4 product modules, CLI, helper and workflow found no unreferenced `TBD`, `FIXME` or `XXX`, implementation placeholder, or empty-handler marker. The full 592-test suite, 46 exact edge checks and 30 Node controls are recorded in the acceptance artifact and `04-VALIDATION.md`; they were not rerun here because their inputs were unchanged and the actual sealed inventory was independently rechecked.

## Human verification and limits

The agent visual checks were completed and recorded in `docs/visual/phase-04-visual-review.md`: local browser at desktop/mobile/200%, A4 raster pages, long tables, figure labels and Spanish text. This is strong technical evidence, but the GSD verifier instruction treats visual appearance as a human verification item. The review explicitly does not certify PDF/UA or complete screen-reader accessibility. Final public release inventory, licensing and publication approval are Phase 5 criteria, not deferred failures of Phase 4.

### Human verification required

**Test:** Open the sealed offline HTML at desktop, mobile width and 200% browser zoom; inspect the A4 PDF, its wide tables and all nine figure groups at print size.

**Expected:** Spanish prose and figures remain readable without clipping or overlap; semantic tables, units, uncertainty, universe, source and status are visible.

**Why human:** Visual readability is a subjective appearance judgment. The existing agent review and raster/browser evidence narrow the check, but do not constitute the developer's acceptance.

_Verified: 2026-09-24T20:47:38Z_  
_Verifier: gsd-verifier; no commit made._
