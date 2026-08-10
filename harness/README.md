# FlowSignal Agentic Payments Runtime Authority Harness

**Executable companion to FS-AN-004 — The Runtime Authority Requirement in Agentic Payments**

**Version:** 0.9  
**Status:** Frozen Reference Demonstrator  
**Date:** August 2026

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
