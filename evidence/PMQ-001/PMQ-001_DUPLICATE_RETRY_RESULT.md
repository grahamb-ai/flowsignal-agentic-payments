# PMQ-001 — Duplicate / Retry / Concurrent Permit Replay Result

**Status:** PASS AFTER REMEDIATION — BOUNDED IN-PROCESS SURFACE  
**Date:** 18 August 2026  
**Failure run:** `32100874115` (run #54)  
**Successful rerun:** `32100938057` (run #56)  
**Remediation commit:** `0cef1b14bdc7e62040b094fcb6627214660ea024`

## Frozen challenge

The unchanged PMQ-001 challenge required one gateway-produced execution permit to authorize at most one represented consequence formation on the in-process MVP surface.

The tests exercised both sequential replay and concurrent replay of the exact same permit.

## Initial result

**FAIL**

The same valid permit formed the represented consequence twice sequentially, and two concurrent uses of one permit both returned `CONSEQUENCE_FORMED`.

Preserved evidence: `PMQ-001_DUPLICATE_RETRY_FAILURE.md`.

## Remediation

`execute_protected_consequence()` now maintains an in-process consumed-permit registry keyed by the authenticated permit signature.

Permit consumption occurs inside the same `authority_state_guard()` critical section used for final standing resolution and represented consequence formation.

The sequence is now:

1. verify permit integrity;
2. verify exact action binding;
3. acquire final authority-state guard;
4. verify current authority-state version;
5. reject an already-consumed permit;
6. mark the permit consumed;
7. form the represented consequence.

The replay rejection is:

```text
DENIED_EXECUTION_PERMIT_REPLAY
```

Marking the permit consumed before the represented formation step makes duplicate/retry behaviour fail closed on this reference surface.

## Unchanged rerun

The failure-first test file was not weakened after the initial result.

GitHub Actions run `32100938057` completed successfully:

```text
33 passed in 0.53s
```

Both frozen replay assertions passed:

- sequential reuse: only the first use can form the represented consequence;
- concurrent reuse: exactly one of two competing uses can form the represented consequence.

## Classification

**PASS — one-time permit consumption demonstrated on the in-process public harness surface.**

This strengthens evidence for PMQ-001.5, PMQ-001.6 and PMQ-001.7 and contributes to PMQ-001.8/.9.

## Residual limitation

The consumed-permit registry is process-local and intentionally non-durable.

This result does **not** demonstrate:

- duplicate suppression after process restart;
- shared duplicate suppression across multiple service instances;
- distributed idempotency;
- payment-rail deduplication;
- transactional exactly-once settlement semantics.

Those remain deployment/integration proof obligations unless separately demonstrated.