# T27 — Provider commitment evidence authenticity (failure-first)

## Threat model
An endpoint returns HTTP 200 and `{"status":"COMMITTED"}` without a signed,
provider-bound commitment record. The current standard adapter treats the status
as formation. This is not proof of a real payment or provider-side authority.

## Frozen requirement
No external commitment may be reported as verified formation solely from an
unsigned status string. Preserve UNRESOLVED pending authenticated evidence.

## Acceptance contract (not yet implemented)
- Provider identity and trust anchor, with key rotation/revocation rules.
- A signed commitment receipt over canonical payment_intent_id, mandate,
  source account, beneficiary, positive integer minor-unit amount, currency,
  authority epoch/version, execution route, executor, provider transaction ID,
  commit sequence and irreversible commitment timestamp.
- Verify signature, issuer, audience, exact action binding, epoch and uniqueness
  before changing the outcome to FORMED.
- Reject forged/missing signature, wrong beneficiary/amount, stale epoch,
  reused receipt across different intent, wrong provider and wrong route.
- Require independent provider-side authoritative revocation fence; signed
  evidence alone does not prevent an unauthorised commitment.
- Define durable reconciliation when acknowledgement is lost and do not treat
  eventual-consistency NOT_FOUND as proof of non-commitment.
- Qualify all adapters, including capability-based route, before claiming
  route closure.

The existing CBP-002 reference provider emits TRANSFER_RECORDED without signed
evidence. Its successful test is a legacy bounded simulation, not an authenticated
provider-evidence qualification. Do not silently upgrade that claim.

T27 deliberately retains its original RED until a qualified protocol exists.
