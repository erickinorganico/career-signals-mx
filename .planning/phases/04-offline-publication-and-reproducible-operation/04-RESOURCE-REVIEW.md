---
phase: 04-offline-publication-and-reproducible-operation
reviewed: 2026-09-23
scope: plan_04-01_resource_runtime_review
source_freeze: a7ef126
files_reviewed:
  - brujula/resources.py
  - pyproject.toml
  - tests/test_installed_runtime.py
  - .planning/phases/04-offline-publication-and-reproducible-operation/04-01-PLAN.md
  - .planning/phases/04-offline-publication-and-reproducible-operation/04-01-SUMMARY.md
  - .planning/phases/04-offline-publication-and-reproducible-operation/04-SECURITY.md
  - .planning/research/FONT-ASSET-AUDIT.md
  - .cache/phase4-wheel/career_signals_mx-0.1.0-py3-none-any.whl
findings:
  critical: 0
  warning: 0
  info: 0
  total: 0
status: clean_bounded
---

# Plan 04-01 resource and installed-runtime review

Reviewed the completed Plan 04-01 resource boundary at source freeze `a7ef126`. The current `brujula/resources.py`, `pyproject.toml`, and `tests/test_installed_runtime.py` have no changes after that freeze. The review covers installed resource authority, wheel inventory, audited font and oracle bytes, and optional PDF capability/failure behavior. It does not certify Plan 04-02 numerical execution, Plan 04-03 model boundaries, publication, or the Phase 4 security register.

## Verdict

No open correctness or security finding was reproduced in this bounded scope. Installed resource access resolves package-owned files first and fails closed when the required resource is absent. The wheel package-data declaration includes the reviewed catalogs, contracts, fixtures, oracle, and five font/notice files; source ZIPs, workbook/PDF inputs, raw records, caches, credentials, and R binaries are absent from the wheel inventory.

`authored_resource_digests()` covers 22 files: ten authored catalog/fixture/oracle resources, seven schemas, and five font/notice assets. `font_path()` accepts only the four audited DejaVu faces and `LICENSE_DEJAVU`; the recorded SHA-256 values match the local files and the Plan 04-01 inventory. The packaged oracle and `scripts/enoe_survey_oracle.R` both hash to `8bd11d3e5a04a3e571a0549df897a457d31f67b9334044c597cce30d8d47a1c1`.

The PDF helper requires `weasyprint==70.0`, performs an actual `write_pdf()` call, checks the `%PDF-` signature, and raises an explicit `RuntimeError` for missing Python dependency, wrong version, native Pango/Fontconfig failure, or non-PDF output. The focused test file passes `12 passed` under `.venv/Scripts/python.exe`.

## Evidence

- Wheel: `.cache/phase4-wheel/career_signals_mx-0.1.0-py3-none-any.whl`; SHA-256 `4c782b5dc5e2afb602349a214eab93191e35dde78cd28caea573df8e7060ac7e`.
- Wheel ZIP inventory: `54` members, exactly `22` authored resource members under `brujula/catalog`, `brujula/contracts`, `brujula/fixtures`, `brujula/oracle`, and `brujula/assets/fonts`.
- Font hashes independently match the five values in `.planning/research/FONT-ASSET-AUDIT.md`; oracle bytes independently match the authored checkout script.
- Accepted temporary outside-checkout install path exists at `${TEMP}/brujula-0401-31a971f43eed4e7088e993a317fb576c/Lib/site-packages/brujula/resources.py`. The Plan 04-01 summary records the isolated import-origin, missing-resource failure, synthetic CLI smoke, and native PDF probe from that install.
- Focused command: `.venv/Scripts/python.exe -m pytest tests/test_installed_runtime.py -q` → exit `0`, `12 passed`.

## Boundary and follow-up

The successful PDF probe demonstrates optional dependency/native loader capability, while the probe HTML does not independently prove that a report selected each shipped DejaVu face. The font byte/hash inventory is verified separately, which is sufficient for this Plan 04-01 resource review; report font selection belongs to the later renderer/release checks.

The authored security entries `T-04-01`, `T-04-02`, and `T-04-SC` remain phase-level mitigations until the later installed numerical, renderer, release, and independent security gates execute. This file records no overall Phase 4 or security completion.

_Reviewer: independent bounded resource review; no source implementation files modified._
