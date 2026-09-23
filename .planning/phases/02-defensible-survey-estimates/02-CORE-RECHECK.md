---
phase: 02-defensible-survey-estimates
reviewed: 2026-09-22
scope: original-core-findings-at-c1f8006
findings_rechecked: 3
resolved: 2
partial: 1
status: issues_found
---

# Phase 2 Core Fix Recheck

The three findings in `02-CORE-REVIEW.md` were rechecked on stable main `c1f8006`. This recheck covers the core fixes only; Plan 02-03 acceptance changes are under separate review.

## CR-01 — Resolved: conflicting geography aliases

**File:** `brujula/metrics.py:80-93`

The selector normalizes both aliases before constructing the domain mask and raises on a conflict. On a loaded disposable frame, `entity=2` and `geography="02"` produced the same vector as `entity=2`; `2` versus `3`, `0`, `33`, and `True` all raised `ValueError`. The conflicting case is rejected before a domain state is cached. This is direct functional verification of the selector semantics; no separate human approval is needed.

## WR-01 — Partial: mapping replacement is blocked, but writable replacement arrays still stale the cache

**File:** `brujula/enoe_adapter.py:52-57`; `brujula/metrics.py:96-123,176-185`

The loaded frame's `columns` and nested `inventory` are immutable mappings, and its official arrays are read-only. `dataclasses.replace` creates a new, empty per-frame cache, so the originally reported mapping-replacement path is fixed. Internal/public/audit JSON serialization tests pass.

**Residual WARNING:** `Frame.__post_init__` copies the mapping but neither copies nor freezes each supplied NumPy array. A supported transformed frame created with `replace(frame, columns={..., "clase2": np.array([2,2,2])})` retains a writable alias. After `occupied_total` primes the cache at `[0,0,0]`, changing that caller-owned array to `[1,1,1]` leaves the next `occupied_total` result at `[0,0,0]`. This repeats the stale-mask failure for a transformed frame, while the current column data says all three are occupied.

**Fix:** In `Frame.__post_init__`, copy each supplied column array into frame-owned storage and mark the copies read-only before wrapping the column mapping. Add a regression that mutates the original input array after caching a metric, or proves mutation is rejected, and confirms the metric result remains consistent with the frame's visible columns. Treat NumPy read-only flags as a local invariant, not a security boundary.

## WR-02 — Resolved for the reported forms: person-row output control

**File:** `tests/phase2_prohibitions_01.py:34-129,132-191`; `tests/phase2_prohibitions_01.test.cjs:27-44`

The scanner now checks prefixed and multiline JSON, Python dict representation, CSV with a data row, tracked data artifacts, and files inside a disposable staged ZIP/report. The seven Node controls passed: clean P1/P2 and five separate synthetic person-row negative controls. Each bad control exited nonzero with the expected leak assertion. This verifies the forms named in the original warning.

## Checks

- `.venv/Scripts/python.exe -m pytest tests/test_enoe_adapter.py tests/test_enoe_metrics.py tests/test_estimates.py -q`: 49 passed.
- `node --test tests/phase2_prohibitions_01.test.cjs`: 7 passed.
- Disposable selector and `dataclasses.replace` probes reproduced the outcomes above without modifying source or tracked fixtures.
