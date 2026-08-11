# FlowSignal Agentic Payments Harness — v0.10

## Adversarial Execution-Boundary Release

v0.10 develops the FlowSignal Agentic Payments Harness beyond determination-level testing into adversarial testing of execution binding and consequence-surface closure.

The preserved pre-challenge implementation remains available as:

`v0.9-baseline`

Development and adversarial testing for this release was performed on:

`adversarial-testing-v0.10`

---

## External Challenge

Following publication of FS-AN-004 and the accompanying reference implementation, external technical challenge raised two related architectural questions:

1. Does the Runtime Authority determination actually bind the executor?
2. Can the same protected financial consequence still be produced through an alternative execution route?

These questions were converted into explicit adversarial test obligations rather than answered only at the architectural or documentation level.

---

## AT-003.1 — Executor Binding

The first adversarial test attempted to produce the protected financial consequence without consuming a Runtime Authority determination.

**Initial result: FAIL**

The test demonstrated that an independently modelled execution path could produce the protected consequence without consuming a valid, current ALLOW determination.

This failure is retained as executable engineering evidence and is classified as an expected failure (`xfail`) in the final regression suite.

The test has not been removed or altered to manufacture a passing result.

---

## AT-003.2 — Protected Execution Path

A protected execution path was introduced in which financial consequence formation occurs only after successful validation of the applicable Runtime Authority determination.

The following conditions were tested:

1. Valid, current and correctly bound ALLOW permits execution.
2. Action-binding mismatch blocks execution.
3. Expired ALLOW blocks execution.
4. REFUSE blocks execution.

Observed result:

```text
4 passed in 0.04s
