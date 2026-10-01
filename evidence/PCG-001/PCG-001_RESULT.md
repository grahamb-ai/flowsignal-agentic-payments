# PCG-001 - Remediation Result

## Result

**PASS - INVALIDATED CANDIDATE GENERATION CANNOT REGAIN EXECUTION**

## Preserved initial failure

Before remediation, the same `(scenario_id, action_binding_hash)` identity
produced:

`ALLOW -> REFUSE -> ALLOW`

The initial integrated run was:

**1 failed / 586 passed**

The failure remains recorded in `PCG-001_INITIAL_FAILURE.md`.

## Remediation

The reference financial runtime now:

1. Assigns every evaluation an explicit `candidate_generation_id`.
2. Includes that generation identity in the authority receipt and its HMAC.
3. Includes that generation identity in the execution permit and its signature.
4. Persists terminal candidate invalidation in a dedicated SQLite lifecycle
   store.
5. Refuses to issue a later ALLOW for a generation that has entered terminal
   invalid space.
6. Blocks pre-invalidation receipts for that generation at the execution
   gateway.
7. Rechecks terminal invalidation at the final protected consequence boundary.
8. Allows a genuinely new generation to qualify after conditions are restored.

## Verified sequence

### Generation g

- Sigma0: valid -> `ALLOW`
- Sigma1: account condition becomes `SUSPENDED` -> `REFUSE`
- Pre-invalidation ALLOW receipt presented after Sigma1 -> `BLOCKED` with
  `CANDIDATE_GENERATION_INVALIDATED`
- Sigma2: account condition restored for the same generation -> remains
  non-ALLOW

### Generation g+1

- New `candidate_generation_id`
- Full evaluation under restored current conditions -> `ALLOW`
- Execution gateway -> `PERMITTED`

This demonstrates both safety and liveness: the invalidated generation remains
unable to execute, while a fresh valid generation can still proceed.

## Final execution

Targeted challenge:

**1 passed**

Integrated suite:

**587 passed in 2.26s**

## Scope

The lifecycle store is a reference-MVP local SQLite mechanism. This result does
not claim production distributed consensus, privileged database rollback
resistance, cross-host transactionality, or production-grade key management.
Those remain deployment responsibilities.
