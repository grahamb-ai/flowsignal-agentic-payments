# IE-W11 — Independent witness custody architecture and hostile acceptance plan

Date: 2026-11-23
Status: DESIGN ONLY / NOT DEPLOYED / NOT QUALIFIED
Scope: FlowSignal Structural Zero, independent runtime authority and durable consequence evidence.

## Grounded starting state

Read-only Google Cloud Console inspection found:
- `flowsignal-structural-zero-lab`, `fs-gateway-evidence-001` and `flowsignal-issuer-research-001` under `flowsignal.ai`.
- The same human account holds Organisation Administrator and Organisation Policy Administrator at organisation scope and an apparently project-level Owner (legacy) role in the inspected projects. Grant origins and effective permissions should be independently exported before reliance.
- Gateway Evidence project grants a CAGE staging runtime Cloud Datastore User and an issuer runtime Cloud Datastore Viewer. These are not witness-only custody grants.
- Project Deny view showed no attached policies but warned of incomplete visibility. Organisation Deny listing failed for lack of `iam.denypolicies.list`. Absence of organisation Deny controls is NOT established.
- Historical local PostgreSQL qualification preserves privileged-owner direct-write RED, rollback of authentic old checkpoint RED, and local replay-store deletion RED.
- Existing signed commitment, revocation ordering, and replay tests provide reference evidence only, not external-rail qualification.

## Proposed trust domains

A. Institution: authoritative mandate, revocation, issuer key state, epoch and freshness; institution or independent delegate controls issuance.
B. FlowSignal execution environment: computes admissibility and submits a fully bound signed instruction; cannot modify institution state, witness history or payment-provider settlement evidence.
C. Commitment provider: checks signature, target, issuer/key lifecycle, fresh mandate epoch and replay/uniqueness at the final commitment operation. Commits or refuses atomically.
D. Independent witness: separately administered from FlowSignal and provider; stores monotonic checkpoint, receipt hash, key identifier, sequence, authority epoch, intent, target and outcome evidence; append-only API with conditional advancement. It cannot be reset or impersonated by a FlowSignal administrator.
E. Payment rail or sandbox: independently returns durable, authenticated external outcomes, including contradictory or unavailable results.

## Required protocol

1. Bind canonical instruction (execution target, operator, mandate, authority epoch, payment intent, amount in integer minor units, currency, source, beneficiary, expiry, issuer/key id and nonce) to signature and final-boundary checks.
2. Acquire authoritative fresh standing at the provider boundary; fail closed if absent, stale, revoked or unverifiable.
3. Coordinate provider commitment and witness acknowledgement with explicit crash semantics. No claim of cross-system atomicity without a proven protocol; if witness cannot confirm, do not infer non-commitment and reconcile with the provider.
4. Witness must reject duplicate event, stale sequence, old authentic checkpoint, invalid issuer, conflicting intent, and unauthorized mutation; produce independently verifiable signed receipt.
5. An outage or ambiguous acknowledgement yields a non-executing or unresolved state, not a blind retry. Resume only after independently verified provider reconciliation.
6. Record precise event ordering and durable external effect; do not equate a pending Firestore claim with settlement.

## Threat model and test matrix

- W11-01 FlowSignal executor cannot write, delete, reset, impersonate or reconfigure witness.
- W11-02 FlowSignal project Owner cannot access witness custody through inherited organisation roles, service account impersonation, KMS, CI/deployment or billing/project administration paths.
- W11-03 Concurrent distinct writers: exactly one monotonic advancement for same expected sequence.
- W11-04 Authentic old signed checkpoint and restored database rejected by independently retained high-water mark.
- W11-05 Privileged deletion/rollback in execution project cannot rewrite independently signed receipts.
- W11-06 Witness outage fails closed before consequence; ambiguous post-commit witness failure triggers provider reconciliation, not blind replay.
- W11-07 Issuer revocation, key rotation and stale epoch refused at final commitment boundary.
- W11-08 Signed rail outcome cannot be forged, replayed, contradicted silently or confused with synthetic state.
- W11-09 Controlled restart, SIGKILL and lost acknowledgement preserve single consequence or explicit unresolved outcome.
- W11-10 Independent operator verifies evidence without relying on FlowSignal's assertions.

## Stop/go

NO-GO for independent-custody claim if common administrator can change both execution and witness evidence; if witness signing key is controlled by execution project; if inherited deny-policy visibility remains unresolved; if no real independently observed consequence outcome exists.

Engineering prototype may use Gateway Evidence ONLY when labelled SAME-ADMIN PROTOTYPE. Do not alter IAM or GCP resources until operator and access plan is approved and separately reviewed.

**Structural Zero NOT QUALIFIED. Main and production unchanged.**
