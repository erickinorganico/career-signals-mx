# Phase 5: Independent Audit and v1.0.0 Release — Research

**Researched:** 2026-09-24 UTC
**Domain:** independent real-data acceptance, bilingual documentation, public asset custody and GitHub release
**Confidence:** HIGH for accepted local interfaces; MEDIUM for final release procedure while 04-06 and native CI remain open. [VERIFIED: `.planning/STATE.md`; `04-INTEGRATED-OPERATION.md`]

## User Constraints

Copied verbatim from `05-CONTEXT.md`:

### Locked decisions

- Deliver Spanish and English onboarding, scope, PRD, architecture, methodology, installation, commands, update instructions, contribution and citation guidance. The research report itself is Spanish as required by PUB-01. Derive all concrete commands and paths from accepted Phase 4 code rather than inventing interfaces early.
- Use the documentation gap map at `.planning/research/FINAL-DOCUMENTATION-GAPS.md` to replace conflicting historical narratives. Preserve historical receipts and synthetic regression instructions with unmistakable version/synthetic labels; avoid duplicate mutable specifications.
- Verify clean Windows and Ubuntu installation and package resources. Separate network-assisted dependency installation/source acquisition from offline numerical replay. CI with fixtures proves software portability; it does not substitute for actual eight-quarter numerical replay, R/official comparison or final PDF visual inspection.
- Publish only validated public aggregates, reports, figures, data dictionaries, code/package resources, sealed manifest and acceptance evidence. Raw ZIPs, person frames, private paths, credentials, local toolchains and software caches stay outside the release.
- Review source redistribution terms, attribution, transformed-data disclaimers, dependency/font licenses and secret/microdata absence against the actual asset inventory and target SHA. Research inventories are inputs, not final audit approval.
- Independent reviews cover numerical and conceptual integrity, comparability, editorial/visual quality, PDF fidelity, cross-format suppression, operation/current invalidation and all milestone requirements. Fix material findings and reverify their affected evidence before claiming completion.
- Final GSD audit must trace each requirement to plans, implementation, checks, reviews and accepted artifacts. Preserve failures and their resolution; unresolved material gates prevent final completion or release publication.
- Publish 1.0.0 to the already authorized repository, linking code/tag, Spanish report, figures, aggregates, manifests and acceptance evidence. Verify uploaded asset hashes by readback and record exact URLs and commit identity. Keep the existing draft PR attached and make it reviewable only after required checks pass.
- There is no hosted application, new data source, paid deployment or user account integration in this release.

### Existing evidence to reuse

`.planning/REQUIREMENTS.md` REL-01 through REL-04 and GSD-01; previous phase verification/acceptance files; `docs/research/DEPENDENCY-LICENSE-INVENTORY.md`; `.planning/research/FINAL-DOCUMENTATION-GAPS.md`; existing `.github/workflows/verify.yml`, package configuration and historical release receipts. Read their actual final state again before executable plans.

### Deferred within the milestone

Executable plans, exact asset lists, final package version changes and release actions wait for the accepted Phase 4 interfaces. This preparation does not mark any REL requirement complete.

<phase_requirements>

## Phase Requirements

| ID | Description (from REQUIREMENTS.md) | Research support |
|---|---|---|
| REL-01 | README en español/inglés, scope, PRD, arquitectura, método, instalación, comandos, guía de actualización, contribución y citación describen capacidades reales y límites actuales. | Bilingual coverage matrix, actual CLI/package readback and stale-document correction map. [VERIFIED: `.planning/REQUIREMENTS.md`; `brujula/cli.py`; `FINAL-DOCUMENTATION-GAPS.md`] |
| REL-02 | Instalaciones limpias y pruebas en Windows/Ubuntu verifican fixtures sin producción; el bundle real recibe revisión independiente numérica, conceptual y visual, además de replay offline. | Separate clean-host fixture proof from accepted real installed/replay evidence and final independent review. [VERIFIED: `.planning/REQUIREMENTS.md`; `04-02-SUMMARY.md`; `04-INTEGRATED-OPERATION.md`] |
| REL-03 | El paquete público pasa revisión de secretos, licencias, atribución y ausencia de microdatos; solo artefactos validados se publican en erickinorganico/career-signals-mx. | Closed allowlist, nested archive scan, exact-target license/source review and tracked planning-path audit. [VERIFIED: `.planning/REQUIREMENTS.md`; `AGENTS.md`; `scripts/check_docs.py`] |
| REL-04 | Un release 1.0.0 enlaza código, informe, figuras, agregados, manifiesto y evidencia de aceptación; la versión final no se declara completa con gates materiales pendientes. | Draft upload/readback, publication/public readback, target-SHA receipt and final phase verification. [VERIFIED: `.planning/REQUIREMENTS.md`; `05-CONTEXT.md`; `GSD-FINAL-GATE-MAP.md`] |
| GSD-01 | Requisitos, fases, planes revisados, ejecución, verificaciones, revisión de código y auditoría final quedan trazables en GSD; las recomendaciones se siguen conservando las autorizaciones y restricciones del proyecto. | Requirement-to-evidence trace, review and security hooks, final UAT/milestone audit after release proof. [VERIFIED: `.planning/REQUIREMENTS.md`; `.planning/config.json`; `GSD-FINAL-GATE-MAP.md`] |

</phase_requirements>

## Project Constraints (from AGENTS.md)

- Read `docs/CONTRACT.md` before interface changes; local code, documentation, fixtures and isolated tests are authorized. [VERIFIED: `AGENTS.md`]
- No paid APIs, external inference, credentials or third-party messages; only publication to `erickinorganico/career-signals-mx` is authorized after secret/license review. [VERIFIED: `AGENTS.md`]
- Deliver local scripts, pipelines, tables, charts, Markdown/HTML reports and agent evidence; no frontend, backend or navigable application. [VERIFIED: `AGENTS.md`]
- Keep field of study, occupation, industry, geography, period and source separate; null remains null and synthetic outputs are explicit. [VERIFIED: `AGENTS.md`]
- Comparability requires source, universe, geography, measure, price basis, method, concept and period; changed dimensions block automatic deltas; unavailable precision remains visible. [VERIFIED: `AGENTS.md`]
- Raw artifacts are content addressed; failed refresh leaves a receipt and invalidates current; only validated evidence-bound artifacts are releasable. [VERIFIED: `AGENTS.md`]
- Preserve concurrent edits, do not delegate further from this assignment, and exclude unrelated proprietary material. [VERIFIED: `AGENTS.md`]

## Summary

Phases 1–3 and Phase 4 plans 04-01 through 04-05 are accepted. The project now has an installed real ENOE analytical path, a guarded public projection, offline Spanish HTML/Markdown/PDF, nine SVG/PNG figure pairs, typed public exports and sealed current/replay commands. The current installed `c222f69` wheel produced run `20260924T010247-81cfb71ea5f1`: 73 content artifacts, 22 typed tables, nine figure groups and 97 PDF pages under manifest SHA-256 `38c3dfc21d816f32d7e4a21d7efd89418fc198fd80e94577783706f00d7fb023`. This is bounded installed build/open and metadata-continuity evidence, not Phase 4 completion or a new full reconstruction replay on this exact wheel. [VERIFIED: `.planning/STATE.md`; `04-01-SUMMARY.md`–`04-05-SUMMARY.md`; `04-INTEGRATED-OPERATION.md`]

04-06 integrated disclosure controls, independent review and native Windows/Ubuntu CI are still running. The final public package version remains `0.1.0`; the existing release receipt records a historical synthetic release. Candidate bilingual documents and license/source maps under ignored `.cache/research/phase5-doc-drafts/` are preparation only and need target-SHA review before integration. No REL-01–04 or GSD-01 completion follows from them. [VERIFIED: `.planning/STATE.md`; `pyproject.toml`; `docs/evidence/release-receipt.json`; `.cache/research/phase5-doc-drafts/INTEGRATION-NOTES.md`]

**Primary recommendation:** After 04-06 acceptance, freeze one target commit and its accepted run, integrate evidence-checked bilingual docs, independently close the numerical/editorial/security/clean-install matrix, then use an exact asset allowlist for draft upload, remote readback, publication, public readback and final GSD verification. [VERIFIED: `05-CONTEXT.md`; `.planning/research/GSD-FINAL-GATE-MAP.md`; `04-INTEGRATED-OPERATION.md`]

## Architectural Responsibility Map

| Capability | Primary tier | Secondary tier | Rationale |
|---|---|---|---|
| Numeric acceptance and offline replay | Installed local CLI | Approved local source cache and R oracle | `enoe-accept`/`enoe-replay` own actual numerical recomputation; public release consumes sealed summaries. [VERIFIED: `brujula/cli.py`; `04-02-SUMMARY.md`] |
| Public projection and report | Local package | Immutable run directory | `research-analyze/build/replay/open` validate, seal and resolve report/export bytes. [VERIFIED: `brujula/cli.py`; `04-03-SUMMARY.md`–`04-05-SUMMARY.md`] |
| Bilingual reader guidance | Repository docs | GitHub release text | Docs describe accepted interfaces, evidence and limits. [VERIFIED: `05-CONTEXT.md`; `FINAL-DOCUMENTATION-GAPS.md`] |
| Independent acceptance and allowlist | Local review/evidence | GitHub draft | The reviewed target SHA, exact manifest and legal/privacy controls determine what can be uploaded. [VERIFIED: `05-CONTEXT.md`; `AGENTS.md`] |
| Public delivery | Authorized GitHub repository | Local receipt | Remote asset readback and public access prove the distribution claim. [VERIFIED: `05-CONTEXT.md`; `GSD-FINAL-GATE-MAP.md`] |

## Standard Stack

| Component | Accepted/current state | Phase 5 use |
|---|---|---|
| Python 3.12+, setuptools `80.10.2`, `career-signals-mx` `0.1.0` | Declared package and installed-wheel proof; 1.0.0 version update awaits release target. [VERIFIED: `pyproject.toml`; `04-INTEGRATED-OPERATION.md`] | Build the final wheel outside checkout and inspect its resources, metadata and members. |
| DuckDB `1.4.4`, jsonschema `4.26.0`, Matplotlib `3.10.8`, NumPy `2.5.3` | Current direct pins. [VERIFIED: `pyproject.toml`] | Reuse accepted runtime closure; no new data library. |
| WeasyPrint `70.0`, pypdf `6.19.0`, pytest `9.0.3` | PDF optional extra, PDF audit/test extras and pinned `requirements-pdf.txt`; DejaVu fonts ship as package data. [VERIFIED: `pyproject.toml`; `requirements-pdf.txt`; `04-01-SUMMARY.md`] | Verify native PDF and font/license custody on final wheel; pypdf is audit tooling. |
| R `survey`/`jsonlite` oracle | Explicit R library and installed acceptance/replay already exercised. [VERIFIED: `04-02-SUMMARY.md`; `brujula/cli.py`] | Preserve independent numerical proof and exact implementation/resource identity; R is an audit prerequisite, not a bundled release asset. |
| GitHub Actions Windows/Ubuntu matrix and `gh release` | Matrix workflow under 04-06 edit; release target is named in context. [VERIFIED: `.github/workflows/verify.yml`; `05-CONTEXT.md`] | Accept final native CI result; upload/read back only after local gates. |

No new third-party package is recommended. Existing pins are read from repository manifests, not fresh registry checks, and must be rechecked at the final target SHA. The release phase should review the actual installed dependency closure rather than treating the 2026-09-22 preparation inventory as final approval. [VERIFIED: `pyproject.toml`; `requirements-pdf.txt`; `docs/research/DEPENDENCY-LICENSE-INVENTORY.md`]

## Architecture Patterns

```text
approved eight snapshots + official workbook/PDF + explicit R library
  → installed numerical acceptance / offline replay → sealed accepted analysis
  → public projection → 22 joined typed tables + Spanish reports + nine figure pairs
  → immutable manifest/run + fail-closed current resolver
  → independent reviews + bilingual docs + exact allowlist
  → frozen commit/tag → GitHub draft assets → remote hash readback
  → publish in authorized repository → public readback → Phase 5 verification
  → UAT and milestone audit → administrative closure
                 ↘ material failure: BLOCKED, no release/completion claim
```

The first four stages have accepted plan evidence and the `c222f69` integrated installed proof; the later Phase 5 stages are research guidance, and 04-06 is pending. [VERIFIED: `04-01-SUMMARY.md`–`04-05-SUMMARY.md`; `04-INTEGRATED-OPERATION.md`; `.planning/STATE.md`]

### 1. Bind a single accepted identity

Use the exact code commit, wheel hash, 24 authored resource hashes, 11 numerical implementation/oracle hashes, seven numerical resource hashes, eight snapshot/source identities, numerical/analysis digests, publication run ID and manifest SHA as a freeze record. Raw snapshot hashes remain checked by source custody; analytical `source_manifest` excludes acquisition-clock-bearing `public_v2_digest` so unrelated refresh timing cannot alter canonical analytical content. Do not imply raw integrity was ignored or that a Phase 2 golden was repinned. [VERIFIED: `04-02-SUMMARY.md`; `04-INTEGRATED-OPERATION.md`; `.cache/research/phase5-doc-drafts/INTEGRATION-NOTES.md`]

The installed `c222f69` proof retained all 87 original publication/numerical/acquisition anchors and matched 22 table row sets, 6,739 record IDs, 4,209 comparison IDs, 38 claim IDs and 625 selected IDs across report formats. The accepted earlier complete installed reconstruction replay is reusable only for AST-identical analysis/replay methods; changed recovery, resolution and rendering were separately exercised. A later code/resource change needs a bounded affected recheck. [VERIFIED: `04-INTEGRATED-OPERATION.md`]

### 2. Separate portability from real-data validation

Require clean Windows and Ubuntu Python 3.12 dependency installation, wheel installation outside checkout, package-resource/PDF smoke and fixture checks from the final 04-06 CI matrix. Independently require real eight-quarter numerical/R/official checks, accepted analysis, network-denied replay and visual/PDF review in the approved real-data environment. Do not demand full real R replay on each CI host merely because fixtures pass there. Preserve separate receipts for install/acquisition (network allowed) and numerical replay (network denied). [VERIFIED: `.planning/REQUIREMENTS.md`; `.github/workflows/verify.yml`; `04-02-SUMMARY.md`; `.cache/research/phase5-doc-drafts/INTEGRATION-NOTES.md`]

Installed CLI names and required path flags are in `brujula/cli.py`: `enoe-refresh --source-root --output-root`; `enoe-accept --source-root --output-root --audit-dir --workbook --pdf --r-lib`; `enoe-replay --source-root --run --audit-dir --r-lib`; `research-analyze --source-root --acceptance-receipt --analysis-output --audit-dir`; `research-build --source-root --output-root --audit-dir --analysis-packet`; `research-replay --source-root --run --audit-dir`; and `research-open --source-root --output-root --format`. Numerical commands also accept explicit `--rscript`/`--r-home`. Derive final public instructions from their post-04-06 readback; do not lead real users to the historical `demo`/`report` flow. [VERIFIED: `brujula/cli.py`; `.cache/research/phase5-doc-drafts/OPERATIONS.md`]

### 3. Make the release inventory closed and public-safe

Derive proposed asset paths from the accepted run manifest, public tables, report/figure files, dictionary, public-safe acceptance summaries, package resources and target commit. Record for each asset: role, source path, release name, size, SHA-256, license/source attribution decision and evidence reference. Inspect loose files and nested wheel/archive members. Reject raw ZIPs, person frames, ignored caches, local command envelopes, workstation paths, secrets, native toolchains and diagnostic suppressed values. Compare suppression and provenance through CSV, Parquet, DuckDB, SVG/PNG, HTML, Markdown, PDF text/alt tables and downloadable metadata. [VERIFIED: `05-CONTEXT.md`; `04-03-SUMMARY.md`; `04-04-SUMMARY.md`; `04-INTEGRATED-OPERATION.md`]

`scripts/check_docs.py` scans selected source/docs paths but omits `.planning`; a current read-only search finds 21 planning files with workstation paths. Phase 5 must normalize tracked planning references to portable repository-relative paths or documented GSD installation placeholders while preserving historical evidence. Scan all git-tracked candidate files, wheel members and release assets at the final target; passing the current docs checker alone does not close privacy/portability review. [VERIFIED: `scripts/check_docs.py`; read-only `.planning` path search; `.cache/research/phase5-doc-drafts/INTEGRATION-NOTES.md`]

### 4. Treat release proof as part of Phase 5

Freeze local review first, then create the authorized draft at the exact target SHA, upload only the approved list, download to an isolated directory and rehash every asset. Publish after local independent, license and privacy gates close; repeat public tag/URL/asset readback. Then run canonical Phase 5 verification, code/security review as applicable, documentation verification, UAT/milestone audit and administrative milestone closure. `gsd-ship` requires phase verification and therefore cannot be a prerequisite for the first draft/readback evidence required by REL-04. Preserve the already attached PR and make it reviewable only when checks pass. [VERIFIED: `05-CONTEXT.md`; `.planning/research/GSD-FINAL-GATE-MAP.md`]

The orchestrator rechecked official GitHub documentation on 2026-09-24 after the research agent's fetch failure. `gh release create --draft --target FULL_SHA` can bind automatic tag creation to the reviewed commit; `--verify-tag` instead requires an existing remote tag. `gh release download TAG --dir FRESH_DIRECTORY` retrieves the named release assets. The asset API documents name, size, SHA-256 digest and download URL, with unauthenticated reads for public resources. Compare local SHA-256 with independently downloaded bytes as well as metadata. Documentation establishes the procedure; only the later actual upload and public readback establish this project's release. [CITED: https://cli.github.com/manual/gh_release_create; https://cli.github.com/manual/gh_release_download; https://docs.github.com/en/rest/releases/assets]

## Don't Hand-Roll

| Problem | Use instead | Why |
|---|---|---|
| Numerical/replay engine | Existing installed `enoe-accept`, `enoe-replay`, `research-replay` and sealed receipts | Preserve accepted estimator, R oracle, fixed references and exact data contracts. [VERIFIED: `04-02-SUMMARY.md`; `04-05-SUMMARY.md`] |
| Package resources and PDF | Existing `brujula.resources`, wheel metadata and `pdf_v2` | These already bind authored fonts/oracle/catalogs and restrict local PDF inputs. [VERIFIED: `04-01-SUMMARY.md`; `04-04-SUMMARY.md`] |
| Public export/report model | Existing `publication_v2`, `export_v2`, `report_v2` | A second projection risks mismatched suppression, keys and claims. [VERIFIED: `04-03-SUMMARY.md`; `04-04-SUMMARY.md`] |
| Hashes and release transport | Python `hashlib.sha256`, local manifest and `gh release`/GitHub readback | Standard hashing and platform release operations cover the requirement. [VERIFIED: `04-05-SUMMARY.md`; CITED: https://cli.github.com/manual/gh_release] |

## Common Pitfalls

| Pitfall | Warning sign | Gate |
|---|---|---|
| Historical synthetic result represented as real 1.0 | `0.1.0`, demo fixture or old release receipt appears as current authority | Label v1 historical; link accepted real run, receipt, period and limits. [VERIFIED: `pyproject.toml`; `docs/evidence/release-receipt.json`; `FINAL-DOCUMENTATION-GAPS.md`] |
| CI fixture portability mistaken for real numerical acceptance | Windows/Ubuntu matrix green but no eight-quarter/R/official/replay/visual receipt | Maintain distinct REL-02 columns and evidence. [VERIFIED: `.planning/REQUIREMENTS.md`; `.github/workflows/verify.yml`] |
| Old license inventory treated as final | 2026-09-22 inventory calls WeasyPrint planned | Review final 35-package candidate against frozen installed wheel, native asset boundary, DejaVu notice and actual released bytes. [VERIFIED: `docs/research/DEPENDENCY-LICENSE-INVENTORY.md`; `.cache/research/phase5-doc-drafts/THIRD_PARTY_NOTICES.bilingual.md`; `pyproject.toml`] |
| Metadata or report leak through broad upload | `.cache`, `.planning` paths, raw archives or person-level records included | Closed allowlist, nested inspection and all-tracked-file path/secret scan. [VERIFIED: `05-CONTEXT.md`; `scripts/check_docs.py`] |
| Source activation confused with accepted input | Old docs still say ENOE analysis blocked despite accepted eight snapshots | Distinguish approved analytical snapshots from future source activation/public redistribution decision. [VERIFIED: `FINAL-DOCUMENTATION-GAPS.md`; `.cache/research/phase5-doc-drafts/INTEGRATION-NOTES.md`] |
| Draft considered public release | Owner can download draft but reader cannot | Publish and independently read back public URLs before REL-04/phase verification. [VERIFIED: `GSD-FINAL-GATE-MAP.md`] |
| Current points at interrupted/failed attempt | Historical run remains valid but resolver fails | Report blocked current; do not silently serve historical success. [VERIFIED: `04-05-SUMMARY.md`; `04-INTEGRATED-OPERATION.md`] |
| Canonical digest confused with byte-identical PDF | Generation date changes front page while selected content and pages 2–97 stay identical | Record canonical content/IDs and byte hashes separately; inspect changed page. [VERIFIED: `04-INTEGRATED-OPERATION.md`] |

## Documentation and license integration

Use `FINAL-DOCUMENTATION-GAPS.md` as the coverage list and the ignored bilingual candidates only as drafts. Their maps are pinned to earlier checkpoints; re-anchor every claim, command, source identity and link to the frozen Phase 4 target. Keep eight-quarter national/professional/focal-field coverage distinct from latest-quarter-only other fields, sex and 32-entity detail. Keep public statuses `MEASURED|REVIEW|UNKNOWN|BLOCKED`, precision limitations visible, and source/metadata attribution specific. [VERIFIED: `FINAL-DOCUMENTATION-GAPS.md`; `.cache/research/phase5-doc-drafts/INTEGRATION-NOTES.md`; `docs/CONTRACT-V2.md`]

The preparation terms read records INEGI reuse conditions including attribution, metadata and a visible transformation/no-endorsement statement, but calls itself `PREPARATION_ONLY_NOT_FINAL_ASSET_AUDIT`. The 35-package candidate and third-party notices similarly require actual target review; do not invent a license for missing expressions. Existing v0.1.0 references remain historical. [VERIFIED: `.cache/research/phase5-doc-drafts/inegi-terms-preparation.json`; `.cache/research/phase5-doc-drafts/dependency-license-candidate.json`; `.cache/research/phase5-doc-drafts/THIRD_PARTY_NOTICES.bilingual.md`]

## Code Examples

Use the accepted CLI interface with supplied, reviewed paths; these placeholders are not asset names or assertions of a completed release. [VERIFIED: `brujula/cli.py`]

```powershell
brujula research-replay --source-root <APPROVED_SOURCE_ROOT> --run <SEALED_RUN_DIR> --audit-dir <NEW_AUDIT_DIR>
brujula research-open --source-root <APPROVED_SOURCE_ROOT> --output-root <PUBLICATION_ROOT> --format pdf
```

Illustrative local readback comparison, grounded in the project's SHA-256 manifest pattern; the exact inventory schema is a Phase 5 output. [VERIFIED: `04-05-SUMMARY.md`; `04-INTEGRATED-OPERATION.md`]

```python
from hashlib import sha256
from pathlib import Path

def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()

assert set(downloaded_asset_names) == set(approved_inventory)
for name, item in approved_inventory.items():
    assert digest(readback_dir / name) == item["sha256"]
```

## State of the Art in This Repository

| Earlier state | Current accepted state | Planning implication |
|---|---|---|
| Historical synthetic `demo`/`report` and 0.1.0 release | Installed real ENOE acceptance, analysis, build, replay and open are accepted through 04-05 | Replace reader-leading commands and release claims only after 04-06/final evidence. [VERIFIED: `brujula/cli.py`; `04-05-SUMMARY.md`; `docs/evidence/release-receipt.json`] |
| Phase 4 PDF was a proposed dependency | WeasyPrint 70 optional extra, DejaVu resources and actual 97-page report | Audit final wheel/native setup and license notices, not the old planned inventory. [VERIFIED: `pyproject.toml`; `04-04-SUMMARY.md`; `04-INTEGRATED-OPERATION.md`] |
| Phase 4 commands/manifest unknown | 04-05 sealed CLI/manifest/current contracts accepted | Derive exact final procedures from live source and accepted receipts. [VERIFIED: `brujula/cli.py`; `04-05-SUMMARY.md`] |

## Assumptions Log

| # | Claim | Section | Risk if wrong |
|---|---|---|---|
| A1 | Resolved: official create/download/asset documentation was read successfully by the orchestrator on 2026-09-24. [CITED: official links above] | Architecture Patterns | Actual tag binding, upload hashes and unauthenticated access remain execution checks. |
| A2 | Final 1.0.0 packaging may use one archive or several individual assets; no exact list has yet been accepted. [ASSUMED] | Architecture Patterns | Planner must derive the allowlist from frozen actual files, not this hypothesis. |

## Open Questions

1. What is the accepted final 04-06 commit, native Windows/Ubuntu CI outcome, integrated disclosure result and phase verification? Current `.planning/STATE.md` says these are pending. Use the resulting receipts; a green local sample cannot replace them. [VERIFIED: `.planning/STATE.md`; `.github/workflows/verify.yml`]
2. Which exact report/export/package files and public-safe evidence summaries will be shipped at the frozen 1.0.0 SHA? Derive from the final manifest and asset privacy/license review. [VERIFIED: `05-CONTEXT.md`; `04-05-SUMMARY.md`]
3. Which final citation format and reader preview will be accepted? Drafts suggest bilingual citation guidance and an aggregate-only preview; choose only after exact report, attribution and license review. [VERIFIED: `05-CONTEXT.md`; `FINAL-DOCUMENTATION-GAPS.md`; `.cache/research/phase5-doc-drafts/INTEGRATION-NOTES.md`]

## Environment Availability

| Dependency | Needed by | Observed state | Final check |
|---|---|---|---|
| Python 3.12 and pinned PDF closure | Wheel/fixture/PDF | Installed isolated real run on Python 3.12; CI matrix declares 3.12. [VERIFIED: `04-INTEGRATED-OPERATION.md`; `.github/workflows/verify.yml`] | Verify final target on both CI hosts. |
| R survey/jsonlite and official workbook/PDF | Independent real numerical checks | Accepted installed numerical acceptance/replay in 04-02; explicit user-supplied paths. [VERIFIED: `04-02-SUMMARY.md`; `brujula/cli.py`] | Record final real audit environment and exact oracle/input identities. |
| Windows native WeasyPrint asset, Ubuntu Pango/Harfbuzz | PDF installed checks | Workflow has reviewed setup steps, but 04-06 CI result pending. [VERIFIED: `.github/workflows/verify.yml`; `.planning/STATE.md`] | Accept native CI receipts before release. |
| Node | Executable negative controls | Workflow invokes `node --test`; result pending for 04-06. [VERIFIED: `.github/workflows/verify.yml`; `.planning/STATE.md`] | Inspect final run. |
| GitHub CLI/auth | Authorized repo release | Procedure documented; this research does not prove live auth. [VERIFIED: `GSD-FINAL-GATE-MAP.md`] | Probe at release execution without exposing credentials. |

## Validation Architecture

| Property | Value |
|---|---|
| Framework | pytest `9.0.3`, Node executable prohibitions, `python -m brujula verify`. [VERIFIED: `pyproject.toml`; `.github/workflows/verify.yml`] |
| Quick checks | Affected docs links, release inventory/hash, privacy/license and installed resource tests; use existing focused tests before adding new ones. [VERIFIED: `scripts/check_docs.py`; `tests/test_installed_runtime.py`; `05-CONTEXT.md`] |
| Full gate | Final `python -m brujula verify`, Node prohibitions, native Windows/Ubuntu CI, independent real-data/visual/replay receipts and public readback. [VERIFIED: `.github/workflows/verify.yml`; `.planning/REQUIREMENTS.md`] |

| Req | Automated and independent evidence | Gap to close |
|---|---|---|
| REL-01 | Bilingual coverage/links/commands check plus editorial review | Integrate candidate docs and correct historical narratives. [VERIFIED: `FINAL-DOCUMENTATION-GAPS.md`; `.cache/research/phase5-doc-drafts/INTEGRATION-NOTES.md`] |
| REL-02 | Clean CI fixture/wheel receipts; real numerical/R/official, conceptual, replay and visual receipts | Accept 04-06 and final independent review. [VERIFIED: `.planning/REQUIREMENTS.md`; `.planning/STATE.md`] |
| REL-03 | Exact allowlist, nested-member/secret/microdata/path scan and source/dependency/font review | Expand current docs scan to `.planning` and freeze asset inventory. [VERIFIED: `scripts/check_docs.py`; `05-CONTEXT.md`] |
| REL-04 | Target/tag identity, draft download hashes, published URL/public download hashes | Create/read back actual 1.0.0 release inside Phase 5. [VERIFIED: `GSD-FINAL-GATE-MAP.md`] |
| GSD-01 | Requirement-to-plan/test/review/artifact matrix; phase verification, code/security review, UAT and milestone audit | Complete only after release evidence and corrections. [VERIFIED: `.planning/config.json`; `GSD-FINAL-GATE-MAP.md`] |

## Security Domain

| ASVS area | Applies | Release control |
|---|---|---|
| V2 authentication / V3 session | No product accounts or sessions | Keep GitHub credentials outside artifacts; use CLI auth only for authorized publication. [VERIFIED: `AGENTS.md`; `05-CONTEXT.md`] |
| V4 access control | Yes, public/private boundary | Publish only independently validated public aggregate projection and allowlisted assets. [VERIFIED: `AGENTS.md`; `04-03-SUMMARY.md`] |
| V5 input validation/encoding | Yes | Verify manifest paths, archive members, CSV formula escaping, static HTML/PDF assets and all format suppression. [VERIFIED: `04-03-SUMMARY.md`; `04-04-SUMMARY.md`; `04-05-SUMMARY.md`] |
| V6 cryptography | Yes, integrity only | Use SHA-256 manifest and downloaded-byte rehash; do not invent signatures. [VERIFIED: `04-INTEGRATED-OPERATION.md`; `05-CONTEXT.md`] |

Main threat patterns are raw/person-record disclosure (information disclosure), suppressed-value reappearance (information disclosure), path/archive traversal (tampering/disclosure), stale-current success (integrity), credential/path leakage (information disclosure) and asset mismatch (tampering). The accepted package already has guarded source/current behavior; Phase 5 must verify the final distribution boundary separately. [VERIFIED: `AGENTS.md`; `04-03-SUMMARY.md`; `04-05-SUMMARY.md`; `scripts/check_docs.py`; `05-CONTEXT.md`]

## Sources

### Primary: current repository evidence

- `AGENTS.md`, `docs/CONTRACT.md`, `.planning/REQUIREMENTS.md`, `.planning/config.json`, `05-CONTEXT.md` — scope and gates.
- `04-01-SUMMARY.md` through `04-05-SUMMARY.md`, `04-INTEGRATED-OPERATION.md`, `.planning/STATE.md` — accepted versus pending execution.
- `brujula/cli.py`, `pyproject.toml`, `requirements-pdf.txt`, `.github/workflows/verify.yml`, `scripts/check_docs.py` — current interfaces, pins and scan scope.
- `.planning/research/FINAL-DOCUMENTATION-GAPS.md`, `.planning/research/GSD-FINAL-GATE-MAP.md`, `.cache/research/phase5-doc-drafts/INTEGRATION-NOTES.md` and candidate maps — reader/release preparation, not acceptance.

### Official references: verify current behavior again before release

- [GitHub CLI create](https://cli.github.com/manual/gh_release_create)/[download](https://cli.github.com/manual/gh_release_download) — release operations, read live by the orchestrator on 2026-09-24.
- [GitHub release asset API](https://docs.github.com/en/rest/releases/assets) — asset metadata and public readback reference, read live by the orchestrator on 2026-09-24.

## Metadata

**Confidence breakdown:** Standard stack HIGH from checked repository manifests and installed evidence; architecture HIGH for local accepted interfaces and MEDIUM for the still-pending release/CI outcome; pitfalls HIGH from observed stale docs, scan scope and actual operation proof. [VERIFIED: cited local files throughout]
**Research date:** 2026-09-24 UTC
**Refresh after:** 04-06 acceptance or any change to final target SHA, resource hashes, CI, license/source terms or release API behavior. [VERIFIED: `.planning/STATE.md`; `05-CONTEXT.md`]
