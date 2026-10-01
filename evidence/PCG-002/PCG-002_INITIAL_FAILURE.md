# PCG-002 — Initial failure

## Frozen proposition

After candidate generation `g` enters terminal invalid space, a caller cannot
restore a path to protected consequence merely by replacing `g` with an
arbitrary identifier. A successor must be authority-issued, causally linked to
the invalidated parent, and bound to the same canonical action.

## Reproduction

```text
python -m pytest -q tests/test_pcg002_unauthorised_successor_generation.py
```

Failure preserved by commit `f8e5040`.

## Observed failure

```text
AssertionError: UNAUTHORISED SUCCESSOR-GENERATION FAILURE: replacing a
terminally invalidated generation with a caller-chosen UUID restored ALLOW.
Candidate identity is caller-asserted rather than authority-issued.

assert 'ALLOW' == 'REFUSE'
1 failed
```

## Meaning

PCG-001 prevented resurrection of the same identifier, but generation identity
was still supplied by the caller. Substituting a fresh UUID bypassed terminal
invalidation because the runtime had no issuance registry or parent lineage.

