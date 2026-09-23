---
phase: 04-offline-publication-and-reproducible-operation
reviewed: 2026-09-23T23:20:46Z
depth: deep
files_reviewed: 4
files_reviewed_list:
  - brujula/report_v2.py
  - brujula/pdf_v2.py
  - tests/test_report_v2.py
  - tests/test_pdf_v2.py
findings:
  critical: 0
  warning: 0
  info: 0
  total: 0
status: clean
---

# Plan 04-04: Renderer code review

This bounded rereview covers the final renderer and PDF code, focused tests, the public-model boundary, and the Phase 4 editorial contract. Source SHA-256: `report_v2.py` `3c928c1e957042ba14a2fc0def98f80b44fc5c4e1db476a836bbe53ce656e471`; `pdf_v2.py` `2194911d18cd78457a3961ab43b6dc7d0415131730f141b9e41a6fc114eeda16`. Test SHA-256: `test_report_v2.py` `8cb5c3903cf3715721944e9e9418364e1bffc7d1d750c84d2ac3263fa8824583`; `test_pdf_v2.py` `4d73bb2bdb739551c40367323246865380f7ffc75a7c5bab965cb9e1e8e4742b`. I independently ran `.venv/Scripts/python.exe -m pytest tests/test_report_v2.py tests/test_pdf_v2.py -q` under the reviewed local WeasyPrint DLL/font configuration: `18 passed in 9.14s`. This code review does not certify the real-data visual/PDF artifact, which is being inspected separately.

## Narrative Findings (AI reviewer)

No open code, security, or material contract finding remains in these four files at the recorded hashes. The four original findings and the root-symlink follow-up have the bounded closure evidence below.

## Final renderer delta

The accepted trend comparison rows now share the same sorted public `trend[0]['comparisons']` list across screen HTML, Markdown and the PDF print table (`brujula/report_v2.py:643-670`). Each row formats only its accepted `absolute_change` and declared unit, with the comparison type, both periods, status, source IDs and short evidence reference. The print helper resolves its endpoint sources through the public model (`:407-431`); no new difference or interval is calculated there. The full canonical comparison ID remains in the evidence index, and the table keeps the no-significance caveat.

Standalone plot annotations now derive source IDs and periods from the exact plotted public points, with explicit project precision wording (`brujula/report_v2.py:287-304`). The revised labels use recorded-sex text in the sex figure, declared unit labels on axes, a categorical limit that includes a missing first row, and wrapped titles (`:231-285`). Print panels still declare their record-ID union and namespace inline SVG IDs (`:334-353`). HTML source links, figure captions and long evidence IDs gain wrapping; print CSS allows natural pagination while retaining repeated table headers (`:500-525`). These code observations and the focused test result are bounded to the hashes above; actual page clipping, glyphs and source visibility require the separate visual/PDF readback.

## Resolved findings from the first review

- **CR-01 · BLOCKER · RESOLVED** (`brujula/pdf_v2.py:85-93,135-145`): The fetcher now hashes the exact `content` bytes returned to WeasyPrint after its path check. The initial HTML is read through that fetcher, decoded from verified bytes, and passed as `HTML(string=..., base_url=...)`; it is not reopened through `HTML(filename=...)`. `tests/test_pdf_v2.py` includes a deterministic swap-after-path-check negative and a verified-HTML-string test. The former reproduction would now raise `PDF asset changed during read`.
- **CR-02 · BLOCKER · RESOLVED** (`brujula/report_v2.py:228-234,240-270`): All-null trend panels hide the quantitative y-axis; all-null point panels hide the x-axis and bottom spine. Both show an unavailable explanation, and `test_fully_unavailable_panel_has_no_quantitative_scale` checks the zero-line point case. The semantic table path remains present.
- **WR-02 · WARNING · RESOLVED** (`brujula/report_v2.py:384-409`): The PDF print table now displays each row's `source_id` beside its short evidence reference. Multi-period rows retain source identity even when the caption lists several sources.
- **WR-01 · WARNING · RESOLVED** (`brujula/report_v2.py:329-369`): Figure alt text names universe, period, unit, source and unavailable count, then identifies the first and last supported public values of each display group with the full field, population, geography, recorded-sex, period, metric, value and source scope. The previously ambiguous state/sex examples now distinguish the points. `test_alt_distinguishes_state_and_recorded_sex_values` exercises two equal-grain values with different state/sex labels, and the final focused report tests passed 8/8. Exact detail remains in the semantic table.

The root-symlink check introduced at `brujula/pdf_v2.py:113-120` rejects a leaf symlink for both `asset_root` and `html_path` before `resolve()`, closing the previously observed bypass where `render_pdf()` resolved the root before constructing `LocalOnlyFetcher`. A live symlink negative could not run in this Windows sandbox (`WinError 1314`, symbolic-link privilege unavailable); the branch was inspected directly. The packaged font/notice hashes in `report_v2.py` still match `.planning/research/FONT-ASSET-AUDIT.md`.

_Reviewer: independent Plan 04-04 code/security review. No source files or Git state changed._
