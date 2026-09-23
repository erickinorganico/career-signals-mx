# Phase 4 revised integration plan check

Checked 2026-09-23. Scope: the revised `04-04-PLAN.md` and `04-05-PLAN.md` only, against `04-CONTEXT.md`, `04-REPORT-LAYOUT-PREFLIGHT.md`, `04-VISUAL-TOOLING.md`, the accepted Phase 2/3 interfaces, and the current `brujula/export_v2.py`, `brujula/enoe_acceptance.py`, `brujula/acquisition.py`, and `brujula/source_inventory.py`. This is static pre-execution review, not implementation or final acceptance.

**Result: PASS for the changed integration seams; 0 BLOCKER, 0 WARNING.** The canonical plan structure check was already reported valid with zero warnings. This check does not re-certify unchanged plans or claim a finished publication.

| Seam | Readback and plan coverage |
|---|---|
| PDF test audit | `04-04` names reviewed `pypdf==6.19.0` in the test/audit extra, requirements and BSD notice, tied to `docs/evidence/phase-04-pdf-audit-dependency.json`. WeasyPrint 70 remains the PDF product renderer. Tests require actual text, accents, font and asset readback. The plan calls for actual desktop/mobile/200%/A4 inspection; `04-VISUAL-TOOLING.md` establishes local browser, native 200% zoom and PDF raster tools, while `04-REPORT-LAYOUT-PREFLIGHT.md` addresses large figure/table pagination without introducing figure keys. |
| Export destination and inventory | `export_public_tables` rejects an existing target, creates its own staged directory and returns names/counts. `04-05` explicitly passes a fresh `run_dir/exports` child and checks the return plus actual disk set against the independently defined 22-table/46-file inventory. It preserves comparison signatures, evidence joins, CSV/Parquet and DuckDB/dictionary. Open paths use the exporter's actual `public-records` and `public.duckdb` names. |
| Refresh custody | `acquire_snapshot(snapshot_id, output_root)` stores raw ZIPs and per-snapshot immutable/current receipts under its output root; `resolve_snapshot` checks the registry URL, SHA, immutable attempt and raw bytes. `04-05` maps CLI `--source-root` to that acquisition custody root and `--output-root` to dependent publication, refreshes all eight approved IDs, invalidates publication current at the refresh boundary, and re-resolves all eight on every open. The registry's `publication_approved=false` microdata restriction remains intact. |
| Numerical acceptance identity | `enoe_acceptance` seals full receipts under `<audit-dir>/attempts/<attempt_id>.json` and writes a mutable current result. A successful acceptance result has `snapshots`, `source_receipt_ids`, `numeric_content_digest` and gate evidence; the replay result instead has `operation=read_only_replay`, `sealed_run` and `recomputed_manifest`. `04-05` explicitly binds a successful immutable acceptance receipt and current identity, and keeps numerical replay distinct from publication replay. An `operation` field must not be required on the acceptance receipt. |
| Error boundary and run sealing | `enoe_acceptance` rejects overlapping roots before a receipt destination exists; valid operational attempts seal receipts. `04-05` makes the same parse/configuration versus operational distinction. Its task actions stage, hash and seal the exact report, figure, export and five font assets before atomic current promotion, then verify manifest, receipt, files and live sources on every resolve. The post-pointer index case may leave a valid current only when the already promoted run is complete and re-verifiable; the index is not separate authority. |

No revised task introduces a new source, shrinks the approved eight-snapshot set, changes a numerical algorithm or precision claim, or treats Phase 4 publication as the final public release. Execution still must prove the planned focused tests, actual real-data render, fault matrix and installed replay.

## Follow-up: acceptance-to-analysis bridge

Checked the additional `04-05-PLAN.md` diff on 2026-09-23. This new bridge was outside the earlier PASS scope. The intended interface is viable: `findings_v2.build_analysis_packet(public_by_snapshot, acceptance, coverage_audits, definition_registry)` calls the guarded public index and validates the resulting packet; `load_definition_registry(entity_reference_code="02")` supplies the reviewed definitions. The immutable Phase 2 acceptance receipt names eight `public_v2_path` and aggregate-audit `path` files plus source receipt IDs; the mutable numerical current is a separate result. The new plan correctly requires these exact accepted files, live source/current identity, separate analysis-operation audit, safe root ancestry, an atomic fresh packet, and no reference or numerical change.

**Follow-up result: ISSUES FOUND — 2 BLOCKER, 0 WARNING.** The following task-level gaps prevent a verified unattended acceptance-to-analysis-to-publication route.

1. **BLOCKER — task_completeness / key_links_planned, Plan 04-05 Task 3.** Task 3's action is the only task that explicitly implements `pipeline_v2.analyze_acceptance`, but its `<files>` lists only `brujula/cli.py` and `tests/test_cli_v2.py`. Task 1 lists `brujula/pipeline_v2.py` yet does not assign the bridge action. The service implementation and direct test ownership are ambiguous to a task executor. **Fix:** add `brujula/pipeline_v2.py` and `tests/test_pipeline_v2.py` to Task 3 `<files>`, or assign service and direct tests explicitly to Task 1 and leave Task 3 responsible for CLI wiring.
2. **BLOCKER — verification_derivation / requirement_coverage, Plan 04-05 Task 3 and phase handoff.** The new Task 3 test asks for a clean installed call from a “fresh accepted fixture,” while Plan 04-05's final verification omits `research-analyze` and Plan 04-06's real integration starts with an already persisted Phase 3 packet. A fixture cannot establish the real guarded route: `build_analysis_packet` enforces exact eight-snapshot source, coverage, numeric and independent reference pins. **Fix:** require a clean outside-checkout installed `research-analyze` invocation against the fresh immutable real 04-02 acceptance receipt, validate and reload its newly generated packet with exact digest/keys, and feed that generated packet to `research-build` in the real 04-05/04-06 lane. Keep disposable fixture checks for CLI errors and isolated boundaries.

```yaml
issues:
  - plan: "04-05"
    task: 3
    dimension: task_completeness
    severity: BLOCKER
    description: "The bridge service action targets pipeline_v2.py, absent from Task 3 files; Task 1 does not assign the bridge."
    fix_hint: "Assign pipeline_v2.py and direct pipeline tests to a task that explicitly implements analyze_acceptance."
  - plan: "04-05"
    task: 3
    dimension: verification_derivation
    severity: BLOCKER
    description: "No planned real installed run proves acceptance receipt -> research-analyze -> freshly persisted packet -> research-build."
    fix_hint: "Run the bridge on the fresh real 04-02 immutable acceptance in the installed lane and consume that packet in the real publication integration."
```

## Final targeted recheck after revision

Checked the subsequent `04-04`, `04-05` and `04-06` plan edits on 2026-09-23. **Result: PASS for these targeted revisions; both follow-up BLOCKER findings above are resolved.** The earlier issue record is retained to show the revision trail; it no longer describes the current plan text.

- `04-05` Task 3 now lists `brujula/pipeline_v2.py`, `brujula/cli.py`, `tests/test_pipeline_v2.py` and `tests/test_cli_v2.py`, and assigns the guarded `analyze_acceptance` service plus CLI wiring and failure tests in its action. This resolves the task/file ownership gap.
- `04-05` Task 3 and its phase verification now separate small portable fixture checks from the real installed gate. The real gate starts with the fresh immutable eight-snapshot 04-02 acceptance, runs `research-analyze` outside checkout, validates the new packet's canonical digest, records, claims and persisted reload, and passes that same generated path to `research-build`. `04-06` repeats this chain as a mandatory real integration gate and records acceptance, analysis operation and publication identities separately. A historical JSON or ignored proof script cannot satisfy it. This resolves the unattended clean-reader handoff gap without relaxing the independent Phase 3 guard.
- `04-04` now preserves canonical `figure:` IDs in metadata and returned mappings, maps them to portable ASCII filenames by stripping only that fixed prefix, and requires collision rejection. Task 1 invokes the exact artifact contract. This changes file representation only; it does not create new figure identities or reduce paired SVG/PNG/table coverage.

Static plan review only. Execution must still produce the specified installed real-data, test, fault and visual evidence before Phase 4 can pass its implementation gate.
