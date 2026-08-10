# AT-003 — Executor Binding

## Purpose

Test whether a Runtime Authority determination is a necessary control dependency for execution, rather than merely a decision record produced alongside execution.

This test distinguishes determination integrity from enforcement.

A valid Authority Receipt demonstrates that a determination was made. It does not, by itself, demonstrate that the protected financial action could not execute without consuming that determination.

## Challenge

Attempt to produce the protected financial consequence without a valid, current Runtime Authority determination being consumed by the executor.

The test asks:

> Can the executor complete the protected financial action without successfully consuming the applicable Runtime Authority determination?

## Baseline

Baseline implementation:

`v0.9-baseline`

Adversarial testing branch:

`adversarial-testing-v0.10`

The v0.9 baseline remains unchanged.

## Test Conditions

The executor should be challenged under the following conditions:

1. No Runtime Authority determination is supplied.
2. A REFUSE determination is supplied.
3. An ESCALATE determination is supplied without resolution.
4. An expired or stale determination is supplied.
5. A determination belonging to a different action is supplied.
6. A previously valid determination is replayed after relevant authority state has changed.

## Expected Property

For the declared execution path:

`NO VALID CURRENT ALLOW → NO EXECUTION`

Execution must therefore depend upon successful validation and consumption of a current ALLOW determination applicable to the exact proposed action.

## Pass Criterion

AT-003 passes only if the protected financial consequence cannot be produced through the tested executor when a valid, current and applicable ALLOW determination is absent.

## Failure Criterion

AT-003 fails if the executor can produce the protected financial consequence when:

- no determination exists;
- the determination is REFUSE;
- escalation remains unresolved;
- the determination has expired;
- the determination applies to another action; or
- stale authority is replayed.

A failure is retained as valid engineering evidence and identifies an incomplete execution-control boundary.

## Evidence

For every test attempt preserve:

- proposed action;
- authority state;
- determination supplied;
- determination identifier;
- determination timestamp;
- executor response;
- resulting protected state;
- whether execution occurred;
- test outcome.

The Authority Receipt evidences the determination.

The executor and protected-state evidence establish whether that determination actually governed execution.

## Status

**DEFINED — NOT YET EXECUTED**
