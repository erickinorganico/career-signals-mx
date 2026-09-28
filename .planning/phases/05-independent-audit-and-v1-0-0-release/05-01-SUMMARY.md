---
phase: 05-independent-audit-and-v1-0-0-release
plan: 01
subsystem: reader-guidance-and-installed-portability
tags: [bilingual-docs, installed-wheel, windows, ubuntu, pdf]
requires:
  - phase: 04-06
    provides: sealed real publication and separate real numerical and operational acceptance
provides:
  - current Spanish and English reader guidance and citation metadata
  - exact-target Windows and Ubuntu installed-wheel portability receipts
  - release verifier with focused negative controls
affects: [05-02, 05-03, phase-05-verification]
key-files:
  created:
    - scripts/verify_release.py
    - tests/test_release_checks.py
    - docs/evidence/phase-05-portability.json
  modified:
    - README.md
    - README.en.md
    - docs/RELEASE.md
    - docs/STATUS.md
    - docs/SPEC.md
    - docs/CONTRACT.md
    - docs/CONTRACT-V2.md
    - docs/research/ENOE-METHOD-REVIEW.md
    - CITATION.cff
    - pyproject.toml
    - .github/workflows/verify.yml
requirements-completed: [REL-01]
completed: 2026-09-28
---

# Phase 05 Plan 01: Reader documentation and portable installation

**The bilingual guides describe the accepted research scope and installed commands, and version 1.0.0 installed outside the checkout on both hosted operating systems.** The clean-host checks establish fixture, resource and PDF portability. They do not represent another eight-quarter numerical or R run.

## Executed evidence

- The Spanish and English entry points, release/status guidance, v2 contract, method review and citation metadata were reconciled with the installed CLI and accepted Phase 4 publication. Historical synthetic work is labeled as historical; the current report retains the eight-quarter versus latest-quarter detail boundary, nonofficial precision and visible null/suppression limits. `docs/OPERATIONS.md` supplies commands with explicit local roots.
- The immutable implementation and package target is `611d2f553597439a0c58807dd6865914ff46281c`. [Hosted run 36464796584](https://github.com/erickinorganico/career-signals-mx/actions/runs/36464796584) passed on Windows and Ubuntu. Each host built and installed the wheel outside checkout, verified authored resources, and produced a searchable Spanish PDF with embedded fonts and negative asset controls. Each host reported 595 Python tests passed, 6 skipped and 30 prohibition controls passed. The skips require the designated R/source-cache/real-packet environment.
- `docs/evidence/phase-05-portability.json` binds both downloaded CI receipts and wheels to the target and version 1.0.0. The distributed Windows wheel has SHA-256 `fe5c6174fccb1effa0d6b34430f66566fe4567c7dd5685a9ce5f7e7c8169b27c`; all 57 `brujula/` members match the Ubuntu wheel byte for byte. The prior local wheel's eight line-ending differences were retained as historical preparation and were not substituted for the distribution wheel.
- `scripts/verify_release.py host` passed against the actual hosted run and approved wheel. Nine focused release-check regressions cover incorrect identity, stale receipts, missing or altered assets, audit binding and GitHub binary headers. A real Actions artifact read exposed an incorrect ZIP accept header; the correction was included in the final target and retested on both hosts. The final affected local run passed 63 tests. An earlier local full-suite attempt was not accepted because the native PDF environment was incomplete and fixture edits overlapped it.

## Scope and decisions

The accepted Phase 4 real numerical/R/official, offline replay, real publication and visual evidence remain separate from the hosted fixtures. `REL-01` is supported by the current bilingual readback. Plan 05-02 supplies the independent research and exact asset review needed for the remaining `REL-02` release gate. Later evidence commits describe the frozen target; they do not retarget its code or wheel.
