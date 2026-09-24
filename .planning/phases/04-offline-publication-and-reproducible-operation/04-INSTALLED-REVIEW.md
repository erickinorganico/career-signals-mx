---
phase: 04-offline-publication-and-reproducible-operation
plan: 02
reviewed: 2026-09-23T21:20:06Z
reviewed_commit: ab01b14
depth: deep
scope: pre-run installed source review and post-run evidence readback
files_reviewed: 13
files_reviewed_list:
  - brujula/enoe_acceptance.py
  - brujula/official_reconciliation.py
  - brujula/analysis_v2.py
  - brujula/findings_v2.py
  - brujula/resources.py
  - brujula/oracle/enoe_survey_oracle.R
  - scripts/accept_enoe_estimates.py
  - scripts/official_reconciliation.py
  - scripts/enoe_survey_oracle.R
  - contracts/analysis-v2.schema.json
  - contracts/publication-v2.schema.json
  - tests/test_installed_acceptance.py
  - tests/test_analysis_integration.py
findings:
  critical: 0
  warning: 0
  info: 0
  total: 0
status: clean
numerical_acceptance: verified_from_immutable_receipts
---

# Phase 4 Plan 02: Installed Migration Source Review

**Verdict:** No remaining Plan 04-02 blocker found at source freeze `ab01b14`. Subsequent immutable installed acceptance, offline recomputation, hash-only reference rebind and persisted analysis evidence pass the independent readback below. This does not certify the whole Phase 4 publication or release.

## Narrative Findings (AI reviewer)

No active finding remains in the reviewed source boundary. The original checks established source behavior and inexpensive negative paths before the real run. The later installed evidence is assessed separately below; this reviewer did not rerun the eight-ZIP workload.

## Verified source controls

- **Installed authority:** `CODE_FILES` is the fixed eleven-path package inventory. `_code_hashes` and `analysis_v2._check_codes` use LF-normalized bytes of the package modules and packaged oracle; the old `scripts/*` inventory is rejected. The golden public pin is independently checked against LF SHA-256 `86bf44b6ab70b78c3b40f03c7366188912d0e7d4de81e87a6b4773b7e7f6764d`. The numeric resource inventory excludes the downstream analysis reference, avoiding a rebind cycle, and is rehashed before PASS. Installed-resource paths must resolve inside the package when `CHECKOUT_ROOT` is absent.
- **Receipts and history:** Public `accept` and `replay` each call the receipt/current boundary once. `run_attempt` first invalidates current, writes a complete immutable per-attempt result including snapshot paths and digests, then promotes current. Operational failures with a valid audit root leave BLOCKED current and a distinct receipt. Existing output artifacts cannot be overwritten by another acceptance; replay writes to unique output and audit locations and compares newly computed full public payloads with the seal.
- **Root and external-input separation:** Source, output and audit ancestry is checked before an acceptance audit write. Replay also rejects audit overlap with the source, prior audit and sealed output before writing. The workbook and PDF are checked against approved SHA-256 values at entry and immediately before PASS. The Rscript executable hash, version, and explicit survey/jsonlite library identities are captured and checked again at the end; the oracle loads both named packages with `lib.loc`.
- **Clock-independent analytical identity:** `findings_v2._source_manifest` omits the raw public payload digest because it includes `acquired_at`; accepted raw payload hashes are still checked by `analysis_v2.index_public_estimates`. The analytical source manifest retains canonical public content, numeric digest, requested count, source and executing-code identity. The analysis and publication schemas match this projection. A focused synthetic test changed only `acquired_at` with a coherent raw digest and retained the same accepted packet; a bad raw digest was rejected.

## Focused verification

- Independent focused checks at the frozen source passed: **6 passed** for failed receipts, path separation, immutable outputs, golden authority and acquisition-clock identity; **2 passed** for the late audit-overlap and benchmark-drift guards. A disposable direct-call replay with a missing sealed file produced BLOCKED current and one immutable receipt.
- The executor reported **32 focused guards passed** after the late fixes. This review did not rerun the full test suite or process the real eight-ZIP input.

## Independent installed evidence readback

- Source freeze `ab01b14` precedes the hash-only reference commit `244bfe2`. The latter changes only `data/fixtures/enoe-analysis-reference.json`. The preserved old copy has SHA-256 `2ecaf5808db2ec26c38f4d28138dc0af50ca191f5fb0fdb498240f650862a520`; the new file has SHA-256 `56ed548f90a2fc5bea44f051198ca75e414231690cb8509e09e34bf6069a4abe`. Parsed reference objects retain the same keys and differ only in `source_manifest_sha256`.
- The immutable acceptance receipt at `.cache/research/phase4-acceptance/audit/attempts/ee11f305-8113-4ff4-855c-bb8727fe89ab.json` hashes to `14f615e7e9dad2aef91e22e270f8d3184be58db10f5051abec15433f3e9d8b9f` and records PASS. The distinct immutable replay receipt at `.cache/research/phase4-replay/audit/attempts/b6ee089e-a08d-4919-ab7d-f1903d2201b4.json` hashes to `2f2821a3f39f22edd037ac0dc47430eb439a40eaa7488e6378d28abc762952fa` and records PASS with an eight-snapshot `recomputed_manifest`. Acceptance, replay and recomputed manifests agree on canonical numeric digest `8db575e9d664864d1513e3b9658bd9b060c4cb3bed8b51561f208adeb97b9a00`, all 11 code hashes, all seven numeric resource hashes and all eight source receipt identities. Every snapshot's numeric and public-v2 digest matches between acceptance and recomputation.
- Both manifests record PASS for 26 independent R oracle cases, four analytic-oracle cases, official workbook reconciliation and the 2026-Q2 PDF benchmark. `.cache/research/phase4-analysis/pre-rebind-proof.json` records 6,739 guarded indexed rows and production rejection with `trusted_reference` before rebind; its candidate remains 6,739 records, 4,209 comparisons and 38 claims.
- The installed analysis receipt at `.cache/research/phase4-analysis/receipt.json` records a module outside the checkout, nonsynthetic PASS, eight source IDs, zero validation errors, 6,739 records, 4,209 comparisons, 38 claims and three opening IDs. The persisted `.cache/research/phase4-analysis/analysis.json` hashes to `71d9fb7d6ceb20cff39a1a10f8428bcb239629e2e723b6e001816bd6d564bce3` and has content digest `15f5bdc0fb366f9b3ae75c1c0b096aed1f7b1f4e7f8b71b514f62133ea8dddca`. An independent current `validate_analysis_packet` readback returned zero errors. These checks establish Plan 04-02 installed acceptance and analysis continuity; report/PDF/export publication and phase-wide gates remain downstream.

## Resolved during this review

The initial migrated source could validate saved public rows without recomputing them, accept caller-controlled or circular resource identity, reuse replay output paths, omit Rscript identity, and load `survey` or `jsonlite` outside the explicit library. Those known migration defects were closed before this review verdict. Additional review findings were also repaired before `ab01b14`: nested and historical audit roots could be written before rejection; complete immutable PASS manifests were unavailable for later replay; repeated acceptance could overwrite earlier output; external benchmark and numeric resources lacked final drift checks; the official CLI retained checkout-relative defaults; and the moved package contained an unused helper referring to an undefined checkout root.

---

_Reviewer: gsd-code-reviewer (independent pre-run Plan 02 source review)_
