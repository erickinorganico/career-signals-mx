# Editorial contract for the offline report

Status: design decisions for Phase 4 implementation, not a rendered or accepted report.
Authority: the full real-data publication scope and `04-CONTEXT.md`.

## Reader and argument

Write in Spanish for a reader deciding what the survey can tell them about work
among people with completed professional studies. Begin with a useful question,
then a supported answer, its scope, and its evidence. Do not lead with software
architecture, test counts, JSON, or a universal ranking of careers.

The cover names Brújula Laboral MX, the eight-quarter window, and the publication
version. Separate the observation period from the build date. Explain the
known-age completed-professional cohort near the first finding; the national
operational 15+ context has its own label. A visible method note says uncertainty
uses the project's approximation and is not official INEGI precision.

Select no more than three opening findings from the accepted claim registry.
Each opening finding links to its figure or table, precise universe, period,
record/comparison keys and limitations. If fewer findings pass, publish fewer;
the layout must not demand invented copy or replacement numbers.

## Reading sequence

1. Cover and supported findings: what can the evidence answer?
2. How to read the report: field of study versus occupation, null versus zero,
   nominal income, observed sample size and uncertainty.
3. National context and the professional cohort, kept as distinct populations.
4. Three complete field profiles in a fixed order: Derecho, Comunicación y
   periodismo, Ciencias políticas. Use official catalog labels in evidence.
5. Eight-quarter evolution with visible gaps, adjacent-quarter seasonality and
   like-quarter annual comparisons. Never connect a line across a null cell.
6. Recorded-sex and territorial contrasts, with all 32 state availability rows.
   Baja California (`02`) is a declared descriptive reference, not a benchmark
   of success; unsupported reference cells block the corresponding contrast.
7. Other identifiable fields, ordered by official classification code rather
   than an implied best-to-worst ranking.
8. Coverage, exclusions, limitations, methods, exact sources and reproducibility.

## Visual system

Use a quiet editorial page with ample margins, a strong title, short paragraphs
and genuine tables. No dashboard tiles, decorative gauges, stock photographs,
gradients, or maps requiring additional unreviewed geographic files.

- Paper/background: `#FFFFFF`; text: `#172B3A`; secondary text: `#405464`.
- Main data: `#145A66`; secondary series: `#A34F23`; unavailable: neutral gray
  with text or a pattern. Encode states with labels and shapes as well as color.
- Typography: evaluate the installed DejaVu Sans regular/bold and DejaVu Serif
  regular/bold family from Matplotlib. Use Serif for major editorial headings,
  Sans for body, tables and plots. Preserve `LICENSE_DEJAVU` for shipped fonts.
  Final font hashes, Spanish glyphs and PDF embedding remain acceptance checks.
- HTML body: at least 17 px with 1.55 line height and a bounded reading width.
  Tables may use a labeled horizontal-scroll container on small screens, without
  causing whole-page horizontal overflow. At 200% zoom, prose remains readable.
- PDF: A4 portrait, approximately 18–20 mm margins, 10.5–11 pt body text and
  1.4 line height. Repeat table headers. Keep section headings with following
  content, avoid split figure/caption groups and orphaned table labels. Page
  footers show a short title, publication version and page number.

Verify actual contrast ratios and rendered layout; color choices and font sizes
alone are not evidence of accessibility conformance.

## Figures and tables

Prefer point-and-interval plots for supported latest-quarter values, line plots
for comparable national series, and a compact availability matrix for sparse
territorial results. Income and rates use separate scales and explicit units.
Do not use bars with truncated baselines, dual axes, or a decorative map to hide
missing states. Show the known-positive-income coverage beside income means.

Every figure has a stable figure key, a reader question as its title, a caption
with universe/period/unit, explicit uncertainty and method, a semantic data
table, and source/evidence links. SVG and PNG represent the same data. Alternative
text summarizes the supported pattern and missingness without introducing a new
number or retrieving an internal diagnostic. Tables retain null/status/reason.

Long machine-readable detail belongs in joined public exports and appendices.
The main narrative may select a declared subset for legibility, while preserving
all required profiles and coverage. Selection cannot conceal a suppressed cell
or change a denominator. Technical IDs should be available in evidence tables
without overwhelming the opening narrative.

## Acceptance evidence

Inspect the actual real-data report at mobile width, desktop width, 200% zoom
and printed A4 pages. Check cover, all three profiles, sparse-state coverage,
long tables and references; inspect PDF pages near each section transition.
Check Spanish accents, searchable text, repeated headers, no clipped labels,
and stable correspondence among claim, chart, table, export and PDF values.

The renderer accepts only the approved analytical/public packet. No rendering
path may access diagnostic estimates, fill nulls by complements, infer missing
values, or create unsupported prose. Record visual findings and fixes alongside
automated cross-format validation; successful PDF generation alone is not a
visual acceptance result.

## Verified preparation

The [font and contrast audit](../../research/FONT-ASSET-AUDIT.md) records exact DejaVu Sans/Serif regular/bold hashes, Spanish glyph coverage, embedding flags, the full-notice obligation and calculated color ratios. Use those reviewed local candidates during implementation; final embedding and rendered inspection remain required.
