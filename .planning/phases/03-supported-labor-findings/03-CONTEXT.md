# Phase 3: Supported Labor Findings - Context

**Gathered:** 2026-09-22  
**Status:** Preparatory decisions; execution depends on accepted Phase 2 estimates.  
**Decision authority:** The user requests a complete final research product and the recommended GSD path. These decisions apply that authorization without adding services, sources or deployment destinations.

<domain>
## Phase Boundary

Build substantive research profiles, descriptive comparisons, coverage and evidence-bound findings from the accepted ENOE estimates. This phase produces a validated analytical publication input. Formatting and sealed operation belong to Phase 4; it does not create a frontend or publish unchecked findings.
</domain>

<decisions>
## Implementation Decisions

### Questions and coverage
- Explain what the ENOE can say about work among people whose completed professional study field is Derecho, Comunicación y periodismo, or Ciencias políticas. Keep the known-age completed-professional cohort label and exclusions visible; do not imply all graduates or all workers in a profession.
- Provide national context and the total professional cohort for all eight quarters. Give the three focal fields full national profiles and trends across those quarters, with employment, participation, unemployment, known positive income and its coverage, main-job informality, recorded sex, employment position, suboccupation and known weekly hours as accepted in Phase 2.
- Include the other identifiable professional fields in a national comparison table for the latest quarter, without inventing fields for missing codes. Use their actual official catalog labels and separate coverage status from substantive outcomes. A sorted table is not a universal career ranking.
- For the latest quarter, include all 32 entities and both recorded sexes for the three focal fields and cohort total. Unsupported cells stay visible with null and a reason; do not drop sparse states to make a chart look complete. Keep sex slices separate from entity slices unless support and a specific question justify an intersection.
- Preserve the national operational 15+ context separately from the known-age professional cohort; comparison requires matching population identity.

### Comparability ledger
- Resolve the 2025-Q3 ENT→CVE_ENT representation change using verified code/name catalogs, matching definitions and official cross-boundary comparisons, not column-name equality alone. Research evidence is in `.planning/research/GEOGRAPHY-COMPARABILITY.md`.
- Require equality of source family, population definition/version, normalized geography concept, recorded-sex selection, field/occupation/industry concepts, metric/denominator, unit, price basis, classification and estimator method/version. Snapshot hashes legitimately differ across quarters and remain exact provenance; same source family is not a license to compare revised editions silently.
- The equality rule above governs longitudinal deltas. For same-period descriptive contrasts, use a separate comparator that allows exactly one declared recorded-sex or entity axis to differ. Keep period, exact source snapshot, population, metric/denominator, unit, price basis, method/version and geography type/concept fixed. Sex contrast uses recorded 1 versus 2 at national geography; entity contrast requires an explicitly reviewed reference state, with recorded sex fixed. Unsupported or two-axis contrasts block.
- Set the reviewed entity reference to Baja California (`02`) before looking at the final differences. It is the state already included in the independent official reconciliation, which provides an auditable methodological anchor. This is a descriptive reference, not a national benchmark, preferred labor market or ranking. Show all 32 state estimates and their availability independently; only compute a contrast when both the selected state and this reference have supported values. Do not swap the reference opportunistically to obtain a non-null or more striking difference.
- Require ordered compatible quarterly periods and supported endpoint values. Block mismatches and null endpoints explicitly with null deltas, never zero. Adjacent-quarter and year-over-year differences are descriptive, not tests of significance.
- Annual comparisons pair like quarters where available. Adjacent-quarter changes include a seasonality caveat. Income changes are nominal; do not call them changes in purchasing power. Do not compare minimum-wage income bands as a stable real-price classification across years.
- Rotating samples overlap. Never add people or sample sizes across quarters as independent individuals, and never infer a difference's precision from independent marginal intervals.

### Coverage and evidence-bound prose
- Report observed support, response coverage and exclusion reasons by relevant period/field, including age unknown, field unknown, technical/postgraduate/incomplete studies and exact income unavailable. Weighted quantities are estimates, not sample sizes.
- Claims use canonical descriptive templates built from exact public records and valid comparisons. Each has IDs for underlying estimates, source snapshots and methods, plus precision and universe limitations.
- Reject arbitrary added numbers, causal phrasing, personal advice, altered metric/population labels and claims based on suppressed or incompatible endpoints. The claim registry is deterministic and testable; no model or external inference is needed.
- Choose up to three opening findings after the data pass, based on supported relevance and coverage rather than preselecting a sensational conclusion. If evidence cannot support three, show fewer and explain the limitation.
- Reports and exports must use only the validated v2 public projection. Analytical helpers cannot restore diagnostic values into public coverage or prose.

### Agent discretion
- Choose concrete module names and data structures after inspecting final Phase 2 interfaces; reuse complete frames and avoid repeated ZIP decoding for each domain.
- Prefer readable Spanish labels, explicit metric units and reusable record IDs. Keep analysis independent from rendering so every format uses the same accepted findings.
</decisions>

<code_context>
## Existing Code Insights

The v1 comparison and insight modules provide canonical prose and fail-closed examples, but their narrow synthetic grain does not replace the strict v2 contract. Phase 2 will provide verified frame/metric/estimate interfaces and acceptance evidence. Inspect those interfaces before finalizing executable plans. The geography review and eight-quarter input audit supply primary evidence without public person rows.
</code_context>

<deferred>
## Deferred Ideas

Static editorial layout, charts/PDF, export packaging, CLI/current promotion and release auditing are committed later phases. No causal model, personalized recommendation, deflator or new source is added to this milestone.
</deferred>
