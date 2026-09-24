# Phase 2 Plan 01 metric semantics audit

Status: **M01–M03 recheck passed at `2936905`; preliminary review, not phase acceptance**
Scope: `brujula/metrics.py`, `brujula/enoe_adapter.py`,
`brujula/populations.py`, `data/catalog/enoe-metrics.json`, and the focused
Plan 01 tests. No implementation, serialization, downstream estimate files,
or broad test rerun was performed.

## Findings

The findings below preserve the original pre-fix review. The final recheck and
its targeted evidence are recorded at the end of this document.

### M01 — dictionary hash is not bound to the loaded frame

The catalog declares a SHA-256 for each quarter in
`data/catalog/enoe-metrics.json:6-14`, but `metric_vectors` only checks that
`frame.period` is a key in that mapping (`brujula/metrics.py:153-154`). It
never compares the declared digest with
`frame.inventory["dictionary_member"]["sha256"]` (the digest produced by the
verified adapter). Consequently a frame carrying a dictionary with a different
hash can still produce metric vectors as long as the quarter key exists. This
violates the Plan 01 requirement for per-quarter official dictionary binding;
the returned `method_version` remains unchanged across that dictionary swap.

Minimal synthetic reproducer (after obtaining any valid fixture frame):

```python
frame.inventory["dictionary_member"]["sha256"] = "0" * 64
result = metric_vectors(frame, NATIONAL_15_PLUS_CONTEXT, {}, "occupied_total")
# Current behavior: succeeds and returns the same method_version.
# Expected: fail closed before vector construction.
```

The adapter validates dictionary structure and records its digest, but that
does not repair the missing binding at the metric API boundary. The fix belongs
in the metric manifest/frame compatibility check (and should preserve the
existing quarter-specific refs).

### M02 — manifest cache is mutable after content hashing

`load_metric_manifest` validates the file digest once and returns a mutable
nested `dict` cached by `@lru_cache` (`brujula/metrics.py:24-44`). A caller can
mutate `manifest["metrics"]`, `manifest["dictionary_refs"]`, or
`manifest["method_version"]`; subsequent `metric_vectors` calls reuse that
mutated object without recomputing or rechecking its canonical hash. This
breaks the stated content-hashed method identity and cache immutability.

Minimal synthetic reproducer:

```python
manifest = load_metric_manifest()
original = manifest["method_version"]
manifest["method_version"] = "tampered"
result = metric_vectors(frame, NATIONAL_15_PLUS_CONTEXT, {}, "occupied_total")
assert result["method_version"] == "tampered"  # current behavior
```

The returned catalog should be immutable (or defensively copied with a fresh
validation) so callers cannot alter definitions or method identity after the
one-time hash check. This is independent of the domain-state cache, whose
single-entry behavior is covered by `tests/test_enoe_metrics.py`.

### M03 — adapter output does not distinguish an explicit synthetic registry

`load_snapshot_frame` accepts an arbitrary `registry_path` and returns an audit
containing source and custody hashes, but no provenance flag
(`brujula/enoe_adapter.py:121-125` and `201-208`). The audit therefore looks
the same whether the caller supplied the approved registry or a disposable
synthetic registry/ZIP that satisfies the same structural checks. The frame
also carries only `source_id` and period, with no synthetic marker. A downstream
consumer that derives record origin from this audit cannot guarantee the
contract rule that synthetic evidence remains explicitly synthetic in every
output.

Minimal boundary reproducer: take the disposable
`tests/test_enoe_adapter.py` fixture, pass its generated registry through
`registry_path`, and compare its returned audit with an approved-registry
audit. Both have the same shape and neither contains `synthetic: true`; the
synthetic fixture is consequently indistinguishable at this API boundary. This
does not treat the test fixture as real data; it demonstrates that the API has
no explicit provenance channel.

The adapter should carry an explicit registry/source provenance decision into
the audit (or reject custom registries for estimation) so later records cannot
silently default a synthetic frame to observed data.

## Reviewed semantics

The source shows the requested distinctions are implemented in the reviewed
scope: `CLASE1=1` drives PEA, `CLASE2=1` drives occupied, unemployment is PEA
plus `CLASE2=2`, unknown labor states are excluded from rate denominators,
known income bands with unknown amounts remain in income-state shares, positive
income means use only `INGOCUP` 1..999998 with bands 1..5, and weekly zero is
accepted only with `DUR9C=1` while `DUR9C=9` is excluded. Population age and
professional-study masks preserve the national age-98 context versus the
known-age professional cohort, and field, sex, entity, occupation, industry,
and geography remain separate selectors/columns in this scope.

These observations do not clear M01/M02 and are not a whole-Phase 2
acceptance; downstream estimation and precision gates remain outside this
review.

## Recheck against upstream fix `2936905`

The three original findings are resolved in the current checkout:

- **M01 resolved.** `metric_vectors` now reads the actual
  `frame.inventory["dictionary_member"]["sha256"]`, validates its shape, and
  compares it with the quarter reference for non-synthetic frames before
  constructing vectors (`brujula/metrics.py:160-169`). The result exposes
  `dictionary_binding` and includes the synthetic dictionary digest in the
  synthetic method identity. The focused mismatch control passed.
- **M02 resolved.** The hashed cached manifest is private and
  `load_metric_manifest` returns a `deepcopy` (`brujula/metrics.py:24-50`).
  Mutating the returned method version, metric ID, and dictionary reference no
  longer changes later calls. The focused mutation control passed.
- **M03 resolved.** The adapter now compares custom registry identity with the
  built-in approved registry and requires an explicit boolean
  `synthetic_fixture=true` for an unapproved custom registry
  (`brujula/enoe_adapter.py:140-160`). It carries `synthetic` and
  `provenance` on both `Frame` and audit (`brujula/enoe_adapter.py:236-241`),
  and metric output preserves the same marker. The unmarked-registry control
  passed.

The CMPE catalog now retains labels in a read-only `MappingProxyType` on the
frame (`brujula/enoe_adapter.py:99-113, 236`); the focused adapter control
also verifies Derecho and Ciencias políticas labels, excludes `999999`, and
rejects label mutation.

Targeted evidence: `.venv/Scripts/python.exe -m pytest` over the two adapter
controls and two metric controls returned **4 passed in 0.68s**. This was a
bounded recheck only; no implementation files were modified here. The audit
can now be treated as **recheck PASS for M01–M03**, while remaining preliminary
for whole-Phase 2 acceptance.
