# PMQ-001 — Pre-Market Adversarial Qualification Results

**Status:** QUALIFICATION RECORD — BOUNDED PUBLIC HARNESS  
**Date:** 18 August 2026  
**Target:** FlowSignal Agentic Payments Runtime Authority MVP  
**Classification vocabulary:** PASS · PARTIAL · FAIL · NOT DEMONSTRATED

## Purpose

PMQ-001 applies the frozen external consequence-boundary proof burden recorded before PMQ-specific remediation and extends it with operational/adversarial checks relevant to a buyer-facing MVP.

This record is not a production certification. A PASS applies only to the exact public harness surface exercised by the cited mechanism and test.

## Result summary

| Proposition | Final classification | Bounded conclusion |
|---|---|---|
| PMQ-001.1 Candidate movement before bind | **PASS** | An unbound candidate movement cannot use the represented execution component to mint a permit and form the represented consequence. |
| PMQ-001.2 Current authority/evidence under present conditions | **PASS** | Current authority-state version, current temporal validity and required screening evidence are checked on the represented harness path; unavailable required screening evidence fails closed. |
| PMQ-001.3 Standing at the boundary | **PASS** | The final protected consequence boundary rechecks permit integrity, temporal validity and current authority-state version before represented formation. |
| PMQ-001.4 Changed-condition loss of standing | **PASS** | A state change committed before the final protected boundary invalidates stale authority; a change attempting to commit inside the guarded final interval is serialized after represented formation. |
| PMQ-001.5 Lawful continuation / loss | **PASS** | Continuation is bounded by current state, exact action binding, temporal validity and one-time permit consumption on the in-process surface. |
| PMQ-001.6 NO_BIND / represented non-formation | **PASS represented / ND external physical** | REFUSE/BLOCKED/no-permit paths do not form the represented harness consequence. External physical payment non-formation is not demonstrated. |
| PMQ-001.7 Credible bypass attempts and route closure | **PARTIAL** | Tested governed routes are closed, and EC-002 removes permit-minting/signing capability from the represented executor component. Universal external route closure and production process/IAM/KMS/HSM isolation remain ND. |
| PMQ-001.8 Receipt of what formed / did not form | **PASS — bounded harness evidence** | The harness emits a separate HMAC-protected consequence-outcome receipt binding represented formation/non-formation to the Authority Receipt identifier and exact action binding. Durable external settlement evidence and production audit-store guarantees remain ND. |
| PMQ-001.9 Same-condition / changed-condition replay | **PASS — bounded** | Historical determination replay, changed-state rejection and same-permit duplicate rejection are demonstrated on the current process surface. Durable replay protection after restart is not demonstrated. |

## Material failures found and preserved

PMQ-001 did not begin green.

### 1. No-bind execution capability bypass

Initial attack obtained a consequence-authorising permit without a Runtime Authority ALLOW/Authority Receipt and formed the represented consequence.

```text
1 failed, 30 passed
CONSEQUENCE_FORMED
```

The failure is preserved in `PMQ-001_INITIAL_FAILURE.md`.

### 2. Duplicate / concurrent permit replay

The exact same valid permit formed the represented consequence more than once, both sequentially and concurrently.

```text
2 failed, 31 passed
```

Preserved in `PMQ-001_DUPLICATE_RETRY_FAILURE.md`.

Remediation added atomic one-time permit consumption inside the final authority-state guard.

### 3. Delayed permit expiry

A permit issued while the Authority Receipt was valid remained usable after the authority validity window expired.

```text
1 failed, 33 passed
CONSEQUENCE_FORMED
```

Preserved in `PMQ-001_DELAYED_PERMIT_EXPIRY_FAILURE.md`.

Remediation bound `valid_until` into the signed permit and rechecked it at the protected consequence boundary.

### 4. Temporal-remediation regression

The first temporal strengthening exposed inconsistent clock semantics between fixed historical scenario fixtures and the live wall-clock protected boundary.

```text
8 failed, 26 passed
```

Preserved in `PMQ-001_TEMPORAL_REMEDIATION_REGRESSION_FAILURE.md`.

The expiry control was not weakened. Normal/live fixture timestamps were rebased to the current UTC harness clock while preserving relative temporal facts.

### 5. Execution-component capability isolation

EC-002 executable challenge confirmed the known EC-001.4 gap. The pre-remediation executor exposed the issuer, signing key, signing primitive and embedded reference secret:

```text
4 failed, 38 passed in 0.59s
```

Preserved in `evidence/EC-002/EC-002_INITIAL_FAILURE.md`.

Remediation separated permit issuance/signing into `app.engines.permit_authority`. The represented executor now consumes/verifies permits but does not contain or export the minting/signing capability. The unchanged EC-002 checks passed on rerun.

A first full regression after the refactor hit a stale PMQ test import because the issuer symbol had intentionally been removed from the executor. The PMQ attack was updated to probe the same execution-side surface dynamically; its proposition was not weakened.

Successful EC-002 full rerun:

```text
42 passed in 0.46s
```

GitHub Actions run: `32102248520`.

## Additional demonstrated controls

The current bounded evidence includes:

- Authority Receipt HMAC integrity and evidence-content integrity;
- stale authority-state rejection;
- exact action-binding / beneficiary substitution rejection;
- normal governed route consumption of the Execution Gateway and protected consequence boundary;
- in-process final-check-to-formation serialization;
- historical Authority Receipt replay;
- represented non-formation for REFUSE/BLOCKED outcomes;
- invalid execution-permit rejection;
- unavailable required screening evidence fail-closed behavior;
- one-time permit consumption under sequential and concurrent replay;
- signed permit expiry enforced at the final represented consequence boundary;
- separately sealed represented consequence-outcome receipts and tamper detection;
- removal of permit-minting/signing capability from the represented execution component.

## Residual proof obligations

### Production capability isolation — NOT DEMONSTRATED

EC-002 demonstrates a reference component/module separation. `permit_authority.py` and `protected_consequence.py` still exist within one Python reference codebase/runtime trust domain. Separate OS identities, processes, network boundaries, IAM, KMS/HSM custody and privileged-operator separation remain production obligations.

### Durable duplicate suppression after restart — NOT DEMONSTRATED

The consumed-permit registry is process-local and non-durable. One-time use is demonstrated during the life of the current reference process, not across restart or multiple instances.

### Distributed atomicity — NOT DEMONSTRATED

The final state/consequence serialization is an in-process lock. No distributed transaction, consensus, serializability or multi-service atomic commit is claimed.

### Universal route closure — NOT DEMONSTRATED

The exercised governed public harness paths are tested. External payment rails, privileged deployment routes and unrepresented consequence paths are outside this proof surface.

### External physical non-formation — NOT DEMONSTRATED

`NO EXECUTION` is a represented harness consequence. No bank/payment-network settlement rail is integrated.

### Durable/external consequence evidence — NOT DEMONSTRATED

The separate consequence-outcome receipt is integrity protected in the harness. Durable write-once storage, independent timestamping, external settlement confirmation and atomic persistence with a real payment rail are not demonstrated.

### Evidence-service transport failures and malformed external payloads — NOT DEMONSTRATED

An `UNAVAILABLE` screening condition is tested fail closed. Real transport timeouts/corruption and provider-specific malformed payloads require integration surfaces not represented here.

### Trusted/distributed time — NOT DEMONSTRATED

The reference harness uses the current UTC process clock. Hardware-rooted time, multi-host skew and cross-service time integrity remain deployment obligations.

## Pre-market conclusion

Within the declared **in-process represented MVP boundary and tested governed routes**, the current evidence demonstrates current-state rejection, exact action binding, determination and consequence-outcome evidence integrity, final temporal standing, one-time permit use, fail-closed unavailable evidence, final-interval serialization, historical replay and removal of direct permit-minting/signing capability from the represented executor component.

The strongest safe market statement is:

> Within the declared MVP boundary, no consequence-producing bypass remains demonstrated on the governed paths and conditions tested in PMQ-001. Remaining gaps are explicitly identified as deployment trust-boundary, durability, distributed-system or external-integration proof obligations.

That statement must not be expanded into universal route closure, production readiness, production credential isolation, distributed atomicity or physical payment-settlement non-formation.