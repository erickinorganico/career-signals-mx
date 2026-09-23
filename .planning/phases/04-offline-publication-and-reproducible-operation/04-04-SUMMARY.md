---
phase: 04-offline-publication-and-reproducible-operation
plan: 04
subsystem: publication
tags: [spanish-report, svg, png, pdf, weasyprint, evidence, offline]
requires:
  - phase: 04-02
    provides: validated public analysis packet and comparison ledger
  - phase: 04-03
    provides: accepted publication model and figure links
provides:
  - complete Spanish HTML and Markdown research report from one validated public model
  - nine paired SVG and PNG figure groups with semantic tables and A4 print panels
  - local-only searchable PDF renderer with audited staged fonts and exact asset hashes
  - actual desktop, mobile, native-zoom and A4 visual review
affects: [04-05-offline-operation, 04-06-release-verification]
tech-stack:
  added: [weasyprint-70.0, pypdf-6.19.0-audit]
  patterns: [one-editorial-model, exact-local-asset-inventory, print-panel-point-parity]
key-files:
  created:
    - brujula/report_v2.py
    - brujula/pdf_v2.py
    - docs/visual/phase-04-visual-review.md
  modified:
    - tests/test_report_v2.py
    - tests/test_pdf_v2.py
    - pyproject.toml
    - requirements.txt
    - THIRD_PARTY_NOTICES.md
key-decisions:
  - "Render only validated public v2r/v2c/v2k evidence; retain full used IDs in the appendix and raw ledger in joined exports."
  - "Use exact reviewed DejaVu hashes and a complete staged asset hash inventory for offline PDF rendering."
  - "Draw A4 print panels at 6.8-inch physical width and give print tables separate readable columns."
patterns-established:
  - "Every accepted figure point appears once in its declared SVG/PNG set and exactly once across print panels."
  - "Screen and print alternatives share the same public records; absent values remain unavailable with reasons."
requirements-completed: [PUB-01, PUB-02, PUB-03]
duration: 1h22m
completed: 2026-09-23
---

# Phase 04 Plan 04: Complete Offline Research Report Summary

**A full Spanish research report now renders accepted public evidence as HTML, Markdown, nine paired figure groups and a searchable offline A4 PDF.**

## Performance

- **Duration:** 1h22m
- **Started:** 2026-09-23T15:06:17-07:00
- **Completed:** 2026-09-23T16:27:51-07:00
- **Tasks:** 3/3
- **Owned files created or modified:** 8

## Accomplishments

- Rendered the accepted 2024-Q3–2026-Q2 analysis packet in the fixed question-led Spanish sequence, with three opening claims, national and professional scopes separated, all 23 profile measures, eight-quarter comparisons, recorded sex, 32-state availability, 115 other-field codes, limitations, methods, exact sources and a complete keyed appendix for every editorially used record, comparison and claim.
- Paired SVG/PNG figures carry the same validated public values, intervals, status and missingness as semantic HTML/Markdown tables. Print-only panels split long figures without losing or adding points; no unavailable value becomes zero and no unsupported trend segment is drawn.
- Rendered a 97-page A4 PDF from verified HTML bytes and a complete SHA-256 asset inventory. Four reviewed DejaVu TTF files and their full license are staged locally. The fetcher rejects network/data URLs, traversal, symlinks, altered/missing files and unlisted resources.
- Direct browser and PDF inspection covered desktop 1440 px, mobile 390 px, native Chrome zoom 200 % at 720 px, standalone PNG/SVG and representative A4 pages. Document width equaled viewport width in all three browser views; long figures and tables scroll within their regions.

## Task Commits

1. **Task 1: Editorial model, paired figures and semantic report** — RED `3641b63`, GREEN `c602556`.
2. **Task 2: Local-only searchable PDF and audited dependencies** — RED `778a7ed`, GREEN `2a4d468`.
3. **Task 3: Actual visual/security review and fixes** — `6cfc874`.

## Verification

- Focused suite: `.venv/Scripts/python.exe -m pytest tests/test_report_v2.py tests/test_pdf_v2.py -q` — **19 passed** with project-local Fontconfig, Matplotlib and WeasyPrint DLL paths.
- Real packet: SHA-256 `71d9fb7d6ceb20cff39a1a10f8428bcb239629e2e723b6e001816bd6d564bce3`; 6,739 public records, 4,209 comparison entries, 38 accepted claims, zero validation errors. The final report uses 446 records, 141 comparisons and all 38 claims, yielding 625 distinct canonical IDs in each of HTML, Markdown and extracted PDF; no missing/extra IDs or duplicate HTML IDs.
- Independent actual-output readback confirmed all nine SVG/PNG point/interval/status payloads and print-panel unions against the accepted packet, and all 96 printed focal trend comparisons with exact changes, endpoint periods, both sources and keyed appendix references. Spanish text is searchable and fonts are embedded.
- Final local artifacts: HTML `8113128bd78f38f2ad4cab03663543b019d712de9149f1618c8cb94e8e907afd`, Markdown `1492abdc73309e5acc3191ce7e15242223411d71a2ab52375eef9aa662dfc3cc`, PDF `438ac478296fc23c29d04eecb47b4d3bf9bff6ff9815c3cd9781652ac95c1721`. Their visual record is [phase-04-visual-review.md](../../../docs/visual/phase-04-visual-review.md).

## Decisions Made

- Kept the full 6,739-record and 4,209-comparison machine-readable exports outside the narrative PDF; the report prints all editorially used evidence and 96 selected accepted trend differences.
- Staged exact reviewed fonts and hashed every declared report asset before and after PDF rendering, with verified HTML bytes passed directly to WeasyPrint.
- Split screen and print representations only for physical legibility; both use the same public point set and source-qualified evidence references.

## Deviations from Plan

### Auto-fixed Issues

1. **[Rule 1 - Bug] Corrected plotted scope and missingness.** Mixed units/universes, a reversed focal-series legend, null points at numeric zero and ambiguous sex/state alt text were corrected. The plot now groups declared units, uses stable field styles, includes full recorded scope in alternatives, and omits all-null quantitative axes. Regression tests inspect actual artists and labels. Committed in `6cfc874`.
2. **[Rule 1 - Bug] Made the printed evolution and long figures complete.** A screen-only comparison table vanished from PDF, plot typography shrank on A4, and print SVG IDs collided. A dedicated readable comparison table, physical-width print panels and unique panel IDs preserve all accepted changes and exact point unions. Committed in `6cfc874`.
3. **[Rule 2 - Critical functionality] Closed PDF asset races and destination checks.** The fetcher now hashes the exact returned bytes, uses verified HTML content rather than reopening a file, validates the declared asset root before resolving it and rejects unsafe destinations before directory creation. Negative tests cover missing/altered listed assets and path escape. Committed in `6cfc874`.
4. **[Rule 1 - Bug] Fixed actual browser and PDF overflow.** Long source/evidence text and coverage tables widened mobile/zoom pages; forced figure page breaks left almost-empty pages; a nonbreaking income value plus unit invaded the state column. Screen text now wraps, pagination is natural, and print numbers remain intact while units may wrap. The final PDF page 32 was inspected at 1600 px. Committed in `6cfc874`.

**Impact on plan:** All fixes preserve accepted numerical and evidence identities. No new data source, API, service or analysis was introduced.

## Known Stubs

None. The scope scan found no TODO/FIXME/placeholder values in owned report, PDF, test or visual-review files.

## Next Phase Readiness

The local report renderer, paired assets, strict PDF path and visual evidence are ready for offline pipeline integration and release verification. Generated real-data files remain in ignored local staging; Phase 04-05/04-06 own promotion, full release gates, publication metadata and GitHub publication. The parent orchestrator owns STATE, ROADMAP and requirement status updates to avoid concurrent edits.

## Self-Check: PASSED

All nine declared files exist; all five task commits are present; the scoped summary diff has no whitespace errors. The final real HTML, Markdown and PDF hashes match the visual-review record.
