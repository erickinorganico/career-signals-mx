---
phase: 05-independent-audit-and-v1-0-0-release
plan: 02
subsystem: independent-content-review-and-release-custody
tags: [independent-review, source-terms, licenses, privacy, asset-inventory]
requires:
  - phase: 05-01
    provides: frozen 1.0.0 implementation and clean-host receipts
  - phase: 04-06
    provides: sealed real publication and numerical/operational acceptance
provides:
  - independent bounded review of sealed research content
  - exact-target five-asset release inventory and member-level redistribution review
affects: [05-03, phase-05-verification]
key-files:
  created:
    - docs/evidence/phase-05-independent-review.json
    - docs/evidence/phase-05-release-inventory.json
    - docs/evidence/phase-05-asset-review.json
    - THIRD_PARTY_NOTICES.md
  modified:
    - docs/research/DEPENDENCY-LICENSE-INVENTORY.md
requirements-completed: [REL-02, REL-03]
completed: 2026-09-28
---

# Phase 05 Plan 02: Independent audit and exact release custody

**The sealed real research received an independent content readback, and the frozen technical candidate received a closed, member-level privacy, terms and license review.** Approval here covers the reviewed content and candidate asset bytes; publication and anonymous access are Plan 05-03 observations.

## Executed evidence

- `docs/evidence/phase-05-independent-review.json` records a separate reviewer and independence basis, inspected artifact IDs, the sealed run `20260924T010247-81cfb71ea5f1` and manifest SHA-256 `38c3dfc21d816f32d7e4a21d7efd89418fc198fd80e94577783706f00d7fb023`. All 73 content hashes matched. The review inspected the 97-page PDF, nine SVG/PNG figure pairs, 22 public DuckDB tables, 6,739 public records, 4,209 comparisons and 38 claims. Its 3,565 suppressed records had null sensitive diagnostics. This was direct content inspection combined with unchanged accepted Phase 4 numerical and operational receipts, not a new R or official-source rerun.
- `docs/evidence/phase-05-release-inventory.json` binds five loose release assets, their exact names, sizes and SHA-256 values, the 1.0.0 target `611d2f553597439a0c58807dd6865914ff46281c`, and the sealed manifest. The archive includes 84 classified members; the wheel includes 63. The separate asset review checked all 147 nested members, the wheel RECORD, 73 research hashes, notices, attribution, and bounded secret/private-path and person-data patterns. It found no raw source ZIP or person-row member, unsafe duplicate ZIP path, or inventory size/hash mismatch.
- The independent distribution reviewer recorded `PASS_CANDIDATE_BOUND` for the exact bytes in `docs/evidence/phase-05-asset-review.json`. The final Windows CI wheel is SHA-256 `fe5c6174fccb1effa0d6b34430f66566fe4567c7dd5685a9ce5f7e7c8169b27c`. Eight text members differ from the earlier local wheel by line endings; their normalized content matches. The candidate's project, DejaVu and source notices, approved eight-source catalog and INEGI attribution/terms were inspected for the actual distribution boundary. The temporary archive with incorrectly decoded Spanish README was rejected and replaced before this approved inventory; no statistical report byte changed.
- `scripts/verify_release.py review` and `inventory` passed against the final receipts. Nine focused release-check tests include altered/added asset and wrong-target failures. The bounded code review in `05-CODE-REVIEW.md` found no issue in the release checker or its tests. `05-SECURITY.md` records the documentation and candidate-member threats as technically mitigated.

## Scope and decisions

The inventory's `release_approved: true` is eligibility for these exact asset bytes. The asset review's `final_release_approved: false` correctly reserves publication, anonymous public readback and final GSD closure. A changed source, member or asset byte reopens the affected checks. `GSD-01` remains open until public proof, requirement traceability and independent phase/milestone verification are complete.
