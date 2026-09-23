# Installed numerical migration preflight

2026-09-23. Read-only preparation for 04-02, not installed numerical acceptance.

The bounded native review identified checkout defaults in `scripts/accept_enoe_estimates.py`: `ROOT`, catalog/golden/oracle lookup, R executable/library, workbook/PDF and historical semantic-baseline cache, subprocess cwd and the old eleven-path implementation inventory. `scripts/official_reconciliation.py` also has checkout CLI defaults. Move actual implementations into `brujula`, retain thin script compatibility, and make external inputs explicit before the expensive real run.

`brujula/analysis_v2.py` currently verifies old `scripts/*` names relative to checkout ROOT and reads golden public pins from `data/fixtures`. Producer and consumer must share the exact fixed package-owned eleven-file inventory in 04-02, with canonical LF source hashes. A passed old receipt must reject after relocation. Installed resource absence must fail without finding a checkout fallback. The small synthetic tests may replace their own independent fixture authority; production guards cannot be patched out for the installed real proof.

## Golden bytes and stable content

The accepted golden JSON has CRLF in the current Windows working copy. Verified on 2026-09-23:

- Raw-byte SHA-256: `ef41c327b3e01dbee92ac92f1bfacaec1a17a0ad2978e1f7349acb684fe55071`.
- Canonical LF SHA-256: `86bf44b6ab70b78c3b40f03c7366188912d0e7d4de81e87a6b4773b7e7f6764d`.

Do not mistake platform line-ending normalization for a new approved golden or silently permit a changed JSON value. Use and document the chosen canonical authoring digest consistently for independent golden verification; artifact inventories still hash actual emitted bytes. No golden regeneration is authorized for ordinary acceptance/replay.

`estimates._method_version` depends on the adapter's canonical source hash and metric manifest digest. Both remain unchanged in this relocation, so exact public records and per-snapshot raw-row numerical digests should remain identical. The existing canonical-content convention additionally excludes method-version copies and acquisition clocks, and sorts records/catalogs; preserve it. Compare implementation/resource/tool identity separately from numerical content. Reference rebinding follows fresh installed acceptance, unchanged replay and explicit pre-rebind `trusted_reference` rejection, exactly as the plan specifies.

## Failure boundary

The existing `run_attempt` marks current BLOCKED before operation, catches ordinary operation errors and creates an exclusive immutable attempt receipt before final current. Preserve this. Its receipt currently has clocks/status/reason/numeric digest; the moved service needs the additional actual package/resource/source/benchmark/R identities required by 04-02.

CLI parsing and audit-directory creation currently precede that boundary. Once an explicit writable audit root is known, keep resource/R/input preflight inside the receipt boundary. An unwritable receipt destination cannot physically promise a receipt: return an explicit error and never claim successful acceptance or revive historical success. Missing arguments should remain clear CLI errors, not a synthetic fallback. Negative tests use disposable roots; preserve the eight accepted acquisition currents in `artifacts/enoe`.

## Verification sequence

1. Implement explicit package services, source/resource inventory alignment and portable positive/negative controls.
2. Build/install the wheel outside checkout and validate cheap prerequisites before the eight-ZIP/R workload.
3. Run fresh frozen numerical acceptance and unchanged offline replay; require the existing numeric digest and exact rows.
4. Prove guarded public indexing passes while the old independent analysis reference rejects the candidate for exactly `trusted_reference`.
5. Rebind only the versioned hash-only analysis reference, preserve historical receipts, then rebuild/reinstall and prove production assembly plus persisted JSON validation passes.

The native review made no source edits or acceptance runs. This preflight supplements, and does not change, 04-02-PLAN.md.
