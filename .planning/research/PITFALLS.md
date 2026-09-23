# Domain Pitfalls: Eight-Quarter ENOE Research Release

**Project:** Brújula Laboral MX 1.0.0  
**Researched:** 2026-09-22  
**Confidence:** HIGH for documented survey behavior and observed 2026-Q2 probe; MEDIUM for the proposed project variance policy; LOW until all eight quarter packages and official precision cells are reconciled.

The critical release risk is publishing an apparently precise field estimate from a design that cannot supply its claimed variance. The 2026-Q2 local full-frame probe found **13 strata with one observed UPM** (`.cache/research/design-probe.json`). The Python default and R `survey` default both fail on that condition. A tested R 4.6.1 / `survey` 4.5 run with `survey.lonely.psu="adjust"` and `survey.adjust.domain.lonely=FALSE` produced four point/SE oracles (`.cache/research/r-survey-oracle.json`). That is evidence that an explicit adjustment can produce estimates, **not** evidence that INEGI uses this adjustment or that the resulting SEs match published precision.

## Critical Pitfalls

### 1. Silent singleton-stratum variance policy

**What goes wrong:** Dropping a one-UPM stratum, assigning zero variance, treating it as a certainty PSU, or silently activating an R option gives a plausible SE whose method the reader cannot identify. Filtering to a career first can create additional apparent singleton strata and alter the variance.  
**Why it happens:** The full responded-resident frame for 2026-Q2 already has 13 singleton strata, so the default design calculation fails. R documents `"adjust"` as centering a singleton PSU at the sample grand mean; it calls this conservative and an ad hoc remedy.  
**Consequences:** CV, confidence interval, precision status, ranking eligibility, and suppression can all change.  
**Prevention:** Keep fail as the default. Define a separate, versioned **project approximation** that centers singleton contributions at the grand PSU mean, records `variance_method`, adjustment policy, singleton count, full-frame definition, and `REVIEW` status, and requires a bounded methodological review before numerical release. Do not label the adjusted SE “official INEGI precision.” Keep `survey.adjust.domain.lonely=FALSE` for the tested full-frame numerator/denominator oracle; a change to that option requires a new oracle and method version.  
**Detection/gate:** Reproduce the four local R oracles in Python, including SEs; prove `survey.lonely.psu="fail"` and the Python default fail on 2026-Q2; inspect all eight frames for singleton counts. Any unapproved policy, drift, or missing SE blocks publication. [R lonely-PSU guidance](https://r-survey.r-forge.r-project.org/survey/exmample-lonely.html), [R survey options](https://r-survey.r-forge.r-project.org/survey/html/surveyoptions.html).

### 2. Mistaking a historical INEGI collapse for the current design

**What goes wrong:** Reconstructing 2026 pseudo-strata using a 2021 procedure without a current mapping, or calling the R adjustment INEGI's own procedure.  
**Why it happens:** The 2021 ENOEN design document describes geographically ordered stratum collapse and subsequent factor adjustment, but it does not supply a verified mapping for these eight releases.  
**Consequences:** Unsupported design degrees of freedom and false official equivalence.  
**Prevention:** Preserve released `EST_D_TRI`, `UPM`, `FAC_TRI` and period-specific metadata. Treat the 2021 document as a methodological precedent only. Escalate to phase research if the current package or INEGI precision file reveals a different design instruction.  
**Detection/gate:** Record the exact quarter document and any design mapping used; absent current evidence, mark official-precision equivalence `UNKNOWN`. [INEGI ENOEN 2021 design, §6.1 and §8](https://www.inegi.org.mx/contenidos/programas/enoe/15ymas/doc/enoe_n_diseno_muestral.pdf).

### 3. National point agreement mistaken for variance validation

**What goes wrong:** The 2026-Q2 exact match for national population, employed, and unemployed is taken as proof that field SEs and 90% intervals are correct.  
**Why it happens:** Weighted point totals can match with the wrong variance estimator. The Q2 probe matched 104,305,022 population, 60,040,094 employed, and 1,636,604 unemployed after its specific `15<=EDA<=98` benchmark filter; that filter is not automatically the field-study universe.  
**Consequences:** Suppression and claims rest on unvalidated precision.  
**Prevention:** Compare an official precision workbook using the same quarter, weight revision, population, measure, confidence convention, and published rounding. Local 2025-Q2 workbook `.cache/research/precision_2025q2.xlsx` provides candidate cells: population 102,615,200 / SE 361,341.3954; PEA 61,065,005 / SE 260,388.0672; unemployed 1,624,245 / SE 41,734.1636. Compare those only after acquiring that quarter and matching its denominator and design; report any discrepancy rather than tuning weights to force agreement.  
**Detection/gate:** A signed reconciliation table records workbook URL, sheet/cell, release edition, universe, estimate, SE, tolerance, and result. No field-level precision claim precedes independent Python/R agreement and an explicit official benchmark comparison. [INEGI 2025-Q2 precision workbook](https://www.inegi.org.mx/rnm/index.php/catalog/1121/download/35892), [INEGI survey design](https://www.inegi.org.mx/contenidos/programas/enoe/15ymas/doc/enoe_n_diseno_muestral.pdf).

### 4. Domain and denominator contamination

**What goes wrong:** Constructing the survey design after filtering to Derecho, women, employed persons, or a state; dividing by all residents for a measure whose denominator is employed graduates; or using `FAC_MEN` for quarterly outputs.  
**Why it happens:** A dataframe filter looks equivalent to an indicator, but it removes out-of-domain PSUs from the variance calculation.  
**Consequences:** Wrong estimates, misleading intervals, and incomparable profiles.  
**Prevention:** Build the quarter's full responded-resident design first; use explicit zero-valued out-of-domain numerator and denominator columns for `svyratio`, with `FAC_TRI`, `EST_D_TRI`, and nested `UPM`. Store measure, population, domain, weighted denominator, eligible observed n, contributing PSUs, and nonresponse coverage. Field profiles require `CS_P13_1=07`, `CS_P16=1`, and a validated CMPE map; the broader 07/08/09 group needs another `population_id`.  
**Detection/gate:** Fixture where filtering first changes a known SE; zero-denominator and absent-domain cases return null public values. Check exact category/denominator definitions per quarter. [R domain-estimation guidance](https://r-survey.r-forge.r-project.org/survey/doc/domain.pdf), [project method review](../../docs/research/ENOE-METHOD-REVIEW.md).

### 5. Hidden income and age sentinels

**What goes wrong:** `INGOCUP=0` or `999999` enters a monetary average; `EDA=98` is treated as age 98; a positive-only income mean is described as pay for all graduates.  
**Why it happens:** Numeric CSV fields encode different response states. The 2026-Q2 package dictionary permits positive income through 999998; a historical reconstruction document gives a different upper bound.  
**Consequences:** Spurious zero-income shares, distorted means, and silent universe shifts.  
**Prevention:** Bind each quarter to its own dictionary. Keep raw income, `ING7C` state, normalized value, exclusion reason, and weighted amount coverage. `ING7C=6` is no income; `INGOCUP=0` with `ING7C=7` is unknown; `999999` is not a monetary amount. Distinguish the official national benchmark's age convention from the field profile's known-age rule and expose exclusions.  
**Detection/gate:** Sentinel fixtures, weighted coverage report, and matched official income-category comparisons; block any quarter whose dictionary/rules remain ambiguous. [INEGI INGOCUP variable](https://www.inegi.org.mx/rnm/index.php/catalog/1121/variable/F42/V5729?name=INGOCUP), [INEGI EDA variable](https://www.inegi.org.mx/rnm/index.php/catalog/1121/variable/F42/V5657?name=EDA), [project method review](../../docs/research/ENOE-METHOD-REVIEW.md).

### 6. A suppressed diagnostic reappears in a chart or export

**What goes wrong:** `estimate` remains populated for auditing and a renderer, downloadable table, alt text, SVG label, or narrative uses it as a fallback when `value=null`.  
**Why it happens:** The survey result deliberately separates internal estimate from public value.  
**Consequences:** The same unsupported figure leaks through another output and acquires apparent authority.  
**Prevention:** Use a single publication projection that accepts only release-eligible `value`; apply it to Markdown, HTML, PDF, charts, tooltips/labels, CSV, Parquet, and DuckDB public tables. Carry null with suppression reason and precision status. Keep n<30 and CV thresholds labeled as **project** rules, not INEGI confidentiality or official quality certification.  
**Detection/gate:** End-to-end tests assert a deliberately suppressed cell is absent as a number across every public artifact and no `UNKNOWN`/`REVIEW` cell is described as a precise difference. [INEGI precision categories](https://www.inegi.org.mx/contenidos/programas/enoe/15ymas/doc/enoe_n_diseno_muestral.pdf), [project method review](../../docs/research/ENOE-METHOD-REVIEW.md).

## Moderate Pitfalls

| Pitfall | Consequence | Prevention / detection |
| --- | --- | --- |
| Treating eight rotational quarters as independent people or independent estimates | Duplicated people, invalid pooled variance and significance claims | Each quarter is a cross-section. Run pairwise source/universe/measure/price/method checks; report descriptive deltas only until an overlap covariance method is justified. Never sum quarterly counts as unique persons. [INEGI RNM 2025](https://www.inegi.org.mx/rnm/index.php/catalog/1121). |
| Assuming one physical SDEMT schema across 2024–2026 | Dropped leading zeros, wrong geography or missing variables | Per-quarter ZIP/member/dictionary manifest and alias validation; test both sides of the 2025-Q3 `ENT`→`CVE_ENT` change and Q1 expanded versus Q2 basic questionnaires. [Project method review](../../docs/research/ENOE-METHOD-REVIEW.md). |
| Mapping education from occupation, or mixing professional and postgraduate fields | A cohort labeled “graduates in Derecho” includes the wrong people | Resolve `CS_P14_C` against each package catalog, preserving leading zero and level. Verify 031300→0313, 032100→0321, 033100→0331 in 2026-Q2; use separate populations for extensions. [INEGI CMPE 2016](https://inegi.org.mx/contenidos/productos/prod_serv/contenidos/espanol/bvinegi/productos/nueva_estruc/702825086664.pdf). |
| Stale `current` after acquisition or build failure | Historical success appears to be a fresh release | Content-address raw files, receipt for every attempt, invalidate `current` on any failure, and replay from immutable snapshots. [Project final plan](../../docs/FINAL-RELEASE-PLAN.md). |
| Publishing private raw microdata or unreviewed third-party assets | Unauthorized distribution or license/attribution breach | Keep raw SDEM local; audit public aggregate files, figure inputs, source terms, attribution, and secrets before repository publication. [Project final plan](../../docs/FINAL-RELEASE-PLAN.md). |

## Phase-Specific Research Flags

| Phase topic | Required decision before completion |
| --- | --- |
| Eight-quarter acquisition | Confirm each official package, field catalog, geography aliases, questionnaire type, source terms, and factor revision. A verified 2026-Q2 package does not certify the other seven. |
| Survey estimation | Review and version the singleton approximation, cross-check all four R oracles plus edge cases, and compare national/one-entity SE against the matching official workbook. This needs deeper statistical review. |
| Metrics and profiles | Freeze population and denominator IDs; audit age and income sentinels, CMPE codes, coverage, and domain support before calculating claims. |
| Editorial publication | Verify every sentence, chart, table, and export links to a validated estimate and applies the same suppression state. Label nominal income and descriptive time changes. |
| Release | Clean offline replay, independent numerical and visual review, license/secret scan, and failed-refresh invalidation are gates; CI green alone does not certify research validity. |

**What may still be missed:** The current Q2 frame may encode official pseudo-strata or finite-population details not exposed by the inspected files; period-specific factor revisions and questionnaire changes remain to be inventoried. The proposed grand-mean adjustment could disagree materially with official precision even when Python and R agree. Treat that disagreement as a research result requiring a documented decision, never as a tolerance to loosen.
