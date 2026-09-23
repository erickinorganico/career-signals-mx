# Phase 4 wave 1 verification

2026-09-23. Accepted scope: Plans 04-01 and 04-03 only. The phase and final release remain in progress.

- Public-model/export source freeze: `a89b782`; 04-03 summary `9bf9e42`. Resource implementation proof: `a7ef126`, with the required publication schema added by 04-03.
- Full Python regression after all export corrections: **476 passed, zero skipped**, one expected duplicate-ZIP-member warning, 436.09 seconds. Command: `.venv/Scripts/python.exe -m pytest -q --junitxml=.cache/research/phase4-wave1/junit-corrected.xml`. Both real packet integration cases executed.
- Mandatory portable publication/export controls in a disposable `git archive HEAD` source copy without ignored data: **18 passed**, with exactly two separate optional real-packet cases skipped. See 04-03-SUMMARY.md.
- Independent 04-EXPORT-REVIEW.md: clean, zero active findings. All three original findings are preserved and resolved: portable tests, complete comparison signatures and supported-only figure links. Actual packet: 4,209 complete comparison rows, 5,474 comparison-evidence links, nine figure groups; trend links have 96 REVIEW and zero BLOCKED entries.
- Existing Node phase 1–3 prohibitions: **25 passed**, zero skipped. Those controls and their inputs are unchanged by the export corrections; the earlier wave run is reused. Phase 4 prohibition controls remain assigned to 04-06.
- Canonical 04-03 summary check: passed, committed files present and self-check passed. Schema drift: block=false/drift=false. Codebase drift: block=false/action_required=false. UI gate: hasUiFiles=false/block=false. API coverage precheck: passed, nine capabilities with six integrations and three explicit per-phase opt-outs. The former unsupported deferred label was corrected without reducing Phase 5 scope.
- Documentation checker: PASS; 193 files, 43 Markdown files, 196 local links and 65 JSON files; diff whitespace check clean.

The earlier full run at `7be3011` (473 passed) is historical baseline evidence only, superseded for changed source by the corrected run above. No current publication, PDF report, fresh installed numerical acceptance, final security audit or release success follows from wave 1. GSD's state counter also counts 04-PLAN-CHECK.md as a plan-shaped document; the execution index has six actual Phase 4 plans and sixteen currently planned execution plans in total, so that denominator is retained explicitly.
