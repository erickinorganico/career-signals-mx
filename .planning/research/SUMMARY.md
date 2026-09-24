# Project Research Summary

**Project:** Brújula Laboral MX v1.0.0  
**Domain:** Reproducible ENOE labor research and static editorial publication  
**Researched:** 2026-09-22  
**Confidence:** MEDIUM overall; the release method and eight-period inputs still require validation

## Executive Summary

This release is a Spanish research publication about labor outcomes by completed field of professional study in Mexico. Experts build this kind of work from period-specific official survey packages, an explicit population and measure dictionary, complex-survey estimates, independent numerical checks, and a traceable editorial layer. The required outcome is real ENOE research across 2024-Q3–2026-Q2, with reusable aggregates and offline HTML, Markdown, PDF, and figures. The synthetic v0.1.0 is a regression fixture, not a final deliverable.

Retain the local Python batch pipeline and its immutable-run/atomic-`current` design. Add a versioned ENOE adapter and v2 aggregate contract, then make one validated public projection the only input to exports, charts, and prose. All eight official ZIPs have been acquired locally, but registry SHA pins, package/dictionary inventories, and full validation remain open. A downloaded ZIP or a matched national point total has no publication authority.

The main risk is false precision: the 2026-Q2 full-frame probe contains 13 one-UPM strata. An R `survey` adjustment produced four local oracles, but Python concordance and agreement with matching INEGI precision cells remain unproved. Keep variance policy and unsupported domain cells in `REVIEW`/`BLOCKED` until those gates pass. Other release risks are drifting quarterly schemas, contaminated denominators and income sentinels, suppressed values leaking through another format, and stale `current` after failure.

## Key Findings

### Recommended Stack

Retain CPython 3.12, DuckDB 1.4.4, `jsonschema` 4.26.0, Matplotlib 3.10.8 and pytest 9.0.3. Declare NumPy 2.5.3 directly because the survey implementation imports it. R 4.6.1 with `survey` 4.5 is an independent audit oracle, not a shipped Python dependency. WeasyPrint 70.0 is the preferred single-HTML-path PDF renderer only after Windows/CI Pango, offline assets, and Spanish print fidelity pass a clean proof. Keep `pyproject.toml` and the exact `requirements.txt` closure aligned. Details: [STACK.md](STACK.md).

### Expected Features

**Must have:** eight source snapshots and receipts (F01); distinct national and completed professional-study populations with verified CMPE codes (F02); Derecho, Comunicación y periodismo, and Ciencias políticas profiles plus supported field context (F03); design-aware estimates, 90% intervals, CV, coverage and suppression (F04); explicit-universe work outcomes (F05); comparable descriptive quarterly change (F06); supported sex and territorial views (F07); a Spanish evidence-bound report (F08); offline HTML/Markdown/PDF and SVG/PNG (F09); CSV/Parquet/DuckDB, dictionary and replay (F10); and fail-closed publication validity (F11). Accessible same-data charts/tables (F12) belong in the publication acceptance gate.

**Distinctive delivery:** stable claim-to-estimate links (D01), visible blocked comparisons (D02), Python/R/INEGI reconciliation (D03), immutable source archive (D04), uncertainty next to interpretation (D05), and a citable static bundle (D06). These support the final release rather than optional polish. **Defer/exclude:** hosted app or dashboard, vacancy feeds, paid inference, causal returns, personal advice, universal rankings, independent-quarter significance claims, and individual-record publication. Details: [FEATURES.md](FEATURES.md).

### Architecture Approach

One locked local pipeline moves approved exact-URL packages through content-addressed raw storage, period manifests, a normalized full survey frame, design-aware estimation, independent reconciliation, v2 quality/precision/comparability gates, public aggregate projection, evidence-bound editorial rendering, and a sealed run manifest before atomic `current.json`. Preserve the strict v1 synthetic route for regression checks; v2 gets its own schema and readers. Keep field of study, occupation, industry, geography, period and source separate, and let only public `value` reach any published artifact. Details: [ARCHITECTURE.md](ARCHITECTURE.md).

### Critical Pitfalls

1. **Singleton-stratum variance:** keep default failure; version and review any project approximation, record options/counts, reproduce R SE oracles in Python, and compare with matching official precision. Never describe adjusted SE as INEGI precision.
2. **Wrong domain or denominator:** construct the full quarterly design before field/sex/state domains; verify `FAC_TRI`, strata, nested UPM, eligibility, CMPE, nonresponse and every metric denominator.
3. **Schema and sentinel drift:** bind each quarter to its own members/dictionary; test geography aliases, joins, age and income response codes, and preserve exclusions and nulls.
4. **Suppression or stale-state leakage:** derive every public format from the same null-preserving projection; failed refresh/build leaves a receipt and invalidates `current`.
5. **False trend or source claims:** compare only compatible quarter pairs, label nominal income and rotating-sample overlap, retain raw microdata locally, and review licenses/attribution before publication. Details: [PITFALLS.md](PITFALLS.md).

## Implications for Roadmap

### Phase 1: Eight-source and v2 method contract
**Rationale:** Estimation needs verified inputs, categories, population definitions and a compatible schema.  
**Delivers / gate:** SHA-pin all eight acquired ZIPs in the registry; inventory official members, terms, dictionaries, questionnaire type, factor revision and aliases per period; verify joins/crosswalks, cohort codes and exclusions; define v2 grain, measure denominators and precision policy. Every quarter must resolve to an approved immutable snapshot and reproducible manifest.  
**Addresses / avoids:** F01–F02, D04; prevents guessed codes, mixed study levels and treating acquisition as release.

### Phase 2: Design-aware estimates and independent acceptance
**Rationale:** No field result is publishable until the variance method and denominators are defensible.  
**Delivers / gate:** full-frame totals/ratios and labor metrics; sample/PSU support, SE, 90% CI, CV, coverage and null/suppression state; explicit singleton policy; Python reproduction of the four R oracles plus matched INEGI point/SE reconciliation for the correct edition and universe. Unresolved precision stays `REVIEW`/`BLOCKED`.  
**Addresses / avoids:** F04–F05, D03/D05; prevents point-agreement-as-SE-proof, domain filtering and sentinel contamination.

### Phase 3: Validated field, sex, territory and time analysis
**Rationale:** Profiles and trends depend on accepted estimates and period metadata.  
**Delivers / gate:** three named profiles, supported CMPE comparators, national/sex/territorial views, explicit coverage gaps, and a comparison ledger whose incompatible pairs have null deltas. Every numeric pair passes source, universe, geography, concept, method, price basis and classification checks; change remains descriptive.  
**Addresses / avoids:** F03/F06–F07, D02; prevents unsupported small-cell claims and independent-sample significance.

### Phase 4: Evidence-bound editorial bundle and replay
**Rationale:** The reader-facing report must consume the same accepted public aggregates as the reusable tables.  
**Delivers / gate:** Spanish question-led findings with stable evidence IDs, national context, field profiles, limits and methods; semantic offline HTML, equivalent Markdown, PDF, SVG/PNG, CSV/Parquet/DuckDB, dictionary and manifest. A deliberately suppressed cell must never appear as a number in prose, figure, PDF or export; an offline replay reproduces hashes and a failed build invalidates `current`.  
**Addresses / avoids:** F08–F12, D01/D06; prevents format drift, hidden diagnostic values and stale publication.

### Phase 5: Independent audit and public v1.0.0 release
**Rationale:** A real-data bundle needs a separate release decision beyond passing component tests.  
**Delivers / gate:** clean Python 3.12 installs and end-to-end replay on Windows and Ubuntu; numerical/conceptual/visual/accessibility review; PDF page/text/resource checks; license, attribution, secret and public-aggregate-only review; sealed final run and verifiable public repository release. Any failed gate leaves the release blocked with its receipt.  
**Addresses / avoids:** F01–F12 as an integrated claim; prevents synthetic substitution, unreviewed raw data and CI-only certification.

### Phase Ordering Rationale and Research Flags

Source/version evidence precedes the v2 adapter and survey design; statistical acceptance precedes field comparisons; eligible public values precede claims and charts; an immutable bundle precedes release. Use `$gsd-plan-phase --research-phase <N>` for **Phases 1–2** (period-specific schema, current design and singleton/official precision) and **Phase 4** (WeasyPrint/Pango and offline PDF proof). Research Phase 3 only if a requested domain or change inference exceeds documented support. **Phase 5** follows established repository release/pointer patterns, but requires independent verification rather than new broad research.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH core; MEDIUM PDF | Existing installed pipeline and official tool docs; Windows/CI Pango proof pending. |
| Features | HIGH scope; MEDIUM editorial priority | User's final-release plan and ENOE concepts are explicit; reader utility has not been field-tested. |
| Architecture | HIGH boundaries; MEDIUM statistical integration | v1 contracts/pointer exist; v2 schema and full official path remain unvalidated. |
| Pitfalls | HIGH observed risks; MEDIUM mitigation | Q2 singleton evidence and official/R methods support the risks; proposed approximation is unapproved. |

**Overall confidence:** MEDIUM. The plan is clear; publishable numerical precision remains unproved.

### Gaps to Address

- Complete SHA pins, member/dictionary/CMPE/terms and factor-version validation for all eight acquired packages; a successful download is only acquisition evidence.
- Decide and version the singleton-stratum project method after Python/R SE concordance and matching INEGI precision review. Record disagreement; do not tune tolerances to hide it.
- Determine which field-by-sex and territorial domains meet project support/precision rules, and which working-condition variables are genuinely comparable in all applicable quarters.
- Prove offline PDF generation and clean cross-platform replay; record exact dependency/native-library versions and report hashes.

## Sources

### Primary (HIGH confidence)
- [Project brief](../PROJECT.md), [interface contract](../../docs/CONTRACT.md), [final release plan](../../docs/FINAL-RELEASE-PLAN.md), and [ENOE method review](../../docs/research/ENOE-METHOD-REVIEW.md) — scope, existing contracts and open gates.
- [INEGI ENOE program](https://www.inegi.org.mx/programas/enoe/15ymas/), [sample-design document](https://www.inegi.org.mx/contenidos/programas/enoe/15ymas/doc/enoe_n_diseno_muestral.pdf), and [R survey design guidance](https://r-survey.r-forge.r-project.org/survey/html/svydesign.html) — source and estimator semantics; match document vintage to each release.
### Secondary (MEDIUM confidence)
- [STACK.md](STACK.md), [FEATURES.md](FEATURES.md), [ARCHITECTURE.md](ARCHITECTURE.md), [PITFALLS.md](PITFALLS.md) — detailed research, repository observations, official links and uncertainty notes.
- [Comparable repositories](../../docs/research/COMPARABLE-REPOSITORIES.md) and [product gap audit](../../docs/research/PRODUCT-GAP-AUDIT.md) — editorial and reproducibility patterns, not statistical authority.

---
*Research completed: 2026-09-22*  
*Ready for roadmap: yes, with statistical release gates explicit.*
