---
phase: 5
slug: independent-audit-and-v1-0-0-release
status: open_threats
threats_open: 1
asvs_level: 1
reviewed: 2026-09-28
---

# Phase 5 security verification

## OPEN_THREATS

**Phase:** 5 — Independent Audit and v1.0.0 Release  
**Closed:** 2/3 | **Open:** 1/3
**ASVS Level:** 1

The three Phase 5 plans each declare one compound `<threat_model>` without an explicit disposition. This register assigns an audit ID to each and classifies all three as `mitigate`, consistent with their required controls. Documentation and a previous candidate are not evidence that a final release target has passed.

| Threat ID | Plan | Category | Disposition | Required mitigation | State and evidence boundary |
|---|---|---|---|---|---|
| T-05-01 | 05-01 | Misleading documentation or stale wheel proof | mitigate | Compare bilingual claims and installed commands to accepted receipts; bind both clean-host results to the exact final wheel. | **MITIGATED / CLOSED technically.** `docs/evidence/phase-05-portability.json` binds actual hosted run 36464796584 at `611d2f553597439a0c58807dd6865914ff46281c`. The live host verifier downloaded both CI wheels/receipts and passed against the audited inventory; both hosts passed outside-checkout installation and Spanish PDF/resource guards. Human visual acceptance remains separate. |
| T-05-02 | 05-02 | Unsafe release members, disclosure, secrets, private paths or missing notices | mitigate | Hash and inspect every loose and nested final member; verify public projection, source terms and actual redistributed notices; close the allowlist. | **MITIGATED / CLOSED TECHNICALLY.** `docs/evidence/phase-05-asset-review.json` binds all five frozen loose assets and their 147 nested members to SHA-256 decisions for target `611d2f553597439a0c58807dd6865914ff46281c`. The 73 sealed research files match the Phase 4 manifest; archive, fonts, notices and supplemental review passed bounded privacy/license review. The exact tested Windows CI wheel is SHA-256 `fe5c6174fccb1effa0d6b34430f66566fe4567c7dd5685a9ce5f7e7c8169b27c`; eight member differences from the prior local wheel are line endings only, and its 63-row RECORD verifies. Any changed byte reopens this threat. Hosted portability, human visual acceptance and public byte readback remain separate gates. |
| T-05-03 | 05-03 | Wrong tag, unreviewed asset, digest mismatch or false public claim | mitigate | Compare frozen target and allowlist to draft uploads and downloads, then verify tag and all public assets through anonymous byte readback. | **OPEN / BLOCKER.** `docs/evidence/phase-05-release-acceptance.json` records draft 398517656 and actual five-asset download PASS at the frozen target. Human visual acceptance and anonymous public/tag readback remain pending; no public v1.0.0 is claimed. |

## Bounded Phase 4 content readback relevant to T-05-02

I independently read the sealed run at `.cache/research/phase4-integrated-publication/runs/20260924T010247-81cfb71ea5f1`. Its manifest lists exactly 73 content paths; all 73 local SHA-256 values match and there are no extra content files. The manifest identifies eight ENOE source snapshots. `analysis.json` is 66,941,824 bytes, SHA-256 `4b35ce4d67f9b0372aa6e418e88ed8aa90f630b36814a1295cbf79481e25b638`; its 6,739 public record entries contain 3,565 null values. For every null record, `weighted_denominator`, `support.weighted_support_total`, `precision.standard_error`, `coefficient_variation` and both CI90 bounds are null. Record objects contain no `estimate` key or named person-level columns checked (`folioviv`, `foliohog`, `numren`, `n_ren`, `fac_tri`, `ingocup`). Its 4,209 comparisons have no numeric change when `comparable` is false, and all 38 claims identify `synthetic=false`.

The sealed DuckDB export has 22 tables, 6,739 `public_records`, 4,209 comparisons and 38 claims. None of the 22 table schemas contains the named internal estimate or person columns. Its 3,565 suppressed `public_records` have null denominator, weighted support, SE, CV and CI bounds. A targeted exact-path/credential-marker scan of the 73 content files found no Windows user path, private-key block or plausible credential assignment. A scan of 380 Git-tracked files found no such credential or real workstation path; a broad path heuristic matched only a Matplotlib documentation URL in `.planning/research/STACK.md`. These checks are bounded to the inspected patterns and bytes, and do not approve an unbuilt final archive.

The official [INEGI terms](https://www.inegi.org.mx/inegi/terminos.html) read on 2026-09-24 permit copying, publication, adaptation and extraction with retained metadata, source/product attribution, transformation disclosure and no implied endorsement. `docs/SOURCES.md` identifies all eight ENOE snapshots, their URLs and hashes, and distinguishes aggregate publication from local raw ZIP/person rows. The sealed Spanish `report.md` credits INEGI and ENOE, describes Brújula Laboral MX's estimation/transformation and disclaims INEGI endorsement. The font notice file `assets/fonts/LICENSE_DEJAVU` is a hashed manifest member. The existing dependency inventory describes the recovery environment; it does not certify what the final wheel or archive redistributes.

## Unregistered flags

No `## Threat Flags` section in the currently available Phase 5 summaries has identified a separate attack surface. Recheck summaries and final inventory before closure; this absence is not a substitute for inspection.

## Closure conditions

Close T-05-01 only after the exact 1.0.0 wheel and both hosted installed receipts are read back. T-05-02 is technically closed for the exact hashes in `docs/evidence/phase-05-asset-review.json` with zero material findings. Reopen it if any released member differs. Human visual acceptance is a separate release gate. Close T-05-03 only after draft byte comparison and anonymous public readback of the authorized tag and every released asset. Update `threats_open` from actual evidence; until then, Phase 5 must not be marked secure.
