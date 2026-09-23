# Feature Landscape: Brújula Laboral MX, final research release

**Domain:** Reproducible, static Mexican labor research by field of study  
**Researched:** 2026-09-22  
**Confidence:** HIGH for project requirements and official ENOE concepts; MEDIUM for editorial priority (product judgment).  
**Scope:** v1.0.0 publication with real official data. The synthetic v0.1.0 remains a technical fixture, not the final result.

## Table Stakes

Missing any P0 item prevents a defensible final publication. “Complexity” includes statistical validation, not just coding.

| ID | Feature | Why readers or reviewers need it | Complexity | Acceptance boundary |
|---|---|---|---|---|
| F01 · P0 | Eight official ENOE quarterly snapshots, 2024-Q3–2026-Q2 | Trend coverage explicitly requested | High | Each quarter has approved official URL, terms, package inventory, source version, SHA-256 and receipt; missing quarter is visible and blocks the eight-quarter claim. |
| F02 · P0 | Declared populations and field classification | Prevents confusing career studied, job held and advanced degrees | High | National 15+ context and a separate completed professional-study population (`CS_P13_1=7`, `CS_P16=1`), with age/residency rules, period-specific CMPE catalog and denominators. |
| F03 · P0 | Three detailed field profiles plus official field comparators | Answers the core field-of-study question without a universal ranking | High | Derecho (`0331`), Comunicación y periodismo (`0321`), Ciencias políticas (`0313`) receive profiles; other identifiable CMPE fields appear as labeled context only where support permits. Confirm source codes per quarter. |
| F04 · P0 | Design-aware estimates and suppression | ENOE is a complex sample, so point estimates alone overstate certainty | High | Quarterly weight, strata and UPM; observed sample support, SE, 90% CI, CV, coverage and project suppression reason travel with every eligible estimate. Independent R and official-margin checks precede release. |
| F05 · P0 | Labor outcomes with explicit universes | A field profile needs interpretable work conditions | High | Occupation, participation, unemployment, positive known monthly income, main-job informality, sex composition and verified working conditions; each metric states numerator, denominator, nonresponse and unit. Omit an unverified metric visibly. |
| F06 · P0 | Descriptive quarter-by-quarter change | Readers need to see direction and gaps across eight cuts | High | A period pair gets a numeric delta only after source, universe, geography, concept, method, price basis and classification pass comparability; no independence-based significance test across rotating samples. |
| F07 · P0 | Sex and territorial views with coverage limits | Aggregate estimates can hide uneven outcomes | High | National sex breakdown and defensible geographic domains; unavailable or imprecise cells show an explicit reason, never zero. `SEX` is described as recorded sex, not gender identity. |
| F08 · P0 | Reader-first report in Spanish | The synthetic table dump is not a finished research product | Medium | Opening scope/status, at most three evidence-backed findings, national context, repeated field profiles, trends, limits, methods, sources and data appendix. Every finding links to an estimand and source. |
| F09 · P0 | Offline HTML, Markdown, PDF and figures | Reader must read, print, cite and share without installing code | Medium | Same validated run produces semantic HTML, equivalent Markdown, print PDF, SVG and PNG; PDF is required for this milestone and records source HTML/version/hash. No network resources. |
| F10 · P0 | Reusable aggregate data and reproduction | Analysts must reconstruct numbers and inspect transformations | High | CSV, Parquet, DuckDB, dictionary, manifest, clean-install commands and offline replay; public package excludes person-level microdata. Chart/table/claim IDs resolve to exact aggregate rows and raw hashes. |
| F11 · P0 | Publication validity and provenance | A stale prior success cannot masquerade as a fresh run | Medium | Failed acquisition/build leaves immutable receipt and invalidates `current`; release consumes only a verified coherent manifest, quality decision and validated artifacts. |
| F12 · P1 | Accessible charts and tables | Visual results must remain readable and auditable | Medium | One question per chart; visible uncertainty and missingness; same-data table with caption and scoped headers, text alternative, color-independent status, 200% zoom and print review. |

## Differentiators

These make the project more useful than an ordinary statistical table or dashboard. They follow the benchmarked repository patterns, but are product requirements for this project rather than claims that competitors lack them.

| ID | Feature | Value proposition | Complexity | Evidence and boundary |
|---|---|---|---|---|
| D01 | Claim-to-evidence cards | A reader can follow a sentence to estimate, sample support, method, snapshot and license in one step | Medium | `PRODUCT-GAP-AUDIT.md` proposes question → finding → limit → source; each claim has stable ID and valid references. |
| D02 | Comparison ledger with visible blocked pairs | Prevents a smooth-looking time series from hiding a changed definition | Medium | Existing comparison contract plus period-specific metadata; chart segments break on incompatibility. |
| D03 | Independent statistical reconciliation | Raises trust beyond passing software tests | High | Python results checked against R `survey` and current INEGI tabulations/precision cells for matching universes and editions. |
| D04 | Versioned source and raw archive | Allows exact replay when INEGI file names or schema change | Medium | Manifest-driven acquisition, immutable content-addressed raw and per-attempt receipts; inspired by the reviewed NHANES pipeline and ENOE packages. |
| D05 | Explicit uncertainty at the point of interpretation | Reduces misuse of small field/geography cells | Medium | CI/CV and precision status beside each finding/figure; suppression cannot be bypassed through renderer fallbacks. |
| D06 | Publication as a citable static artifact | Serves students, journalists and analysts without an app or hosted runtime | Medium | Version, data period, run date, URL/terms, manifest/hash and method included in HTML/MD/PDF bundle. |

## Anti-Features

| Feature to exclude | Why | Appropriate treatment |
|---|---|---|
| Frontend, backend, hosted dashboard or navigable app | Outside project contract and adds operations unrelated to the research claim | Static offline HTML/Markdown/PDF with internal links and downloadable aggregates. |
| Vacancy scraping, paid APIs or external inference | Outside approved source catalog and budget; vacancies are a different unit | ENOE population outcomes only, labeled as people rather than postings. |
| Causal returns, personal career advice or universal “best degree” ranking | Repeated cross-sectional ENOE estimates cannot identify those claims | Descriptive differences with universe, uncertainty and limitations. |
| Summing eight quarters as unique people or treating adjacent cuts as independent | ENOE rotation overlaps households | Quarterly cross-sections; descriptive compatible trend without unvalidated significance. |
| Filling missing/suppressed cells with zero, midpoint income or last successful run | Invents evidence or masks failure | Null plus explicit state/reason, with historical runs separate from current. |
| Public release of individual ENOE records or unreviewed borrowed code | Adds privacy/licensing risk beyond the editorial output | Publish aggregates and evidence; review software and data licenses separately. |
| Fine territorial or sex breakdowns unsupported by design | Small domains may have poor precision | Suppress cells and show coverage gap; do not promise every crossing. |

## Feature Dependencies and Phase Boundaries

```text
F01 source packages + dictionaries → F02 universe/classification → F04 estimators
F02 + F04 → F05 labor metrics → F03 profiles and F07 sex/territory
F01–F05 + D03 independent validation → eligible real estimates
Eligible estimates + D02 comparison ledger → F06 trends
Eligible estimates + F06 + D01 claim cards → F08 report → F09 formats + F12 accessibility
F01–F11 + F10 replay/data + license/secret review → final public release
```

**Roadmap recommendation:** First lock the eight package contracts and population definitions; then validate design-based estimation and metrics against R/INEGI; then build field, sex, territorial and time-series analyses; then create the editorial bundle and replay/release gate. Keep synthetic fixtures for structure checks while real-data validation is underway, but do not label them findings. PDF must ship in the final phase even though the earlier product-gap draft called it optional: the later final-release mandate requires it.

## Sources and Confidence

- Project scope and acceptance: [`PROJECT.md`](../PROJECT.md), [`FINAL-RELEASE-PLAN.md`](../../docs/FINAL-RELEASE-PLAN.md), [`PRODUCT-GAP-AUDIT.md`](../../docs/research/PRODUCT-GAP-AUDIT.md) — **HIGH** for requirements.
- Existing nine-repository primary-source review: [`COMPARABLE-REPOSITORIES.md`](../../docs/research/COMPARABLE-REPOSITORIES.md) — **MEDIUM** for benchmark implications; it is a repository sample, not a full market survey. Primary examples: [renoe](https://github.com/aniuxa/renoe), [surveytable](https://github.com/CDCgov/surveytable), [svy](https://github.com/samplics-org/svy), [NHANES pipeline](https://github.com/simonaseno/NHANES), [lfsclean](https://github.com/sheffield-health-and-work-modelling/lfsclean).
- Official method and variable evidence compiled in [`ENOE-METHOD-REVIEW.md`](../../docs/research/ENOE-METHOD-REVIEW.md): [INEGI ENOE program](https://www.inegi.org.mx/programas/enoe/15ymas/), [survey design](https://www.inegi.org.mx/contenidos/programas/enoe/15ymas/doc/enoe_n_diseno_muestral.pdf), [2025 data dictionary](https://www.inegi.org.mx/rnm/index.php/catalog/1121/data-dictionary) — **HIGH** for documented concepts, **MEDIUM** for applying older design documentation to every 2026 file until period-specific checks finish.
- Accessibility: [W3C tables](https://www.w3.org/WAI/tutorials/tables/) and [W3C images](https://www.w3.org/WAI/tutorials/images/) — **HIGH** for HTML semantics.

**Research flags:** Confirm all 2024/2026 package members, codes and licensing per quarter; resolve singleton UPM treatment and R/INEGI precision comparison; validate which territorial and field-by-sex cells survive suppression; establish PDF generation and visual QA on the final real-data report. These are release gates, not optional polish.
