# T23 — Consequence-bound provider commitment qualification

## Falsifiable claim
For a defined provider, payment intent, mandate and commitment operation, no
payment can commit after an effective authoritative revocation, even when the
revocation occurs after FlowSignal's local standing check.

## Original challenge
test_fs_sz_pay_001_t23_provider_commitment_fence.py uses the original FlowSignal
external adapter with a simulated independent provider. Provider revocation
occurs just before commitment. The provider has no authoritative fence and
accepts the payment. This is a **modelled counterexample**, not a live-rail test
or evidence of a specific real payment provider defect.

## Boundary requirements
- Define the authoritative revocation source and its effective instant.
- Define the provider's precise irreversible commitment point.
- Define the shared serialisation/epoch protocol between revocation and commit.
- Bind mandate, intent, amount in minor units, beneficiary, route, executor,
  authority epoch, and single-use commitment identity.
- Prove provider refusal for stale/revoked epochs and for duplicate intent.
- Qualify provider-side enforcement, including all privileged/alternate routes.
- Preserve crashes, retries, lost acknowledgements, and reconciliation evidence.
- Test concurrent revocation and commit ordering, not merely sequential calls.

## No false GREEN
The current local RLock only serialises authority changes in one Python process.
The current adapter posts a permit-signature transaction ID, but does not pass
an independently enforced provider-side revocation fence. A local SQLite claim
or post-hoc outcome receipt cannot replace a commitment fence.

## Candidate choices (design, not implemented)
A. Provider checks a short-lived signed authority lease at its commitment
   boundary with revocation propagation guarantees and an explicit risk window.
B. A shared authoritative state/transaction service serialises revocation and
   provider commit with a provider-enforced fencing token.
C. A provider-controlled commit API validates and consumes a FlowSignal-derived
   authority claim against current authoritative state before irreversible effect.

All candidates require a precisely specified threat model, freshness semantics,
provider cooperation and non-bypassable routing. None is automatically universal
Structural Zero.
