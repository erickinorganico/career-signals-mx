---
phase: 05
slug: independent-audit-and-v1-0-0-release
status: planned
nyquist_compliant: false
wave_0_complete: false
created: 2026-09-24
---

# Phase 5 validation strategy

The three proposed plans have not received an independent GSD plan-checker review. Phase 4 independent verification is still required before their release gates may close. This strategy preserves the real publication, clean-host fixtures, exact release custody and public readback as separate observations.

| Requirement | Plan | Executable or inspectable evidence | Acceptance limit |
|---|---|---|---|
| REL-01 | 05-01 | `scripts/check_docs.py`; installed CLI help/command readback; bilingual paragraph/links review against Phase 4 receipts | Passing links alone cannot certify methodological wording. |
| REL-02 | 05-01, 05-02 | Clean Windows/Ubuntu installed-wheel fixture/resource/PDF artifacts; separately pinned eight-quarter R/official acceptance, offline replay, actual real publication, visual/PDF review and independent review | Fixture CI does not become a second real numerical run. |
| REL-03 | 05-02 | Closed manifest-derived allowlist; tracked/wheel/ZIP/asset scans; source terms, attribution and dependency/font license decisions | A preparation license inventory stays `REVIEW` until exact-target review. |
| REL-04 | 05-03 | Exact-target GitHub draft upload and downloaded hash readback, then authorized public release and anonymous tag/asset readback | Owner-only draft access is insufficient. |
| GSD-01 | 05-02, 05-03 | Requirement-to-plan/summary/verification matrix, Phase 4/5 independent verification, code/security review, UAT and milestone audit | No override can silently convert a material gap to complete. |

For each plan, a changed code, package, source, method, report or asset input invalidates the affected prior check; unaffected immutable evidence may be reused by exact hash and receipt identity. `nyquist_compliant` remains false until the independent reviews, negative controls, candidate/public readback and final traceability are observed. No microdata or credential-bearing command envelope enters public evidence.
