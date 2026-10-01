# PCG-002 — Repair result

## Repair

The reference runtime now:

1. mints candidate-generation identifiers inside an authority-owned issuance
   boundary;
2. persists immutable scenario and canonical-action bindings for each issued
   generation;
3. rejects unregistered, mismatched, or caller-substituted identifiers;
4. issues a successor only when its registered parent is already terminally
   invalidated; and
5. requires the successor to preserve the parent's scenario and canonical
   action binding.

The existing PCG-001 liveness test now obtains its valid fresh generation from
the lifecycle authority rather than constructing a UUID directly.

## Verification

Targeted regression:

```text
python -m pytest -q \
  tests/test_pcg002_unauthorised_successor_generation.py \
  tests/test_postcandidate_invalid_generation_cannot_regain_execution.py \
  tests/test_agentic_payments_harness.py

14 passed
```

Full harness after the additional lineage cases:

```text
python -m pytest -q
590 passed in 2.09s
```

## Boundaries

This is a reference implementation. Issuance authority is represented by an
in-process unforgeable object capability, and lifecycle records are stored in
local SQLite. A production deployment still requires a service/process trust
boundary, authenticated callers, transactional storage appropriate to the
deployment topology, and operational key/capability management.

