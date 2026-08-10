# Adversarial Test Suite

## Purpose

This directory contains adversarial tests derived from external technical challenges raised following publication of the FlowSignal Agentic Payments Harness and FS-AN-004.

The tests are intended to challenge the implementation rather than demonstrate predetermined success.

A failed adversarial test is a valid engineering result where it identifies a bypass, incomplete control boundary, unsupported assumption or evidential limitation.

---

## Baseline

The preserved pre-challenge implementation is:

**v0.9-baseline**

Adversarial testing is developed on:

**adversarial-testing-v0.10**

The v0.9 baseline must not be rewritten to incorporate later findings.

---

## Test Progression

The adversarial suite follows this progression:

**Determination Integrity**  
↓  
**Executor Binding**  
↓  
**Alternate-Route Challenge**  
↓  
**Protected-State Observation**  
↓  
**Preserved Evidence**

The objective is not merely to confirm that Runtime Authority returned the expected determination.

The stronger test is whether that determination actually governed the protected financial consequence within the declared execution surface.

---

## Test Families

### AT-001 — Authority Predicate Isolation

Tests mandate validity, action scope and continuing approval applicability independently and in combination.

### AT-002 — Escalation Timeout and Fail-Closed Behaviour

Tests unresolved escalation, expiry, unavailable escalation infrastructure and late responses.

### AT-003 — Executor Binding

Attempts execution without a valid current Runtime Authority determination.

### AT-004 — Stale and Replayed Determinations

Attempts execution using expired, replayed or action-mismatched ALLOW determinations.

### AT-005 — Alternate-Route Challenge

Attempts to recreate a refused financial consequence through alternative execution routes represented within the test environment.

### AT-006 — Protected-State Verification

Observes the resulting protected state after each execution attempt to determine whether the financial consequence actually occurred.

### AT-007 — Evidence Preservation

Ensures each adversarial test preserves the determination, execution result, protected-state observation and source revision required for later reconstruction.

---

## Result Classification

Each adversarial test must produce one of the following outcomes:

**PASS**  
The implementation demonstrated the property being tested within the declared test conditions.

**FAIL**  
The implementation did not demonstrate the property, or an execution path successfully bypassed the claimed control.

**LIMITATION**  
The current reference environment is not capable of testing the property sufficiently to support a PASS or FAIL conclusion.

A FAIL or LIMITATION must not be converted into PASS by changing the implementation before the original result has been preserved.

---

## Evidence Principle

Results must preserve enough evidence to identify:

- test identifier;
- source revision;
- input conditions;
- Runtime Authority determination;
- executor response;
- protected-state observation;
- expected result;
- actual result;
- PASS / FAIL / LIMITATION classification;
- relevant timestamps.

---

## Scope

Passing these tests does not establish universal enforcement across arbitrary external financial infrastructure.

Claims apply only to the execution surface explicitly represented and tested by this reference implementation.
