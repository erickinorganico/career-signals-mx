---
phase: 01-official-sources-and-research-contract
fixed_at: 2026-09-23T04:05:23Z
review_path: .planning/phases/01-official-sources-and-research-contract/01-REVIEW.md
iteration: 1
findings_in_scope: 5
fixed: 5
skipped: 0
status: all_fixed
---

# Phase 1: Code Review Fix Report

**Fixed at:** 2026-09-23T04:05:23Z
**Source review:** `.planning/phases/01-official-sources-and-research-contract/01-REVIEW.md`
**Iteration:** 1

**Summary:** Five findings in scope; five fixed; none skipped. All five change validation or normalization logic and require human verification of the intended semantics before the phase proceeds.
The status label flags the fixer's syntax-only verification limit; it does not
create a new user-approval gate. The orchestrator's independent review and
affected/full tests can complete the verification.

## Fixed Issues

### CR-01: Claimed CV can contradict the standard error and estimate

**Status:** fixed: requires human verification
**Files modified:** `brujula/research_contract.py`, `tests/test_research_contract.py`, `docs/CONTRACT-V2.md`
**Commit:** `93355a2`
**Applied fix:** Compare declared CV with 100 × SE / visible value within 0.005 percentage points; apply grade thresholds to declared and calculated CV. Added contradiction, tolerance, and threshold regressions. Interval endpoint reconciliation with the declared CI method remains a Phase 2 numerical gate.

### CR-02: Impossible support counts can satisfy the release gate

**Status:** fixed: requires human verification
**Files modified:** `brujula/research_contract.py`, `tests/test_research_contract.py`, `docs/CONTRACT-V2.md`
**Commit:** `31aad41`
**Applied fix:** Domain PSUs cannot exceed observed n. A visible value requires positive contributing weighted support no greater than its weighted denominator. Added impossible PSU, missing/zero support, and excess support regressions.

### CR-03: Suppressed estimate leaks through public reason

**Status:** fixed: requires human verification
**Files modified:** `brujula/research_contract.py`, `contracts/research-v2-public.schema.json`, `tests/test_research_contract.py`, `docs/CONTRACT-V2.md`
**Commit:** `9b2d615`
**Applied fix:** Projection maps exact known internal reasons to controlled public codes and maps other internal text to a bounded status code. Public schema rejects arbitrary reason text. Added suppression sentinel and known-category regressions.

### CR-04: Nonfinite Decimal crashes the validator

**Status:** fixed: requires human verification
**Files modified:** `brujula/research_contract.py`, `tests/test_research_contract.py`, `docs/CONTRACT-V2.md`
**Commit:** `11a6fd5`
**Applied fix:** Validate JSON-native scalars before schema and semantic comparisons. Decimal, nonfinite floats, oversized integers, and cycles return deterministic failures. Added internal and public malformed-number regressions.

### WR-01: Focus-code helper rejects its normalized form

**Status:** fixed: requires human verification
**Files modified:** `brujula/source_inventory.py`, `tests/test_source_inventory.py`, `docs/CONTRACT-V2.md`
**Commit:** `0eec8c6`
**Applied fix:** Match zero-filled ASCII input against the three reviewed normalized focus codes in the verified coding catalog. Tests cover five- and six-digit forms for all three fields and reject unknown or malformed codes.

## Verification

`tests/test_research_contract.py tests/test_source_inventory.py`: 52 passed, 1 skipped in the isolated worktree. The skipped test expects an ignored local cache at the current working directory; a separate offline inventory read against the existing repository cache resolved all eight approved periods (2024-Q3 through 2026-Q2). Python syntax checks, public-schema JSON parse, and `git diff --check` passed. The full suite is delegated to the orchestrator after integration.

---

_Fixed: 2026-09-23T04:05:23Z_  
_Fixer: the agent (gsd-code-fixer)_  
_Iteration: 1_
