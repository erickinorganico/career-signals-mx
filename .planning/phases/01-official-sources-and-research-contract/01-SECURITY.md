---
phase: 1
slug: official-sources-and-research-contract
status: verified
threats_open: 0
asvs_level: 1
register_authored_at_plan_time: true
created: 2026-09-22
---

# Phase 1 — Security

GSD L1 verification of the threat register authored in the three plans, at implementation `0eec8c6`. The configured threshold is high. Local batch custody, semantic validation and public suppression are the applicable boundaries; authentication/session controls do not apply. This is not final release or numerical acceptance.

## Trust boundaries

Approved remote ZIP bytes enter local content-addressed custody; only selected metadata leaves the raw area. Untrusted row codes enter population rules. Internal estimate diagnostics enter a strict public projection.

## Threat register and evidence

The plans did not assign numeric severity. High is assigned conservatively to integrity/disclosure threats below; supply-chain continuation is low. No threshold-based omission is used.

| Threat | Category/component | Severity | Disposition | Evidence of mitigation | Status |
|---|---|---|---|---|---|
| T-01-01 | Tampering: current/raw/member | high | mitigate | `acquisition.resolve_snapshot`, `source_inventory._assert_latest_attempt` and exact member SHA; tests reject corrupt raw, missing attempt, newer failed attempt and similar member names | closed |
| T-01-02 | Disclosure: inventory | high | mitigate | `source_inventory._inventory` constructs metadata-only mapping; `_member` retains no person-member bytes; fixture and eight-quarter integration check metadata and publication=false | closed |
| T-01-03 | Spoofing: source identity | high | mitigate | Registry exact eight IDs/periods, HTTPS host, terms identity and pinned hashes; bad-host/URL/registry tests | closed |
| T-01-04 | DoS: ZIP/member read | high | mitigate | Acquisition download/expanded-size bounds; ZIP traversal/duplicates rejected; named metadata <=1 MiB; streamed full member hashing | closed |
| T-01-SC | Tampering: dependencies | low | accept | No new dependency in source inventory | closed |
| T-02-01 | Tampering: codes/sentinels | high | mitigate | ASCII lexical rules, period catalog membership, age/education/residence fixtures in `test_population_rules.py` | closed |
| T-02-02 | Disclosure: population summaries | high | mitigate | Explicit count/reason/weighted-total summary dictionaries; no row payload returned; denominator fixtures | closed |
| T-02-03 | Repudiation: exclusions | high | mitigate | Reason-specific exclusion counts, unknown-age/field distinction and separate professional/national definitions | closed |
| T-02-04 | Tampering: denominator | high | mitigate | `_weight` rejects nonfinite/nonpositive inputs; `_sum_weights` fails overflow; observed count separate from weighted total | closed |
| T-02-SC | Tampering: dependencies | low | accept | No new dependency in population rules | closed |
| T-03-01 | Tampering: record/reference | high | mitigate | Separate strict schemas, JSON-native finite inputs, reference/grain checks; malformed Decimal and impossible-support negative fixtures after CR-01/02/04 fixes | closed |
| T-03-02 | Disclosure: public projection | high | mitigate | Allowlisted projection clears suppressed estimate-equivalent diagnostics, controlled public reason codes; serialized sentinel and free-text reason regressions after CR-03 | closed |
| T-03-03 | Spoofing: source/method/evidence | high | mitigate | Resolvable source/period/evidence references and matching design/method/version; orphan and mismatch fixtures | closed |
| T-03-04 | Repudiation: precision | high | mitigate | Support/CV consistency, reason/status and singleton checks; adjustment cannot assert official precision; uncertainty estimation remains Phase 2 | closed |
| T-03-SC | Tampering: dependencies | low | accept | Existing JSON Schema dependency only; both schemas packaged by existing mapping | closed |

## Accepted risks

The three SC entries retain existing project dependencies; no new package was added by these plans. This narrow plan-time acceptance does not replace the Phase 5 dependency/license review. No unresolved integrity or disclosure risk is accepted.

## Audit trail

| Date | Registered | Closed | Open | Method |
|---|---|---|---|---|
| 2026-09-22 | 15 | 15 | 0 | Root source/fixture inspection, original independent code review, five corrective commits and focused test evidence |

GSD `secure-phase` permits the authored-register, zero-open-threat L1 short circuit. No additional security agent or new threat scan is required. Independent review recheck and phase goal verification remain separate gates.
