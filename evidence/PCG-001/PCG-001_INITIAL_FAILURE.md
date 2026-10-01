# PCG-001 - Initial Failure

## Frozen proposition

> Once a specific candidate generation has entered invalid space under a
> material condition, restoring that condition MUST NOT allow the same
> generation to regain a path to protected consequence. A later valid attempt
> must be represented as a fresh candidate generation and fully requalified.

## Challenge sequence

1. At Sigma0, the frozen AP-001 candidate evaluates `ALLOW`.
2. At Sigma1, `account_status` becomes `SUSPENDED`; the same scenario/action
   identity evaluates `REFUSE`.
3. At Sigma2, `account_status` is restored while the scenario identifier and
   canonical action-binding hash remain unchanged.
4. The same candidate identity is evaluated again.

## Initial execution

Local integrated run on 2026-10-01:

**1 failed / 586 passed**

Targeted result:

**1 failed**

## Classification

**FAIL - INVALIDATED CANDIDATE GENERATION RESURRECTED**

## Observed failure

The same `(scenario_id, action_binding_hash)` identity produced the sequence:

`ALLOW -> REFUSE -> ALLOW`

After the load-bearing condition was restored, `evaluate_financial()` issued a
fresh ALLOW receipt without requiring a distinct candidate-generation
identity. The implementation therefore could not distinguish a legitimate new
candidate from resurrection of the previously invalidated candidate.

Failure message:

> CANDIDATE-GENERATION RESURRECTION FAILURE: the same scenario/action identity
> moved ALLOW -> REFUSE -> ALLOW after condition restoration. FlowSignal issued
> a fresh receipt without requiring a fresh candidate generation, so the
> invalidated generation regained a path to protected consequence.

## Existing controls confirmed

The related authority-state rollback, concurrent revocation, and consumed
permit restart/replay tests were rerun from the canonical harness working
directory and remained green:

**4 passed**

This confirms the failure is not stale-receipt or stale-permit acceptance. It
is the absence of an explicit, irreversible candidate-generation invalidation
boundary across fresh evaluations.

## Scope

This is a failure of the reference financial runtime's candidate lifecycle
semantics. It does not establish a production exploit or invalidate the
existing protections against stale authority-state versions, permit replay,
action substitution, or concurrent revocation.

The failure is preserved before remediation.

