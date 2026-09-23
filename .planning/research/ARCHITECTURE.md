# Architecture Patterns: ENOE research release

**Domain:** Local, reproducible Mexican labor research using ENOE microdata
**Researched:** 2026-09-22
**Confidence:** HIGH for repository boundaries; MEDIUM for statistical release design pending R and official reconciliation

## Recommended Architecture

Keep one local batch pipeline and one canonical publication pointer. Add a versioned ENOE adapter and v2 analytical contract between the separately tested acquisition/survey components and the existing artifact pipeline. Preserve v1 synthetic behavior as a regression path; an ENOE ZIP receipt, parsed row, or computed estimate has no publication authority on its own.

```text
approved exact-URL catalog -> acquisition receipts -> verified raw ZIPs (local only)
    -> period manifests + ENOE adapter -> normalized full survey frames
    -> survey estimator + independent R/official checks -> v2 aggregate candidates
    -> strict quality / precision / comparability / claim gates
    -> per-run DuckDB, CSV/Parquet, evidence, static HTML/MD/PDF, figures
    -> sealed receipt + manifest -> atomic current.json

v1 fixture -> existing v1 build and synthetic renderer (unchanged gate semantics)
```

The official [ENOE program](https://www.inegi.org.mx/programas/enoe/15ymas/) is the data source; the current repository [architecture](../codebase/ARCHITECTURE.md), [v1 contract](../../docs/CONTRACT.md), and [acquisition ADR](../../docs/decisions/0006-real-research-scope-and-acquisition.md) define the local integration constraints. Do not add a server, browser application, remote database, or hosted inference.

### Component Boundaries

| Component | Owns | Must return or verify | Must not do |
|---|---|---|---|
| `acquisition.py` | Allowlisted transfer/cache, ZIP safety, raw SHA-256, attempt receipts | Verified immutable package handle per exact period | Decide variables, estimate, or publish |
| Period manifest + `enoe` adapter | Member selection, period-specific dictionary/catalog, alias map, codes, joins, eligibility, missingness | Normalized full respondent/resident frame, transformation audit, source references | Guess column/CMPE meanings or silently fill missing values |
| `survey.py` | Weighted totals/ratios and design variance on the full frame | Estimate, public `value`, SE/CI/CV, support, suppression reasons | Infer source authority or release eligibility |
| v2 contract + `quality.py` | Grain, source/universe/method metadata, precision, evidence links, comparison policy | Validated aggregates and explicit blocked rows | Restore diagnostic estimates into public values |
| Research coordinator in `pipeline.py` | Stage order, locks, receipts, run sealing, current invalidation | Complete immutable run or current BLOCKED | Treat old success as current after a failed refresh |
| `insights.py` + editorial renderer | Evidence-bound descriptive prose, tables, figures and offline report | Claim-to-estimate references and identical display values across formats | Create new numbers, causal claims, or a hidden unsuppressed fallback |
| `warehouse.py`/`export.py` | Reusable validated aggregate tables | Null-preserving public outputs and per-run metadata | Export individual ENOE records or internal diagnostics |

The v1 schema is strict and cannot carry v2 design, coverage, CI, and suppression metadata as extra fields. Define `schema_version: 2` with explicit readers/validators and tests; route v1 through its existing validator. A new v2 aggregate key should include concept **type and ID**, geography, period, metric, population, method, source snapshot, and any necessary sex/domain dimensions. Keep field of study, occupation, and industry separate, with bridges under review. The existing v1 grain and quality rules are documented in [CONTRACT.md](../../docs/CONTRACT.md); the ENOE variable and design proposals are in [ENOE method review](../../docs/research/ENOE-METHOD-REVIEW.md).

### Data Flow and Authority

1. The CLI starts a locked refresh and sets `current.json` to RUNNING/BLOCKED before source work. Every attempted snapshot gets its own receipt. A failed fetch, manifest, adapter, estimator, reconciliation, or render stage seals a failure and leaves `current` nonpublishable; historical runs remain immutable. Offline replay resolves verified local raw hashes without network.
2. The period manifest pins the ZIP hash, selected SDEM/SDEMT and any COE members, headers, dictionary/catalog versions, location aliases, join key, code crosswalk, and transformations. The adapter checks cardinality and exclusion counts, retaining original values and missingness reasons. Period changes are explicit manifest revisions; 2025-Q3 geography renaming is a known example ([INEGI program configuration](https://www.inegi.org.mx/programas/enoe/15ymas/data/pestana/pestanadata.js)).
3. Build the full responding/resident survey frame before selecting an educational field or labor subgroup. Validate weights, strata, UPM nesting, eligibility, and nonresponse. Then compute domain contributions with `survey.py`; do not filter the design down to Derecho or another field before variance. Singleton design strata and unexplained zero weights remain blocking questions until documented treatment is accepted. The [INEGI ENOE design document](https://www.inegi.org.mx/contenidos/programas/enoe/15ymas/doc/enoe_n_diseno_muestral.pdf) supports the stratified cluster design; its 2021 vintage does not certify every 2026 detail.
4. Reconcile defined national controls against INEGI outputs and an independent R `survey` calculation before accepting the Python estimator. Store exact oracle inputs, versions, options, tolerances, mismatches, and review disposition as run evidence. The [R survey manual](https://r-forge.r-universe.dev/survey/doc/manual.html) describes `svydesign`, domain estimation, and lonely PSU options; choosing a software option is not approval of a statistical treatment.
5. Apply the project precision policy to a candidate: diagnostic estimate and uncertainty can remain in restricted run evidence, while **only the gated public `value`** enters aggregate exports, report tables, chart input, prose templates, and DuckDB public views. Null public value plus reason is the single representation of suppression. Verify export/report projections against that same public aggregate set.
6. Generate comparisons only for a shared source, universe, geography, measure, price basis, method, concept, classification, and compatible period. Adjacent quarterly differences are descriptive; rotating ENOE samples overlap, so no independent-sample significance claim follows from two marginal CIs. The [final release plan](../../docs/FINAL-RELEASE-PLAN.md) establishes this scope.
7. Seal the bundle, receipt, manifest, and static publication, then atomically point `current.json` to the verified run. Every consumer resolves `current` and checks hashes; an old report path is never treated as current evidence. This extends the implemented [v1 pointer contract](../../docs/CONTRACT.md) rather than creating a second publication authority.

## Patterns to Follow

### Versioned adapter, frozen source evidence

Use one adapter interface per supported ENOE schema family, selected by a manifest with an exact period and raw hash. Expose normalized columns and a transformation audit, not a generic untyped CSV. Reject conflicting aliases, duplicate headings, unknown codes, and unverified joins. This makes schema drift reviewable before any estimate. Source reads stay within the approved catalog; raw ZIPs and individual rows stay local. **Confidence: HIGH** for need and boundary, based on [ADR 0006](../../docs/decisions/0006-real-research-scope-and-acquisition.md) and the [official 2026-Q2 ZIP](https://www.inegi.org.mx/contenidos/programas/enoe/15ymas/datosabiertos/2026/conjunto_de_datos_enoe_2026_2t_csv.zip).

### One public projection from the precision gate

Represent each candidate with `{diagnostic_estimate, value, status, suppression_reason, precision, evidence_refs}` in internal state. The public projection omits `diagnostic_estimate` entirely and every output consumes that projection. Test report, chart, CSV, Parquet, DuckDB, Markdown, HTML and PDF for suppressed sentinel leakage. An adapter or renderer must never choose `diagnostic_estimate` when `value` is null. **Confidence: HIGH** as a safety architecture; the exact v2 schema requires design.

### Claim registry before prose

Assign each publishable finding an ID and references to the exact aggregate IDs, source hashes, method and limits. Generate numeric text from the public projection or validate it against that projection. A figure and its alternative table share one data selection. The report can lead with a reader question, while each sentence still resolves to a validated number and its uncertainty. Keep synthetic banners for v1 and explicit official/source attribution for v2. **Confidence: HIGH** from the [product gap audit](../../docs/research/PRODUCT-GAP-AUDIT.md) and v1 insight contract.

## Anti-Patterns to Avoid

| Anti-pattern | Consequence | Boundary to enforce |
|---|---|---|
| Treat a successful download or `official_snapshot` enum as publication permission | Real-looking but unvalidated results | Separate acquisition, estimation, statistical acceptance and release gates |
| Append design fields to strict v1 rows | Broken readers or weakened v1 validation | Explicit v2 schema, migration and regression tests |
| Filter to a field before constructing the survey design | Wrong domain variance | Full frame design, zero algebraic contributions outside domains |
| Let renderer/exports read internal estimates | Suppressed values reappear in figures or prose | Single validated public projection and cross-format leak tests |
| Concatenate quarterly rows or assume independent quarters | Inflated support and false trend precision | Separate cross sections, descriptive deltas until covariance is justified |
| Use `current` from a prior success after refresh failure | Stale report presented as fresh | Write failure receipt and invalidate current in every failed stage |
| Let editorial templates bridge education to occupation | Misstated field outcomes | Separate concepts and explicit reviewed bridge authority |

## Build Order and Roadmap Implications

1. **Source and method contract:** Freeze eight period manifests, local raw receipts, source terms, dictionary/crosswalk rules, v2 grain, populations and suppression policy. Review unknown 2024 periods and singleton PSU treatment before promising eight comparable quarters.
2. **Adapter and statistical acceptance:** Normalize each period, audit joins and missingness, implement metrics on a full design frame, then reconcile national controls and R/official precision. A 2026-Q2 national total match alone does not validate field estimates or SEs.
3. **Integrated quality and replay:** Add the v2 research coordinator, public projection, evidence registry, export/warehouse mappings, and fail-closed refresh/offline replay. Preserve the synthetic v1 tests as controls.
4. **Editorial publication:** Render national context, named field profiles, territorial/sex slices where supported, descriptive trends, limitations, HTML/Markdown, figures and PDF from the same accepted public aggregates. Seal all files under one run manifest.
5. **Independent release audit:** Verify numerical, conceptual, suppression, license/privacy, static/offline and clean-install evidence before public release. The final release requires real data and review; a synthetic template remains a test fixture.

**Research flags:** Period-specific ENOE headers/crosswalks and joins; current singleton PSU treatment and R/official precision concordance; overlap-aware change uncertainty if inferential trend claims are later requested; offline PDF fidelity and reproducibility. These merit phase-specific investigation. The local pipeline, hashes, manifests and pointer pattern are established repository practice.

## Sources

- [Repository architecture](../codebase/ARCHITECTURE.md), [v1 contract](../../docs/CONTRACT.md), [final release plan](../../docs/FINAL-RELEASE-PLAN.md), [ENOE method review](../../docs/research/ENOE-METHOD-REVIEW.md) — current local design and open validation gates, reviewed 2026-09-22.
- [INEGI ENOE program](https://www.inegi.org.mx/programas/enoe/15ymas/), [program configuration](https://www.inegi.org.mx/programas/enoe/15ymas/data/pestana/pestanadata.js), [survey design](https://www.inegi.org.mx/contenidos/programas/enoe/15ymas/doc/enoe_n_diseno_muestral.pdf) — primary source and methodology; confirm period-specific documentation before release.
- [R survey manual](https://r-forge.r-universe.dev/survey/doc/manual.html) — independent oracle semantics, not release authority.
