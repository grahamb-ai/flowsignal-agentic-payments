# FS-SZ-PAY-001 — Final commitment authentication decision (candidate design)

## Verified checkpoint
- Provider process-isolation run: https://github.com/grahamb-ai/flowsignal-agentic-payments/actions/runs/44520441552
- Two process-isolation tests passed; HTTP integration passed.
- Preserved direct-function bypass RED: https://github.com/grahamb-ai/flowsignal-agentic-payments/actions/runs/44519057787
- A holder of `fs_payment_executor` can call `fs_provider.commit_if_current` with arbitrary unsigned payment fields while a mandate is active. The reference DB records the payment. Caller-role denial does not close this path.

## Architectural acceptance decision
**Do not call this reference Structural Zero while the private executor credential alone is sufficient to form a commitment.** The next candidate must make the *final database commitment operation* require independently verified, transaction-bound institutional instruction evidence. Credential isolation remains defence-in-depth, not the sole authentication control.

### Minimum final-boundary contract
1. Exact signed instruction identity: payment intent, mandate, epoch, source account, beneficiary, amount in integer minor units, currency, action, target, expiry, issuer key identity and signature.
2. The commitment boundary validates institutional issuer authenticity against separately administered trust material, verifies all bound fields, expiry and revocation/freshness, and checks mandate standing in the same serialised transaction as the durable commit.
3. The executor cannot read or alter issuer trust material, authority state, or any independent verification secret; SQL `SECURITY DEFINER` must use a fixed search path and least privilege.
4. Revoke EXECUTE on the **old unsigned** `commit_if_current` for every runtime identity before enabling the new boundary. No alternate privileged function or direct INSERT route may remain accessible to protected payment credentials.
5. Reject replay and changed fields, including attempts to substitute an action, target, mandate or epoch. Fail closed on unavailable verification state; uncertain provider outcomes remain unresolved until authoritative reconciliation.
6. Demonstrate separate database login credentials and protected signing keys; ephemeral CI secrets do not qualify production key custody.

## Implementation choice to validate
PostgreSQL alone does not natively verify the existing Ed25519 instruction format with the current schema. Do **not** replace it silently with an unqualified HMAC or assert that an HTTP signature check proves database-level authenticity. Choose one of:
- A reviewed database verification extension/service with a genuinely enforced, transactional commit API; or
- A separately isolated commitment service whose database role is the only role permitted to commit, with independently enforced service identity and no exposed SQL function path to untrusted executors.

Either choice requires an explicit threat model covering stolen provider credentials and privileged database operators. Superuser access cannot be contained by ordinary PostgreSQL grants.

## Acceptance gates
- BOUNDARY-01: old unsigned direct function is inaccessible to every runtime login (preserve original RED as historical evidence).
- BOUNDARY-02: private executor credential without authentic signed instruction cannot commit, even via direct SQL.
- BOUNDARY-03: valid instruction commits once with exact field binding.
- BOUNDARY-04: revoked/stale mandate and replayed/expired/forged instruction refuse.
- BOUNDARY-05: concurrency, forced-crash and lost-ack tests run through the *same final authenticated boundary*, not a different test-only function.
- BOUNDARY-06: deployment inventory proves no unexamined in-scope payment route, credential or privileged bypass.
- BOUNDARY-07: independently reproducible CI evidence and frozen source/configuration; original REDs retained.

## Current disposition
**NOT MERGE READY.** Integrated HTTP path and role separation GREEN in bounded tests; direct-function authentication bypass RED. Real provider integration, production IAM, KMS and complete route closure NOT RUN.
