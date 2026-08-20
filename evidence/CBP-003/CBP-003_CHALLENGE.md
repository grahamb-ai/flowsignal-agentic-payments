# CBP-003 — Protected External Route Closure Challenge

## Status

**FROZEN CHALLENGE — NOT YET EVALUATED**

## Starting point

Repository: `grahamb-ai/flowsignal-agentic-payments`

Frozen base commit:

`cb89c5c4ae1edba4c3c38931ae53e94421d0732d`

CBP-001 established bounded consequence-boundary claim/mechanism correspondence inside the reference harness.

CBP-002 moved the boundary outward to an independently running HTTP consequence target and established that stale or mismatched authority could not form the external consequence through the named protected integration. CBP-002 explicitly did **not** establish universal alternate-route closure: the test target retained administrative/direct mutation capability outside the FlowSignal-protected route.

CBP-003 deliberately tests the next narrower architectural proposition: whether, for one specifically constructed external capability, the consequence-forming credential/capability can be made unavailable except through a current FlowSignal-authorised execution path.

This proposition is committed **before** the CBP-003 capability broker/target integration, executable qualification test, or result is added.

## Challenged seam

`external consequence capability -> FlowSignal-authorised capability release -> current exact-action authority -> consequence formation -> stale/replayed/substituted authority -> NO_CAPABILITY / NO_EXTERNAL_EFFECT -> direct protected-route bypass failure -> fresh-authority positive control`

## Frozen proposition

For one named non-production external consequence integration, possession of an historical FlowSignal execution permit MUST NOT be sufficient to obtain or reuse the consequence-forming capability after authoritative runtime state changes.

For the protected capability under test:

1. the external consequence-forming credential/token/capability MUST not be statically available to the calling workflow;
2. release or activation of that capability MUST depend on a current exact-action FlowSignal-authorised execution;
3. a stale permit MUST fail before a usable consequence-forming capability is released or exercised;
4. a materially substituted action MUST fail before a usable consequence-forming capability is released or exercised;
5. replay of an historical permit after current authority reacquisition MUST remain unable to obtain or exercise the capability;
6. a direct attempt to use the protected consequence route without the released capability MUST fail and leave external state unchanged; and
7. a fresh current exact-action permit MUST be able to obtain/use the bounded capability and form the intended external consequence exactly once.

A PASS earns only route/capability closure for the named protected integration and capability tested. It MUST NOT be reported as universal production non-bypassability.

## Required architecture

The first CBP-003 implementation MUST contain a distinguishable capability boundary between the caller and the external consequence-forming operation.

The consequence-forming capability MAY be represented by a short-lived token, one-time credential, signed capability, isolated service credential, broker-issued grant, or equivalent bounded mechanism.

The architecture MUST satisfy all of the following:

- the ordinary calling workflow does not begin with the protected external capability;
- the capability is issued, activated or made usable only after the FlowSignal protected execution path has established current exact-action authority;
- the external target independently validates the capability before mutating its state;
- capability scope is bound to the intended action or consequence sufficiently to prevent transfer to the materially substituted action used in the qualification;
- capability reuse/replay behaviour is explicitly exercised; and
- external before/after state remains independently queryable.

The exact capability mechanism and target MUST be recorded in the executable test and result.

## Required observations

1. Establish independently queryable initial external target state.
2. Demonstrate that a direct consequence attempt without the protected capability is rejected and leaves external state unchanged.
3. Establish current FlowSignal authority for one exact external action and obtain a bound execution permit.
4. Through the protected route, obtain/activate the bounded consequence capability only after current exact-action authority has been established.
5. Positive control: use that protected capability to form the exact intended external consequence and independently verify exactly one external effect.
6. Establish a distinct challenged external state.
7. Obtain a second current exact-action FlowSignal permit.
8. Change authoritative runtime state after permit issuance and before capability release/consequence formation.
9. Present the historical permit through the protected capability route.
10. PASS this stale-authority observation only if no usable consequence capability is released/exercised and independent external state remains unchanged.
11. Attempt the materially substituted action under the historical permit. No usable capability for the substituted consequence may be obtained/exercised and external state MUST remain unchanged.
12. Attempt the protected external consequence endpoint directly without a valid released capability. The target MUST reject the attempt and external state MUST remain unchanged.
13. Reacquire current FlowSignal authority for the original intended exact action and obtain a new current permit.
14. Re-present the historical permit after reacquisition. It MUST remain unable to obtain/exercise the protected capability and external state MUST remain unchanged.
15. Present the fresh current permit through the same protected capability route. The intended external consequence MUST form exactly once.
16. Attempt replay/reuse of the consequence-forming capability where the mechanism permits such an attempt. A one-time capability MUST not cause a second external effect.
17. Query and preserve final external target state independently of FlowSignal's internal consequence record.

## Route-closure requirement

CBP-003 is specifically about the **named protected capability route**.

A PASS requires executable evidence that the ordinary caller cannot form the tested consequence merely by bypassing the FlowSignal adapter and invoking the protected target operation without the required capability.

The qualification MUST distinguish this from unrelated administrator/root/test-fixture powers. If a privileged administrator can reconfigure the target, mint credentials, replace code or reset state, those powers MUST be documented as outside the tested route-closure boundary.

The existence of such administrative powers does not automatically fail this bounded proposition, but they prevent any claim of universal or production-wide non-bypassability.

## Failure classifications

- `FAIL — PROTECTED CONSEQUENCE FORMED WITHOUT RELEASED CAPABILITY`
- `FAIL — STALE AUTHORITY OBTAINED OR EXERCISED CONSEQUENCE CAPABILITY`
- `FAIL — ACTION SUBSTITUTION OBTAINED OR EXERCISED CONSEQUENCE CAPABILITY`
- `FAIL — HISTORICAL PERMIT OBTAINED OR EXERCISED CAPABILITY AFTER REACQUISITION`
- `FAIL — CAPABILITY REPLAY CAUSED DUPLICATE EXTERNAL EFFECT`
- `FAIL — POSITIVE CONTROL COULD NOT FORM EXTERNAL CONSEQUENCE`
- `FAIL — EXTERNAL STATE COULD NOT BE INDEPENDENTLY OBSERVED`
- `NOT EVALUATED — CAPABILITY OR TARGET FIXTURE DID NOT REACH THE INTENDED CONDITION`

## Evidence discipline

- Do not modify this frozen proposition after observing the first executable result.
- Do not modify the existing CBP-001/CBP-002 evidence records to accommodate CBP-003.
- New CBP-003 capability-boundary code is permitted because that architecture is the proposition under test.
- Preserve the first executable result whether PASS or FAIL.
- If remediation is required, preserve `failure -> fix -> rerun` as separate commits/runs.
- Test count is not evidence of route closure.
- A PASS earns only the exact route/capability proposition exercised by the named integration.

## Explicit scope limitation

Even a CBP-003 PASS will not by itself establish:

- universal production non-bypassability;
- control of a real bank settlement rail;
- absence of root/administrator/cloud-provider override capability;
- production IAM or process isolation;
- HSM/KMS guarantees unless separately exercised;
- cross-provider distributed atomicity;
- resistance to compromise of the capability issuer itself;
- production availability or operational fitness; or
- fitness for every deployment architecture.

Those are separate propositions requiring separate evidence.

## Success classification

If every required observation is met without changing this proposition after the first executable result is known, classify the result as:

**CBP-003 — PROTECTED EXTERNAL ROUTE/CAPABILITY CLOSURE: PASS (BOUNDED TO NAMED TARGET, CAPABILITY AND INTEGRATION)**

Otherwise preserve and report the applicable failure or NOT EVALUATED classification.
