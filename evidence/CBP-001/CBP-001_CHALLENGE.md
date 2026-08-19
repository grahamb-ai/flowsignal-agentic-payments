# CBP-001 — Consequence-Boundary Proof Challenge

## Status

FROZEN CHALLENGE — NOT YET EVALUATED

## Starting point

Repository: `grahamb-ai/flowsignal-agentic-payments`

Frozen base commit: `4c5092c8df704a58327c4a5e5c6ae9fc81755ef2`

The challenge is defined before the executable result is observed.

## External proof seam

The challenged chain is:

`real represented protected consequence -> current standing -> changed condition -> attempted bind -> NO_BIND -> bypass failure -> receipt -> replay/current-state separation`

## Frozen proposition

A previously valid, exact-action execution permit MUST NOT form the represented protected consequence after the authoritative runtime state has changed. Direct execution through the protected-consequence primitive using the stale permit MUST return a denial, the denial receipt MUST attest that consequence was not formed, an altered action binding MUST also fail, and a fresh authority evaluation under the changed state MUST be distinguishable from reuse/replay of the historical permit.

## Required observations

1. Establish a valid current-state `ALLOW` for an exact payment action and obtain the resulting execution permit.
2. Establish the control condition that the represented protected consequence can form when current standing and exact action binding remain valid.
3. Obtain a second fresh valid permit for the same represented action.
4. Change authoritative runtime state after that permit has been issued but before consequence formation.
5. Invoke the protected-consequence primitive directly using the stale permit.
6. PASS only if the attempted bind returns `DENIED_AUTHORITY_STATE_STALE` and does not return `CONSEQUENCE_FORMED`.
7. Produce a consequence outcome receipt for that denied bind and verify that it is cryptographically/tamper-evidently valid and records `consequence_formed == False`.
8. Attempt an alternate action binding with the stale permit and PASS only if consequence formation is denied.
9. Re-evaluate the same represented business action under current authoritative state and confirm any newly permitted execution is backed by a newly issued authority receipt / authority-state version rather than resurrection of the historical permit.
10. Re-present the stale historical permit after fresh evaluation and PASS only if it remains unusable.

## Failure classifications

- `FAIL — STALE AUTHORITY FORMED CONSEQUENCE`
- `FAIL — ACTION SUBSTITUTION FORMED CONSEQUENCE`
- `FAIL — DENIAL RECEIPT CLAIMS CONSEQUENCE FORMED`
- `FAIL — HISTORICAL PERMIT RESURRECTED AFTER REEVALUATION`
- `NOT EVALUATED — FIXTURE OR TEST CONSTRUCTION DID NOT REACH THE INTENDED CONDITION`

## Evidence discipline

- Do not modify the proposition after seeing the result.
- Do not modify the production/reference implementation before the first executable run.
- If the frozen test fails, preserve the initial failure and commit before remediation.
- If remediation is required, rerun the same proposition semantics.
- Report represented-MVP scope only; do not claim external banking-rail or production deployment closure.

## Explicit scope limitation

CBP-001 is a reference-MVP consequence-boundary test against the represented protected-consequence primitive in this repository. It does not establish physical prevention on an external bank/payment rail, production IAM/process isolation, HSM/KMS guarantees, or universal closure of systems outside the represented execution surface.
