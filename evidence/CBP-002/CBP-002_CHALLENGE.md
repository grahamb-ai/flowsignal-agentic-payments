# CBP-002 — External Consequence Boundary Challenge

## Status

FROZEN CHALLENGE — NOT YET EVALUATED

## Starting point

Repository: `grahamb-ai/flowsignal-agentic-payments`

Frozen base commit: `cadfaade73867a56c61a4dcc04a5f4434e30d0d5`

CBP-001 established bounded consequence-boundary claim/mechanism correspondence inside the FlowSignal reference harness. CBP-002 deliberately moves the proof boundary outward.

This proposition is committed **before** the external consequence adapter, executable qualification test, or result is added.

## Challenged seam

`independently observable external consequence -> current authority -> changed condition -> attempted external bind -> NO_EXTERNAL_EFFECT -> alternate-route failure -> evidence -> changed-world replay/current-state separation -> fresh-authority positive control`

## Frozen proposition

For a specifically integrated external consequence surface, a previously valid exact-action FlowSignal execution permit MUST NOT cause the external consequence after the authoritative runtime state on which that permit depends has changed.

The qualification MUST observe the external system's state independently of FlowSignal's internal consequence-outcome record.

A stale-authority attempt MUST leave the external target state unchanged. A materially substituted action MUST not be transferable under the historical permit. A replay of the historical permit MUST remain unusable after current authority is reacquired. A newly evaluated, current exact-action permit MAY form the external consequence, establishing a non-vacuous positive control.

## Required external consequence surface

The first CBP-002 implementation MUST use a bounded, non-production external service or independently running target that exposes an observable state-changing operation.

The target MUST be outside the FlowSignal protected-consequence state store. FlowSignal's own `CONSEQUENCE_FORMED` record is not sufficient evidence for CBP-002.

Acceptable examples include a sandbox API, local independently running HTTP consequence service, or other non-production target where the before/after state can be queried independently.

The exact target chosen MUST be recorded in the executable test and result.

## Required observations

1. Establish an external target with independently queryable initial state.
2. Establish current FlowSignal authority for one exact external action and obtain the bound execution permit.
3. Positive control: present a current valid permit through the protected external adapter and verify, by querying the external target itself, that the intended state change occurred exactly once.
4. Reset or create a distinct external target state suitable for the challenged attempt.
5. Obtain a second current exact-action permit for the challenged external consequence.
6. Change authoritative runtime state after permit issuance but before external consequence formation.
7. Present the historical permit through the protected external adapter.
8. PASS only if FlowSignal denies the attempted bind and an independent query of the external target confirms **NO_EXTERNAL_EFFECT**.
9. Preserve evidence binding the denial to the attempted action and recording non-formation/non-execution.
10. Attempt the same protected adapter path again with the historical permit; the external target MUST remain unchanged.
11. Attempt at least one materially substituted external action under the historical permit; the external target MUST remain unchanged.
12. Reacquire current authority for the same intended external action and obtain a newly issued authority receipt/permit bound to the current authority state.
13. Re-present the historical permit after current-state reacquisition; it MUST remain unable to affect the external target.
14. Present the fresh current permit through the same protected external adapter; verify independently that the intended external state change now occurs exactly once.
15. Query the external target after execution and preserve the observed final state as qualification evidence.

## Alternate-route requirement

CBP-002 MUST distinguish between:

- the **protected external route** controlled by the FlowSignal integration; and
- any **unprotected administrative/direct route** deliberately left available by the chosen sandbox or test target.

The test MUST NOT claim universal alternate-route closure merely because the protected adapter refuses stale authority.

If the external target itself permits an administrator or holder of separate credentials to mutate state outside FlowSignal, that route MUST be documented as outside the proven closure boundary.

A stronger claim of alternate-route closure may only be made if the integration architecture technically makes FlowSignal authorisation a necessary precondition for the relevant external credential, endpoint, capability or state transition and that property is itself exercised.

## Failure classifications

- `FAIL — STALE AUTHORITY CAUSED EXTERNAL EFFECT`
- `FAIL — EXTERNAL EFFECT OCCURRED WITHOUT CURRENT EXACT-ACTION AUTHORITY`
- `FAIL — ACTION SUBSTITUTION CAUSED EXTERNAL EFFECT`
- `FAIL — HISTORICAL PERMIT CAUSED EXTERNAL EFFECT AFTER REACQUISITION`
- `FAIL — POSITIVE CONTROL COULD NOT FORM EXTERNAL CONSEQUENCE`
- `FAIL — EXTERNAL STATE COULD NOT BE INDEPENDENTLY OBSERVED`
- `NOT EVALUATED — EXTERNAL TARGET OR TEST FIXTURE DID NOT REACH THE INTENDED CONDITION`

## Evidence discipline

- Do not modify this frozen proposition after observing the first executable result.
- Do not modify the existing FlowSignal authority/consequence mechanism merely to manufacture a PASS before the first run.
- The external adapter may be new code because external integration is the proposition under test; its architecture and exact role MUST be visible in the evidence chain.
- Preserve the first executable result whether PASS or FAIL.
- If remediation is required, preserve failure -> fix -> rerun as separate commits/runs.
- Test count is not evidence of the proposition. External state observation is required.
- A PASS earns only the proposition actually exercised by the chosen external integration.

## Explicit scope limitation

Even a CBP-002 PASS will not by itself establish universal production non-bypassability, control of bank settlement rails, production IAM/process isolation, HSM/KMS guarantees, cross-provider distributed atomicity, or fitness for every deployment.

It will establish only the consequence-boundary properties actually exercised against the named external target and integration architecture.

## Success classification

If every required observation is met without changing this proposition after the result is known, classify the result as:

**CBP-002 — EXTERNAL CONSEQUENCE BOUNDARY: PASS (BOUNDED TO NAMED EXTERNAL TARGET AND INTEGRATION)**

Otherwise preserve and report the applicable failure or NOT EVALUATED classification.