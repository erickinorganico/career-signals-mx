# Phase 2 integration coverage decision

The detector combines the words “integration” and “API” in the plans. Here API means local Python interfaces called by tests, not a new remote service. This matrix records the actual complete boundary without changing the detector. Decisions do not imply implementation or numerical acceptance.

| capability | decision | reason |
|---|---|---|
| Offline resolution of the eight approved ENOE snapshots | INTEGRATE | Reuse Phase 1 current/attempt/hash inventory and the exact local registry; Phase 2 must not download during acceptance. |
| Local frame, metric, survey and v2 validation interfaces | INTEGRATE | Explicit adapters and tests in 02-01/02-02; no hosted application, credential or remote call. |
| Local R survey oracle | INTEGRATE | Versioned subprocess and aggregate comparison ledger; ignored person-derived input stays local. |
| Offline official reconciliation files | INTEGRATE | SHA-pinned 2025-Q2 precision workbook and 2026-Q2 official bulletin identified in 02-RESEARCH; local parsing and exact/rounding checks. |
| Remote HTTPS file retrieval during numerical acceptance | OPT-OUT | Inputs are already acquired through the authorized source catalog; acceptance is deliberately offline. Later refresh reuses the governed acquisition boundary. |
| Other INEGI remote API capabilities | OPT-OUT | No external INEGI API is integrated in this phase and no extra source capability is approved by these plans. |
| External inference or third-party service integration | OPT-OUT | AGENTS prohibits paid/external inference and the deterministic numerical workflow has no such requirement. |

Sources and exact file identities: `data/catalog/enoe-snapshots.json`, `01-VERIFICATION.md`, `02-CONTEXT.md`, `02-RESEARCH.md`. The numerical and failure checks remain executable requirements, not coverage-table attestations.
