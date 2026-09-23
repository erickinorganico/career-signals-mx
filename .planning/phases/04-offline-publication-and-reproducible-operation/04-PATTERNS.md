# Phase 4: Offline Publication and Reproducible Operation - Pattern Map

**Mapped:** 2026-09-22
**Scope:** preparatory map, refreshed 2026-09-23; Phase 2 is accepted. Phase 3 profile, comparison, claim and packet code exists; final claim/packet review and acceptance remain pending. This map is not an executable plan or a Phase 3 acceptance decision.
**Source edits:** none.

## File Classification

The paths marked * are proposed boundaries from `04-RESEARCH.md` and the packaging/runtime readbacks, not locked filenames. Phase 3 callable signatures below are current source interfaces, still subject to final acceptance. Existing files are marked `modify`.

| New/modified file | Role | Data flow | Closest existing analog | Match quality |
|---|---|---|---|---|
| `brujula/publication_v2.py`* | model/validation | transform | `brujula/research_contract.py` | role and flow |
| `brujula/report_v2.py`* | renderer | transform, file I/O | `brujula/report.py` | role and flow, v1 shape only |
| `brujula/export_v2.py`* | exporter | transform, file I/O | `brujula/export.py`, `brujula/warehouse.py` | role and flow, v1 shape only |
| `brujula/pipeline_v2.py`* | batch service | file I/O, event-driven state | `brujula/pipeline.py`, `brujula/acquisition.py` | role and flow, v1 input only |
| `brujula/cli.py` (modify) | CLI | request-response | `brujula/cli.py` | exact entry-point pattern |
| `brujula/resources.py` (modify if packaged assets) | utility | file I/O | `brujula/resources.py` | exact package-resource pattern |
| `pyproject.toml` (modify) | config | dependency/package | `pyproject.toml` | exact packaging pattern |
| `contracts/publication-v2.schema.json`* | schema | validation | `contracts/research-v2-public.schema.json` via `research_contract._validator` | role match; proposed contract |
| `contracts/publication-manifest-v2.schema.json`* | schema | validation | `contracts/run.schema.json` via `pipeline.seal_receipt` | role match; proposed contract |
| `tests/test_publication_v2.py`* | test | transform | `tests/test_report.py`, `tests/test_research_contract.py` | role match |
| `tests/test_export_v2.py`* | test | file I/O | `tests/test_export.py` | role and flow |
| `tests/test_pipeline_v2.py`* | test | file I/O, event-driven state | `tests/test_pipeline.py`, `tests/test_acquisition.py` | role and flow |
| `brujula/enoe_acceptance.py`* | service | batch, file I/O | `scripts/accept_enoe_estimates.py` | exact role and flow; relocation seam |
| `brujula/official_reconciliation.py`* | service | batch, file I/O | `scripts/official_reconciliation.py` | exact role and flow; relocation seam |
| `scripts/accept_enoe_estimates.py` (modify) | compatibility CLI | request-response | its current `main` and `accept` | exact |
| `scripts/official_reconciliation.py` (modify) | compatibility CLI | request-response | its current `main` and reconciliation callables | exact |
| `brujula/oracle/enoe_survey_oracle.R`* | package resource | batch, file I/O | `scripts/enoe_survey_oracle.R` | exact content; new package location |
| `tests/test_installed_runtime.py`* | test | batch, file I/O | `tests/test_analysis_v2.py`, `tests/test_acquisition.py`, `tests/test_cli.py` | role match; installed wheel is a new boundary |

No proposed Phase 4 Python API filename, argument list, or canonical publication digest is accepted by this map. The current Phase 3 packet shape is defined in `contracts/analysis-v2.schema.json:1-62`, but its acceptance remains pending. The output artifact names (HTML, Markdown, PDF, SVG/PNG, CSV/Parquet/DuckDB, receipt, manifest, current) are locked in `04-CONTEXT.md` and `04-EDITORIAL-SPEC.md`.

## Pattern Assignments

### `brujula/publication_v2.py`* — public model and stable IDs

**Analog:** `brujula/research_contract.py:17-27,212-229,232-273`. The existing public boundary validates the internal packet, copies an explicit allowlist, nulls suppressed diagnostics, then validates the public result:

```python
failures = validate_research_v2(payload)
if failures:
    raise ValueError(f"invalid internal research v2: {failures}")
# ... catalog_fields and record_fields allowlists ...
suppressed = row["value"] is None
projected["weighted_denominator"] = None if suppressed else row["weighted_denominator"]
projected["support"]["weighted_support_total"] = None if suppressed else row["support"]["weighted_support_total"]
for key in ("standard_error", "coefficient_variation", "ci90_lower", "ci90_upper"):
    projected["precision"][key] = None if suppressed else row["precision"][key]
failures = validate_public_research_v2(result)
```

The ten-key `GRAIN` remains the identity input. `analysis_v2.py:280-286` creates `v2r:` IDs from canonical JSON of the grain. `build_profiles` propagates complementary parent redactions into its sanitized `record_index` (`analysis_v2.py:369-380,438-461`). `findings_v2.py:156-180` then places that index in the analytical packet. Reuse those IDs after final Phase 3 acceptance. The publisher must consume the final validated packet and its `record_index`; reprojecting original Phase 2 estimates would restore additional redactions. Preserve controlled public reasons and `redaction_reason`; internal diagnostics never enter publication.

**Current packet validation seam** (`brujula/findings_v2.py:208-226,227-259,265-272`):

```python
schema = json.loads(contract_path("analysis-v2.schema.json").read_text(encoding="utf-8"))
for err in Draft202012Validator(schema).iter_errors(packet):
    errors.append({"id": "schema", "message": f"{'/'.join(map(str, err.path))}: {err.message}"})
trusted = _load_reference()
observed = _reference_from_packet(packet)
if observed != trusted:
    errors.append({"id": "trusted_reference", "message": "sanitized inputs or source manifest differ from independent accepted pins"})
```

The actual root fields are `source_manifest`, `record_index`, `profiles`, `coverage`, `comparisons`, `claims`, `opening_claim_ids`, `limitations`, and `content_digest` (`analysis-v2.schema.json:7-62`). `validate_analysis_packet` also recomputes the ledger and canonical claims. The Phase 4 boundary should call it before building any editorial or export model, and pin the accepted packet digest and source dependencies in the run receipt. A schema-only pass is insufficient.

**Hash-only reference dependency:** `_reference_from_packet` (`findings_v2.py:43-50`) binds source manifest, sanitized index, profiles, coverage and accepted numerical digest, while `_load_reference` (`:39-40`) reads `enoe-analysis-reference.json`. When installed numerical implementation/resource paths change, review and rebind the Phase 2 code inventory and this Phase 3 reference only after fresh installed numerical acceptance, unchanged replay and full Phase 3 packet validation. Keep prior hashes as historical evidence. Never disable `_check_codes` (`analysis_v2.py:79-95`) or substitute the old proof for the new runtime.

### Phase 3 comparison, claim and editorial input seams

**Comparison ledger:** `brujula/comparisons_v2.py:387-458` accepts a profiles mapping containing the **sanitized** `record_index`, checks each `v2r:` identity and profile value, then emits `v2c:` IDs for adjacent-quarter, like-quarter annual, recorded-sex and entity slots. `_result` (`:287-376`) records `reasons`, `limitations`, endpoint record/source IDs and signatures. Its decisive pattern is:

```python
if item.get("redaction_reason"):
    reasons.append(item["redaction_reason"])
if row.get("status") not in ("MEASURED", "REVIEW") or row.get("value") is None:
    reasons.append(label + "_unsupported")
reasons = sorted(set(reasons))
comparable = not reasons
delta = b["value"] - a["value"] if comparable else None
```

The publisher should display accepted `packet["comparisons"]` entries and their limits; it must not compute a new difference from arbitrary rows. `load_definition_registry(entity_reference_code="02")` (`:83-159`) pins the reviewed source/geography/method definitions; `findings_v2.py:248-251` regenerates the ledger during packet validation. Existing negative controls are `tests/test_comparisons_v2.py:106-115,133-160,212-265`.

**Claims:** `brujula/claims_v2.py:117-175` binds each `v2k:` claim to supported `v2r:` rows or one passing comparison, exact source SHA-256, method/version, evidence refs, quantities, Spanish copy and limitation. `validate_claim` (`:178-189`) regenerates the entire object and rejects altered text; `select_opening_claims` (`:192-216`) yields at most three distinct supported themes. `findings_v2.py:108-139` creates the packet's claim registry and `opening_claim_ids`. Use those IDs and canonical text in the question-led report; if fewer than three pass, show fewer. `tests/test_claims_v2.py:56-82,85-149,152-176` are the close analogs for exact provenance, suppressed cells, grammar and stable selection. Do not use the renderer to mint new quantitative prose.

**Output model:** the packet's `record_index` entries contain `record_id`, ten-field `grain`, public `record`, `snapshot_sha256`, `method_version`, `display` and optional `redaction_reason` (`analysis-v2.schema.json:64-85`). `profiles` provides national, latest field, state and recorded-sex slots; `coverage` counts missing reasons; `source_manifest` binds eight snapshots and accepted numerical content. These are the concrete inputs for the editorial model. The packet is still pending final Phase 3 acceptance, so executable Phase 4 planning must confirm the final accepted hash-only reference and packet readback.

### `brujula/report_v2.py`* — HTML, Markdown, paired figures and PDF

**Analog:** `brujula/report.py:13-19,26-56,70-113,227-266`.

```python
os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "brujula-matplotlib"))
matplotlib.use("Agg")

def _display_row_value(row):
    if row.get("status") in _UNAVAILABLE:
        return "No disponible"
    return _number(row.get("value"), row.get("unit"))

def _chart_save(fig, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    rcParams["svg.hashsalt"] = "brujula-laboral-mx-v1"
    rcParams["svg.fonttype"] = "none"
    fig.savefig(target.with_suffix(".svg"), format="svg", metadata={"Creator": "Brujula Laboral MX", "Date": None}, bbox_inches="tight")
    fig.savefig(target.with_suffix(".png"), format="png", metadata={"Creator": "Brujula Laboral MX", "Date": None}, dpi=144, bbox_inches="tight")
```

`report.py:41-56` escapes untrusted Markdown and HTML and makes text tables. `:81-84` hashes payload IDs before using them in chart paths. `:92-100` plots a line segment only for an explicitly comparable adjacent pair; `:197-205` leaves unusable values as visible gaps. `tests/test_report.py:32-40,43-60,63-72,75-92,107-139` tests escaping, no invented zero, deterministic artifacts, safe paths, and gaps. Preserve these properties while deriving every format from one accepted public/editorial model.

**Do not copy the v1 content model:** `_maps` at `report.py:59-67` reads `dataset.dimensions`; `_latest_metric_charts` at `:137-174` selects synthetic fields and bars; `_income_trend` at `:177-215` assumes `observation.id` and v1 comparisons; `render_report` at `:227-266` renders synthetic warning and loosely related HTML/Markdown strings. The v2 report needs fixed question-led sections, semantic `<caption>`/header scope, coverage and uncertainty, stable figure/record/claim links, and an actual cross-format parity gate.

**PDF:** no project-owned restricted WeasyPrint URL fetcher exists. `brujula/resources.py:9-17` resolves authored package resources and fails on absence; it is a useful fail-closed convention, **not** a safe PDF fetcher. The Windows probe in `.planning/research/PDF-PROBE.md:3-13` establishes feasibility only. Implement a new local-only resolver restricted to validated assets under the sealed run tree, reject network/data URLs and traversal, and make missing resources fatal. Integrate it when `WeasyPrint` renders the same HTML model. Verify clean Windows/Ubuntu and final pages; the probe does not certify the final report.

### `brujula/export_v2.py`* — CSV, Parquet and DuckDB

**Analog:** `brujula/export.py:17-29,32-53` and `brujula/warehouse.py:8-21,23-57`.

```python
writer = csv.DictWriter(buffer, fieldnames=FIELDS, lineterminator="\n")
writer.writeheader()
row["evidence_refs"] = json.dumps(row["evidence_refs"], ensure_ascii=False)
for key, value in row.items():
    if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@")):
        row[key] = "'" + value
writer.writerow(row)
```

`export.py:35-46` blocks export when quality/warehouse prerequisites fail and refuses to overwrite existing files; `:50-52` uses a read-only DuckDB connection and ordered `COPY ... FORMAT PARQUET`. `warehouse.py:14-21,56-57` creates typed tables inside a transaction, uses parameterized inserts, and commits after row count. `tests/test_export.py:19-42` checks formula prefixes, JSON evidence refs, nulls, Parquet round trip, and a blocked quality gate. Reuse these mechanics with the public v2 projection and stable ten-field grain key. Export a data dictionary and relational keys for distinct source, population, field, occupation, industry, geography, recorded sex, period, metric and method. Keep nulls typed as nulls.

**Do not copy:** `export.FIELDS` (`:12-14`), `dataset["observations"]` (`:22`), or `warehouse.observation` and its five-key unique grain (`warehouse.py:40-50`). `export.py:48` writes a full v1 dataset JSON; passing an internal v2 packet there would publish diagnostic estimates. The v2 exporter must reject a non-public input before writing any file. The current `export_csv` formula neutralization is reusable, while CSV's apostrophe representation differs intentionally from typed Parquet/DuckDB values.

### `brujula/pipeline_v2.py`* — sealed build, current resolution, replay

**Analog:** `brujula/pipeline.py:25-51,58-62,106-149,152-184,187-271`; `brujula/acquisition.py:201-288,291-324`; `brujula/runlock.py:9-54`.

```python
with BuildLock(out) as lock:
    _recover_interrupted(out)
    # mark current RUNNING and persist journal before input work
    # stage validated artifacts in a fresh run directory
    immutable_bytes(run_dir / "bundle.json", json_bytes(payload))
    seal_receipt(run_dir / "receipt.json", receipt)
    manifest = {p.relative_to(run_dir).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in sorted(run_dir.rglob("*")) if p.is_file() and p.name != "journal.json"}
    immutable_bytes(run_dir / "manifest.json", json_bytes(manifest))
    atomic_json(out / "current.json", current)
```

The excerpt follows `pipeline.py:192-205,252-263`. `atomic_json` (`:29-39`) fsyncs a temporary file and replaces it; `immutable_bytes` (`:42-51`) uses exclusive creation and collision checking. `_failure` (`:152-172`) writes an immutable failure receipt, uses `publication-failure.json` if success receipt already exists, and publishes BLOCKED current. `_recover_interrupted` (`:175-184`) turns prior RUNNING into failure. `resolve_current` (`:115-149`) verifies current status, manifest digest, each relative artifact path and hash, receipt/current agreement and source raw hash before returning paths. `tests/test_pipeline.py:55-84,118-137,147-211` exercises failure invalidation, tampering, staging after renderer failure, crash recovery, sealed-receipt preservation, and post-commit index failure. `tests/test_runlock.py:9-32` tests exclusive/crash-released lock behavior.

Add v2-specific schema and an **exact expected artifact set** to the seal and resolver; v1 `resolve_current` checks required report entries but otherwise trusts the manifest's own inventory. A PDF and each public CSV/Parquet/DuckDB/figure must be present, hashed, and safe. Keep mutable journal and current out of the sealed artifact map. A failed export/PDF/validation/seal must leave BLOCKED current; an older immutable run is historical only.

The v1 resolver verifies **one** `raw/<sha>.json` (`pipeline.py:140-145`). V2 must resolve all eight required acquisition currents on build **and each open**, using `acquisition.resolve_snapshot` (`:291-324`) and comparing the sealed dependency receipt IDs, URLs and digests to the returned receipts. Acquisition's `acquire_snapshot` writes RUNNING current then a final immutable attempt plus current (`:226-279`); a failed attempt replaces a prior success. `tests/test_acquisition.py:38-54,116-135,198-207` covers failure invalidation, offline replay, pinned hash and mismatch rejection. Do not call network acquisition from the publisher's read path.

Phase 2 already supplies accepted `numeric_content_digest` (`analysis_v2.py:296-301`), and Phase 3 packet `content_digest` hashes its own canonical JSON (`findings_v2.py:175-180,221-222`). Phase 4 still needs a versioned replay equality contract that states which accepted numerical/public records and claims it compares, separately from run ID, timestamps and PDF/container bytes. Reuse those existing digests and exact `v2r:`/`v2c:`/`v2k:` identities; do not invent a second record key. V1 `make_comparisons` (`pipeline.py:65-79`) is observation-ID based and cannot replace the Phase 3 ledger.

### `brujula/cli.py`, `brujula/resources.py`, `pyproject.toml` — integration

`cli.py:35-72` is the exact argparse pattern: explicit `--input`, `--output`, `--as-of` on build; `report --format` calls `resolve_current` before printing a path; blocked/error exits 1. Add clearly named real v2 build/replay/report commands with explicit source/output roots while keeping existing v1 `build`/`demo` fixture behavior. `tests/test_cli.py:6-15` covers blocked and missing-manifest report access.

`resources.py:9-29` checks packaged paths before checkout paths and raises `FileNotFoundError` for missing authored resources. `pyproject.toml:11-31` pins dependencies, declares the CLI, and includes JSON contract/catalog/fixture package data. Extend these only for actually shipped v2 schema/assets and WeasyPrint runtime setup; the existing resolver is not a general user-path sanitizer or a PDF URL authorization policy.

### Installed-wheel numerical and resource seams

**Package resource helper — `brujula/resources.py` (modify).** `_resource` (`:9-17`) looks under `brujula/<package_directory>/<filename>`, permits a checkout fallback only when `CHECKOUT_ROOT` exists, and raises `FileNotFoundError` otherwise. `contract_path` (`:20-21`) shows the typed accessor convention. Add typed authored-resource accessors for accepted snapshot/metric catalogs, golden aggregate baseline, v2 schemas and packaged R oracle; inventory their SHA-256 values in the installed receipt. `pyproject.toml:17-31` already declares `brujula` as CLI and includes JSON data for contracts/catalog/fixtures. It currently lacks an oracle package location and PDF extra; extend package data and dependency declaration only for assets cleared by license review. Never package ZIP microdata, local R/cache paths, official XLSX/PDF or credentials.

**Acceptance service and wrapper — `brujula/enoe_acceptance.py`*, `scripts/accept_enoe_estimates.py` (modify).** Move the current `accept(output_root: Path, audit_dir: Path, *, generate_golden=False)` implementation (`scripts/accept_enoe_estimates.py:467-480`) behind a package-owned callable; preserve the script callable and CLI compatibility. `run_attempt` (`:162-185`) invalidates acceptance current at RUNNING, writes an immutable attempt receipt and final current, and returns BLOCKED on failure. `_execute_r` (`:293-303`) currently falls back to checkout `.cache` R executable, library and script; installed behavior must resolve an explicit `BRUJULA_RSCRIPT` or configured R home, then `shutil.which("Rscript")`, verify its version, use an R library only when explicitly configured, and load the packaged authored oracle. This resolver has no close installed-runtime analog. The present `_code_hashes` (`:99-106`) names checkout scripts and implementation files; after relocation, the new hash inventory must name the actual package implementation and oracle resource, retain historical inventory, and pass fresh acceptance/replay before promotion.

**Official reconciliation service and wrapper — `brujula/official_reconciliation.py`*, `scripts/official_reconciliation.py` (modify).** Preserve `workbook_cells(path)` (`scripts/official_reconciliation.py:57-103`), `reconcile(output_root, workbook, records)` (`:130-159`) and `check_2026_pdf_benchmark(pdf, records)` (`:162-198`). `reconcile` calls `resolve_snapshot`, checks the pinned source SHA-256, then compares accepted aggregate records to workbook cells; the PDF check hashes its caller-provided file before comparing national context totals. Keep old script as a thin compatibility entry point. Installed CLI must take explicit workbook/PDF and accepted aggregate run paths; checkout `.cache` defaults (`:199-206`) are not installed resource paths.

**Acquisition custody — reuse without copying ZIPs.** `acquisition.resolve_snapshot(snapshot_id, output_root)` (`:291-324`) verifies current success, URL and pinned hash, matching immutable attempt receipt, raw ZIP hash and ZIP safety offline. `source_inventory.inventory_all(output_root)` (`:272-281`) returns eight current packages in approved order and checks the latest attempt. Use this seam on publication build **and access**; compare each resolved receipt ID, URL and SHA-256 with the sealed publication dependencies. A ZIP path alone does not establish a successful current acquisition.

**CLI — `brujula/cli.py` (modify).** `main(argv=None)` (`:35-72`) uses argparse subcommands, explicit `Path` arguments, `resolve_current` on report access and exit 1 on blocked/errors. Keep `build`/`demo` for synthetic v1 and add clearly named installed real-data acceptance/replay and publication commands with separate `--source-root`, `--output-root`, `--audit-dir`, `--workbook`, `--pdf` and R configuration where applicable. The existing `verify()` (`:15-32`) requires `CHECKOUT_ROOT` and is not an installed acceptance gate. Record resolved paths, package/R/PDF versions, catalog/source hashes and numerical/public digests in receipts; missing resources or capabilities fail closed with a receipt.

**Oracle and installed tests.** `scripts/enoe_survey_oracle.R` is the exact R content analog for proposed `brujula/oracle/enoe_survey_oracle.R`; only its package location changes. `tests/test_analysis_v2.py:153-181,235-255,273-316` covers accepted-content IDs, sanitized parent redaction and code/golden pin failures; `tests/test_acquisition.py:38-54,116-135,198-207` covers invalidation and offline receipt identity; `tests/test_cli.py:6-15` covers blocked access. Add focused installed-wheel tests for resource lookup outside checkout, missing resource/receipt/R/PDF failures, source/output/audit separation and offline replay. On **Windows and Ubuntu**, install a fresh wheel and run fixture/resource/failure checks plus a small offline Spanish PDF render. Run the **full real numerical acceptance and unchanged replay** from the installed package in the designated local research environment after the implementation/resource refactor; cross-platform fixture/PDF evidence does not duplicate the full eight-snapshot R workload on both OSes (`04-RUNTIME-PATH-MAP.md:99-107`).

## Shared Patterns

**Public data boundary.** `research_contract.py:232-273` is the Phase 2 public projection gate; `analysis_v2.py:438-461` adds Phase 3 complementary suppression, and `findings_v2.validate_analysis_packet` (`:208-262`) validates the complete analytical handoff. Every renderer/exporter consumes only that validated packet's sanitized `record_index`, profiles, claims and comparisons. Suppressed records keep null `value`, weighted denominator/support total, SE, CV and CI. `research_contract.py:198-201` rejects leaked suppressed diagnostics. Never reconstruct a direct null measure from complementary aggregates; compare only through the accepted Phase 3 ledger.

**Fail-closed paths and integrity.** `pipeline.py:106-112,130-136` validates run IDs and resolved manifest paths; `report.py:81-84` derives opaque chart filenames. Apply those to all v2 outputs. Validate the complete artifact inventory and acquisitions in addition to existing hash checks.

**Error and receipt discipline.** `pipeline.py:152-184` records failure without overwriting sealed receipt, and `acquisition.py:213-279` invalidates current on a failed attempt. Keep `status` (public), `build_status` (execution) and acquisition status distinct. Public errors must not expose local paths or diagnostic payloads; `acquisition.py:196-198` redacts output root.

**No authentication pattern applies.** This is an offline CLI and static artifact workflow; there is no controller, route, middleware, user session or network reader in Phase 4.

## No Analog Found

| Planned capability | Reason / planning action |
|---|---|
| Restricted WeasyPrint URL fetcher and fatal missing-asset policy | No existing PDF code or fetcher. Use the documented Phase 4 research design, then verify local-only behavior. |
| One typed editorial section/figure/claim model with HTML/Markdown/PDF parity | V1 render strings are independent and synthetic. Establish the model from accepted Phase 3 claims and `04-EDITORIAL-SPEC.md`. |
| Phase 4 replay equality contract | Phase 2 numeric and Phase 3 packet content digests exist, but no run-level v2 replay receipt separates accepted content from timestamps/PDF bytes. Specify its exact fields and version using those digests. |
| V2 publication/manifest schemas and full eight-snapshot resolver | Existing schemas/state machine are v1 and verify one raw JSON. Define a separate v2 contract with exact dependency and artifact inventory. |
| Installed R executable discovery and restricted PDF fetcher | `_execute_r` currently has checkout defaults; no project-owned installed R resolver or PDF URL policy exists. Define these from the runtime map and test failures. |

## Upstream Readback Gate

Phase 2 numerical acceptance is complete. Current Phase 3 source defines the `v2r:`, `v2c:` and `v2k:` keys and `build_analysis_packet`/`validate_analysis_packet` interfaces, but final claim/packet tests and review are still executing. Before executable Phase 4 planning, inspect the **accepted** Phase 3 packet, hash-only reference, claim registry, supported comparisons, coverage and evidence refs; confirm every output binds to its sanitized record and exact source/method version. The installed numerical path refactor also changes hash identity and requires fresh installed acceptance/replay, followed by review/rebinding of dependent Phase 3 accepted references. Do not treat old hash-only pins as proof for a new implementation or approve Phase 4 on the basis of this pattern map.

## Metadata

**Analog search scope:** the prior v1 analogs plus `brujula/{analysis_v2,comparisons_v2,claims_v2,findings_v2,source_inventory}.py`, `contracts/analysis-v2.schema.json`, `scripts/{accept_enoe_estimates,official_reconciliation}.py`, `tests/{test_analysis_v2,test_comparisons_v2,test_claims_v2}.py`, `04-PACKAGING-READBACK.md` and `04-RUNTIME-PATH-MAP.md`. Phase 3 source may still change during review.
**Files classified:** 18 proposed/modified files. **With analog:** 18/18 by role or integration seam; the new capabilities above lack direct implementations.
**Pattern extraction date:** 2026-09-23.
