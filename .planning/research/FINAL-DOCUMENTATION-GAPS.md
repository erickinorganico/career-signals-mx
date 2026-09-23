# Final documentation gaps — Phase 4 handoff

Audit date: 2026-09-23. This is a read-only documentation audit. It compares the
reader-facing documentation that exists in the repository with the accepted
Phase 2 numerical receipt, the accepted Phase 3 aggregate handoff, and the six
checked Phase 4 plans. It proposes documentation work only; it does not change
source policy, activate a source, create Phase 5 execution plans, or claim that
Phase 4 has passed.

## Accepted baseline used for comparison

`docs/evidence/phase-03-analysis-acceptance.json` records `status: PASS`, eight
ENOE snapshot IDs from 2024-Q3 through 2026-Q2, 6,739 sanitized records, 4,209
comparisons, 38 claims, zero persisted JSON validation errors, and the explicit
scope limitation that Phase 4 rendering/exports/installed runtime/sealing/current
resolution remain separate gates. `.planning/phases/04-offline-publication-and-reproducible-operation/04-UPSTREAM-PREFLIGHT.md`
confirms the same persisted packet and says to preserve historical evidence
while requiring fresh installed runtime proof. The Phase 4 plans define the
remaining publication and reproducible-operation work; their completion is not
inferred here.

## Findings

| ID | Existing reference | Gap observed | Concrete required update |
|---|---|---|---|
| DOC-01 | `README.md:10-24`; `README.en.md:7-24` | The banners correctly say Phases 1–3 are accepted and Phases 4–5 remain pending, but they link only the Phase 2 numerical receipt. The accepted Phase 3 packet and its limitation boundary are not reachable from the landing page. | Add direct links to `docs/evidence/phase-03-analysis-acceptance.json` and the Phase 4 upstream/readback status. Keep the 0.1.0 synthetic-demo warning and the statement that publication/release remain separate gates. |
| DOC-02 | `README.md:51`; `README.en.md:41-44` | “Fuente real futura” / “An ENOE extension is future work” and “No real source ingestion” are stale or misleading after the accepted eight-snapshot real analytical handoff. | Say that the real ENOE analytical packet is accepted for the Phase 2–3 scope, while Phase 4 publication and Phase 5 release evidence remain pending. Preserve the rule that catalog inclusion or agent proposals never activate a new source or authorize publication. |
| DOC-03 | `docs/README.md:3-11,31-32` | It says numerical acceptance is still pending, and describes existing `RELEASE.md` and the synthetic example as files the integrator will create. It names `CONTRACT-V2` as authoritative without linking it in the implementation row. | Change the status to “numerical Phase 2–3 acceptance complete; offline publication and final release pending”; link the Phase 3 receipt, `CONTRACT-V2.md`, and current Phase 4 status. Replace future creation wording with the actual historical/current status. |
| DOC-04 | `docs/ARCHITECTURE.md:3,17-19,188-191` | The historical architecture says ENOE real belongs to M6 and remains blocked, while the active repository has accepted real Phase 2–3 analysis. The historical banner does not provide a direct current-architecture entrypoint. | Retain the v1 historical scope, but add a clearly labeled current Phase 2–4 boundary: accepted real analytical handoff, Phase 4 publication in progress, Phase 5 release separate. Route readers to `CONTRACT-V2.md` and `04-UPSTREAM-PREFLIGHT.md`. |
| DOC-05 | `docs/CONTRACT-V2.md:45-47`; `docs/research/ENOE-METHOD-REVIEW.md:39,195` | `completed_professional_known_age` is described as accepting “15–97”, which can be read as an exact upper age or as treating code 97 as age 97. The method review says EDA 97 means 97 or more. | State explicitly that EDA 15–96 are ordinary ages, EDA 97 is the top-coded 97-or-more category, and EDA 98/99 are unknown according to the applicable universe. Do not render 97 as an exact age or silently turn unknown age into a number. |
| DOC-06 | `docs/CONTRACT-V2.md:86-94,118,137-142` | The contract still says Phase 2 will calculate/contrast estimates and precision and that Phase 3 equivalence remains under review. Those gates are accepted in the Phase 2–3 receipts, although project precision remains explicitly nonofficial and Phase 4 is separate. | Replace future-tense gate language with links to the accepted receipts and list the remaining limits: nonofficial project precision, installed-code/resource identity, rendering/export, sealing, current resolution, and final release. Preserve the contract’s rule that it does not itself authorize publication. |
| DOC-07 | `docs/METHODOLOGY.md:96-119,123-125` | The “Precisión para ENOE real (M6)” section says real figures remain internal and the source is inactive until variance is implemented; the current accepted handoff already contains real aggregate analysis and validated precision diagnostics. | Mark the text as the historical/pre-publication policy boundary, then state that Phase 2 numerical and Phase 3 analytical acceptance exists for the eight snapshots. Explain that nonofficial precision and Phase 4/5 publication gates still prevent treating the handoff as a released public report. Update “candidato primario de M6” to distinguish accepted snapshot custody from future source activation/publication decisions. |
| DOC-08 | `docs/SOURCES.md:8-16,24-25,31`; `docs/source-research.json:82,299` | “Prioritized candidate”, “future extension”, and `numeric_ingestion_allowed=false` are safe for an unactivated catalog source but are misleading when read as describing the already accepted eight-snapshot analytical input. | Add an explicit two-state note: the eight catalogued ENOE snapshots are the accepted Phase 2–3 analytical input; source activation/public release remains a separate controlled decision. Keep OLA/Data México/IMCO as reference or benchmark sources and retain the prohibition on automatic activation. |
| DOC-09 | `docs/STATUS.md:3-18,20-26,40`; `docs/RELEASE.md:64-75`; `docs/SPEC.md:168-175` | These documents correctly preserve the synthetic v0.1.0 release, but “official data blocked by M6/source_activation” can hide the accepted real analysis and make the active status appear pre-Phase 2. `STATUS.md:23` is also dated 2026-09-22 while the accepted Phase 3 receipt is 2026-09-23. | Keep the v1 release as historical and blocked for real publication, but name the accepted Phase 2–3 analytical packet and link its receipt. Update the status date and reserve `source_activation` wording for a new public source/release decision, not the already accepted handoff. |
| DOC-10 | `docs/research/ENOE-METHOD-REVIEW.md:181,201-211` | It reports R/official precision comparison as pending even though the Phase 2 acceptance and Phase 3 preflight record the accepted numerical/R/reference checks. It also mixes implementation caveats with current release status. | Mark the completed Phase 2 checks as accepted with receipt links; retain unresolved nonofficial-precision and publication limitations as explicit Phase 4/5 dependencies. Keep the open methodological caveats that are genuinely outside the accepted packet. |
| DOC-11 | `docs/CONTRACT.md:1-9,95,168-174`; `docs/SPEC.md:1-7` | The v1 contract/spec is useful for the historical synthetic release, but the main documentation route can leave readers believing it is the current real-data interface. | Label these documents as v1 historical compatibility references in their reader-facing introductions and add a prominent link to `CONTRACT-V2.md` and the accepted Phase 3 packet. Do not rewrite v1 schemas or synthetic examples into v2. |

## Missing reader routes and present-file inventory

The repository has `README.md`, `README.en.md`, `CONTRIBUTING.md`,
`docs/README.md`, `docs/RELEASE.md`, and the research/method/source documents
listed above. No `INSTALL.md`, `UPDATE.md`, `docs/UPDATE.md`, `CITATION.cff`, or
`docs/CITATION.md` exists at audit time. The required reader updates are:

| Route gap | Required route or decision |
|---|---|
| Landing page → accepted analytical handoff | Link both README languages to `docs/evidence/phase-03-analysis-acceptance.json`; keep Phase 2 evidence as upstream numerical support. |
| Documentation index → current contract | Make the `CONTRACT-V2.md` link explicit in the `SPEC`/implementation row, rather than mentioning it only in the introductory paragraph. |
| Documentation index → Phase 4 status | Add a reader-facing route to the Phase 4 upstream preflight and, once produced, the aggregate-only publication acceptance receipt. Do not link an unproduced Phase 5 plan as if it were evidence. |
| Installation/update guidance | Keep the existing install/replay commands in README and RELEASE; if update or clean-install policy is needed for Phase 5, add a dedicated file and link it instead of implying that an absent file exists. |
| Citation route | Decide whether the final public release needs `CITATION.cff` or a citation page. Until created, state that no citation file is present; do not invent a citation target. |

## Phase 4 dependency matrix for Phase 5

Phase 5 may use a Phase 4 row only after its receipt identifies the exact
inputs, implementation/resource hashes, commands, exits and status. A planned
artifact or a local test result alone is not release evidence.

| Phase 4 plan | Required Phase 4 output | Phase 5 dependency | Evidence needed before release |
|---|---|---|---|
| 04-01 | Installed wheel resources, audited fonts/PDF dependency declaration, outside-checkout resource checks | Clean install must resolve the same package/resource identity and license inventory | Wheel/resource SHA-256, license review, missing-resource failure, installed fixture regression |
| 04-02 | Installed real eight-snapshot acceptance, unchanged replay, guarded trusted-reference rebind | Release must bind the actual executing implementation and accepted numerical/analysis digests | Immutable acceptance/replay receipts, module/oracle/R identity, exact digest and row readback, no caller repin |
| 04-03 | Validated public model and CSV/Parquet/DuckDB/dictionary exports | Release bundle must preserve typed grain, provenance, suppression and CSV safety in every format | Actual-container row/key parity, schema/readback, suppression and formula-injection controls |
| 04-04 | Offline HTML/Markdown/PDF, SVG/PNG pairs, semantic tables, visual review | Release must expose equivalent accessible static outputs with no network/private-file fetch | Extracted-PDF semantic parity, local-fetcher negatives, font/asset hashes, visual evidence and recheck |
| 04-05 | Sealed manifest/receipt, fail-closed current resolver, refresh/build/replay/open CLI | Release must resolve only a live verified current and invalidate it after failed acquisition | Eight live acquisition checks, manifest/artifact hashes, atomic failure receipt, replay determinism and fault matrix |
| 04-06 | Aggregate-only Phase 4 acceptance evidence and bundle/secret/license scan | Release review must distinguish Phase 4 completion from publication/tagging and preserve public-safe evidence | Full edge/prohibition results, installed Windows/Ubuntu checks, visual/PDF outcomes, receipt SHA and publication review |

Phase 5 should update the reader routes only after these dependencies have
concrete receipts. The synthetic v0.1.0 release, examples and v1 contracts
remain historical compatibility material throughout that update.


## Preserved full REL-01 documentation scope

This refreshed audit supplements the earlier 2026-09-22 map; it does not reduce its required deliverables. Spanish and English coverage must include the following reader material. An English README linking only Spanish instructions does not satisfy the full bilingual requirement.

| Deliverable | Existing files | Required final evidence and content |
|---|---|---|
| Reader entrypoints | README.md, README.en.md | Actual report/data/release links, observation versus publication dates, accepted findings and visible limits; synthetic history remains labeled. |
| Scope and questions | docs/SCOPE.md, docs/PRD.md | Accepted eight-quarter real ENOE scope, three focal fields, professional cohort, separate national context, recorded sex, 32 entities, measures, coverage and unsupported questions. |
| Architecture and contracts | docs/ARCHITECTURE.md, docs/CONTRACT-V2.md, docs/CONTRACT.md | Current source-to-publication data-flow diagram, ten-dimensional grain, public projection, receipt/manifest/current authority; v1 remains a historical synthetic compatibility contract. |
| Method and definitions | docs/METHODOLOGY.md, docs/GLOSSARY.md, docs/research/ENOE-METHOD-REVIEW.md | Accepted population/metric/sentinel rules; observed n versus weights; variance, singleton, IC90/CV and suppression policies; R/official reconciliation and untuned limitations. |
| Installation and commands | README.md, README.en.md, docs/RELEASE.md, CONTRIBUTING.md | Verified installed Windows/Ubuntu commands, Python/PDF/native/R prerequisites, explicit offline source and benchmark paths, actual output inventory. |
| Refresh and update | Dedicated guide or consolidated docs/RELEASE.md | Approved source acquisition, current receipts, offline replay, source changes, failure invalidation and re-publication procedure. |
| Contribution and citation | CONTRIBUTING.md, THIRD_PARTY_NOTICES.md, LICENSE, docs/SOURCES.md | Fixture-isolated development, reviewed source/bridge rules, INEGI attribution, transformation authorship, release tag/SHA, method and artifact citations. |
| Public reports and data | Phase 4 report/export outputs and dictionary | Equivalent Spanish HTML/Markdown/PDF, SVG/PNG and semantic tables; join keys, nulls, uncertainty, provenance and exact downloadable public aggregate inventory. |
| Release and acceptance | docs/RELEASE.md, docs/STATUS.md, docs/evidence | Exact source/package/bundle identities, independent conceptual/numerical/visual/security reviews, clean reproduction, GitHub public asset readback and final GSD audit. |

Provide English counterparts or bilingual sections for the required guides; the primary research report itself is Spanish per PUB-01. Do not substitute historical synthetic tests/releases for real-data acceptance.

## Evidence families and active authority

Phases 1–3 are accepted; their evidence should be linked without reopening unchanged checks or claiming they certify Phase 4. Final claims map as follows:

| Claim family | Accepted or required authority |
|---|---|
| Eight official inputs and custody | Phase 1 VERIFICATION/VALIDATION, approved snapshot catalog and immutable acquisition receipts; final bundle binds exact current inputs. |
| Populations, metrics and complex-survey precision | Phase 2 numerical acceptance receipt and metric audit, independently checked R/official reconciliation, current population definitions. |
| Findings, comparability and redactions | Phase 3 analytical acceptance receipt, strict accepted persisted packet, canonical claim/record/comparison references and complementary suppression. |
| Installed resources | 04-01 summary and exact wheel/resource proof; full real installed acceptance still belongs to 04-02/05. |
| Single public projection and exports | Required 04-03 and 04-06 exact-container readbacks, null/status/provenance parity and disclosure controls. |
| Offline report and figure quality | Required 04-04/06 actual HTML/MD/PDF/SVG/PNG, semantic parity, visual inspection and restricted fetcher results. |
| Fail-closed operation | Required 04-05/06 sealed manifest, current/source checks, replay and fault-injection evidence. |
| Final publication | Required Phase 5 independent audit, clean-install/replay and public GitHub tag/asset hashes; final GSD traceability. |

Keep .planning/PROJECT.md, REQUIREMENTS.md and ROADMAP.md as active milestone planning authority. Consolidate implemented research method in docs/METHODOLOGY.md, architecture in docs/ARCHITECTURE.md and release/operation in docs/RELEASE.md with a concise docs/STATUS.md. docs/README.md is the reader index. Old docs/PLAN.md, docs/ROADMAP.md, docs/VALIDATION-PLAN.md and M0–M6 scope must be rewritten to actual accepted scope or visibly retained as historical synthetic design with current links. Preserve v1 contracts and examples for regression, after the current real research entrypoint.

Derive final command names and artifact paths from accepted Phase 4 interfaces. As of this refresh, 04-01 is complete and 04-03 is executing; Phases 4–5 are not accepted. No final release claim follows from this documentation inventory.
