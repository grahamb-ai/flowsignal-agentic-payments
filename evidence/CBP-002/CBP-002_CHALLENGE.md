# CBP-002 — Adversarial Consequence Attack Challenge

**Status:** FROZEN BEFORE EXECUTABLE TEST

## Proposition

A represented protected consequence must remain non-formable when an attacker attempts to use stale, replayed, substituted, duplicated, or otherwise invalid execution material against the protected consequence boundary.

This challenge is committed before the executable test is added. The first observed result must be preserved whether PASS or FAIL.

## Frozen attack surface

The test must attempt, at minimum:

1. **Duplicate execution** — a permit that has already formed a consequence must not form it again.
2. **Stale permit after authority change** — a permit issued under an earlier authority-state version must not form a consequence after a newer authority state has committed.
3. **Exact-action substitution** — changing the action binding presented at consequence formation must not form the consequence.
4. **Direct protected-consequence invocation** — calling the protected consequence function directly must not bypass permit, authority-state, replay, or action-binding checks.
5. **Historical replay after fresh re-authorisation** — issuance and successful use of a new current-state permit must not make a historical stale permit usable again.
6. **Positive control** — a fresh, valid, exact-action permit under current authority must still be capable of forming the represented protected consequence.

## Required evidence

For each denied attack, the executable test must assert the explicit denial outcome and must not infer non-formation merely from an evaluator result. Where the implementation exposes a signed consequence-outcome receipt, the test must verify its integrity and confirm `consequence_formed == false` for the denied attempt.

The positive control must demonstrate `CONSEQUENCE_FORMED` so that a passing challenge cannot be explained by disabling the executor.

## Scope

This is a reference-MVP proof over FlowSignal's represented protected-consequence primitive and its local persistence mechanisms. It does **not** claim control over an external bank, payment rail, settlement network, operating-system privilege boundary, IAM boundary, HSM/KMS boundary, or distributed transaction coordinator.

## Failure discipline

If any frozen attack forms the represented consequence when it should not, CBP-002 is FAIL. The failing commit and first run are to be preserved before remediation.