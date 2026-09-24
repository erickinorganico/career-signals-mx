---
phase: 4
slug: offline-publication-and-reproducible-operation
status: in_progress
threats_open: 4
asvs_level: 1
register_authored_at_plan_time: true
created: 2026-09-23
---

# Phase 4 — Security verification

This register verifies the authored threats from Plans 04-01 through 04-06 against code and actual artifacts. Phase 4 remains in progress: thirteen mitigations have bounded evidence, and four are open. ASVS level 1 is scoped to the local offline publication and reproducible-operation pipeline. Authentication, sessions and a server boundary do not apply.

## Trust boundaries

Approved installed resources and local native assets feed the PDF runtime. Installed numerical code reads only pinned ZIPs and receipts through explicit paths. The validated Phase 3 public packet crosses into typed models and static exports; renderer assets are staged and local-only. The sealed manifest and current pointer resolve only live, hash-matching acquisitions. Local fixtures, aggregate output and acceptance receipts feed reviewable evidence. No person rows, diagnostic payloads, credentials, network resources or unchecked paths cross these boundaries.

## Authored register

Severity is an initial planning classification. High covers integrity or disclosure failures that could publish or expose unsafe results; medium covers bounded availability, injection, or dependency-install risks. The Phase 04 dependency legitimacy receipt is planning input about registry identity and package-name heuristics only; it is not proof of source-code safety, vulnerability status, or any code mitigation.

| Plan / threat | Component | Severity | Disposition | Required mitigation | Evidence / status |
|---|---|---|---|---|---|
| 01 / T-04-01 | package resource lookup | high | mitigate | Hash exact shipped catalogs, schema, oracle and font assets. | CLOSED — `brujula/resources.py:85-157` hashes 24 authored package resources; final-wheel resource inventory and audited font hashes are recorded in `phase4-candidate-content-audit.json`. |
| 01 / T-04-02 | wheel contents | high | mitigate | Inspect wheel inventory to exclude ZIP, person rows, credentials and caches. | CLOSED — corrected `phase4-candidate-content-audit.json` inspected the final 63-member wheel (SHA-256 `709b62ff…63e8e`) and 24 resources; no ZIP, cache, credential or raw person-row member was identified. |
| 01 / T-04-SC | PyPI/Pango install | medium | mitigate | Use reviewed WeasyPrint 70.0 registry identity, fixed version and local clean install; no assumed package. | CLOSED — `pyproject.toml:16` pins WeasyPrint 70.0; `brujula/resources.py:122-143` checks imported version and renders a native PDF; outside-checkout install and registry identity appear in `04-RESOURCE-REVIEW.md` and preflight. |
| 02 / T-04-03 | installed numerical code | high | mitigate | Hash actual executing package modules/oracle, then rerun full frozen acceptance and replay. | CLOSED — `brujula/enoe_acceptance.py:42-49,138-143,681-690` checks 11 executing code/oracle hashes and seven numeric resources; immutable full acceptance/replay receipts are verified in `04-INSTALLED-REVIEW.md:52-57`. |
| 02 / T-04-04 | prior trusted references | high | mitigate | Rebind only after unchanged digest and row-level proof; preserve old receipts. | CLOSED — `pre-rebind-proof.json` records 6,739 guarded rows and exact `trusted_reference` rejection; `reference-rebind.json` records the hash-only change and preserved old reference; `brujula/findings_v2.py:210-229` enforces the pin. |
| 02 / T-04-05 | missing R/benchmark/source | medium | mitigate | Fail attempt with receipt and no synthetic fallback. | CLOSED — `brujula/enoe_acceptance.py:198-229,536-558` invalidates current and writes an immutable failed attempt when required numerical inputs fail; focused negatives and installed receipt readback are in `04-INSTALLED-REVIEW.md`. |
| 03 / T-04-06 | model/export | high | mitigate | Reject internal payload and scan suppressed point plus nested diagnostics in actual exports. | OPEN — `brujula/publication_v2.py:80-135` and `brujula/export_v2.py:180-185` reject altered/internal models, but deliberate nested-sentinel proof across actual CSV, Parquet and DuckDB exports remains assigned to 04-06. |
| 03 / T-04-07 | record joins | high | mitigate | Validate v2r ten-key identity and exact v2c/v2k references. | CLOSED — `brujula/analysis_v2.py:65-69,282` derives ten-grain v2r IDs; `brujula/findings_v2.py:210-258` and `brujula/publication_v2.py:115-135` revalidate record, comparison, claim and figure references. |
| 03 / T-04-08 | CSV | medium | mitigate | Neutralize spreadsheet formula prefixes and document reversible representation. | CLOSED — `brujula/export_v2.py:129-137,167` prefixes formula/apostrophe text and documents reversal; `tests/test_export_v2.py:137-147` covers prefixes, null and zero. |
| 04 / T-04-09 | renderer metadata/alt | high | mitigate | Render only validated model; scan actual SVG/PNG/HTML/MD/PDF for nested sentinels. | OPEN — `brujula/report_v2.py:123-151` validates the model and actual formats passed parity/readback, but the deliberate nested-sentinel SVG/PNG/HTML/MD/PDF scan remains assigned to 04-06. |
| 04 / T-04-10 | PDF URL fetcher | high | mitigate | Allowlist real staged assets and reject all external/data/traversal/symlink URLs; fatal missing asset. | CLOSED — `brujula/pdf_v2.py:24-91,111-159` enforces exact SHA allowlist, local containment and verified returned bytes; `tests/test_pdf_v2.py:16-116` exercises unsafe URLs, missing/altered assets and read races. |
| 04 / T-04-11 | figure/report parity | high | mitigate | Assert canonical figure-point/table/alt/claim keys and quantities match. | CLOSED — `brujula/report_v2.py:145-150,334-352,590-605,650-676,758-788` derives formats from one validated model; `04-REPORT-REVIEW.md:43-63` verifies nine figure sets, print unions, 96 accepted changes and 625 keys in HTML/MD/PDF. |
| 05 / T-04-12 | current pointer | high | mitigate | Verify manifest/receipt digest and eight live acquisition IDs on every read. | CLOSED — `brujula/pipeline_v2.py:422-510` checks pointer, manifest, receipt, packet, eight live acquisition receipts and artifact hashes twice per resolution; installed opens and copied-source failure are in `04-WAVE3-CHECKS.md`. |
| 05 / T-04-13 | manifest paths/files | high | mitigate | Exact inventory, safe relative paths and all artifact SHA hashes. | CLOSED — `brujula/pipeline_v2.py:74-85,208-226,422-483` derives an exact model-specific inventory, rejects unsafe paths/reparse points and compares all hashes; corrected candidate audit found 73 matching content artifacts with no extras/misses. |
| 05 / T-04-14 | crash/concurrency | medium | mitigate | BuildLock, journal recovery, immutable failure receipts and fault matrix. | CLOSED — `brujula/pipeline_v2.py:278-365,429-430` recovers prior RUNNING journal/current under `BuildLock`, records each run before work, preserves immutable failure bytes on interrupted recovery and rejects a failed promotion marker on reads. `tests/test_pipeline_v2.py:117-276` covers five interruption stages, process exit, idempotence, invalid IDs, junction and malformed receipts; `04-INTEGRATED-OPERATION.md` records actual installed `os._exit(17)` followed by recovered BLOCKED receipt, fresh sealed build/open and 87 unchanged anchors. |
| 06 / T-04-15 | acceptance evidence | high | mitigate | Record exact command, hashes, exit, edge/prohibition and visual outcomes. | OPEN — installed 04-05 commands/hashes and report visual review exist, but 04-06 edge, prohibition and CI acceptance evidence is incomplete. |
| 06 / T-04-16 | bundle/evidence | high | mitigate | Scan actual wheel/bundle for microdata, secrets and nested sentinels before evidence seal. | OPEN — corrected candidate content audit inspected wheel/bundle allowlists, schemas and markers; deliberate nested canary and 04-06 evidence seal remain pending. |

## Acceptance gate

This register remains in progress while four authored mitigations are open: T-04-06, T-04-09, T-04-15 and T-04-16 await the specified 04-06 execution evidence. Dependency identity review does not certify package vulnerability status.

## Audit trail

Initial plan-time register: 17 authored entries, all pending execution evidence. The register records planned controls only; it makes no claim that source changes, installed behavior, rendered artifacts, or release evidence are secure. Phase 5 publication remains a separate gate.

2026-09-24 bounded security progress at source freeze `26c9864`: twelve mitigations have implementation and affected execution evidence; five remain OPEN. The installed 04-05 chain produced a real analysis packet and 73-artifact sealed run, then passed reconstruction on the final wheel; see `04-WAVE3-CHECKS.md` and `04-OPERATION-REVIEW.md`. Directly reviewed SHA-256: `pipeline_v2.py` `63b341060c76a6a4b5b9441b5186b513c54aae43eb3f810e9d8143e3b58e3613`, `runlock.py` `382a44c2d368d9750d018c2b20533a93b50e2c643805e2c8d0e2fdeb0a3162e6`, manifest schema `ab543f5f3361f7065a0dceadc7a66eebc9c547382b423b152907a6c946924bc2`. No implementation file was changed by this audit.

2026-09-24 recovery closure at source freeze `c222f69`: independent rereview found no remaining T-04-14 gap in `pipeline_v2.py` SHA-256 `e4581b3c688c522c1433829f44c3b6c6f13e26956fd188aa3fcbc07f47ce5483`. Installed wheel SHA-256 `77e6a0e36aa897a3e7f054b49b6259837be3ccb83b5200adec9e63e0fb61e983` was interrupted through a Python audit hook with actual process exit 17 before journal promotion. The next unmodified installed build recovered immutable BLOCKED receipt SHA-256 `db3d5a5ff07dddf9a3da38dea8e6dfbbae72f44833dfea134ee661147058c605`, built a fresh 73-artifact run with manifest SHA-256 `38c3dfc21d816f32d7e4a21d7efd89418fc198fd80e94577783706f00d7fb023`, and passed an installed PDF open. `04-INTEGRATED-OPERATION.md` and `recovery-proof.json` record zero network attempts and 87 unchanged original anchors. T-04-14 is now CLOSED; four Phase 4 threats remain OPEN.

## Resource implementation readback

At Plan 04-01 time, resource proof at a7ef126 and the bounded `04-RESOURCE-REVIEW.md` established wheel/resource/font/oracle hashes, 12 focused controls, outside-checkout installation and native PDF capability. The later final-wheel inspection and report readback now support closure of T-04-01/T-04-02/T-04-SC at the reviewed inputs above.

## Public-model and export readback

Plan 04-03 is independently clean at a89b782 after resolving all three initial findings. The corrected full suite had 476 passed and zero skipped; the clean-source boundary suite had 18 passed with only two optional real integrations skipped. Complete comparison signatures/evidence survive all formats, and figure links exclude blocked comparisons. `04-EXPORT-REVIEW.md` and `04-WAVE1-CHECKS.md` support T-04-07/T-04-08 closure. T-04-06 remains open for deliberate actual-export sentinel evidence.
