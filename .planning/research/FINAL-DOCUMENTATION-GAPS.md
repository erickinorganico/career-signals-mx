# Final documentation gap map — real-data v1.0.0

**Review date:** 2026-09-22  
**Scope:** inventory for the Phase 5 documentation rewrite; no public documentation was changed.  
**Authority used:** `AGENTS.md`, `docs/CONTRACT.md`, `.planning/PROJECT.md`, `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`, current README files, and the current phase/release evidence.

## Current completion boundary

The canonical planning record says that v1.0.0 is the complete real-data ENOE
publication, not the historical synthetic demo. Phase 1 is complete; Phase 2 is
executing; Phases 3–5 are not accepted. `.planning/STATE.md` records 1/5 phases
accepted and explicitly says this is not release completion. The final public
claim must therefore remain conditional until numerical, analytical,
publication, operation, and release gates have receipts.

The current checkout has concurrent edits in `brujula/estimates.py` and
`brujula/populations.py`; this inventory does not touch them.

## Required bilingual deliverables and current ownership

`REL-01` in `.planning/REQUIREMENTS.md` is the canonical list: Spanish and
English README, scope, PRD, architecture, method, installation, commands,
update guide, contribution guide, and citation. The table below maps each
deliverable to its current evidence and the final rewrite needed.

| Final deliverable | Current file(s) | Current state | Final evidence required before claiming complete |
|---|---|---|---|
| Spanish/English entry point | `README.md`, `README.en.md` | Both correctly warn that real v1.0.0 is under construction, but the English page still presents the pilot as the implemented design and calls ENOE future work. | Accepted real bundle ID/version, supported commands, public output paths, report/data links, exact limitations, and matching Spanish/English wording. |
| Scope and questions | `docs/SCOPE.md`, `docs/PRD.md`, `.planning/PROJECT.md`, `.planning/REQUIREMENTS.md` | `docs/*` describe the original synthetic first release and list numerical ENOE as out of scope; `.planning/*` defines the real eight-quarter scope. | Phase 3 claim registry and accepted coverage matrix proving fields, cohort, national context, quarters, sex, entity, measures, exclusions, and unsupported questions. |
| Architecture and contracts | `docs/ARCHITECTURE.md`, `docs/CONTRACT.md`, `docs/CONTRACT-V2.md`, `.planning/codebase/ARCHITECTURE.md` | v1 synthetic architecture remains presented as current; v2 is the real-data contract but is explicitly not an activation or precision certificate. | Final data-flow diagram and contract/version boundary tied to the public projection, accepted run, manifest, and current pointer. |
| Method and definitions | `docs/METHODOLOGY.md`, `docs/GLOSSARY.md`, `docs/research/ENOE-METHOD-REVIEW.md`, `.planning/phases/02-defensible-survey-estimates/02-METRIC-AUDIT.md` | Existing method explains the pilot and future M6; detailed real-data rules are split across v2 contract and Phase 2 research. | Accepted estimator/oracle comparison, official reconciliation, metric denominator/nonresponse/sentinel ledger, singleton policy, CV/IC90 policy, and known limitations. |
| Installation and commands | `README.md`, `README.en.md`, `docs/RELEASE.md`, `CONTRIBUTING.md` | Commands are demo-oriented (`demo`, synthetic `report`, `verify`, `scout`); no accepted real-data replay command/output contract is documented. | Clean Windows and Ubuntu receipts, dependency lock/install evidence, real replay command, fixture isolation proof, and exact artifact paths. |
| Refresh/update guide | No dedicated guide; partial rules in `docs/RELEASE.md`, `docs/FINAL-RELEASE-PLAN.md`, `docs/CONTRACT.md` | Receipt/hash/current rules exist, but acquisition, snapshot rotation, invalidation, and re-publication instructions are not consolidated or bilingual. | One documented refresh/replay procedure with source catalog, hashes, receipts, failure behavior, and a verified clean replay. |
| Contribution and citation | `CONTRIBUTING.md`, `THIRD_PARTY_NOTICES.md`, `LICENSE`, `docs/SOURCES.md` | Contribution and source attribution exist; citation guidance is not a single final bilingual artifact and must not cite synthetic release evidence as real findings. | Citation block for INEGI/source snapshots, transformation/method code, release SHA/tag, report, aggregates, and attribution/license review. |
| Editorial report | `.planning/phases/04-offline-publication-and-reproducible-operation/04-EDITORIAL-SPEC.md`, `brujula/report.py` | Editorial design is a Phase 4 specification; no accepted real report, PDF, or cross-format parity receipt exists. | Accepted HTML/Markdown/PDF generated from one public projection, visual checks at required sizes, PDF inspection, claim/figure/table/export parity, and suppression proof. |
| Reusable data/evidence | `docs/CONTRACT-V2.md`, `brujula/export.py`, `brujula/warehouse.py`, `docs/evidence/*` | Public v2 schema and export rules exist; current evidence files mostly certify the synthetic 0.1.0 release. | Public aggregate files, dictionary, keys, manifest, hashes, source/method/evidence references, and proof that no microdata or diagnostic estimates ship. |
| Release and acceptance | `docs/RELEASE.md`, `docs/STATUS.md`, `docs/evidence/release-receipt.json`, `.planning/STATE.md`, Phase 5 requirements | Existing receipt/status are historical synthetic v0.1.0 evidence; Phase 5 plans are `TBD` and REL/GSD requirements are pending. | Independent numerical/conceptual/visual/security/license review, clean replay, final GSD audit, GitHub tag/release, and receipt whose target SHA and assets match. |

There is only one English public README. The rest of the required user-facing
documentation is Spanish or technical JSON/schema material. Phase 5 should
either provide English counterparts for the listed user-facing documents or
state an explicit bilingual boundary; it should not imply that linking the
Spanish technical docs satisfies bilingual coverage.

## Historical or demo claims that must be replaced or clearly quarantined

The following claims are valid only for the synthetic historical release and
must not survive in a final real-data narrative without an explicit
“historical fixture” label:

* `README.md` and `README.en.md` describe three pilot fields, 2025-Q2–Q4,
  illustrative Jalisco, 54 synthetic observations, and an ENOE extension as
  future work. Those statements conflict with the active v1 scope of eight
  quarters (2024-Q3–2026-Q2), real ENOE estimates, and the completed-study
  cohort.
* `docs/SCOPE.md`, `docs/METHODOLOGY.md`, `docs/ARCHITECTURE.md`, `docs/PLAN.md`,
  `docs/ROADMAP.md`, and `docs/VALIDATION-PLAN.md` retain the M0–M6 narrative
  in which real ENOE is conditional/post-MVP. In the active milestone, real
  ENOE is the v1.0.0 product and the old M6 text is stale, although its
  synthetic regression controls remain useful.
* `docs/STATUS.md`, `docs/RELEASE.md`, `docs/evidence/release-receipt.json`,
  `examples/synthetic/README.md`, and `docs/README.md` are evidence for v0.1.0
  only. Their test counts, release PASS, wheel, and report language cannot be
  used as evidence of real-data numerical acceptance or v1.0.0 completion.
* The current CLI examples (`demo`, synthetic `report`, and `verify`) prove
  local replay mechanics but do not prove ENOE estimation, R/oracle agreement,
  official reconciliation, or final publication.

The final docs should preserve a short historical-demo section because the
fixture is a regression gate, but place it after the real-data status and label
every synthetic artifact, number, and receipt as such.

## Evidence that future final claims must cite

| Claim family | Existing implementation/research evidence | Missing acceptance evidence |
|---|---|---|
| Official inputs and provenance | `brujula/acquisition.py`, `brujula/source_inventory.py`, `brujula/enoe_adapter.py`, `data/catalog/sources.json`, `docs/SOURCES.md`, Phase 1 `01-VERIFICATION.md` and `01-VALIDATION.md` | Final eight-snapshot receipt set and source terms/attribution review linked to the accepted run. |
| Population and dimension separation | `brujula/populations.py`, `brujula/research_contract.py`, `contracts/research-v2*.schema.json`, `docs/CONTRACT-V2.md` | Phase 2/3 accepted records proving cohort eligibility, unknown handling, code mapping, and no cross-dimension substitution. |
| Complex-survey estimates and precision | `brujula/survey.py`, `brujula/estimates.py`, `tests/test_survey.py`, Phase 2 plans/research/audits | Real-data full-design outputs; independent R `survey` comparison; official national/entity reconciliation; final singleton and suppression decisions. |
| Metrics and coverage | `brujula/metrics.py`, `brujula/enoe_adapter.py`, `.planning/phases/02-defensible-survey-estimates/02-METRIC-AUDIT.md` | Per-metric numerator/denominator, sentinels, nonresponse, observed n, UPM/strata, CV/IC90 and support receipts. |
| Findings and comparability | `brujula/quality.py`, `brujula/insights.py`, `brujula/pipeline.py`, `.planning/REQUIREMENTS.md` ANA-01–06 | Phase 3 accepted claim ledger with exact estimate/source/method IDs, blocked deltas, and no unsupported causal or personal recommendation prose. |
| Public projection and exports | `brujula/research_contract.py`, `brujula/export.py`, `brujula/warehouse.py`, v2 public schema | Phase 4 proof that one validated projection feeds every format and that suppressed diagnostics never appear in tables, figures, text, PDF, or alt text. |
| Offline publication | `brujula/report.py`, `.planning/.../04-EDITORIAL-SPEC.md` | Real HTML/Markdown/PDF, SVG/PNG, semantic tables, mobile/desktop/200%/A4 inspection, parity and accessibility receipts. |
| Fail-closed operation | `brujula/pipeline.py`, `brujula/runlock.py`, `docs/CONTRACT.md`, synthetic tests | Real refresh/replay receipts showing manifest/hash sealing precedes current promotion and any required-source failure invalidates current. |
| Final release | `.planning/REQUIREMENTS.md` REL-01–04/GSD-01, `.planning/ROADMAP.md`, `.planning/STATE.md` | Phase 5 independent audit, clean-install/replay results, secret/license/microdata review, target SHA, tag/release URL and final GSD traceability. |

The presence of a module or isolated test is implementation evidence, not
acceptance evidence. The final docs should link the acceptance receipt for each
claim family and retain “pending”, “blocked”, or “review” where that receipt is
absent.

## Consolidation proposal for Phase 5

Use `.planning/PROJECT.md`, `.planning/REQUIREMENTS.md`, and
`.planning/ROADMAP.md` as the single active v1.0.0 planning authority. Use
`docs/CONTRACT-V2.md` as the real-data interface authority and
`docs/CONTRACT.md` as the synthetic regression contract. Use one final
`docs/METHODOLOGY.md` for accepted definitions and precision, one final
`docs/ARCHITECTURE.md` for the implemented real pipeline, and one final
`docs/RELEASE.md` for installation, refresh, replay, evidence, and release
acceptance. Keep `docs/FINAL-RELEASE-PLAN.md` as the milestone narrative, with
links to those canonical documents rather than duplicated requirements.

Retain `docs/SCOPE.md`, `docs/PRD.md`, `docs/PLAN.md`, `docs/ROADMAP.md`, and
`docs/VALIDATION-PLAN.md` as history only if their headers clearly mark the
synthetic/M0–M5 baseline and link to the active planning files. Otherwise
rewrite them around the accepted real scope. `docs/STATUS.md` must become a
short current status page that distinguishes implementation, local checks,
phase acceptance, publication, and GitHub release. `docs/README.md` should be a
navigation index, not a second specification.

Do not invent a new CLI name or output directory in the rewrite. Derive those
from the accepted Phase 4 implementation and its receipts. Do not call a
source active, a number measured, a report final, or a release complete merely
because a schema, prototype, historical receipt, or plan exists.

## Critical contradiction

The single material contradiction is between the active planning authority and
the legacy public design docs: `.planning/PROJECT.md`, `.planning/REQUIREMENTS.md`,
`.planning/ROADMAP.md`, `README.md`, and `README.en.md` state that real ENOE
v1.0.0 is the current target, while `docs/SCOPE.md`, `docs/METHODOLOGY.md`,
`docs/ARCHITECTURE.md`, `docs/PLAN.md`, `docs/ROADMAP.md`, and
`docs/VALIDATION-PLAN.md` still state that ENOE is a future conditional M6
extension. A reviewer could therefore mistake the published synthetic v0.1.0
for the active product or read stale “out of scope” text as the final contract.

This is a documentation contradiction, not evidence that v1.0.0 is complete.
The current authoritative completion state remains: Phase 1 accepted, Phase 2
executing, numerical acceptance pending, Phases 3–5 pending, and no final
real-data release accepted.
