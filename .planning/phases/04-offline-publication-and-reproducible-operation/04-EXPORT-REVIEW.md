---
phase: 04-offline-publication-and-reproducible-operation
reviewed: 2026-09-23T20:16:27Z
depth: deep
files_reviewed: 7
files_reviewed_list:
  - brujula/publication_v2.py
  - brujula/export_v2.py
  - brujula/resources.py
  - contracts/publication-v2.schema.json
  - tests/test_publication_v2.py
  - tests/test_export_v2.py
  - tests/test_installed_runtime.py
findings:
  critical: 2
  warning: 1
  info: 0
  total: 3
status: issues_found
---

# Phase 4 Plan 03: Export Boundary Review

**Depth:** deep  
**Status:** issues_found

## Summary

The public model revalidates the independently pinned Phase 3 packet before export, and the current real packet contains 6,739 records, 23 metrics, 4,209 comparisons and 38 claims. The reviewed implementation still has two blocking gaps in the export contract and reproducible verification, plus a figure-link selection error. This review covers Plan 03 only; it does not establish Phase 4 or release acceptance.

## Narrative Findings (AI reviewer)

### BLOCKER CR-01: Clean runners cannot execute either new boundary test module

**File:** `tests/test_publication_v2.py:12-17`, `tests/test_export_v2.py:15-20`  
**Issue:** Both module fixtures unconditionally open `.cache/research/phase3-analysis/analysis.json`. `git check-ignore -v` confirms `.gitignore:2` excludes that path. A clean checkout lacks the file, so every new Plan 03 test errors with `FileNotFoundError` before exercising the boundary. The existing `tests/test_analysis_integration.py:19-28` already builds a compact independently pinned synthetic packet, but neither new module uses it. This leaves the required isolated null, suppression, join and interrupted-export checks absent from reproducible CI.  
**Evidence:** The local packet exists, while `git check-ignore -v .cache/research/phase3-analysis/analysis.json` returns `.gitignore:2:.cache/`. All four publication tests and both model-dependent export tests use the unconditional fixtures; only the ten `_csv_value` parameter cases can run without the cache.  
**Fix:** Move the boundary and negative checks to a committed synthetic fixture that supplies valid Phase 3 pins; keep the real packet readback as an optional integration test with an explicit skip when the cache is absent. Run the focused modules in a clean worktree to prove they exercise assertions rather than erroring or all skipping.

### BLOCKER CR-02: Comparison exports irreversibly discard comparability signatures

**File:** `brujula/export_v2.py:32-38`, `brujula/export_v2.py:78-85`  
**Issue:** Every accepted comparison contains `signature_previous` and `signature_current`, but `COMPARISON_COLUMNS` and `_table_data` omit both from CSV, Parquet and DuckDB. A direct field comparison against the current packet shows these are the only two non-evidence comparison fields lost. Their nested values include edition review, geography concept, metric numerator and denominator, and suppression-policy version; those cannot be reconstructed from the exported endpoint rows. Thus consumers cannot audit the source, method and concept basis of a comparison from the promised joined aggregate exports. The current test only checks the comparison row count.  
**Evidence:** The current packet comparison has 17 top-level fields; the emitted table maps 14 scalar/list fields, plus `evidence_refs` in the separate evidence table. `set(input_comparison) - set(COMPARISON_COLUMNS) - {'evidence_refs'}` yields exactly `{'signature_previous', 'signature_current'}`.  
**Fix:** Export both signatures in a lossless, documented form (for example canonical JSON text columns or a typed comparison-signature table keyed by comparison ID and endpoint), then assert field-level parity against the accepted packet in all three formats.

### WARNING WR-01: Figure links include blocked comparisons

**File:** `brujula/publication_v2.py:31-34`  
**Issue:** Figure membership tests only whether both endpoint records are selected; it does not require `comparable` or an accepted `REVIEW` status. Against the current packet, `figure:eight-quarter-trends` links 99 comparisons, including three `BLOCKED` rows with `current_unsupported` or `previous_unsupported`. The link table therefore advertises unsupported changes to downstream figure consumers, even though those comparisons contain null deltas.  
**Evidence:** Calling `_figure_links` on the persisted accepted packet yields status counts `REVIEW: 96, BLOCKED: 3` for `figure:eight-quarter-trends`; all three blocked rows have unsupported-endpoint reasons.  
**Fix:** Select only comparisons whose canonical status and comparability permit an interpreted change, and add a test asserting that no figure comparison link targets a blocked comparison. Keep unsupported endpoint records separately so the report can show unavailable cells and their reasons.

---

_Reviewer: gsd-code-reviewer (scoped independent Plan 03 review)_
