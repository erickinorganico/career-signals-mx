# Phase 5 independent plan review — final revision

## VERIFICATION PASSED

**Phase:** Independent Audit and v1.0.0 Release  
**Plans verified:** 3  
**Status:** No remaining plan blocker or warning. This verifies that the plans can achieve the goal if their stated gates pass; it does not certify Phase 4 visual approval, Phase 5 execution, or publication.

| Requirement | Covering plans | Planned outcome |
|---|---|---|
| REL-01 | 05-01 | Current bilingual guides, citation and historical labels checked against installed interfaces. |
| REL-02 | 05-01, 05-02 | Exact-target Windows/Ubuntu installed receipts, separate real numerical/replay evidence and independent conceptual/visual review. |
| REL-03 | 05-02 | Frozen asset/member allowlist, full tracked/package/archive scans, source and license decisions. |
| REL-04 | 05-03 | Draft byte readback, then authorized publication and anonymous public asset readback. |
| GSD-01 | 05-02, 05-03 | All-requirement trace receipt, independent phase verification, code/security review, UAT and milestone audit before administrative closure. |

| Plan | Tasks | Files modified | Wave | Check |
|---|---:|---:|---:|---|
| 05-01 | 2 | 13 | 1 | Complete; Phase 4 acceptance is an entry gate. |
| 05-02 | 2 | 4 | 2 | Complete; depends on 05-01. |
| 05-03 | 3 | 5 | 3 | Complete; depends on 05-02. |

All seven tasks have Files, Action, Verify and Done; `verify.plan-structure` reports valid with no warnings. Each task has an automated verification command. The new `scripts/verify_release.py` and its negative-control tests are owned by 05-01 task 1 and verified there; its host, review, inventory, remote and trace checks have distinct responsibilities. The trace receipt is assigned to 05-03 task 3. `05-VALIDATION.md` exists. The manual `05-EDGE-COVERAGE.md` resolves the classifier's five unclassified exact-language cases with positive and negative acceptance criteria. `05-RESEARCH.md` replaces its open questions with explicit planning decisions and leaves exact bytes and human visual approval as execution gates.

The dependency graph is acyclic. Key links connect reader docs to installed CLI, release inventory to the sealed Phase 4 manifest, and remote receipt to approved hashes. The target rule freezes code, wheel and payload at one SHA, records later evidence against that SHA without retargeting the tag, and requires payload equality before publication. This permits public readback inside Phase 5 before canonical Phase 5 verification, as REL-04 requires. The existing preview remains preliminary. No deferred app, paid inference, new source, third-party message or unapproved destination appears. Planned work stays in the research package, local evidence and authorized GitHub release tiers. Shared data IDs and hashes have compatible contracts across plans. `AGENTS.md` security, synthetic-label, precision, disclosure and local-first constraints are respected. `05-PATTERNS.md` identifies current repository analogs and the plans use the relevant CLI, Phase 4 receipt, docs checker and hosted installed-wheel workflow.

**Execution preflight:** Phase 4's pending human visual approval and independent verification status must be accepted before 05-01 begins. The successful technical checks alone do not close that gate. Then run the plans in wave order and enforce each stated receipt/readback gate before claiming a complete v1.0.0 release.
