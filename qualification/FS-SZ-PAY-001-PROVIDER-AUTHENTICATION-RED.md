# FS-SZ-PAY-001 — Provider authentication RED disposition

## Frozen counterexample
Run https://github.com/grahamb-ai/flowsignal-agentic-payments/actions/runs/44503920073
Commit `3d8eee40f7b6e288d1c400ba9c834acd9e5e170b`.
Focused 20 passed, 1 failed; full 88 passed, 2 failed (including historical T23).
A caller supplied matching active mandate and epoch and committed a simulated GBP 750,000 transfer to ATTACKER without an independently authenticated institutional payment instruction.

## Required remediation contract — not yet implemented
1. Provider must verify a **trusted issuer-signed authorization** for the exact business intent, mandate, provider epoch, source account, beneficiary, amount (integer minor units), currency, action and target. Do not accept caller-controlled identity fields alone.
2. Issuer/verifier key roles and permissions must be separate; provider may verify but must not mint. A reference test key is not production IAM/KMS.
3. Provider must check signature, expiry, exact payload binding, and current mandate epoch/revocation **inside the commitment decision**. No check-then-write window.
4. A second request with a changed beneficiary/amount/mandate/epoch must refuse even when replaying a valid signed authorization.
5. Fresh permit for the same authenticated business intent must not commit twice. Lost acknowledgement must remain unresolved until provider reconciliation by stable intent.
6. All configured protected routes must use the same enforcement primitive. Legacy mode must remain outside the claimed protected boundary and inaccessible to protected credentials.
7. Preserve the initial RED and rerun the unchanged hostile direct-caller test; add positive authorised commit and hostile tamper/replay/race cases.

## Caution
FlowSignal's existing reference permit signature is not an independently trusted provider-side institutional credential. Merely passing its signature to the provider, sharing a mutable test secret, or checking a self-asserted mandate is not sufficient to close this RED.

**Disposition: OPEN / RED. Do not merge to main or claim Structural Zero.**
