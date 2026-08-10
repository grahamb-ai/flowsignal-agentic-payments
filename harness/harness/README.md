# FlowSignal Agentic Payments — Canonical Scenario Harness

This directory contains the deterministic scenario harness used by the
FlowSignal Agentic Payments Runtime Authority Demonstrator.

It forms part of:

**FlowSignal Agentic Payments Runtime Authority Harness — v0.9**

Executable companion to:

**FS-AN-004 — The Runtime Authority Requirement in Agentic Payments**

---

## Purpose

The scenario harness provides reproducible test cases demonstrating how
the same authenticated autonomous agent may receive different execution
outcomes when the authority conditions applying to a proposed financial
action change at runtime.

The harness evaluates authority immediately before execution rather than
treating identity, authentication or prior approval as sufficient authority
for the financial consequence.

---

## Canonical Scenarios

The reference harness contains six scenarios:

| Scenario | Condition | Expected Outcome |
|---|---|---|
| AP-001 | Authority conditions satisfied | ALLOW |
| AP-002 | Autonomous limit exceeded | ESCALATE |
| AP-003 | Counterparty state changed | REFUSE |
| AP-004 | Required evidence stale | ESCALATE |
| AP-005 | Delegated mandate expired | REFUSE |
| AP-006 | Proposed action differs from authorised action | BLOCKED |

Together these scenarios demonstrate that execution authority is
action-specific, context-dependent and evaluated at the execution boundary.

---

## Directory Structure

- `scenarios/` — canonical runtime scenario inputs
- `expected/` — expected deterministic outcomes
- `policies/` — reference policy used by the scenario harness
- `runner.py` — scenario execution and evaluation
- `run_ap006.py` — action-binding enforcement demonstration
- `VISUAL_DEMO.md` — guidance for the visual demonstration

---

## Deterministic Evaluation

Each scenario is designed to produce a defined result from the same
canonical input conditions.

The principal Runtime Authority outcomes are:

- `ALLOW`
- `ESCALATE`
- `REFUSE`

AP-006 additionally demonstrates execution enforcement. An authority
determination issued for one proposed action cannot be reused to execute
a materially different action. The Execution Gateway therefore returns:

`BLOCKED — ACTION_BINDING_MISMATCH`

This distinguishes the Runtime Authority determination from enforcement
of that determination at the execution boundary.

---

## Reference Status

This directory is part of the **v0.9 Frozen Reference Demonstrator**.

It is an engineering reference implementation intended to demonstrate
the architectural concepts described in FS-AN-004. It is not a production
payment system, regulated financial service, or representation of an FCA
implementation.

For the complete demonstrator documentation, see the parent:

[`../README.md`](../README.md)
