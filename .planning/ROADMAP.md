# Roadmap: Brújula Laboral MX v1.0.0

## Overview

This milestone delivers a reproducible, real-data ENOE research publication across 2024-Q3–2026-Q2. Verified official source snapshots and a strict v2 contract establish the inputs; independently checked complex-survey estimates establish which numbers may be used; supported comparisons establish the findings; one public projection feeds every offline output; and an independent release review determines whether the complete bundle may be published. The synthetic v0.1.0 remains a regression fixture, not milestone completion. Existing acquired ZIPs and acquisition/survey prototypes are partial work until their phase gates pass.

## Phases

**Phase Numbering:** Integer phases are planned milestone work; decimal phases are reserved for urgent insertions.

- [x] **Phase 1: Official Sources and Research Contract** - Eight immutable ENOE snapshots and explicit populations, dimensions, and method rules can be verified. (completed 2026-09-22)
- [x] **Phase 2: Defensible Survey Estimates** - Real-data estimates and precision states pass independent numerical and official reconciliation.
 (completed 2026-09-23)
- [ ] **Phase 3: Supported Labor Findings** - Readers can inspect field, time, sex, and territorial findings with comparable evidence and visible limits.
- [ ] **Phase 4: Offline Publication and Reproducible Operation** - One validated public projection produces the editorial report, reusable data, and fail-closed replayable run.
- [ ] **Phase 5: Independent Audit and v1.0.0 Release** - Clean reproduction and release review support a verifiable public research bundle.

## Phase Details

### Phase 1: Official Sources and Research Contract

**Goal**: Analysts can verify the eight official inputs and apply unambiguous research definitions before estimating any result.
**Depends on**: Nothing (first phase)
**Requirements**: SRC-01, SRC-02, SRC-03, SRC-04, CTR-01, CTR-02
**Success Criteria** (what must be TRUE):

  1. An analyst can resolve all eight approved ENOE quarters to SHA-256-pinned local packages and inspect per-attempt receipts; a failed acquisition cannot appear as a current success.
  2. For each quarter, an analyst can inspect the official package members, dictionary, study catalog, edition or correction, coding, geographic aliases, acquisition date, terms, and transformation record while individual records remain local.
  3. An analyst can identify the exact national and completed-professional-study populations, eligibility exclusions, and denominators, including treatment of postgraduate study, age, and unknown fields.
  4. A consumer can validate a strict v2 research record with distinct dimensions, evidence, and precision state while the v1 synthetic regression contract still rejects invalid inputs.

**Plans**: 4/4 plans executed and independently verified

- [x] 01-01-PLAN.md
- [x] 01-02-PLAN.md
- [x] 01-03-PLAN.md
- [x] 01-04-PLAN.md (mechanical prohibition controls)

### Phase 2: Defensible Survey Estimates

**Goal**: Analysts can distinguish supported real-data survey estimates from imprecise or unverified cells.
**Depends on**: Phase 1
**Requirements**: STAT-01, STAT-02, STAT-03, STAT-04, STAT-05, STAT-06
**Success Criteria** (what must be TRUE):

  1. An analyst can obtain national and domain totals, proportions, and means using the complete FAC_TRI/EST_D_TRI/UPM design, with each labor measure's eligible numerator, denominator, unit, nonresponse, and sentinel rules visible.
  2. Every estimate exposes observed n, contributing UPM and strata, degrees of freedom, standard error, IC90, CV, method, and singleton treatment; a project approximation is explicitly distinguished from official precision.
  3. A consumer sees null and a reason where support or precision fails, including n<30, fewer than two contributing UPM, CV>=30, null denominator, or degenerate precision, and never reads observed n as effective sample size.
  4. An independent reviewer can reproduce Python point estimates and errors against R survey on real and analytic controls and inspect untuned discrepancies against compatible official national and state totals and precision cells.

**Plans**: 3/3 plans executed; all-eight numerical replay and independent verification accepted

- [x] 02-01-PLAN.md
- [x] 02-02-PLAN.md
- [x] 02-03-PLAN.md

### Phase 3: Supported Labor Findings

**Goal**: Readers can explore field and labor patterns across periods and geographies without unsupported differences or claims.
**Depends on**: Phase 2
**Requirements**: ANA-01, ANA-02, ANA-03, ANA-04, ANA-05, ANA-06
**Success Criteria** (what must be TRUE):

  1. A reader can inspect supported profiles for Derecho, Comunicación y periodismo, and Ciencias políticas alongside the total professional cohort and other identifiable official fields.
  2. A reader can follow the eight national quarters and inspect descriptive changes only where source, universe, geography, measure, concept, price basis, classification, method, and both precision states permit comparison.
  3. A reader can inspect supported differences by recorded sex and entity, with suppressed cells, missing coverage, response rates, and exclusions visible for each relevant period and field.
  4. A reviewer can trace each proposed finding to exact estimate, source, and method IDs; unsupported causal prose, new quantities, and personal recommendations fail the claim gate.

**Plans**: 2/3 plans executed; profiles and comparisons accepted, 03-03 findings executing

- [x] 03-01-PLAN.md
- [x] 03-02-PLAN.md
- [ ] 03-03-PLAN.md

### Phase 4: Offline Publication and Reproducible Operation

**Goal**: Readers receive consistent, evidence-bound offline research outputs from a sealed run that can be replayed and whose current status fails closed.
**Depends on**: Phase 3
**Requirements**: PUB-01, PUB-02, PUB-03, PUB-04, PUB-05, OPS-01, OPS-02, OPS-03
**Success Criteria** (what must be TRUE):

  1. A reader can open the Spanish, question-led report in offline HTML, equivalent Markdown, and printable PDF, finding supported opening claims, national context, field profiles, evolution, territory, limits, methods, and sources without network resources or credentials.
  2. A reader can use SVG/PNG figures and semantic tables at print size, mobile width, and 200% zoom, with units, uncertainty, universe, source, and state visible.
  3. An analyst can join public CSV, Parquet, and DuckDB aggregates to figures and claims through documented keys while preserving distinct dimensions, nulls, precision states, and provenance.
  4. A deliberately suppressed internal cell remains absent as a number from all public tables, exports, figures, report text, PDF, and alternative text because each consumes the same validated public projection.
  5. An analyst can refresh and replay from the documented CLI; the same source snapshots reproduce numerical content, a sealed manifest and hashes precede current promotion, and acquisition/build failures leave receipts and invalidate dependent current access without erasing history.

**Plans**: TBD

### Phase 5: Independent Audit and v1.0.0 Release

**Goal**: The public v1.0.0 package is reproducible, reviewed, traceable, and complete against its full real-data scope.
**Depends on**: Phase 4
**Requirements**: REL-01, REL-02, REL-03, REL-04, GSD-01
**Success Criteria** (what must be TRUE):

  1. A new analyst can install on clean Windows or Ubuntu, follow accurate bilingual scope, method, architecture, contribution, citation, and update instructions, and replay the accepted real bundle offline while isolated fixtures run without production access.
  2. An independent reviewer can inspect numerical, conceptual, visual, and PDF checks and trace every requirement through reviewed phase plans, execution, verification, code review, and final GSD audit evidence.
  3. A reviewer can confirm the release contains only validated, redistributable public aggregates and artifacts, with secrets, licenses, attribution, and microdata absence checked.
  4. A reader can retrieve a 1.0.0 release in erickinorganico/career-signals-mx linking code, report, figures, aggregates, manifest, and acceptance evidence; unresolved material gates prevent a complete designation.

**Plans**: TBD

## Progress

**Execution Order:** 1 → 2 → 3 → 4 → 5. Phase research is recommended before planning Phases 1–2 and 4; singleton-stratum precision uses the explicitly nonofficial project adjustment verified in Phase 2. No phase is complete merely because downloads or prototypes exist.

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Official Sources and Research Contract | 4/4 | Complete    | 2026-09-22 |
| 2. Defensible Survey Estimates | 3/3 | Complete    | 2026-09-23 |
| 3. Supported Labor Findings | 2/3 | Executing 03-03 | - |
| 4. Offline Publication and Reproducible Operation | 0/TBD | Not started | - |
| 5. Independent Audit and v1.0.0 Release | 0/TBD | Not started | - |
