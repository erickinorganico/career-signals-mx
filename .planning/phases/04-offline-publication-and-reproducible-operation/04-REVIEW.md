---
phase: 04-offline-publication-and-reproducible-operation
reviewed: 2026-09-24T02:00:00Z
depth: deep
files_reviewed: 17
files_reviewed_list:
  - brujula/report_v2.py
  - brujula/pdf_v2.py
  - tests/test_report_v2.py
  - tests/test_pdf_v2.py
  - brujula/pipeline_v2.py
  - brujula/cli.py
  - brujula/resources.py
  - contracts/publication-manifest-v2.schema.json
  - tests/test_pipeline_v2.py
  - tests/test_cli_v2.py
  - tests/test_installed_runtime.py
  - .github/workflows/verify.yml
  - requirements-pdf.txt
  - scripts/check_installed_runtime.py
  - tests/phase4_prohibitions.py
  - tests/phase4_prohibitions.test.cjs
  - tests/test_phase4_edge_acceptance.py
findings:
  critical: 0
  warning: 0
  info: 0
  total: 0
status: clean
---

# Phase 04: Code Review Report

**Reviewed:** 2026-09-24T02:00:00Z  
**Depth:** deep, bounded by the four direct review artifacts  
**Files reviewed:** 17  
**Status:** clean for reviewed local code; release and hosted CI remain pending

## Narrative Findings (AI reviewer)

No unresolved code, data-disclosure or material contract finding remains in the reviewed Phase 4 renderer, operation, metadata and 04-06 control/CI scopes. The detailed adversarial histories and closure evidence are in `04-RENDERER-CODE-REVIEW.md` (four resolved findings), `04-OPERATION-REVIEW.md` (five resolved findings), `04-METADATA-REVIEW.md` (no finding), and `04-INTEGRATED-CODE-REVIEW.md` (five resolved findings). The 04-06 control source is `ad73a72`; its CI/helper source is `4dda477`. The later operation recovery delta is covered by separate installed crash/recovery and real-output evidence in `04-INTEGRATED-OPERATION.md`; this consolidated report does not invent an independent rerun of the full real chain.

Exact current SHA-256 anchors for product code and schema are: `report_v2.py` `8e368c2b579795bf0805277b428e5252d4a6310a5f5c54dd2601e53fdbf04a85`; `pdf_v2.py` `2194911d18cd78457a3961ab43b6dc7d0415131730f141b9e41a6fc114eeda16`; `pipeline_v2.py` `e4581b3c688c522c1433829f44c3b6c6f13e26956fd188aa3fcbc07f47ce5483`; `cli.py` `303524fb3203dfd037a00c8b299763a56711a0ee2c99915af2f800aff1c42c26`; `resources.py` `1eea5cf7391430b7eb3640049ab97db8a0245ac35affb2e25d7cdf8150f2d9cd`; `publication-manifest-v2.schema.json` `ab543f5f3361f7065a0dceadc7a66eebc9c547382b423b152907a6c946924bc2`.

The final 04-06 anchors are: `verify.yml` `a70a9c4a93a0aba393a3122886b8a47fbceaa52a9c5979c0f8b11e65329e07b2`; `requirements-pdf.txt` `b03f2b2a61c0c60a1ec5ef061c95dcb3e372fa1b6c78d68ddcd052b78a953450`; `check_installed_runtime.py` `4b31fa22fd11db43a2d017967a291a236e9e57bea17d511c364cbcd0ce326883`; `phase4_prohibitions.py` `c749fc7b39acf6f46074cfb06084b6f51c4bcaee149032f82528d876bd171f45`; `phase4_prohibitions.test.cjs` `bce21ca479248c7602e17d2c8767ef471381c61b0d90dcc47f20f652ba8616cc`; `test_phase4_edge_acceptance.py` `0e3025464120c6ea62ca7136d5d8d117391936d4b4324e723dddc078c715b3e7`.

Current focused-test anchors are: `test_report_v2.py` `85108032636f3c274ea22e4bb4c4c9edac18028caf8cc3be17110df8264a1cb8`; `test_pdf_v2.py` `4d73bb2bdb739551c40367323246865380f7ffc75a7c5bab965cb9e1e8e4742b`; `test_pipeline_v2.py` `f0c87aef3aa3744731b818148afef6b054a204656c8cfbc7911a52990ded060e`; `test_cli_v2.py` `758409f8b6532bfab7cbc530a2bf6837ebbe4710124e1cf6e69f2307072a10be`; `test_installed_runtime.py` `90a27aa6f4f2c42b14ae6b2e74e0b2792e6fe839c3069c44ac88a1c65b64fb20`.

Independent focused reruns established the amended canary, OPS fault, PUB precision/join/order and Node bad-selector paths. The executor reports the final 04-06 focused suite **108/108 passed**, full checkout verification **592 passed**, Node controls **30 passed**, canonical GSD prohibition producers green with fail-first violation fixtures, and an outside-checkout installed-helper positive plus corrupted-module-wheel negative. The accepted-model real permutation receipt at `.cache/research/phase4-real-permutation/readback.json` has SHA-256 `68a65608a03483a0cb5c013c59cd7a88c114b4f53a57326ee2aeaca3d1111c2c`: production validation passed; all nine figure pixel/point-manifest outputs and 22 CSV/Parquet/DuckDB tables stayed equal under reversed insertion order; figure and claim joins were nonempty. These are separate evidence layers, not interchangeable test claims.

The public acceptance evidence remains `LOCAL_PASS_PENDING_CI`. Hosted Windows and Ubuntu CI readback, the Plan 04-06 summary, and formal final GSD verification/security gates were pending at this review handoff. This code review does not designate Phase 4 or v1.0.0 released.

---

_Reviewer: independent Phase 04 code reviewer. No product source or Git state was changed by this reviewer._
