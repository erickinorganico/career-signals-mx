---
phase: 02-defensible-survey-estimates
reviewed: 2026-09-23T06:32:16Z
depth: standard
scope: partial-upstream-02-01-and-02-02
files_reviewed: 21
files_reviewed_list:
  - brujula/enoe_adapter.py
  - brujula/metrics.py
  - brujula/survey.py
  - brujula/estimates.py
  - brujula/populations.py
  - data/catalog/enoe-metrics.json
  - tests/test_enoe_adapter.py
  - tests/test_enoe_metrics.py
  - tests/test_survey.py
  - tests/test_estimates.py
  - tests/test_population_rules.py
  - tests/phase2_prohibitions_01.py
  - tests/phase2_prohibitions_01.test.cjs
  - tests/fixtures/phase2_prohibitions/01.clean.json
  - tests/fixtures/phase2_prohibitions/01-p1.bad.json
  - tests/fixtures/phase2_prohibitions/01-p2.bad.json
  - tests/phase2_prohibitions_02.py
  - tests/phase2_prohibitions_02.test.cjs
  - tests/fixtures/phase2_prohibitions/02.clean.json
  - tests/fixtures/phase2_prohibitions/02-p3.bad.json
  - tests/fixtures/phase2_prohibitions/02-p4.bad.json
findings:
  critical: 1
  warning: 2
  info: 0
  total: 3
status: issues_found
---

# Phase 2: Core Code Review Report

**Reviewed:** 2026-09-23T06:32:16Z
**Depth:** standard
**Scope:** partial upstream review of Plans 02-01 and 02-02; excludes active Plan 02-03 scripts, oracle, official reconciliation, and final numerical acceptance.
**Status:** issues_found

## Summary

The complete-frame adapter, 23 metric vectors, survey estimator, v2 assembly, and existing focused controls were read against the Phase 2 contracts and plans. One accepted selector combination returns a different geography than requested. Two other defects leave stale derived masks possible and weaken the person-row prohibition control. These findings do not judge the still-running eight-quarter R/official acceptance or authorize publication.

## Narrative Findings (AI reviewer)

## Critical Issues

### CR-01 — Conflicting geography selectors silently choose one geography (BLOCKER)

**File:** `brujula/metrics.py:80-86`
**Issue:** `_domain` permits both `entity` and `geography`, but `selector.get("entity", selector.get("geography"))` ignores `geography` whenever `entity` is present. A real loaded synthetic frame with `{"entity": 2, "geography": 3}` returned the entity-2 mask `[True, True, False]` and `domain_n=2`, even though the same request also explicitly named entity 3. `metric_vectors` can therefore return a valid-looking estimate for a contradictory requested domain. The v2 assembler currently supplies only `entity`, so this defect is at the exported metric API boundary.

**Fix:** Reject selectors containing both aliases unless their normalized official entity codes agree; preferably accept only one canonical selector. Add a conflicting-alias regression covering numeric and zero-padded forms before any vector is constructed.

## Warnings

### WR-01 — Frame mutation leaves cached metric masks stale (WARNING)

**File:** `brujula/enoe_adapter.py:37-50`; `brujula/metrics.py:90-117,170-179`
**Issue:** `Frame` is frozen and its NumPy arrays are marked read-only, but `columns` and `inventory` are writable dictionaries. Metric state is cached without a version of those mappings. After computing `occupied_total`, replacing `frame.columns["clase2"]` with `[2,2,2]` left the next `occupied_total` vector at `[1,0,1]`. The returned vector disagreed with the frame's current data. This is an in-process robustness defect for callers that transform or reuse a frame, and the shallow `frozen=True` contract makes that easy to miss.

**Fix:** Expose an immutable column mapping and immutable custody metadata (or a read-only frame interface), and keep mutable caches private. If controlled frame transformation is required, construct a new frame with an empty cache and revalidate provenance.

### WR-02 — Person-row prohibition check misses common logged and packaged forms (WARNING)

**File:** `tests/phase2_prohibitions_01.py:65-79`
**Issue:** `_stream_has_person` recognizes only a whole log line that parses as JSON. A logger prefix (`INFO person=...`), Python dictionary representation, multiline JSON, or CSV row/header in stdout or stderr passes the check. The tracked-artifact scan also searches only Git-tracked `data`/`artifacts` files with `.json`, `.csv`, or `.zip` suffixes, so an untracked packaged report or other publication artifact is not inspected. The current bad fixture injects exactly the one-line JSON shape that the scanner detects, which does not establish the broader no-person-row prohibition stated in Plan 02-01.

**Fix:** Capture and inspect the actual serialization formats emitted by each Phase 2 entry point, including generated package/report outputs in a disposable staging directory. Add negative controls for prefixed logger text, multiline JSON, CSV, and an untracked packaged artifact; require each to make the named control fail.

---

_Reviewed: 2026-09-23T06:32:16Z_
_Reviewer: the agent (gsd-code-reviewer)_
_Depth: standard, partial upstream scope_
