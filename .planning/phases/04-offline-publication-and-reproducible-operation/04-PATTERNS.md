# Phase 4: Offline Publication and Reproducible Operation - Pattern Map

**Mapped:** 2026-09-22
**Scope:** preparatory map only; Phase 2 numerical acceptance and Phase 3 claim/comparison packets are pending.
**Source edits:** none.

## File Classification

The paths marked * are proposed module boundaries from `04-RESEARCH.md`, not locked filenames or accepted upstream APIs. Confirm them after reading the accepted Phase 2/3 packets. Existing files are marked `modify`.

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

No Python API filename, argument list, packet field beyond `docs/CONTRACT-V2.md`, or canonical numerical digest format is accepted by this map. The output artifact names (HTML, Markdown, PDF, SVG/PNG, CSV/Parquet/DuckDB, receipt, manifest, current) are locked in `04-CONTEXT.md` and `04-EDITORIAL-SPEC.md`.

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

The ten-key `GRAIN` at `research_contract.py:17-20` and duplicate-grain check at `:135-140` are the stable identity inputs; v2 records have no `id`. A versioned, length-safe canonical hash key for exports/figures/claims is **new code**, not an existing function. Define exact key bytes and a collision check after upstream packet readback. Use `public_research_projection` and `validate_public_research_v2` as the release gate. The public `reason` code mapping at `:32-46` must be preserved; internal free-form reason text cannot enter publication. The Phase 3 claim registry and comparison interface still require actual accepted readback.

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

No existing function computes the proposed canonical `numerical_content_sha256`; define and version the exact canonical record/claim/comparison serialization after accepted upstream packet readback. Separate numerical equality from run ID, timestamps and PDF/container bytes. V1 `make_comparisons` (`pipeline.py:65-79`) is observation-ID based and cannot be the Phase 3 validated comparison gate.

### `brujula/cli.py`, `brujula/resources.py`, `pyproject.toml` — integration

`cli.py:35-72` is the exact argparse pattern: explicit `--input`, `--output`, `--as-of` on build; `report --format` calls `resolve_current` before printing a path; blocked/error exits 1. Add clearly named real v2 build/replay/report commands with explicit source/output roots while keeping existing v1 `build`/`demo` fixture behavior. `tests/test_cli.py:6-15` covers blocked and missing-manifest report access.

`resources.py:9-29` checks packaged paths before checkout paths and raises `FileNotFoundError` for missing authored resources. `pyproject.toml:11-31` pins dependencies, declares the CLI, and includes JSON contract/catalog/fixture package data. Extend these only for actually shipped v2 schema/assets and WeasyPrint runtime setup; the existing resolver is not a general user-path sanitizer or a PDF URL authorization policy.

## Shared Patterns

**Public data boundary.** `research_contract.py:232-273` is the only existing v2 projection gate. Every renderer/exporter input must validate as public v2 and bind accepted Phase 3 evidence. Suppressed records keep null `value`, weighted denominator/support total, SE, CV and CI. `research_contract.py:198-201` rejects leaked suppressed diagnostics. Never reconstruct a direct null measure from complementary aggregates; compare only through the accepted Phase 3 contract.

**Fail-closed paths and integrity.** `pipeline.py:106-112,130-136` validates run IDs and resolved manifest paths; `report.py:81-84` derives opaque chart filenames. Apply those to all v2 outputs. Validate the complete artifact inventory and acquisitions in addition to existing hash checks.

**Error and receipt discipline.** `pipeline.py:152-184` records failure without overwriting sealed receipt, and `acquisition.py:213-279` invalidates current on a failed attempt. Keep `status` (public), `build_status` (execution) and acquisition status distinct. Public errors must not expose local paths or diagnostic payloads; `acquisition.py:196-198` redacts output root.

**No authentication pattern applies.** This is an offline CLI and static artifact workflow; there is no controller, route, middleware, user session or network reader in Phase 4.

## No Analog Found

| Planned capability | Reason / planning action |
|---|---|
| Restricted WeasyPrint URL fetcher and fatal missing-asset policy | No existing PDF code or fetcher. Use the documented Phase 4 research design, then verify local-only behavior. |
| One typed editorial section/figure/claim model with HTML/Markdown/PDF parity | V1 render strings are independent and synthetic. Establish the model from accepted Phase 3 claims and `04-EDITORIAL-SPEC.md`. |
| V2 stable record key and numerical replay digest | V1 observation IDs and artifact byte determinism are different contracts. Specify canonical bytes/key version first. |
| V2 publication/manifest schemas and full eight-snapshot resolver | Existing schemas/state machine are v1 and verify one raw JSON. Define a separate v2 contract with exact dependency and artifact inventory. |

## Upstream Readback Gate

Phase 2 currently has active adapter/metrics code, while Phase 3 is planned. Before turning this map into executable Phase 4 plans, inspect **accepted** Phase 2 public numerical packet, validation/precision results and all eight snapshot receipts; then inspect **accepted** Phase 3 claim registry, supported comparison keys, coverage and evidence references. Confirm how record grain, method/version, source snapshot, precision, claim/figure binding and comparison IDs are actually represented. Adapt module names and schemas to those facts. This map does not infer signatures for unaccepted Phase 2/3 work.

## Metadata

**Analog search scope:** `brujula/{report,export,warehouse,pipeline,runlock,cli,resources,acquisition,research_contract}.py`, `tests/{test_report,test_export,test_pipeline,test_runlock,test_cli,test_acquisition}.py`, `pyproject.toml`, and the Phase 4 context/research/editorial documents.
**Files classified:** 12 proposed/modified files. **With analog:** 12/12 by role or integration seam; four new capabilities above have no direct existing implementation.
**Pattern extraction date:** 2026-09-22.
