# PMQ-001 — Pre-Market Adversarial Qualification Results

**Status:** QUALIFICATION RECORD — BOUNDED PUBLIC HARNESS  
**Date:** 18 August 2026  
**Target:** FlowSignal Agentic Payments Runtime Authority MVP  
**Classification vocabulary:** PASS · PARTIAL · FAIL · NOT DEMONSTRATED

## Purpose

PMQ-001 applies the frozen external consequence-boundary proof burden recorded before PMQ-specific remediation and then extends it with operational/adversarial checks relevant to a buyer-facing MVP.

This record is not a production certification. A PASS applies only to the exact public harness surface exercised by the cited mechanism and test.

## Result summary

| Proposition | Final classification | Bounded conclusion |
|---|---|---|
| PMQ-001.1 Candidate movement before bind | **PASS** | An unbound candidate movement cannot use the ordinary public permit-issuance call to form the represented consequence after remediation. |
| PMQ-001.2 Current authority/evidence under present conditions | **PASS** | Current authority-state version, current temporal validity and required screening evidence are checked on the represented harness path; unavailable required screening evidence fails closed. |
| PMQ-001.3 Standing at the boundary | **PASS** | The final protected consequence boundary rechecks signed permit integrity, temporal validity and current authority-state version before represented formation. |
| PMQ-001.4 Changed-condition loss of standing | **PASS** | A state change committed before the final protected boundary invalidates stale authority; a change attempting to commit inside the guarded final interval is serialized after represented formation. |
| PMQ-001.5 Lawful continuation / loss | **PASS** | Continuation is bounded by current state, exact action binding, signed temporal validity and one-time permit consumption on the in-process surface. |
| PMQ-001.6 NO_BIND / represented non-formation | **PASS represented / ND external physical** | REFUSE/BLOCKED/no-permit paths do not form the represented harness consequence. External physical payment non-formation is not demonstrated. |
| PMQ-001.7 Credible bypass attempts and route closure | **PARTIAL** | Governed harness routes, direct no-bind permit use, stale state, action substitution, invalid receipts and permit replay are closed on tested paths. Production-grade capability isolation and universal external route closure are not demonstrated. |
| PMQ-001.8 Receipt of what formed / did not form | **PARTIAL** | Authority Receipts preserve the determination and integrity-protected evidence; the harness exposes represented consequence outcome. A separately sealed consequence-outcome receipt is not currently demonstrated. |
| PMQ-001.9 Same-condition / changed-condition replay | **PASS — bounded** | Historical determination replay, changed-state rejection and same-permit duplicate rejection are demonstrated on the current process surface. Durable replay protection after restart is not demonstrated. |

## Material failures found and preserved

PMQ-001 did not begin green.

### 1. No-bind execution capability bypass

Initial attack obtained a consequence-authorising permit without a Runtime Authority ALLOW/Authority Receipt and formed the represented consequence.

Initial result:

```text
1 failed, 30 passed
CONSEQUENCE_FORMED
```

The failure is preserved in `PMQ-001_INITIAL_FAILURE.md`.

Remediation added a governed in-process mint capability. The identical challenge then passed. This closes the specific public no-bind call path but does **not** prove process/IAM/KMS capability isolation.

### 2. Duplicate / concurrent permit replay

The exact same valid permit formed the represented consequence more than once, both sequentially and concurrently.

Initial result:

```text
2 failed, 31 passed
```

Preserved in `PMQ-001_DUPLICATE_RETRY_FAILURE.md`.

Remediation added atomic one-time permit consumption inside the final authority-state guard. The unchanged sequential and concurrent replay tests then passed.

### 3. Delayed permit expiry

A permit issued while the Authority Receipt was valid remained usable after the authority validity window expired.

Initial mechanism result:

```text
1 failed, 33 passed
CONSEQUENCE_FORMED
```

Preserved in `PMQ-001_DELAYED_PERMIT_EXPIRY_FAILURE.md`.

Remediation bound `valid_until` into the signed permit and rechecked it at the protected consequence boundary.

### 4. Temporal-remediation regression

The first temporal strengthening exposed inconsistent clock semantics between fixed historical scenario fixtures and the live wall-clock protected boundary.

Regression:

```text
8 failed, 26 passed
```

Preserved in `PMQ-001_TEMPORAL_REMEDIATION_REGRESSION_FAILURE.md`.

The final expiry check was **not** removed. Instead, scenario loading was corrected so normal/live harness runs rebase deterministic fixture timestamps to the current UTC harness clock while preserving relative temporal facts. Explicit historical tests remain able to control their own seal time.

The resulting full rerun returned:

```text
34 passed
```

A subsequent unavailable-evidence fail-closed test increased the current tested branch surface to:

```text
35 passed
```

## Additional demonstrated controls

The PMQ result also relies on pre-existing public tests only where they exercise the frozen proposition directly:

- Authority Receipt HMAC integrity and evidence-content integrity;
- current authority-state version rejection of stale ALLOW;
- exact action-binding / beneficiary substitution rejection;
- normal represented route consumption of the Execution Gateway and protected consequence boundary;
- in-process final-check-to-formation serialization;
- historical Authority Receipt replay without rewriting current state;
- represented non-formation for REFUSE/BLOCKED outcomes;
- arbitrary execution-permit signature rejection;
- unavailable required screening evidence fails closed.

## Residual proof obligations

The following are deliberately **not converted into PASS claims**:

### Production capability isolation — NOT DEMONSTRATED

The public reference harness remains a Python reference implementation. Permit issuance/signing and consequence execution are not separated by a demonstrated production process/IAM/KMS/HSM trust boundary. EC-001.4 therefore remains PARTIAL at that stronger scope.

### Durable duplicate suppression after restart — NOT DEMONSTRATED

The consumed-permit registry is process-local and non-durable. PMQ demonstrates one-time use during the life of the current reference process, not across restart or multiple instances.

### Distributed atomicity — NOT DEMONSTRATED

The final state/consequence serialization is an in-process lock. No distributed transaction, consensus, serializability or multi-service atomic commit is claimed.

### Universal route closure — NOT DEMONSTRATED

The exercised governed public harness paths are tested. External payment rails, alternative credentials, privileged deployment operators and unrepresented consequence paths are outside this proof surface.

### External physical non-formation — NOT DEMONSTRATED

`NO EXECUTION` is a represented harness consequence. No bank/payment-network settlement rail is integrated into this reference harness.

### Separately sealed consequence receipt — NOT DEMONSTRATED

The Authority Receipt records the Runtime Authority determination and evidence. The current public harness reports the represented protected-consequence outcome but does not yet produce a separate integrity-protected consequence-outcome receipt.

### Evidence-service transport failures and malformed external payloads — NOT DEMONSTRATED

An `UNAVAILABLE` screening condition is tested fail-closed. Real service timeouts, transport corruption and provider-specific malformed payloads require integration surfaces that are not represented here.

### Trusted/distributed time — NOT DEMONSTRATED

The reference harness uses the current UTC process clock. Hardware-rooted time, clock-source integrity, multi-host skew bounds and cross-service temporal consensus remain deployment obligations.

## Pre-market conclusion

The public MVP is materially stronger as a result of PMQ-001 because the exercise found and preserved genuine consequence-boundary failures rather than merely adding positive-path tests.

Within the declared **in-process represented MVP boundary and tested governed routes**, the current evidence demonstrates:

- current-state rejection of stale authority;
- exact action binding;
- receipt integrity;
- final temporal standing enforcement;
- represented no-bind non-formation on the tested public path;
- atomic one-time permit use during process lifetime;
- fail-closed unavailable evidence;
- final-interval state serialization;
- historical determination replay.

The strongest safe market statement is:

> Within the declared MVP boundary, no consequence-producing bypass remains demonstrated on the governed paths and conditions tested in PMQ-001. Remaining gaps are explicitly identified as capability-isolation, durability, distributed/deployment or external-integration proof obligations.

That statement must not be expanded into universal route closure, production readiness, production credential isolation, distributed atomicity or physical payment-settlement non-formation.