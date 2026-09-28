# Technical release preparation — 2026-09-28

This is preparation evidence, not a Phase 5 completion summary. Phase 4 human visual acceptance remains pending in `04-UAT.md`; GSD is not closed.

Frozen implementation: `611d2f553597439a0c58807dd6865914ff46281c`. [Hosted run 36464796584](https://github.com/erickinorganico/career-signals-mx/actions/runs/36464796584) passed Windows and Ubuntu: **595 tests passed, 6 skipped**, plus **30 prohibition controls passed** on each platform. The six skips require the local reviewed R runtime, eight-package source cache or accepted real packets; this CI does not claim a new real-data replay. Both platforms built and installed 1.0.0 outside checkout, verified authored resources, and generated searchable Spanish PDF with embedded fonts and negative asset controls.

The distributed wheel is the exact Windows CI artifact. All 57 `brujula/` package members match the Ubuntu CI wheel byte for byte. The earlier locally built wheel differed in eight text files only by CRLF/LF; it is retained as historical local preparation evidence, not substituted for the distributed wheel. Statistical code and source-generation evidence remain unchanged.

The independent release-checker review is clean. Nine focused regression tests cover wrong targets, stale/forged receipts, missing or altered assets, exact audit binding, and GitHub binary endpoint headers. A real API read caught the Actions ZIP media-type error; the final commit fixes it and was retested on both hosts.

An initial local full-suite attempt was not accepted: it lacked native PDF environment variables and overlapped edits to release-test fixtures. After the files stabilized and native PDF paths were configured, all **63 affected tests passed** (`tests/test_pdf_v2.py`, `tests/test_phase4_edge_acceptance.py`, `tests/test_release_checks.py`). The complete hosted run above supplies the stable whole-suite result.

Candidate audit rejected a temporary ZIP README with incorrectly decoded Spanish text. That unpublished candidate was preserved separately. The replacement restores the exact previously reviewed UTF-8 README and research archive; no statistical report byte changed. The current inventory and independent asset review identify the accepted candidate explicitly.

Final receipts in `docs/evidence/` distinguish independent content review, exact member redistribution decisions, installed-host portability, and any later draft/public download proof. `release_approved` within the inventory means asset eligibility only; `final_release_approved` remains false until the separate acceptance and publication gates finish.
