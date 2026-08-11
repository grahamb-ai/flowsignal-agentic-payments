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
---

## Initial Execution Result

**Classification: FAIL**

The first executable AT-003 test was run against the preserved `v0.9-baseline`.

### Test Executed

`test_at003_execution_without_authority_determination`

### Observed Result

The simulated protected payment executed successfully without a Runtime Authority determination being supplied to the executor.

Observed protected state:

- `executed = True`
- `amount = 25000.00`
- `beneficiary = supplier-001`

The test therefore failed the required invariant:

`NO VALID CURRENT ALLOW -> NO EXECUTION`

### Finding

The result demonstrates that the v0.9 reference implementation does not establish the Runtime Authority determination as a necessary execution dependency.

The implementation demonstrates that an authority determination can be formed and evidenced. AT-003 shows that this does not, by itself, prove that the protected financial consequence cannot occur independently of that determination.

This is classified as an **executor-binding control-boundary gap** in the reference implementation.

It does not demonstrate a vulnerability in external payment infrastructure or any production financial system.

### Evidence

Executable test:

`harness/tests/test_at003_executor_binding.py`

Observed pytest outcome:

**FAIL**

Failure reason:

`AT-003 FAILURE: protected financial consequence occurred without a valid current ALLOW determination.`

This failing result is intentionally preserved before any v0.10 enforcement changes are introduced.

### Next Test Obligation

The v0.9 baseline already provides an execution gateway that validates a Runtime Authority determination before permitting execution on the declared gateway path.

AP-006 demonstrates that this gateway blocks an attempted financial action where the execution binding differs from the action authorised by the Runtime Authority determination.

AT-003 establishes a different obligation.

The next implementation step is to determine whether the protected financial consequence can be made unreachable except through an execution path that successfully consumes the applicable Runtime Authority determination.

The required property is therefore not merely:

> The execution gateway validates authority.

It is:

> Every route capable of producing the protected financial consequence is bound to that enforcement dependency.

AT-003 will then be rerun against that strengthened execution boundary.
<img width="1606" height="884" alt="image" src="https://github.com/user-attachments/assets/2ca8ea03-9d34-42f5-b4b8-426cd1b52125" />
