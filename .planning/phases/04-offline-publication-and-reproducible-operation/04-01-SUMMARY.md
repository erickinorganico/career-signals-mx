---
phase: 04-offline-publication-and-reproducible-operation
plan: 01
subsystem: packaging
tags: [wheel, resources, oracle, fonts, pdf, weasyprint]
requires:
  - phase: 02
    provides: accepted eight-snapshot numerical baseline and exact R oracle
  - phase: 03
    provides: accepted analysis reference and coverage pins
provides:
  - typed authored-resource paths and SHA-256 inventory in an installed wheel
  - byte-identical packaged R oracle and audited DejaVu fonts with full notice
  - reviewed optional WeasyPrint 70 PDF dependency and native capability probe
affects: [04-02 installed numerical authority, 04-04 offline reports, 04-06 release verification]
tech-stack:
  added: [weasyprint==70.0 optional pdf extra]
  patterns: [package-owned importlib.resources lookup, explicit native PDF probe]
key-files:
  created:
    - brujula/oracle/enoe_survey_oracle.R
    - brujula/assets/fonts/DejaVuSans.ttf
    - brujula/assets/fonts/DejaVuSans-Bold.ttf
    - brujula/assets/fonts/DejaVuSerif.ttf
    - brujula/assets/fonts/DejaVuSerif-Bold.ttf
    - brujula/assets/fonts/LICENSE_DEJAVU
    - tests/test_installed_runtime.py
  modified:
    - brujula/resources.py
    - pyproject.toml
key-decisions:
  - Preserve the accepted Phase 2 source files and historical code-hash inventory; 04-02 owns executing-code migration and fresh numerical acceptance.
  - Keep PDF optional at import time and require an actual local render before claiming native capability.
patterns-established:
  - Typed installed paths raise for absent files; checkout fallback is limited to the authored source tree.
  - Every shipped catalog, schema, fixture, oracle and font file appears in the resource digest map.
requirements-completed: []
requirements-addressed: [OPS-01]
coverage:
  - id: installed-resource-custody
    description: Installed wheel resolves 22 authored files and fails when a required file is absent
    requirement: OPS-01
    verification:
      - kind: integration
        ref: outside-checkout installed test_installed_runtime.py (12 passed)
        status: pass
      - kind: artifact
        ref: wheel ZIP inventory and SHA-256 table below
        status: pass
    human_judgment: false
  - id: installed-pdf-capability
    description: Optional reviewed WeasyPrint 70 and local Pango/Fontconfig render a PDF
    requirement: OPS-01
    verification:
      - kind: integration
        ref: outside-checkout require_pdf_capability() returned 70.0
        status: pass
      - kind: unit
        ref: tests/test_installed_runtime.py missing Python/native capability controls
        status: pass
    human_judgment: false
  - id: real-installed-replay
    description: Eight-snapshot acceptance, identical-input replay, receipts and locks
    requirement: OPS-01
    verification:
      - kind: planned
        ref: 04-02 and 04-05
        status: pending
    human_judgment: false
duration: 16min
completed: 2026-09-23
---

# Phase 4 Plan 01: Installed Resources and PDF Capability Summary

Verified repository files: `brujula/resources.py`, `brujula/oracle/enoe_survey_oracle.R`, `pyproject.toml` and `tests/test_installed_runtime.py`.

**A clean wheel now carries 22 authored research resources and audited fonts, while an isolated installed copy resolves them and renders a local WeasyPrint 70 PDF.** This prepares OPS-01; the real installed eight-snapshot acceptance, replay receipts and publication lock behavior remain gates in 04-02 and 04-05.

## Performance

- Started: approximately 2026-09-23T19:23:00Z; first RED commit at 19:28:37Z.
- Completed: 2026-09-23T19:42:00Z.
- Tasks: 2/2, each with RED and GREEN commits.
- Source files changed: 9, including five audited font/notice assets.

## Task commits

| Task | RED | GREEN |
|---|---|---|
| 1. Package exact authored resources | `9909e4e` | `1033e96` |
| 2. Declare and verify portable PDF/resource packaging | `37faf1c` | `b2dcfd2` |

## Installed proof

- Fresh wheel: `.cache/phase4-wheel/career_signals_mx-0.1.0-py3-none-any.whl`, SHA-256 `4c782b5dc5e2afb602349a214eab93191e35dde78cd28caea573df8e7060ac7e`.
- Isolated Python 3.12 install: `C:\Users\erick\AppData\Local\Temp\brujula-0401-31a971f43eed4e7088e993a317fb576c\Lib\site-packages\brujula`. `brujula.__file__` resolved there from a separate temporary working directory.
- Wheel ZIP inspection found 54 members, of which exactly 22 are authored catalogs, contracts, fixtures, oracle or font/notice files. No `.zip`, `.xlsx`, `.pdf`, `.cache/`, `raw/` or person-named member appeared. The wheel does not contain R binaries or source records.
- Installed `authored_resource_digests()` returned 22 entries. Removing installed `catalog/enoe-metrics.json` temporarily yielded `FileNotFoundError: Missing bundled resource: catalog/enoe-metrics.json` and process exit 1 from outside the checkout; the file was restored.
- Installed v1 `python -m brujula demo --as-of 2026-09-22` completed with a synthetic `REVIEW` receipt, 54 observations, and `report --format html` resolved the verified current report. This is a synthetic regression, not numerical acceptance.
- With `WEASYPRINT_DLL_DIRECTORIES` set to the reviewed project-local WeasyPrint onedir `_internal` directory and `FONTCONFIG_FILE` to `.cache/research/fontconfig.conf`, the installed `require_pdf_capability()` rendered a PDF and returned `70.0`. The function raises on absent optional Python dependency, wrong version, native Pango/Fontconfig render failure, or non-PDF output. Ubuntu still needs its own Pango/font probe in 04-06.
- Affected checkout tests: `14 passed` (`tests/test_installed_runtime.py` plus `tests/test_cli.py`). Installed package tests from an outside working directory: `12 passed`, with the project pytest runner and `PYTHONPATH` directed to the isolated installed `site-packages`; import origin was verified. The temporary install did not have offline-cached pytest, so no alternative package was installed.

### Authored resource SHA-256 inventory

| Wheel-relative resource | SHA-256 |
|---|---|
| `assets/fonts/DejaVuSans-Bold.ttf` | `b184b89e3c1075f22f6b71575b6fc20d4972b3cfd3b23322ca6fd596dcaef167` |
| `assets/fonts/DejaVuSans.ttf` | `3fdf69cabf06049ea70a00b5919340e2ce1e6d02b0cc3c4b44fb6801bd1e0d22` |
| `assets/fonts/DejaVuSerif-Bold.ttf` | `c3753f2ed6bc673f15846dc45addbeb3b9c872f32fb18fd53a21f1bef1ed7676` |
| `assets/fonts/DejaVuSerif.ttf` | `107244956e9962b9e96faccdc551825e0ae0898ae13737133e1b921a2fd35ffa` |
| `assets/fonts/LICENSE_DEJAVU` | `d75938dec098f06f0ac3c00853065d94f020be1c3c62ef1dc2975ba15b4d9b0e` |
| `catalog/enoe-geography-equivalence.json` | `525238d870c0521d0375b71dfade86bda1b2209dfffab2fe9254d4f6c1165134` |
| `catalog/enoe-metrics.json` | `72b53c6e4da6c2e7190effe2cc880999fa5fd54018a0a8bf371b8b4f1cd5a929` |
| `catalog/enoe-snapshots.json` | `ff8cdf5615b9f4591e07af5f4c1522c890548e0fa497ce19ad3ccd668a0fc2a7` |
| `catalog/sources.json` | `d27188bb3aa517bb4227ccc9203d4dcdab69bc566fb28ba66a127a18030ca67b` |
| `contracts/agent-run.schema.json` | `3c1690b55c46e87b3f581bbc14a6708a33916fa6baec28cdff192ba7ced01de0` |
| `contracts/analysis-v2.schema.json` | `b078baa5b85076cbdba8f356f6cb8233c5de650e9cb56f5e8d7393fcc9e50c0c` |
| `contracts/dataset.schema.json` | `1020f1f56eeeb97c14b8d859385f3d15d8a8ed30b729a96f5d33b37c45be6023` |
| `contracts/insight.schema.json` | `b695c311eb56e307934fe6f2f265136ef3c53eb5f0e778de4e7e6564f4b06937` |
| `contracts/research-v2-public.schema.json` | `52079cad4a134559edb14081ada407d29db80c5f766ac1da89b993171e7dfd12` |
| `contracts/research-v2.schema.json` | `c0d99b0a62c4a9623f23c1b75baef764820935641f47c0f06bbf3b1435d10845` |
| `contracts/run.schema.json` | `7e68b6f37faf9bb51942a858f1d830434439208c27099f7d23d59177fab6c0df` |
| `fixtures/analysis-v2-golden.json` | `d2eaff964638b781ecfee5c872441c866e8813c22c234031c62465cf7c55a6e9` |
| `fixtures/enoe-aggregate-golden.json` | `ef41c327b3e01dbee92ac92f1bfacaec1a17a0ad2978e1f7349acb684fe55071` |
| `fixtures/enoe-analysis-coverage-pins.json` | `61c80d225795ef430002187edba6ba01dc7b1b38fe92656c621d16d34621c287` |
| `fixtures/enoe-analysis-reference.json` | `2ecaf5808db2ec26c38f4d28138dc0af50ca191f5fb0fdb498240f650862a520` |
| `fixtures/pilot.json` | `62de3d3345235ffd389ec86d8d3f2ac0c48f5ee03a71f9a714a2279de45eb6a5` |
| `oracle/enoe_survey_oracle.R` | `8bd11d3e5a04a3e571a0549df897a457d31f67b9334044c597cce30d8d47a1c1` |

The five font/notice hashes match `.planning/research/FONT-ASSET-AUDIT.md`. The packaged R hash is byte-identical to `scripts/enoe_survey_oracle.R`. The historical Phase 2 code hash inventory was not edited.

## Deviations from Plan

None in implementation scope. The existing `resources.py` checkout fallback remains for authored source-tree compatibility; the installed wheel has no checkout fallback. We exercised pytest against the installed package using the existing project pytest runner because the temporary uv cache lacked the optional test dependency.

## Known stubs and threat flags

No new stubs. No new network endpoint, auth path, or trust-boundary file access beyond package-owned read-only resources and a local PDF probe. Source ZIP/current-receipt locks, real-data receipt emission and identical-input replay are not implemented by this packaging plan and remain assigned to 04-02/04-05.

## Next plan readiness

04-02 can use `snapshot_catalog_path`, `metric_catalog_path`, `aggregate_golden_path`, `analysis_reference_path`, `coverage_pins_path`, `oracle_script_path`, `font_path`, and `authored_resource_digests` from the installed package. The source/output/audit paths and full numerical acceptance still need to be wired and proven. OPS-01 stays open until those later gates pass.

## Self-Check: PASSED

All nine task files and this summary exist. Commits `9909e4e`, `1033e96`, `37faf1c` and `b2dcfd2` resolve as commits. The final wheel hash, 22-resource inventory, outside-checkout import origin, missing-resource exit and native PDF render were verified after the implementation commits; `git diff --check` found no whitespace errors.
