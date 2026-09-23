# Phase 4 runtime path map

Status: preparation only, read-only audit on 2026-09-23. This map does not change Phase 2 evidence, recompute ZIP/R inputs, install dependencies, or declare installed real-data acceptance.

## Runtime boundary

Phase 4 needs two path classes:

| Class | Installed-wheel interface | Explicit caller path |
|---|---|---|
| Authored package resources | importlib.resources.files("brujula"), exposed by typed helpers in brujula.resources | None; checkout fallback is compatibility only |
| Real source and acceptance inputs | Never embedded in wheel | --source-root with raw ZIPs, current receipts and immutable attempt receipts; --output-root; --audit-dir |
| Official benchmark files | Never embedded without an explicit license decision | --workbook for pinned 2025-Q2 XLSX and --pdf for pinned 2026-Q2 PDF |
| R runtime | External executable and survey library | BRUJULA_RSCRIPT or explicit --r-home/config; optional BRUJULA_R_LIB |
| Publication output | Run-owned filesystem state | Explicit output/run roots |

The installed command must receipt package version, resource digests, source/output/audit roots, R executable/version/library identity, and PDF capability. Missing resources, receipts, R, official files, or required PDF capability must fail closed with a receipt; no synthetic fallback.

## Current assumptions and seams

### Acceptance

scripts/accept_enoe_estimates.py derives ROOT from its script location. It reads:

- data/catalog/enoe-snapshots.json, including eight approved IDs/order;
- data/fixtures/enoe-aggregate-golden.json, including public/internal pins, metric digest, official cells, semantic baseline and oracle cases;
- scripts/enoe_survey_oracle.R;
- the Phase 2 code-hash inventory;
- source ZIPs/receipts through brujula.source_inventory and brujula.acquisition;
- .cache/research/precision_2025q2.xlsx;
- .cache/research/enoe2026_08.pdf.

Smallest seam: package-owned brujula.enoe_acceptance.accept(output_root, audit_dir, *, source_root=None, workbook=None, pdf=None, rscript=None, r_lib=None, generate_golden=False), plus CLI brujula enoe-accept. Keep scripts/accept_enoe_estimates.py as a thin checkout wrapper. Preserve callable compatibility. generate_golden remains false by default and must continue rejecting changes to approved public, official, or existing internal pins.

### R oracle

_execute_r currently chooses BRUJULA_RSCRIPT, then .cache/R-4.6.1/bin/Rscript.exe, then literal Rscript; it uses .cache/R-library and a checkout R script. Installed behavior should resolve an explicit BRUJULA_RSCRIPT file, then an explicit --r-home/config path, then shutil.which("Rscript"). Validate executable file, run Rscript --version, record path/version, and set BRUJULA_R_LIB only when explicitly configured. Package the authored R script at a stable location such as brujula/oracle/enoe_survey_oracle.R and expose it through resources.py. Do not mutate PATH or silently use a checkout cache. R and survey remain external prerequisites.

### Official reconciliation

scripts/official_reconciliation.py pins the enoe_2025_q2 source SHA, workbook SHA/cells, 2026-Q2 PDF SHA and five national counts. Move implementation to brujula.official_reconciliation, preserving reconcile(output_root, workbook, records), check_2026_pdf_benchmark(pdf, records), workbook_cells(path), and main(argv=None). Keep the script as a thin wrapper. Installed CLI requires explicit --workbook, --pdf and accepted aggregate records/run; checkout defaults may remain only in the wrapper. Hash workbook/PDF before comparison; never infer missing files.

### Source inventory and acquisition

brujula.acquisition._default_registry already resolves enoe-snapshots.json through _resource. resolve_snapshot requires output_root/acquisitions/<snapshot_id>/current.json, its matching immutable attempt receipt, and output_root/raw/<sha256>.zip. source_inventory.inventory_all/inventory_snapshot use the same output root and registry. A source-root adapter may map --source-root to this layout, but must preserve receipt/current/hash invariants and never treat a ZIP path alone as successful acquisition.

### Metrics, analysis, and resources

brujula.metrics.load_metric_manifest reads enoe-metrics.json through _resource and compares its digest with the accepted golden manifest digest. brujula.analysis_v2 still uses checkout ROOT for the Phase 2 hash guard and public golden fixture. Its approved source registry already resolves through acquisition._default_registry; the independently pinned aggregate coverage resource added in de69626 uses resources._resource as well. Phase 4 must consume validated public v2 payloads through a separate resolver; it must not reuse the synthetic v1 grain or substitute analysis output for numerical acceptance.

Current pyproject.toml packages brujula, contracts, catalog and fixtures with JSON globs. It does not package scripts, the R oracle, official XLSX/PDF, or acquired ZIPs. Extend package data only for approved authored resources: catalogs, golden aggregate baseline, schemas and the R oracle after license review. Add typed resource helpers for enoe-snapshots.json, enoe-metrics.json, enoe-aggregate-golden.json, the oracle script and accepted v2 schemas. Preserve existing v1 helper meanings.

## Installed command shape and clean checks

After implementation:

    python -m brujula enoe-accept --source-root SOURCE_ROOT --output-root OUTPUT_ROOT --audit-dir AUDIT_DIR --workbook XLSX --pdf PDF [--rscript RSCRIPT] [--r-lib R_LIB]
    python -m brujula enoe-replay --source-root SOURCE_ROOT --run SEALED_RUN --audit-dir AUDIT_DIR [--rscript RSCRIPT] [--r-lib R_LIB]

Replay is read-only against sources, verifies all eight current receipts/hashes and packaged catalog/golden digests, compares canonical numeric/public records, and emits a sealed receipt. Invoke the installed wheel outside the checkout.

Meaningful clean-install checks:

- resource lookup outside checkout;
- missing resource/catalog/receipt/R/PDF failure with exit 1 and receipt;
- source/output/audit separation;
- Windows and Ubuntu R identity reporting;
- same eight snapshots produce same numeric digest/public records;
- v1 synthetic tests remain a separate regression lane;
- replay has no network or production access.

A wheel install or synthetic fixture PASS is not real-data acceptance.

## Fresh acceptance and code hashes

Accepted Phase 2 source: commit 86406f6. Combined numeric digest:
8db575e9d664864d1513e3b9658bd9b060c4cb3bed8b51561f208adeb97b9a00.

The frozen code hash inventory contains exactly:

    scripts/accept_enoe_estimates.py
    scripts/enoe_survey_oracle.R
    scripts/official_reconciliation.py
    brujula/acquisition.py
    brujula/source_inventory.py
    brujula/enoe_adapter.py
    brujula/populations.py
    brujula/metrics.py
    brujula/survey.py
    brujula/estimates.py
    brujula/research_contract.py

Changes to these files, the R oracle, metric manifest, golden public/official pins, source catalog, or snapshot/member custody require fresh frozen acceptance and unchanged replay. Path changes require the same when they change which resource, receipt, workbook, R library, method, or catalog is read. Preserve the old manifest/receipt as historical evidence. Never disable the hash guard, override golden pins, or call path mapping new numerical proof.

Packaging-only changes still require installed-wheel acceptance because the runtime boundary changed. A wrapper must not replace a hashed implementation and claim old proof. If package modules replace hashed files, create a new explicit hash inventory naming the actual implementation modules and oracle resource; retain old inventory and rerun full acceptance before publishing a new digest.

Phase 4 renderer/exporter/pipeline changes consume the validated Phase 3 sanitized projection. Layout, presentation ordering, format serialization and downstream complementary suppression require affected parity, disclosure, claim and replay checks; they do not by themselves require rerunning survey estimation. Fresh numerical acceptance is required when accepted statistical code, numerical inputs, source selection, estimators or their definition/resource resolution change. Keep this boundary explicit rather than expanding every report edit into a survey rerun.

## Required evidence

1. Package resource inventory with SHA-256.
2. Explicit installed CLI interfaces for source/output/audit/workbook/PDF/R.
3. Receipt with runtime versions, resolved paths, resource/source digests, code hash inventory and numeric/public digests.
4. Installed-wheel acceptance and replay on Windows and Ubuntu.
5. Failure evidence: failed acquisition invalidates current and preserves history.
6. One validated public projection feeds reports, figures, tables and exports; no diagnostics/person rows cross the boundary.

Authoritative current Phase 2 evidence remains docs/evidence/phase-02-numerical-acceptance.json. This map prepares Phase 4 packaging/runtime work and does not upgrade that evidence.

