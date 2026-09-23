# Local visual inspection tooling

Prepared 2026-09-23 for 04-04. This is tool readiness, not final report acceptance.

- Bundled Poppler `pdftoppm` is available on PATH, version 26.07.0. It can render actual PDF pages to PNG for visual inspection without adding a product dependency.
- The ignored project PDF environment has WeasyPrint 70.0 and verified `pypdf==6.19.0`. The latter's wheel hash, installed version and historical synthetic text/font readback are in `docs/evidence/phase-04-pdf-audit-dependency.json`. Add its reviewed test/audit declaration and license notice when implementing actual PDF tests; do not make clean CI depend on a Codex-only interpreter.
- The host's bundled Node runtime exposes Playwright 1.62.1; its existing Chromium 151.0.7922.34 launches headlessly from the sandbox. An offline file-URL probe loaded the historical synthetic HTML at 1440×960 and 390×844 and captured screenshots. No HTTP(S) request was observed. The probe's 80 table rows and Spanish heading were read back. No package/global browser installation or local HTTP server was needed.
- A 200% CSS-zoom case is also available. Record it as CSS enlargement/reflow, not as evidence of a native browser zoom setting or accessibility certification. Final checks must inspect actual content fit and screenshots at the enlarged size.

Local probe: `.cache/research/phase4-preflight/browser_probe.cjs`; evidence under `.cache/research/phase4-preflight/browser/`. Runtime paths come from the Codex workspace-dependencies tool. Those environment-specific probe scripts and browser caches stay ignored. They are visual-audit tooling, not an installation prerequisite for readers.

For the final report, build a fresh QA inventory from 04-EDITORIAL-SPEC.md and 04-04-PLAN.md, load the actual generated HTML with all network disabled, inspect desktop/mobile/enlarged content and table scrolling, then render actual PDF cover/profile/state/transition/source pages to PNG. Record exact source/asset identity, page/viewport, observed issue, fix and recheck. A successful browser launch, existing screenshot, PDF text extraction or this preparation document cannot substitute for that inspection.
