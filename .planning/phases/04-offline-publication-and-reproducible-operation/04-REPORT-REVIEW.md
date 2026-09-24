# Report implementation review

2026-09-23. Root review began with the first renderer draft at `c602556`.
All twelve findings are now closed by corrected source, focused regression
and actual real-data artifact readback described below. This accepts the
bounded Plan 04-04 renderer; installed publication integration, cross-platform
CI and final release remain separate gates.

| ID | Initial finding | Required evidence for closure | State |
|---|---|---|---|
| R01 | National, focal, sex and trend plots share one numeric scale across percent and nominal MXN. Null points are placed at data coordinate zero. | Separate metric/unit axes or panels within the same canonical figure; unavailable marks outside numeric coordinates; gap-aware ordered trends; exact figure point membership/value tests. | Closed |
| R02 | Mandatory report tests read the ignored real packet directly. | Portable independently pinned synthetic fixtures with explicit synthetic labels; separate real acceptance; clean-source run without `.cache` data. | Closed |
| R03 | Mixed-population and recorded-sex tables omit those dimensions. | Explicit population/sex row labels or clearly separated homogeneous tables; exact universe and evidence keys retained. | Closed |
| R04 | Coverage section contains generic prose only; evidence appendix does not include all profile/detail rows printed elsewhere. | Accepted coverage counts/reasons with overlapping profile appearances identified; full cited-row/key union and complete 23-metric profiles. No invented exclusion count. | Closed |
| R05 | Print CSS hides canonical plots before print panels exist and uses 6.7/5.6 pt dense tables. Long identifiers break across lines. | Complete canonical/print-panel point union, readable compact tables, short evidence links and full unbroken appendix identifiers; actual A4/mobile/native-zoom inspection. | Closed |
| R06 | Font staging compares against a freshly computed source hash only. | Independent reviewed font/notice hashes enforced on both package and copied bytes; changed package/staged file negatives and actual PDF embedding. | Closed |
| R07 | Standalone synthetic figures lack a synthetic notice; the cover says build date is unavailable. | Explicit synthetic notice in every applicable standalone figure; actual build date separate from observation window and excluded from canonical reproducibility identity. | Closed |
| R08 | Evolution shows levels and generic caveats without the accepted adjacent/annual descriptive changes. | Legible tables or canonical comparison claims over declared trend comparison links, with exact accepted delta/unit, endpoints/type, non-significance caveat and full v2c evidence. Blocked deltas remain unavailable; the full 4,209-slot ledger stays in exports. | Closed |
| R09 | The initial PDF fetcher allows names without expected hashes and checks only font bytes; destination parent creation precedes containment validation. | Exact path-to-SHA inventory checked for every asset before/fetch/after rendering, changed nonfont and missing listed asset negatives, and unsafe output rejection before filesystem writes. | Closed |
| R10 | The revised trend draft assigns markers in ascending field-code order but its fixed legend names Derecho first, reversing Derecho and Ciencias políticas. | Explicit field-code-to-style mapping or legends generated from actual labeled artists; regression asserting each field's marker/color/label agrees. | Closed |
| R11 | Actual native 200% browser zoom exposes a 900 px coverage table outside a scrolling container, expanding a 720 px viewport document to 922 px. | Responsive compact coverage tables or contained scrolling; final desktop/mobile/native-zoom document width equals viewport and actual captures remain legible. | Closed |
| R12 | Actual standalone PNGs use raw sex codes without labels, English unit names, and omit visible period/source attribution outside the HTML caption. | Human recorded-sex labels, Spanish units with nominal income basis, and visible actual-point periods/INEGI source/project-precision annotation in standalone SVG/PNG and print panels; inspect all nine graphics after the shared annotation change. | Closed |

The independent [renderer code review](04-RENDERER-CODE-REVIEW.md) additionally
reproduced an exact-byte PDF fetch race and an invented numeric axis on an
all-null panel, and identified incomplete figure alternatives and print-row
source identity. Its four findings have separate closure on corrected
source hashes and regression checks. The initial visual inspection is not a
substitute for that code review.

The real expected readback was derived independently from the accepted packet
at `.cache/research/phase4-report-review/expected-report.json` (ignored
preparation, not publication acceptance). The source packet SHA-256 is
`71d9fb7d6ceb20cff39a1a10f8428bcb239629e2e723b6e001816bd6d564bce3`;
its analytical digest is
`15f5bdc0fb366f9b3ae75c1c0b096aed1f7b1f4e7f8b71b514f62133ea8dddca`.
The validated publication model digest is
`ff4f7ef1c34927812c15488d46220edd2cebb55378c264827c15b378970a385e`.
Nine figure groups contain 6, 9, 72, 12, 32, 115, 1, 1 and 1 records;
the trend group has one unavailable point and the other-fields group has 31.
Those missing values must remain unavailable throughout every representation.

## Final root readback

The accepted real render has HTML SHA-256
`8113128bd78f38f2ad4cab03663543b019d712de9149f1618c8cb94e8e907afd`,
Markdown `1492abdc73309e5acc3191ce7e15242223411d71a2ab52375eef9aa662dfc3cc`
and PDF `438ac478296fc23c29d04eecb47b4d3bf9bff6ff9815c3cd9781652ac95c1721`.
The PDF contains 97 A4 pages. All three formats contain the same 625 canonical
identifiers, with no missing/extra identifiers or duplicate HTML IDs. Spanish
search strings survive extraction, no replacement characters or blank text
pages occur, and all three used PDF font faces have embedded descendant fonts.

Root independently parsed all nine SVG and PNG metadata payloads and compared
public values, intervals, status and suppression reasons against the accepted
packet. Every ordered print-panel record union also matches. The 96 printed
trend comparison rows retain their exact accepted formatted change, both
periods, both source IDs and an appendix reference. All 25 renderer-returned
file hashes match actual bytes. These checks close R01, R03, R04, R08 and R10
alongside the focused regression and reviewed implementation.

Root viewed all 97 pages in contact sheets and inspected representative pages
at higher resolution: long opening labels, income rows and comparison table,
recorded-sex labels, first unavailable other-field row, and evidence appendix.
The final income fix was rechecked on pages 4 and 32: numeric tokens remain
intact while nominal units wrap inside their own column, clear of REVIEW.
The earlier isolated evidence/continuation pages, clipped subplot titles and
unavailable-label overlap are resolved. Panel pages intentionally retain space
to keep each plot readable. This closes R05 and R12.

Browser readback used isolated Chromium 151.0.7922.34, offline, with no remote
requests: desktop viewport/document width 1440/1440, mobile 390/390, and actual
native zoom 2.0 with CSS zoom 1 and viewport/document width 720/720. Captures
cover the opening, context, evolution, sex/entities, other fields and evidence.
The native zoom was set/read through the browser tab API, not simulated with
CSS. These checks close R11. Their HTML hash was
`42ff1dd744dabdba9015fe173f5d6b1e5b12513ee1c052043dab5bd1d5d08784`;
the only later change splits the number and unit within hidden print-table
markup. Screen CSS, screen tables and figure bytes are unchanged, so their
browser inspection is reused for this explicit unchanged boundary.

The independent code review closes the exact-byte PDF fetch race, all-null
axis, ambiguous alternative text and print-source findings. The final tiny
print-only delta was reviewed directly by root: `_html_table` formats the
same public number with the same `_number` precision and declared unit, in
separate spans, without changing source selection or calculations. Final
`report_v2.py` SHA-256 is
`1b66bc45f956d0bba95ef714a109e09b65f045b5652abed527ce3b6ffbb3b900`;
`test_report_v2.py` is
`b553d7086710274fedf71a23324d79452d9a9fabc1906a11757e5e737c79f266`.
The PDF implementation and PDF test hashes remain those in the independent
review. The executor's final focused run has 19 passing tests, including the
new income-wrap regression. Portable pinned synthetic inputs, explicit
synthetic annotations, independent five-font/notice pins, build-date display
and fatal exact asset guards close R02, R06, R07 and R09.

Ignored local supporting receipts are `final-print-document-readback.json`,
`final-print-evidence-readback.json`, `browser-accepted/receipt.json`,
`native-accepted/receipt.json` and `pdf-accepted/` under
`.cache/research/phase4-report-review/`. Public-safe visual evidence is recorded
in [the visual review](../../../docs/visual/phase-04-visual-review.md).
This is not PDF/UA certification or a final release designation.

Canonical GSD `verify-summary` passed for 04-04. After the report commit,
the active Wave 2 post hooks `verify.schema-drift`, `verify.codebase-drift`
and `ui.safety-gate` all returned `block: false`; no remapping was requested.
Plan 04-05 structure and frontmatter validation also passed with no warnings
before its execution began. Phase 4 remains in progress at four of six plans.
