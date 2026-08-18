# PMQ-001 — Initial Failure Record

**Status:** PRESERVED FAILURE  
**Date:** 18 August 2026  
**GitHub Actions run:** `32099764223` (run #49)  
**Head commit under test:** `31363e9e9ceb00841659a29809a1cc25d189eb2e`

## Frozen propositions exercised

- PMQ-001.1 — Candidate movement before bind
- PMQ-001.6 — NO_BIND / actual non-formation
- PMQ-001.7 — Credible bypass attempts and route closure

## Unchanged challenge

The adversarial test deliberately avoided `evaluate_financial()` and therefore obtained no Runtime Authority ALLOW and no authentic Authority Receipt.

It constructed an attacker-controlled `ExecutionAttempt`, calculated the action-binding hash, directly invoked the execution-side-accessible `issue_execution_permit()` function using a fabricated receipt identifier and the current authority-state version, then submitted the resulting permit to `execute_protected_consequence()`.

## Observed result

The represented protected consequence formed:

```text
CONSEQUENCE_FORMED
```

The frozen assertion therefore failed:

```text
assert 'CONSEQUENCE_FORMED' != 'CONSEQUENCE_FORMED'
```

Full suite result:

```text
1 failed, 30 passed in 0.52s
```

## Initial classification

**FAIL — represented consequence formation without Runtime Authority bind was demonstrated on the current in-process public harness surface.**

The counterexample shows that permit-minting capability was usable without an authentic Authority Receipt because `issue_execution_permit()` accepted caller-supplied receipt identity, action binding and authority-state version and did not itself require evidence that the Execution Gateway had validated a Runtime Authority determination.

## Scope

This is a bounded reference-harness failure. It is not a claim about a production deployment or external payment rail.

## Remediation constraint

The frozen adversarial test must not be weakened or rewritten to green. Remediation must make the same direct no-bind attack unable to obtain a consequence-authorising permit. Any subsequent PASS remains bounded to the mechanism actually demonstrated and must not be presented as proof of production-grade process/KMS/IAM isolation.
