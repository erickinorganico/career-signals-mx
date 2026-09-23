---
phase: 04-offline-publication-and-reproducible-operation
plan: 02
reviewed: 2026-09-23T21:20:06Z
reviewed_commit: ab01b14
depth: deep
scope: pre-run installed source review
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
numerical_acceptance: pending
---

# Phase 4 Plan 02: Installed Migration Source Review

**Verdict:** No remaining source blocker found at `ab01b14` for starting the installed eight-ZIP acceptance and offline recomputation. This is a pre-run source review; no real numerical result, reference rebind, or Phase 4 release is certified here.

## Narrative Findings (AI reviewer)

No active finding remains in the reviewed source boundary. The checks below establish source behavior and inexpensive negative paths only. The installed wheel, eight approved ZIPs, independent R comparison, official workbook/PDF reconciliation, unchanged public rows, expected pre-rebind rejection and post-rebind packet validation remain separate required evidence.

## Verified source controls

- **Installed authority:** `CODE_FILES` is the fixed eleven-path package inventory. `_code_hashes` and `analysis_v2._check_codes` use LF-normalized bytes of the package modules and packaged oracle; the old `scripts/*` inventory is rejected. The golden public pin is independently checked against LF SHA-256 `86bf44b6ab70b78c3b40f03c7366188912d0e7d4de81e87a6b4773b7e7f6764d`. The numeric resource inventory excludes the downstream analysis reference, avoiding a rebind cycle, and is rehashed before PASS. Installed-resource paths must resolve inside the package when `CHECKOUT_ROOT` is absent.
- **Receipts and history:** Public `accept` and `replay` each call the receipt/current boundary once. `run_attempt` first invalidates current, writes a complete immutable per-attempt result including snapshot paths and digests, then promotes current. Operational failures with a valid audit root leave BLOCKED current and a distinct receipt. Existing output artifacts cannot be overwritten by another acceptance; replay writes to unique output and audit locations and compares newly computed full public payloads with the seal.
- **Root and external-input separation:** Source, output and audit ancestry is checked before an acceptance audit write. Replay also rejects audit overlap with the source, prior audit and sealed output before writing. The workbook and PDF are checked against approved SHA-256 values at entry and immediately before PASS. The Rscript executable hash, version, and explicit survey/jsonlite library identities are captured and checked again at the end; the oracle loads both named packages with `lib.loc`.
- **Clock-independent analytical identity:** `findings_v2._source_manifest` omits the raw public payload digest because it includes `acquired_at`; accepted raw payload hashes are still checked by `analysis_v2.index_public_estimates`. The analytical source manifest retains canonical public content, numeric digest, requested count, source and executing-code identity. The analysis and publication schemas match this projection. A focused synthetic test changed only `acquired_at` with a coherent raw digest and retained the same accepted packet; a bad raw digest was rejected.

## Focused verification

- Independent focused checks at the frozen source passed: **6 passed** for failed receipts, path separation, immutable outputs, golden authority and acquisition-clock identity; **2 passed** for the late audit-overlap and benchmark-drift guards. A disposable direct-call replay with a missing sealed file produced BLOCKED current and one immutable receipt.
- The executor reported **32 focused guards passed** after the late fixes. This review did not rerun the full test suite or process the real eight-ZIP input.

## Resolved during this review

The initial migrated source could validate saved public rows without recomputing them, accept caller-controlled or circular resource identity, reuse replay output paths, omit Rscript identity, and load `survey` or `jsonlite` outside the explicit library. Those known migration defects were closed before this review verdict. Additional review findings were also repaired before `ab01b14`: nested and historical audit roots could be written before rejection; complete immutable PASS manifests were unavailable for later replay; repeated acceptance could overwrite earlier output; external benchmark and numeric resources lacked final drift checks; the official CLI retained checkout-relative defaults; and the moved package contained an unused helper referring to an undefined checkout root.

---

_Reviewer: gsd-code-reviewer (independent pre-run Plan 02 source review)_
