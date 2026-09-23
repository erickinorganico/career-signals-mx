# Phase 5: Independent Audit and v1.0.0 Release — Research

**Researched:** 2026-09-22  
**Domain:** clean installation, independent acceptance, documentation, release integrity  
**Confidence:** MEDIUM — the release procedure is grounded, but Phase 2 acceptance and Phase 3/4 interfaces are pending. [VERIFIED: `.planning/STATE.md`; `05-CONTEXT.md`]

## User Constraints

The following is copied verbatim from `05-CONTEXT.md`. [VERIFIED: `05-CONTEXT.md`]

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

| ID | Description | Research support |
|---|---|---|
| REL-01 | Bilingual README, scope, PRD, architecture, method, installation, commands, update, contribution and citation accurately describe actual capability and limits. | Documentation gap map and accepted-artifact readback drive a bilingual coverage matrix. |
| REL-02 | Clean Windows/Ubuntu fixture tests without production; real bundle independent numerical, conceptual, visual review and offline replay. | Separate clean install, fixture CI, eight-snapshot replay and PDF/claim review receipts. |
| REL-03 | Public package passes secrets, license, attribution and microdata absence review; only validated artifacts go to named repository. | Closed allowlist, inspected package contents and final source/font/dependency notices. |
| REL-04 | Release 1.0.0 links code, report, figures, aggregates, manifest and acceptance evidence; no completion with material gates pending. | Target-SHA release receipt, uploaded asset inventory and independent download/hash readback. |
| GSD-01 | Requirements, phases, reviewed plans, execution, verification, code review and final audit traceable in GSD. | Requirement-to-evidence matrix and canonical final audit after fixes/rechecks. |

</phase_requirements>

## Project Constraints (from AGENTS.md)

- Read `docs/CONTRACT.md` before changing interfaces; local code, docs, fixtures and isolated tests are authorized. [VERIFIED: `AGENTS.md`]
- No paid APIs, external inference, credentials or third-party messages; only publication to `erickinorganico/career-signals-mx` is authorized after secret/license review. [VERIFIED: `AGENTS.md`]
- Deliver scripts, pipelines, tables, charts, Markdown/HTML research reports and evidence; no frontend, backend, or navigable application. [VERIFIED: `AGENTS.md`]
- Keep field, occupation, industry, geography, period and source distinct; missing remains null; every synthetic output stays labeled. [VERIFIED: `AGENTS.md`]
- Comparability spans source, universe, geography, measure, price basis, method, concept and period; changed dimensions block automatic deltas, and unavailable precision remains visible. [VERIFIED: `AGENTS.md`]
- Raw inputs are content addressed; failed refreshes leave receipts and invalidate current; only validated evidence-bound artifacts may be released. [VERIFIED: `AGENTS.md`]
- Preserve other contributors' edits; delegated assignments do not delegate further; do not use proprietary unrelated-workspace material. [VERIFIED: `AGENTS.md`]

## Summary

Phase 5 is an acceptance and distribution gate for a real eight-quarter ENOE publication. The current checkout still has a `0.1.0` package, fixture-oriented Windows/Ubuntu CI, and a historical synthetic release receipt. These are useful implementation analogs, not release evidence for 1.0.0. Phase 2 is executing, and the final Phase 3/4 packet, CLI, bundle layout, PDF, and manifest are not accepted. Executable Phase 5 plans must begin with a fresh readback of those outputs. [VERIFIED: `pyproject.toml`; `.github/workflows/verify.yml`; `docs/evidence/release-receipt.json`; `.planning/STATE.md`; `05-CONTEXT.md`]

The correct release unit is a reviewed target commit plus a closed set of approved assets. Build a machine-readable release inventory from the accepted Phase 4 manifest; independently inspect the files and installed wheel, hash every upload, then download and rehash the actual GitHub assets. GitHub releases are tag based and expose uploaded asset names, sizes, URLs and SHA-256 digests. [VERIFIED: `docs/CONTRACT.md`; `04-CONTEXT.md`; CITED: https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases; https://docs.github.com/en/rest/releases/assets]

**Primary recommendation:** Make one signed-off acceptance matrix and one exact-asset allowlist prerequisites to tagging and publishing `v1.0.0`; record the target SHA, final checks, asset hashes, URLs and remaining limitations in the release receipt. [VERIFIED: `05-CONTEXT.md`; `docs/evidence/release-receipt.json`]

## Architectural Responsibility Map

| Capability | Primary tier | Secondary tier | Rationale |
|---|---|---|---|
| Clean install and wheel resources | Local package/build | Windows and Ubuntu CI | Wheel is the installable unit; hosts prove platform behavior. [VERIFIED: `pyproject.toml`; `.github/workflows/verify.yml`] |
| Real replay | Local batch CLI | Local verified snapshot cache | Phase 4 will own the accepted numerical replay contract. [VERIFIED: `04-CONTEXT.md`] |
| Independent acceptance | Review/evidence | Local artifacts | Review must compare outputs to accepted source, methods, claims and visual receipts. [VERIFIED: `05-CONTEXT.md`] |
| Asset filtering and hash sealing | Release preparation | GitHub release | The release publishes only approved bytes and records remote readback. [VERIFIED: `05-CONTEXT.md`; CITED: https://docs.github.com/en/rest/releases/assets] |
| Bilingual docs | Repository documentation | Release notes | Docs describe the actual accepted commands and limits. [VERIFIED: `.planning/research/FINAL-DOCUMENTATION-GAPS.md`] |

## Standard Stack

| Component | Current version/status | Purpose | Evidence |
|---|---|---|---|
| Python | `>=3.12`, local shim currently unset | Runtime and isolated virtual environments | [VERIFIED: `pyproject.toml`; local `python --version` probe] |
| setuptools | `80.10.2` build requirement | Existing wheel/package data | [VERIFIED: `pyproject.toml`] |
| DuckDB, jsonschema, Matplotlib, NumPy | Exact existing pins in `pyproject.toml` and `requirements.txt` | Existing runtime closure; recheck final Phase 4 pins | [VERIFIED: `pyproject.toml`; `requirements.txt`] |
| pytest | `9.0.3` existing test extra | Fixture and release-gate tests | [VERIFIED: `pyproject.toml`; `requirements.txt`] |
| WeasyPrint | Phase 4 planned `70.0`, not declared now | PDF renderer if accepted upstream | [VERIFIED: `docs/research/DEPENDENCY-LICENSE-INVENTORY.md`; `pyproject.toml`] |
| GitHub CLI | Local `2.87.3` | Release metadata/upload/readback | [VERIFIED: local `gh --version`; CITED: https://cli.github.com/manual/gh_release] |
| GitHub Actions | Existing Windows/Ubuntu matrix | Clean fixture portability; extend only against accepted commands | [VERIFIED: `.github/workflows/verify.yml`] |

No new package is recommended or installed by this research. Phase 4 owns any PDF dependency decision and its legitimacy/license gate. Version pins and package resources must be re-read from its accepted final state. [VERIFIED: `05-CONTEXT.md`; `pyproject.toml`]

## Architecture Patterns

```text
approved eight ENOE snapshots + accepted Phase 2/3 evidence
        → Phase 4 offline replay → validated public projection
        → sealed reports / figures / aggregates / manifest
        → independent numerical + conceptual + visual + security review
        → closed release allowlist → target commit/tag → GitHub assets
        → remote download/hash readback → final GSD audit and receipt
                                      ↘ material failure: BLOCKED, no completion
```

The diagram describes the target gate, not current implementation. [VERIFIED: `05-CONTEXT.md`; `04-CONTEXT.md`]

### Clean install versus offline replay

Run two separately named experiments on clean Windows and Ubuntu: first an online dependency/package install plus synthetic fixture test with no production access; then a real offline replay using the already acquired and hash-verified eight snapshots, with network disabled at execution. Test wheel resource lookup outside a source checkout, including v2 schemas/catalog assets and any accepted fonts. Compare canonical numerical/public-record hashes and validated output joins across platforms while separately recording run IDs, timestamps and PDF byte differences. Exact commands and artifact paths come from accepted Phase 4 CLI, never from current synthetic `demo`/`report`. [VERIFIED: `.github/workflows/verify.yml`; `brujula/resources.py`; `docs/RELEASE.md`; `04-CONTEXT.md`; `04-PATTERNS.md`]

### Closed release inventory

Start from the accepted Phase 4 manifest and record each proposed asset's role, relative path, size, SHA-256, source/method/claim references, license/attribution decision, and target release name. Reject any file outside this list; inspect nested ZIP/wheel archives as well as loose files. Assert the public projection alone supplied numerical report/export content and that suppressed diagnostic values are absent across CSV, Parquet, DuckDB, SVG/PNG, HTML, Markdown, PDF text and alternative text. The final inventory is a Phase 5 output; no exact file list exists yet. [VERIFIED: `05-CONTEXT.md`; `04-CONTEXT.md`; `04-PATTERNS.md`]

### Release order

Freeze and review the target commit and assets; complete affected checks and reviews; create or update a draft release against the exact tag/commit; upload the closed asset list; fetch release metadata and download each uploaded asset to an isolated readback directory; compare names, sizes, SHA-256 and GitHub's digest fields with local inventory; then publish and record final URLs and commit identity. A remote mismatch remains a blocked gate. GitHub CLI supports release creation, upload, view, download and asset verification; GitHub's asset API exposes `digest`, `size`, `state` and `browser_download_url`. [VERIFIED: `05-CONTEXT.md`; CITED: https://cli.github.com/manual/gh_release; https://docs.github.com/en/rest/releases/assets]

## Don't Hand-Roll

| Problem | Use | Reason |
|---|---|---|
| Cryptographic hashing | `hashlib.sha256` and independent remote downloads | Existing project hashes are SHA-256; the hash implementation is standard library. [VERIFIED: `brujula/pipeline.py`; `docs/CONTRACT.md`] |
| Package resources | Existing setuptools package-data plus installed-wheel test | Source-tree presence alone misses wheel omissions. [VERIFIED: `pyproject.toml`; `brujula/resources.py`; `docs/evidence/release-receipt.json`] |
| Release API | `gh release` and GitHub release metadata | Avoid a custom uploader/auth workflow. [CITED: https://cli.github.com/manual/gh_release; https://docs.github.com/en/rest/releases/assets] |
| PDF rendering | Accepted Phase 4 WeasyPrint integration | Phase 5 verifies it rather than writing a PDF renderer. [VERIFIED: `04-CONTEXT.md`; `04-RESEARCH.md`] |

## Common Pitfalls

| Pitfall | Warning sign | Gate |
|---|---|---|
| Synthetic success relabeled as real | 0.1.0 receipt, `demo` command, fixture counts cited for 1.0.0 | Require accepted eight-quarter replay and Phase 2/3/4 receipts. [VERIFIED: `.planning/research/FINAL-DOCUMENTATION-GAPS.md`] |
| Source checkout hides missing wheel data | Tests pass only beside repository files | Install wheel outside checkout on both platforms; resolve every packaged schema/catalog/font. [VERIFIED: `brujula/resources.py`; `docs/evidence/release-receipt.json`] |
| Build success treated as offline replay | Online install or acquisition network remains available during numerical run | Separate acquisition/install receipts from network-disabled replay. [VERIFIED: `05-CONTEXT.md`] |
| Public ZIP leaks local inputs | Archive creation uses broad directory glob | Build from explicit allowlist; inspect nested members and binary/text content. [VERIFIED: `AGENTS.md`; `05-CONTEXT.md`] |
| Suppressed value reappears in another format | One format uses diagnostic packet or computed complement | Cross-format sentinel and complement-reconstruction negative controls. [VERIFIED: `04-CONTEXT.md`; `04-EDITORIAL-SPEC.md`] |
| PDF smoke substituted for acceptance | PDF exists but accents, tables or pages are clipped | Inspect final real PDF pages and text on both target platforms. [VERIFIED: `04-EDITORIAL-SPEC.md`; `docs/research/DEPENDENCY-LICENSE-INVENTORY.md`] |
| Mutable historical docs conflict | Scope/method docs call ENOE future work | Replace or prominently quarantine M0–M6 synthetic narrative in both languages. [VERIFIED: `.planning/research/FINAL-DOCUMENTATION-GAPS.md`] |
| Upload bytes differ from local review | Only local hash or release URL recorded | Remote download/hash readback and exact tag SHA in receipt. [VERIFIED: `05-CONTEXT.md`; CITED: https://docs.github.com/en/rest/releases/assets] |

## Code Examples

Illustrative verification pattern; adapt paths and asset names only after Phase 4 acceptance. [VERIFIED: `04-CONTEXT.md`; `05-CONTEXT.md`]

```python
from hashlib import sha256
from pathlib import Path

def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()

assert set(downloaded_asset_names) == set(approved_inventory)
for name, expected in approved_inventory.items():
    assert digest(readback_dir / name) == expected["sha256"]
```

For a release, use the documented `gh release` operations with explicit repository, tag, target commit and the reviewed list of files; the current historical receipt's command and asset names are not the v1.0.0 contract. [VERIFIED: `docs/evidence/release-receipt.json`; CITED: https://cli.github.com/manual/gh_release_create; https://cli.github.com/manual/gh_release_download]

## Assumptions Log

| # | Claim | Risk if wrong |
|---|---|---|
| A1 | [ASSUMED] The accepted Phase 4 bundle will expose a canonical numeric/public-content digest suitable for cross-platform replay comparison. | Planner must add or specify this gate after final interface readback. |
| A2 | [ASSUMED] The final release will ship an installable wheel plus one public research archive. | Actual packaging and asset names depend on accepted Phase 4 implementation. |

These are planning hypotheses, not locked decisions. [ASSUMED]

## Open Questions and Readback Gate

1. Which exact Phase 2 estimator/oracle, official reconciliation, singleton policy and eight-quarter acceptance receipts passed? Current Phase 2 is executing. [VERIFIED: `.planning/STATE.md`]
2. Which Phase 3 claim registry, comparison IDs, coverage and evidence links were accepted? No Phase 3 acceptance is present in the checked state. [VERIFIED: `.planning/STATE.md`; `.planning/ROADMAP.md`]
3. What are the final Phase 4 CLI commands, public projection, stable keys, manifest schema, artifact inventory, PDF resource resolution, replay digest and current invalidation receipt? `04-PATTERNS.md` names candidates, not accepted APIs. [VERIFIED: `04-PATTERNS.md`; `04-CONTEXT.md`]
4. What exact fonts, native PDF components and source terms apply at the release target SHA? The current inventory is preparatory. [VERIFIED: `docs/research/DEPENDENCY-LICENSE-INVENTORY.md`]

**Required before executable plans:** Read back accepted Phase 2/3/4 outputs, the final package metadata, CI, source terms, report, manifest and artifact tree. Do not turn this preparatory file into a claim that REL-01–04 or GSD-01 passed. [VERIFIED: `05-CONTEXT.md`]

## Environment Availability

| Dependency | Needed for | Current probe | Planning implication |
|---|---|---|---|
| Python 3.12+ | Package and replay | Global `python` shim says no version configured; project-local `.venv` was inventoried as 3.12.13 earlier | Use explicit isolated interpreter in clean-install receipts; re-probe at execution. [VERIFIED: local probe; `docs/research/DEPENDENCY-LICENSE-INVENTORY.md`] |
| Node | Existing prohibition controls | `v24.13.1` present locally | Keep existing controls in CI. [VERIFIED: local probe; `.github/workflows/verify.yml`] |
| GitHub CLI | Release/readback | `2.87.3` present locally | Recheck authentication only at authorized publication. [VERIFIED: local probe] |
| Windows/Ubuntu CI | Portability | Matrix exists but currently runs fixture `demo` | Extend after accepted real interface; CI fixture result alone is insufficient. [VERIFIED: `.github/workflows/verify.yml`] |
| R `survey` oracle | Phase 2 independent numeric comparison | Earlier project context records local R 4.6.1/survey 4.5; current availability not reprobed | Consume accepted Phase 2 receipt, do not make R a product runtime. [VERIFIED: `.planning/PROJECT.md`] |

## Validation Architecture

| Property | Current value |
|---|---|
| Framework | Existing pytest `9.0.3`, Node executable negative controls, `python -m brujula verify` in checkout. [VERIFIED: `pyproject.toml`; `.github/workflows/verify.yml`] |
| Quick command | Select affected existing tests after accepted Phase 4 changes; do not preassign unimplemented v2 test names. [VERIFIED: `05-CONTEXT.md`] |
| Full suite | Final accepted `python -m brujula verify` plus `node --test tests/phase*_prohibitions_*.test.cjs` and clean CI matrix. [VERIFIED: `.github/workflows/verify.yml`] |

| Requirement | Test/evidence architecture |
|---|---|
| REL-01 | Bilingual document matrix, path/command link check, reader reproduction of accepted commands; review all stale synthetic narratives. |
| REL-02 | Clean Windows/Ubuntu wheel install outside checkout; fixture CI; separate network-disabled eight-snapshot replay; R/official comparison readback; visual/PDF and conceptual reviews. |
| REL-03 | Exact asset allowlist; recursive archive/wheel inspection; secret/private-path and microdata sentinel scan; source/dependency/font notices and transformation attribution review. |
| REL-04 | Target-SHA/tag check; asset name/size/hash equality; remote download rehash; exact URLs and release receipt. |
| GSD-01 | Every requirement maps to plan, implementation, test, phase verification, security/code review and accepted artifact; unresolved gates remain open. |

All five rows are required phase gates, not proof that they have passed. [VERIFIED: `.planning/REQUIREMENTS.md`; `05-CONTEXT.md`]

## Security Domain

| ASVS area | Applies | Release control |
|---|---|---|
| V2 authentication / V3 session | No product account/session | Offline CLI and static report; GitHub authentication stays in `gh`, never in artifacts. [VERIFIED: `AGENTS.md`; `05-CONTEXT.md`] |
| V4 access control | Yes, data-release boundary | Only validated public projection and explicitly approved release assets. [VERIFIED: `04-CONTEXT.md`; `05-CONTEXT.md`] |
| V5 validation/encoding | Yes | Inspect manifest paths, archive members, CSV formula handling, static HTML/PDF resources and public schemas. [VERIFIED: `docs/CONTRACT.md`; `04-PATTERNS.md`] |
| V6 cryptography | Yes, integrity | SHA-256 on local and remotely retrieved assets and pinned source snapshots. [VERIFIED: `docs/CONTRACT.md`; `brujula/acquisition.py`] |

Threats: accidental microdata/secret disclosure from broad archive selection; tampered or stale current/manifest; unapproved remote PDF resource; release tag or uploaded asset mismatch. Block publication on any material finding. [VERIFIED: `AGENTS.md`; `04-CONTEXT.md`; `05-CONTEXT.md`]

## Sources

**Primary local:** `AGENTS.md`, `docs/CONTRACT.md`, `.planning/{PROJECT,REQUIREMENTS,ROADMAP,STATE,config.json}`, Phase 5 context, Phase 4 context/research/editorial spec/patterns, `.planning/research/FINAL-DOCUMENTATION-GAPS.md`, `docs/research/DEPENDENCY-LICENSE-INVENTORY.md`, `pyproject.toml`, `requirements.txt`, `.github/workflows/verify.yml`, `brujula/{resources,cli,pipeline,acquisition}.py`, `docs/RELEASE.md`, `docs/evidence/release-receipt.json`. [VERIFIED: local files]

**Primary official:** [GitHub releases](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases), [release asset API](https://docs.github.com/en/rest/releases/assets), [GitHub CLI release manual](https://cli.github.com/manual/gh_release), [GitHub CLI create](https://cli.github.com/manual/gh_release_create), [download](https://cli.github.com/manual/gh_release_download), [Python packaging MANIFEST guide](https://packaging.python.org/en/latest/guides/using-manifest-in/). [CITED: linked official documentation]

## Metadata

**Confidence breakdown:** release mechanics HIGH from official docs and historical project receipt; current package/CI state HIGH from direct reads; exact real-data commands/assets LOW until Phase 4 acceptance; final source/font licensing MEDIUM pending target-SHA review.  
**Valid until:** 2026-10-06 or any earlier Phase 2/3/4 interface, source-term or package change. [ASSUMED]
