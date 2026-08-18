# PMQ-001 — Duplicate / Retry / Concurrent Permit Replay Failure

**Status:** PRESERVED FAILURE  
**Date:** 18 August 2026  
**GitHub Actions run:** `32100874115` (run #54)  
**Head commit under test:** `a6a843e1f69a3e5ef68f374c45474c4caf4b3a80`

## Frozen challenge

The frozen challenge in `PMQ-001_DUPLICATE_RETRY_CHALLENGE.md` required one gateway-produced execution permit to authorize at most one represented consequence formation on the tested in-process MVP surface.

The challenge covered both sequential reuse and concurrent replay of the exact same valid permit.

## Observed result

Both attacks succeeded in forming more than one represented consequence.

### Sequential replay

The first use returned:

```text
CONSEQUENCE_FORMED
```

The exact same permit was then reused and returned:

```text
CONSEQUENCE_FORMED
```

### Concurrent replay

Two threads presented the same permit concurrently. Both returned:

```text
CONSEQUENCE_FORMED
CONSEQUENCE_FORMED
```

The frozen assertion observed two consequence-forming outcomes where exactly one was permitted.

## Full suite result

```text
2 failed, 31 passed in 0.60s
```

## Initial classification

**FAIL — duplicate and concurrent replay of one valid execution permit could form multiple represented consequences on the current in-process harness surface.**

## Mechanism gap

`execute_protected_consequence()` validated permit authenticity, action binding and current authority-state version, but did not record or enforce one-time permit consumption. A still-valid permit therefore behaved as a reusable consequence-forming capability.

## Scope

This is a bounded reference-harness failure. It is not a claim about external payment rails or a production deployment.

## Remediation constraint

The frozen tests must remain unchanged. Remediation must make permit consumption atomic with the represented consequence boundary so sequential retry and concurrent replay of the same permit cannot produce a second represented consequence.

Any subsequent PASS remains bounded to the in-process harness. Persistence of duplicate suppression across process restart, multiple service instances or distributed infrastructure remains a separate proof obligation unless explicitly demonstrated.