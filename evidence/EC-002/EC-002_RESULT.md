# EC-002 — Capability Isolation Result

**Status:** PASS AFTER REMEDIATION — BOUNDED REFERENCE COMPONENT/MODULE SURFACE  
**Date:** 18 August 2026  
**Initial failure run:** `32102086782` (run #73)  
**Successful rerun:** `32102248520` (run #78)  
**Successful head:** `0de93ca49adaa196a694e36ade436904c172a0d3`

## Frozen proposition

Code acting only as the represented execution component must not possess an independent usable capability to mint a consequence-authorising execution permit.

## Initial failure

All four frozen checks failed on the pre-remediation execution component:

```text
4 failed, 38 passed in 0.59s
```

The execution-side module exposed a callable permit issuer, contained the permit-signing key, exposed the signing primitive and embedded the reference signing secret.

The initial result is preserved in `EC-002_INITIAL_FAILURE.md`.

## Remediation

Permit issuance/signing was separated into a dedicated reference component:

`app.engines.permit_authority`

The represented execution component:

`app.engines.protected_consequence`

now consumes and verifies an `ExecutionPermit` but no longer contains or exports:

- `issue_execution_permit`;
- `_PERMIT_KEY`;
- `_sign`; or
- the embedded reference permit secret.

The Execution Gateway is the represented component that calls the permit authority after validating an authentic ALLOW Authority Receipt, exact action binding, current authority-state version and temporal validity.

## Regression encountered during remediation

The first full suite after separating the components failed during collection because the older PMQ-001 no-bind attack imported the now-removed issuer symbol directly from the execution component.

That was an API/test compatibility issue rather than evidence that the frozen proposition failed. The PMQ-001 challenge was preserved semantically: it now probes whether a callable issuer exists on the execution component and, if it does, attempts the same direct no-bind mint-and-form attack.

No execution-side issuer now exists, so the attack fails closed with no permit.

## Unchanged EC-002 rerun

The four frozen EC-002 assertions were not weakened. GitHub Actions run `32102248520` completed:

```text
42 passed in 0.46s
```

## Classification

**PASS — the represented execution component/module no longer contains an independent permit-minting/signing capability on the exercised public reference-harness surface.**

## Residual limitation

This result does **not** prove production-grade capability isolation.

`permit_authority.py` and `protected_consequence.py` remain Python components in the same reference codebase/runtime trust domain. The result therefore does not demonstrate:

- separate operating-system identities;
- process isolation;
- network-service isolation;
- IAM policy enforcement;
- KMS/HSM-backed signing;
- privileged-operator separation;
- production secret custody.

Those remain deployment proof obligations.

The safe conclusion is narrower:

> The obvious execution-component minting capability identified by EC-001.4 and confirmed by the EC-002 initial failure has been removed from the represented executor component. Production trust-boundary isolation remains NOT DEMONSTRATED.