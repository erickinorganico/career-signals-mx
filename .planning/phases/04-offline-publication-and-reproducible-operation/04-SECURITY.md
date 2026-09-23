---
phase: 4
slug: offline-publication-and-reproducible-operation
status: in_progress
threats_open: 17
asvs_level: 1
register_authored_at_plan_time: true
created: 2026-09-23
---

# Phase 4 — Security verification

This register carries the authored threat models from Plans 04-01 through 04-06 into execution. These are planned threats, not discovered bugs; no mitigation is verified by this register. ASVS level 1 is scoped to the local offline publication and reproducible-operation pipeline. Authentication, sessions and a server boundary do not apply.

## Trust boundaries

Approved installed resources and local native assets feed the PDF runtime. Installed numerical code reads only pinned ZIPs and receipts through explicit paths. The validated Phase 3 public packet crosses into typed models and static exports; renderer assets are staged and local-only. The sealed manifest and current pointer resolve only live, hash-matching acquisitions. Local fixtures, aggregate output and acceptance receipts feed reviewable evidence. No person rows, diagnostic payloads, credentials, network resources or unchecked paths cross these boundaries.

## Authored register

Severity is an initial planning classification. High covers integrity or disclosure failures that could publish or expose unsafe results; medium covers bounded availability, injection, or dependency-install risks. The Phase 04 dependency legitimacy receipt is planning input about registry identity and package-name heuristics only; it is not proof of source-code safety, vulnerability status, or any code mitigation.

| Plan / threat | Component | Severity | Disposition | Required mitigation | Evidence / status |
|---|---|---|---|---|---|
| 01 / T-04-01 | package resource lookup | high | mitigate | Hash exact shipped catalogs, schema, oracle and font assets. | PENDING — authored plan only; affected checks and independent code/security audit required. |
| 01 / T-04-02 | wheel contents | high | mitigate | Inspect wheel inventory to exclude ZIP, person rows, credentials and caches. | PENDING — authored plan only; affected checks and independent code/security audit required. |
| 01 / T-04-SC | PyPI/Pango install | medium | mitigate | Use reviewed WeasyPrint 70.0 registry identity, fixed version and local clean install; no assumed package. | PENDING — dependency legitimacy receipt is planning input only; clean-install/runtime checks and independent security audit required. |
| 02 / T-04-03 | installed numerical code | high | mitigate | Hash actual executing package modules/oracle, then rerun full frozen acceptance and replay. | PENDING — authored plan only; installed readback and independent code/security audit required. |
| 02 / T-04-04 | prior trusted references | high | mitigate | Rebind only after unchanged digest and row-level proof; preserve old receipts. | PENDING — authored plan only; rebind checks and independent code/security audit required. |
| 02 / T-04-05 | missing R/benchmark/source | medium | mitigate | Fail attempt with receipt and no synthetic fallback. | PENDING — authored plan only; failure-path checks and independent code/security audit required. |
| 03 / T-04-06 | model/export | high | mitigate | Reject internal payload and scan suppressed point plus nested diagnostics in actual exports. | PENDING — authored plan only; export disclosure checks and independent security audit required. |
| 03 / T-04-07 | record joins | high | mitigate | Validate v2r ten-key identity and exact v2c/v2k references. | PENDING — authored plan only; join-integrity checks and independent code/security audit required. |
| 03 / T-04-08 | CSV | medium | mitigate | Neutralize spreadsheet formula prefixes and document reversible representation. | PENDING — authored plan only; CSV injection checks and independent security audit required. |
| 04 / T-04-09 | renderer metadata/alt | high | mitigate | Render only validated model; scan actual SVG/PNG/HTML/MD/PDF for nested sentinels. | PENDING — authored plan only; rendered-output checks and independent security audit required. |
| 04 / T-04-10 | PDF URL fetcher | high | mitigate | Allowlist real staged assets and reject all external/data/traversal/symlink URLs; fatal missing asset. | PENDING — authored plan only; fetcher boundary checks and independent security audit required. |
| 04 / T-04-11 | figure/report parity | high | mitigate | Assert canonical figure-point/table/alt/claim keys and quantities match. | PENDING — authored plan only; parity checks and independent code/security audit required. |
| 05 / T-04-12 | current pointer | high | mitigate | Verify manifest/receipt digest and eight live acquisition IDs on every read. | PENDING — authored plan only; resolver checks and independent code/security audit required. |
| 05 / T-04-13 | manifest paths/files | high | mitigate | Exact inventory, safe relative paths and all artifact SHA hashes. | PENDING — authored plan only; manifest/path checks and independent security audit required. |
| 05 / T-04-14 | crash/concurrency | medium | mitigate | BuildLock, journal recovery, immutable failure receipts and fault matrix. | PENDING — authored plan only; fault-matrix checks and independent code/security audit required. |
| 06 / T-04-15 | acceptance evidence | high | mitigate | Record exact command, hashes, exit, edge/prohibition and visual outcomes. | PENDING — authored plan only; acceptance evidence review and independent code/security audit required. |
| 06 / T-04-16 | bundle/evidence | high | mitigate | Scan actual wheel/bundle for microdata, secrets and nested sentinels before evidence seal. | PENDING — authored plan only; bundle disclosure checks and independent security audit required. |

## Acceptance gate

This register remains in progress until every authored mitigation has execution evidence from the affected checks and an independent code/security audit. The high-severity findings must be closed before Phase 4 security acceptance. Dependency review evidence may support package identity/provenance scoping, but cannot close a threat or certify package code, native runtime behavior, or rendered output.

## Audit trail

Initial plan-time register: 17 authored entries, all pending execution evidence. The register records planned controls only; it makes no claim that source changes, installed behavior, rendered artifacts, or release evidence are secure. Phase 5 publication remains a separate gate.

## Resource implementation readback

Plan 04-01 now has concrete resource proof at a7ef126 and an independent bounded clean review in 04-RESOURCE-REVIEW.md: wheel/resource/font/oracle hashes and forbidden-content inventory match; 12 focused controls pass; installed outside-checkout and Windows native PDF proof is recorded. This supplies evidence for T-04-01/T-04-02/T-04-SC. Entries remain pending final phase audit because later schemas, installed numerical code and actual report font selection still change this boundary. No authored threat is silently waived.

## Public-model and export readback

Plan 04-03 is independently clean at a89b782 after resolving all three initial findings. The corrected full suite has 476 passed and zero skipped; the clean-source boundary suite has 18 passed with only the two optional real integrations skipped. Complete comparison signatures/evidence survive all formats, and figure links exclude blocked comparisons. 04-EXPORT-REVIEW.md and 04-WAVE1-CHECKS.md supply bounded evidence for T-04-06/T-04-07/T-04-08; final security closure remains a phase audit after renderer and sealed-operation checks.
