---
phase: 04-offline-publication-and-reproducible-operation
reviewed: 2026-09-24T01:59:00Z
depth: deep
files_reviewed: 6
files_reviewed_list:
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

# Plan 04-06 integrated code review

This is a bounded review of the Plan 04-06 CI/helper and executable edge/prohibition controls. The control source is frozen at `ad73a72` and the CI/helper source at `4dda477`. The Windows/Ubuntu CI matrix, pinned PDF dependency set, outside-checkout wheel install, reviewed native prerequisites, offline font/PDF probe and aggregate-only runtime receipt are present in the reviewed source. This code verdict is not a hosted CI result.

## Narrative Findings (AI reviewer)

No open implementation or test-reliability finding remains in the reviewed snapshot. The five adversarial findings below are retained with their closure evidence. Exact SHA-256 of the reviewed 04-06 files: `verify.yml` `a70a9c4a93a0aba393a3122886b8a47fbceaa52a9c5979c0f8b11e65329e07b2`; `requirements-pdf.txt` `b03f2b2a61c0c60a1ec5ef061c95dcb3e372fa1b6c78d68ddcd052b78a953450`; `check_installed_runtime.py` `4b31fa22fd11db43a2d017967a291a236e9e57bea17d511c364cbcd0ce326883`; `phase4_prohibitions.py` `c749fc7b39acf6f46074cfb06084b6f51c4bcaee149032f82528d876bd171f45`; `phase4_prohibitions.test.cjs` `bce21ca479248c7602e17d2c8767ef471381c61b0d90dcc47f20f652ba8616cc`; `test_phase4_edge_acceptance.py` `0e3025464120c6ea62ca7136d5d8d117391936d4b4324e723dddc078c715b3e7`.

## Resolved findings

### CR-01 · BLOCKER · RESOLVED · A projected suppression canary was disconnected from the rendered subject

**Files:** `tests/phase4_prohibitions.py:69-99`, `tests/test_phase4_edge_acceptance.py:305-325`.

The initial implementation rendered a different pinned model. At `ad73a72`, `_canary_model` injects nested diagnostic canaries into an internal synthetic input, projects it to the public record, feeds that same projection through packet and publication model validation, then `_suppressed` renders and exports that model and verifies the selected null record in text, PDF, SVG/PNG metadata, CSV, Parquet and DuckDB. The bad mutation on that model is rejected. The focused PUB-05 boundary and all four clean Node controls pass.

### CR-02 · BLOCKER · RESOLVED · Stale-current control bypassed sealed authority

**Files:** `tests/phase4_prohibitions.py:206-250`, `tests/test_phase4_edge_acceptance.py:456-458`.

The current disposable control builds a sealed fixture and calls the unpatched `resolve_publication_current`/`_verify_sealed`. It rejects a changed artifact, changed required source dependency, and failed required acquisition through a live source-service double, then resolves the unchanged seal again. The separate actual installed copied-source experiment records failed acquisition attempt `20260924T002741769026Z-1ee9bcb4edf2`, blocked current access and unchanged original source/audit/bundle anchors. This distinguishes the synthetic service seam from the full acquisition proof.

### CR-03 · BLOCKER · RESOLVED · Unknown bad prohibition fixture yielded a vacuous green Node run

**File:** `tests/phase4_prohibitions.test.cjs:14-17`.

The original unknown `.bad.json` selector exited 0 with zero cases. It now throws unless exactly one known case matches. I independently reran the known and unknown bad selectors: each exits 1; the four clean Node controls pass.

### WR-01 · WARNING · RESOLVED · Mapped OPS edge checks did not exercise named faults

**File:** `tests/test_phase4_edge_acceptance.py:411-458`.

At `ad73a72`, OPS-02 ordering injects distinct source, real PDF, export, receipt, manifest, pointer and final-index faults and checks blocked current plus retained historical seal. OPS-02 concurrency covers abrupt builder interruption, lock refusal and recovered failed receipt. OPS-03 ordering/idempotency use the real sealed resolver in the disposable source fixture. Three independently selected OPS checks passed, and the executor reports the complete 46/46 mapping plus registry test passing.

### WR-02 · WARNING · RESOLVED · Installed helper froze resource cardinality

**File:** `scripts/check_installed_runtime.py:74`.

The helper now derives resource membership from `authored_resource_digests()`, checks exact installed Python/resource bytes against the built wheel, and records the observed count and aggregate identity hash without a fixed cardinality. The reviewed Windows workflow points Fontconfig at the existing bundled font directory, verifies it exists and escapes the path in XML. The corrected source is frozen at `4dda477` and its exact hashes are above.

## Evidence boundary

The nonempty synthetic figure/claim test bypasses whole-model validation only for its isolated renderer/exporter fixture. A separate accepted-model installed proof at `.cache/research/phase4-real-permutation/readback.json` (SHA-256 `68a65608a03483a0cb5c013c59cd7a88c114b4f53a57326ee2aeaca3d1111c2c`) validates the production model without patched functions or reference override, reverses 6,739 record insertions, and finds identical nine plot pixels/point manifests and 22 CSV/Parquet/DuckDB exports. Its figure-record, figure-comparison, figure-claim, figure-source and claim-record joins are nonempty (249/133/3/16/65 rows). This is actual local output evidence, separate from hosted Windows/Ubuntu CI. My focused rechecks passed one PUB-05 canary edge, five amended PUB pairs, three OPS pairs, four clean Node cases and known/unknown bad Node failures. The executor's final required 04-06 focused suite passed 108/108, full `brujula verify` passed 592 tests, all Node controls passed 30/30, and the installed helper positive/current-wheel Python-byte corruption negative passed. These are reported executor results, not independently rerun here. The public evidence correctly records `LOCAL_PASS_PENDING_CI`; hosted Windows/Ubuntu readback and final GSD gates remain pending. No source file was edited by this reviewer.

_Reviewer: independent Plan 04-06 code/security review._
