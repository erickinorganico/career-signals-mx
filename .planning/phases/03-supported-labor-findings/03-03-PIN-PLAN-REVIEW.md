# 03-03 pin amendment: targeted pre-execution review

**Current verdict: PASS (targeted amendment).** This review covers the amended independent-reference and sanitized-index work in `03-03-PLAN.md`, not the in-flight Plan 02 implementation or the previously reviewed Phase 3 plan set. The original blocker and its resolution remain below as an audit trail.

## Re-review after Task 2 revision

Task 2 now explicitly requires the exact allowlisted `source_manifest` to match independently trusted accepted-source and acceptance pins. It also requires standalone validation to regenerate comparisons and claims from pinned inputs, recompute exact `opening_claim_ids` from validated candidates and the deterministic selection policy, and derive exact packet-level limitations from the same inputs and comparator outcomes. It names coherent digest-repinning negative tests for altered provenance, substituted or dropped opening IDs, and removed or invented limitations. Those instructions close the original publication-facing tampering gap without changing the accepted bootstrap, sanitized index boundary or hash-only fixture scope. **Current issues: none in this targeted delta.** This is plan verification, not evidence that the implementation or tests have run.

## What the amendment now covers

- **Accepted bootstrap is feasible.** Plan 01's `index_public_estimates` validates all eight public v2 roots against the accepted manifest, independently approved Phase 1 source catalog, Phase 2 public golden hashes, coverage pins and numerical digest. `build_profiles` returns the sanitized `profiles["record_index"]` while leaving the original index private. The proposed reference can be generated once from that guarded path, including the existing five complementary-redacted parents, without a normal runtime bypass or person-level input. Sources: `brujula/analysis_v2.py` (`index_public_estimates`, `build_profiles`); `03-01-SUMMARY.md`.
- **Safe labels and hidden numbers are addressed.** Task 1 resolves display metadata from the validated per-snapshot catalogs and reviewed definitions, then adds it only to sanitized index items. Task 2 pins the canonical sanitized/enriched index and profiles/coverage, preserves `redaction_reason`, checks all profile appearances against their record IDs and scans nested complementary-suppression sentinels. The hash-only resource does not need original suppressed parent numbers. Sources: `03-03-PLAN.md` Tasks 1–2; `docs/CONTRACT-V2.md` public suppression rules.
- **Standalone record and coverage tampering is addressed.** Task 2 explicitly rejects coherently recomputed caller `content_digest` after record-value, official-label and coverage changes by checking independently packaged hashes first. Its synthetic trusted-loader monkeypatch takes an independent deep copy before mutation, so the test mechanism is separate from normal production validation. The packaging path is viable through `brujula/resources.py` and the `brujula.fixtures` JSON package-data rule. Sources: `03-03-PLAN.md` Task 2; `brujula/resources.py`; `pyproject.toml`.
- **Full scope and ordering are addressed at construction.** Task 2 retains the accepted eight periods and complete field/entity/sex cells; Task 1 requires deterministic claim IDs, canonical text and opening selection under input permutation. These match `03-CONTEXT.md` and the accepted Plan 01 counts.

## Original structured issue (resolved by the Task 2 revision)

```yaml
issues:
  - plan: "03-03"
    task: 2
    dimension: "verification_derivation"
    severity: "BLOCKER"
    description: "Standalone validation pins record_index and profiles/coverage and regenerates comparisons/claims, but does not explicitly authenticate source_manifest or regenerate opening_claim_ids and packet-level limitations. A caller can change one of those publication-facing fields, recompute its own content_digest, retain valid record/profile hashes and valid claim references, and still satisfy the described checks. This can misstate provenance or replace the deterministic supported opening/limitation decision at the Phase 4 handoff."
    fix_hint: "In Task 2, require source_manifest identity to match the independently trusted acceptance/source reference; recompute and require exact opening_claim_ids from deterministic select_opening_claims and exact packet-level limitations from pinned inputs/validated claims. Add coherent repin-negative tests for source_manifest, opening selection and limitations. Keep the accepted real eight-quarter resource hash-only and the synthetic loader override test-only."
```

The extra JSON file has no substantive scope-sanity issue: it is an independent reference needed by the proposed standalone gate. The revision stayed within the existing three tasks.
