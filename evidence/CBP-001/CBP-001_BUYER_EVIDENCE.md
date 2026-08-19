# CBP-001 — When Permission Exists but Authority Has Changed

## Buyer Evidence Brief

**FlowSignal™ — Execute with Authority. Defend with Evidence.**

### The business question

An AI agent, automation or workflow has already been told that it may perform an action.

Then something changes.

The mandate changes. Authority is revoked. The permitted amount changes. The beneficiary changes. Evidence becomes stale. A human authority holder becomes unavailable. Or another condition required for legitimate execution no longer holds.

The operational question is not simply:

> Was this action approved?

It is:

> **Does the organisation still have legitimate authority to form this consequence now, for this exact action?**

CBP-001 tests that boundary.

---

## The scenario

Consider an autonomous treasury workflow preparing a payment.

At **T0**, the payment is within delegated authority. The runtime determination is ALLOW and an execution permit is bound to the exact attempted action.

Before the consequence forms, the authoritative state changes.

At **T1**, the agent still possesses its earlier permission — but the world underneath that permission is no longer the same.

A conventional workflow may continue because it still has an approval, token, queued instruction or previously valid decision.

FlowSignal asks again at the consequence boundary:

> **Is this authority still current and does it still apply to this exact consequence?**

---

## What we tested

The proposition was frozen before the executable CBP-001 test was added.

The frozen seam was:

`represented protected consequence -> current standing -> changed condition -> attempted bind -> NO_BIND -> bypass failure -> receipt -> replay/current-state separation`

We then exercised the following sequence against the existing FlowSignal protected-consequence implementation.

### 1. Establish the positive control

A current authority determination returned ALLOW.

A permit was issued for the exact attempted consequence.

The fresh permit was presented to the protected-consequence boundary.

**Result: CONSEQUENCE FORMED.**

This establishes that the boundary can permit consequence formation when the required authority remains current.

### 2. Obtain authority — then change the world

A second valid authority determination and execution permit were obtained.

Before that permit was used, the authoritative state version was advanced.

The agent still held a permit that had been valid when issued.

It was no longer current.

### 3. Attempt consequence formation with stale authority

The stale permit was presented directly to the protected-consequence boundary.

**Result: DENIED_AUTHORITY_STATE_STALE.**

**The represented consequence did not form.**

### 4. Produce evidence of non-formation

The denied attempt produced a signed consequence outcome receipt.

The receipt bound the result to the attempted action and recorded that consequence formation was false.

The receipt itself was verified.

### 5. Try the direct route again

The stale permit was presented again directly to the protected-consequence boundary.

**Result: DENIED_AUTHORITY_STATE_STALE.**

Repeating the historical permission did not resurrect authority.

### 6. Change the beneficiary

The attempted action was altered while retaining the historical permit.

**Result: DENIED_ACTION_BINDING_MISMATCH.**

### 7. Change the amount

The payment amount was altered while retaining the historical permit.

**Result: DENIED_ACTION_BINDING_MISMATCH.**

The permission was not transferable to a different consequence.

### 8. Reacquire current authority

FlowSignal then evaluated the same intended consequence against the current authority state.

A new authority receipt and new execution permit were produced, bound to the new authority-state version.

The historical stale permit remained unusable.

### 9. Present the fresh permit

The newly issued current permit was presented to the same protected-consequence boundary.

**Result: CONSEQUENCE FORMED.**

---

# What this demonstrates

CBP-001 demonstrates a specific architectural property of the FlowSignal reference implementation:

> **A previous ALLOW is not sufficient to form the represented protected consequence after the authoritative state on which that permission depended has changed.**

At the boundary, FlowSignal requires both:

- authority that remains current; and
- exact binding between that authority and the attempted consequence.

The distinction is important.

An organisation can have a perfectly valid historical record showing why an action was approved and still lack legitimate authority to execute that action now.

FlowSignal separates those two questions.

---

# What the buyer sees

The practical sequence is deliberately simple:

```text
AGENT INTENDS ACTION
        |
        v
CURRENT AUTHORITY VALID?
        |
       YES
        |
        v
BOUND EXECUTION PERMIT
        |
        |      authoritative state changes
        v
CONSEQUENCE BOUNDARY
        |
        v
OLD PERMIT PRESENTED
        |
        v
      NO_BIND
        |
        +----> signed evidence of non-formation
        |
        v
CURRENT AUTHORITY REACQUIRED
        |
        v
NEW BOUND PERMIT
        |
        v
CONSEQUENCE FORMED
```

The important control is not another dashboard decision.

It is the dependency between **current authority** and **consequence formation**.

---

# Why this matters for agentic AI

Agentic systems increase the distance between human intent and machine consequence.

An agent may plan correctly, receive permission correctly and begin execution correctly — while the conditions that made that action legitimate change before the consequence actually forms.

That creates an execution gap.

FlowSignal is designed to sit immediately before consequence formation and independently determine whether delegated authority remains legitimately exercisable for the exact attempted action.

The output is deterministic:

**ALLOW / ESCALATE / REFUSE**

Where execution is permitted, the authority is bound to the attempted consequence. Where current authority no longer holds, prior permission alone does not authorise formation.

---

# Evidence, not assertion

CBP-001 was structured as a failure-first engineering challenge.

The proposition was committed before the executable test.

The executable test was then run in GitHub Actions against the frozen PR state.

Observed GitHub Actions result:

```text
1 passed in 0.09s
```

The accompanying EC-001 and regression workflow also completed successfully against the same PR state.

The evidence record, challenge and executable test are retained in the public repository.

---

# What CBP-001 does not prove

This boundary matters just as much as the PASS.

CBP-001 is evidence for the **represented protected-consequence primitive in the FlowSignal reference harness**.

It does not claim to prove:

- control of an external bank settlement rail;
- production-grade distributed transactionality;
- production process or IAM isolation;
- HSM/KMS-backed production key isolation;
- closure of every possible infrastructure or external execution route;
- that the public reference harness is itself a production deployment.

Those claims require evidence from the environment in which FlowSignal is deployed.

That is the next useful stage of validation: put the authority boundary in front of a real sandbox or pilot consequence and attempt to defeat it there.

---

# A practical pilot

A FlowSignal pilot does not need an enterprise-wide AI transformation.

Choose **one consequential workflow**.

Examples include:

- an agentic payment;
- an AI-assisted clinical-record commit;
- an autonomous infrastructure change;
- supplier onboarding or release;
- a regulated customer action;
- another machine-initiated operation where authority can change between approval and execution.

Then define the consequence that must be protected.

We establish the authority conditions, bind them to that exact action and deliberately change those conditions before execution.

The pilot question is straightforward:

> **Can the consequential action still form when the organisation no longer has current authority to perform it?**

The result should not depend on a slide deck.

It should be observable and evidenced.

---

## Public engineering record

Canonical CBP-001 result:

`evidence/CBP-001/CBP-001_RESULT.md`

Frozen challenge:

`evidence/CBP-001/CBP-001_CHALLENGE.md`

Executable test:

`harness/tests/test_cbp001_consequence_boundary_proof.py`

GitHub Actions run ID:

`32275844799`

Merged evidence baseline:

`1ef1852512defaeed0c2efbd305efaa9628a98ff`

---

**FlowSignal™**

**The independent authority infrastructure required before consequence formation.**

**Execute with Authority. Defend with Evidence.**
