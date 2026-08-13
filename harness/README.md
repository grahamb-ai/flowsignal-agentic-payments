# FlowSignal Agentic Payments Runtime Authority Harness

**Executable companion to FS-AN-004 — The Runtime Authority Requirement in Agentic Payments**

**Baseline:** v0.9 Frozen Reference Demonstrator  
**Branch Status:** AT-004 Adversarial Assurance Candidate  
**Assurance Baseline:** 60 non-database tests passing  
**Date:** 13 August 2026

> **Baseline preservation:** v0.9 remains the frozen reference demonstrator. This branch records subsequent adversarial assurance work, observed failures, remediations and regression tests. It does not alter the historical v0.9 baseline.
---

## Purpose

This repository contains an executable reference harness demonstrating the Runtime Authority architecture described in:

**FS-AN-004 — The Runtime Authority Requirement in Agentic Payments**

The harness examines a specific question arising as autonomous agents move from proposing financial actions to causing financial consequences:

> Once an autonomous agent is known, authenticated and operating under delegated authority, what determines whether that authority remains sufficient for the specific financial action immediately before execution?

The harness demonstrates an independent Runtime Authority determination at the execution bind point.

It does not determine whether an agent is intelligent, trustworthy or generally authorised.

It determines whether sufficient institutional authority exists for a **specific proposed consequence under the conditions established now**.

---

## Core Principle

> **Same trusted agent. Different execution authority.**

Identity and authentication establish important facts about an autonomous agent.

They do not, by themselves, establish whether a particular financial action remains authorised at the moment of execution.

Runtime Authority therefore evaluates the proposed action against the applicable mandate, institutional state, constraints and trusted evidence immediately before consequence formation.

---

## Architecture

The demonstrator separates three functions:

### 1. Proposed Payment

The autonomous system proposes a financial action.

The harness receives the relevant actor, mandate, action and runtime context.

### 2. Runtime Authority

At the execution bind point, the Runtime Authority asks:

> Does sufficient valid institutional authority exist for this specific proposed consequence under the conditions established now?

The determination is deterministic.

Canonical outcomes are:

- **ALLOW**
- **ESCALATE**
- **REFUSE**

### 3. Execution Enforcement

The resulting authority is enforced before the financial consequence is permitted to occur.

An ALLOW applies only to the action that was evaluated.

It cannot be reused as authority for a materially different action.

---

## Canonical Scenarios

The frozen v0.9 harness contains six scenarios.

### AP-001 — Within Authority

All required authority conditions remain satisfied.

**Outcome: ALLOW**

The proposed payment may proceed to execution.

---

### AP-002 — Limit Exceeded

The proposed payment exceeds the autonomous ceiling established by the delegated mandate.

The agent remains authenticated and the mandate remains valid, but sufficient autonomous authority is not established for the proposed amount.

**Outcome: ESCALATE**

Execution is withheld pending additional authority.

---

### AP-003 — State Changed

The counterparty was previously approved but is restricted at the execution bind point.

Earlier approval does not override current institutional state.

**Outcome: REFUSE**

No execution is permitted.

---

### AP-004 — Evidence Stale

The relevant screening evidence remains substantively CLEAR but is no longer sufficiently current.

The scenario demonstrates the distinction between evidence being correct and evidence being sufficiently current for execution.

**Evidence age:** 8,100 seconds  
**Maximum permitted age:** 3,600 seconds

**Outcome: ESCALATE**

Execution is withheld pending sufficiently current evidence.

---

### AP-005 — Mandate Expired

The autonomous agent remains authenticated, but its delegated mandate has expired.

This demonstrates the distinction between identity and continuing execution authority.

**Outcome: REFUSE**

No execution is permitted.

---

### AP-006 — Action Substituted

Runtime Authority evaluates and ALLOWs an authorised action:

**£750,000 → SUPPLIER-X**

A materially different action is subsequently presented to the Execution Gateway:

**£750,000 → SUPPLIER-Y**

The Runtime Authority determination remains valid for the action it actually evaluated.

The Execution Gateway detects that the attempted action does not match the action cryptographically bound into the Authority Receipt.

**Runtime Authority: ALLOW**

**Execution Gateway: BLOCKED**

**Reason: ACTION_BINDING_MISMATCH**

**Financial consequence: NO EXECUTION**

This scenario demonstrates that:

> **ALLOW A cannot be reused to execute materially different Action B.**

---

## Runtime Authority Checks

The reference scenarios exercise action-specific runtime checks including:

- actor authentication;
- Know Your Agent status;
- mandate validity;
- mandate expiry;
- permitted action;
- autonomous amount ceiling;
- permitted currency;
- permitted source account;
- counterparty state;
- account state;
- institutional risk state;
- screening status; and
- evidence freshness.

The purpose is not to prescribe a universal set of financial controls.

The harness demonstrates how institution-specific authority conditions can be evaluated deterministically at the execution boundary.

---

## Authority Receipts

Each Runtime Authority determination produces an evidential Authority Receipt.

The receipt records information required to reconstruct the determination, including the scenario, decision, reason code and relevant execution evidence.

For permitted actions, the receipt also provides the basis for binding the determination to the action that was actually evaluated.

This allows downstream enforcement to distinguish between:

- the action that was authorised; and
- the action subsequently presented for execution.

---

## Action Binding

AP-006 demonstrates cryptographic action binding.

The authorised action is canonicalised and hashed when Runtime Authority establishes authority.

Immediately before execution, the Execution Gateway independently derives the hash of the action presented for execution.

If the two hashes differ:

**Execution Gateway → BLOCKED**

This does not retrospectively change the original Runtime Authority determination.

The original ALLOW remains valid for the action that was evaluated.

The attempted execution is blocked because it is not the authorised action.

---

## Running the Demonstrator

### Requirements

- Python 3.11 or later
- FastAPI
- Uvicorn

Install the required dependencies:

```powershell
py -m pip install -r requirements.txt
```

---

## AT-004 — Adversarial Runtime Authority Assurance

Following the frozen v0.9 reference baseline, the harness was subjected to a further series of adversarial tests examining whether the Runtime Authority architecture remained effective when assumptions about authority source, evaluator control, execution routing, receipt integrity and runtime state freshness were challenged.

The purpose of AT-004 was not to demonstrate that the architecture could pass tests written around its existing behaviour.

The purpose was to identify conditions under which a consequential execution could escape, weaken or outlive the Runtime Authority determination intended to govern it.

Where a test exposed a weakness, the failure was preserved before remediation and the same class of challenge was subsequently retested.

### Assurance Sequence

| Test | Question exercised | Initial result | Current status |
| --- | --- | --- | --- |
| AT-004.1 | Can locally presented authority state change the Runtime Authority outcome? | Differential observed | PASS |
| AT-004.2 | Is authority-source separation sufficient if the execution environment controls the evaluator? | Differential observed | PASS |
| AT-004.3 | Can a represented consequential execution bypass the current authority determination? | FAIL | PASS after remediation |
| AT-004.4 | Can an altered Authority Receipt remain acceptable to the Execution Gateway? | FAIL | PASS after remediation |
| AT-004.5 | Can evidential content change while the Authority Receipt continues to verify? | FAIL | PASS after remediation |
| AT-004.6 | Can a valid ALLOW receipt remain executable after authoritative runtime state advances? | FAIL | PASS after remediation |

### AT-004.1 — Authority Source Separation

AT-004.1 challenged whether the Runtime Authority evaluator should trust authority state supplied by the execution environment.

For the exercised scenario, the proposed payment was GBP 1.4m.

The locally presented mandate limit was GBP 2m.

The authoritative mandate limit was GBP 1m.

When the presented authority value governed the evaluation, the request produced ALLOW.

When the independently sourced authoritative value governed the evaluation, the same request produced ESCALATE.

The test therefore established a material distinction, within the exercised implementation, between authority presented by the execution environment and authority obtained from an authoritative source.

### AT-004.2 — Evaluator Independence

AT-004.2 then challenged a stronger assumption.

Separating authoritative state does not by itself ensure that the correct state will govern execution if the execution environment can control or replace the evaluator.

Using the same request and authoritative state, an evaluator configured to consume the authoritative limit produced ESCALATE, while a locally controlled variant consuming the presented limit produced ALLOW.

This demonstrated, within the exercised implementation, that authority-state separation and evaluator control are distinct architectural concerns.

The deliberately weakened evaluator used for this experiment is not part of the maintained public regression surface.

### AT-004.3 — Determination Non-Bypassability

AT-004.3 tested whether every represented path capable of producing the governed consequence consumed the Execution Gateway determination.

The initial adversarial test failed.

A normal demonstrator path could report:

`EXECUTION PERMITTED`

without consuming the Execution Gateway.

The demonstrator was remediated so that normal execution paths consume the gateway before the represented consequence is permitted.

The unchanged assurance invariant subsequently passed.

### AT-004.4 — Authority Receipt Integrity

AT-004.4 challenged whether possession of an Authority Receipt was sufficient, or whether the gateway could independently establish that the receipt had not been altered.

The initial architecture did not provide a receipt-level integrity proof verifiable by the Execution Gateway.

The test failed.

A proof-of-concept HMAC-SHA256 integrity mechanism was introduced and verification was placed before gateway enforcement.

Altered receipts are now blocked with:

`AUTHORITY_RECEIPT_INTEGRITY_INVALID`

The fixed HMAC key in this public harness exists solely to demonstrate integrity behaviour. It is not a production secret, trust boundary or key-management design.

### AT-004.5 — Authority Receipt Evidence Integrity

AT-004.5 extended the integrity challenge beyond the enforcement-critical fields.

The initial HMAC protected only a subset of the Authority Receipt.

An adversarial test changed evidential content after sealing and demonstrated that the receipt could still verify.

The test failed.

The integrity boundary was subsequently expanded to include:

- `request_snapshot`
- `checks`
- `evidence_references`

The same class of modification then invalidated the receipt.

### AT-004.6 — Runtime Authority Context Freshness

AT-004.6 examined a different form of staleness.

A receipt can remain authentic, unexpired and correctly bound to an action while the authoritative state under which it was issued has subsequently changed.

The initial gateway did not distinguish receipt freshness from authority-state freshness.

The adversarial test failed.

The remediation introduced an `authority_state_version` into the Runtime Authority determination and its integrity-protected receipt.

Immediately before consequence formation, the Execution Gateway compares the receipt state version with the current authoritative state version.

If they differ, execution is blocked with:

`AUTHORITY_STATE_STALE_REEVALUATION_REQUIRED`

The gateway does not make the new policy decision itself.

It requires a new Runtime Authority determination against current state.

### Resulting Enforcement Chain

The exercised architecture now forms the following chain:

```text
Authoritative State
        |
        v
Runtime Authority Determination
        |
        v
State-bound + integrity-protected Authority Receipt
        |
        v
Mandatory Execution Gateway
        |
        v
Current-state validation
        |
        v
Consequence
```

The emerging engineering proposition is therefore narrower than simply requiring an `ALLOW` decision.

For the exercised harness, consequential execution must remain bound to:

- the action that was evaluated;
- the authoritative state under which authority was determined;
- the evidential record sealed with that determination; and
- an execution path that consumes the current authority determination.

### Preserved Evidence

The AT-004 evidence record is maintained separately under:

`/evidence/AT-004/`

Where an adversarial test initially failed, the failure record is retained alongside the remediated result.

AT-004.5 includes a reconstructed failure note because the original local Markdown failure file was subsequently found to be empty. The reconstruction is explicitly identified in that evidence record and is based on the recorded test result and remediation sequence.

### Current Assurance Baseline

Current non-database regression result:

```text
60 passed
```

The database-backed API tests are not included in this figure because the local PostgreSQL service required by those tests was not available during the AT-004 assurance run.

The 60-test result should therefore be read as the exercised non-database regression baseline, not as evidence that every deployment path, integration or production configuration has been tested.

### Scope

AT-004 provides evidence about the behaviour of this proof-of-concept under the specific adversarial conditions exercised.

It does not establish that:

- every possible consequence-producing path is non-bypassable;
- the proof-of-concept HMAC mechanism is production-grade key management;
- authority-state versioning provides distributed consensus or atomic cross-system commit;
- architectural independence alone is sufficient for institutional governance;
- every implementation of Runtime Authority requires the same technical mechanisms; or
- the harness proves legal or regulatory compliance.

The purpose of the series is falsifiable engineering evidence: preserve what failed, identify why it mattered, strengthen the exercised boundary, and rerun the challenge.
