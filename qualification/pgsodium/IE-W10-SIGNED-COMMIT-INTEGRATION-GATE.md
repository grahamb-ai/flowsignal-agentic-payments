# IE-W10 signed commitment integration gate — candidate review

Status: DESIGN / NOT RUN. Base evidence: isolated direct-function EXECUTE containment GREEN (GitHub run 45178144099); historical unsigned direct-function RED preserved.

## Required identity topology

- fs_payment_executor: no EXECUTE on either unsigned or signed commitment function; no direct INSERT/UPDATE/DELETE on commitment tables; no role membership allowing escalation.
- fs_commit_service: only the narrowly scoped signed function; no old unsigned EXECUTE or direct table writes.
- institutional issuer: independently controlled signing key; pinned trusted issuer and authenticated, versioned key-state lifecycle.
- migration administrator/function owner: excluded from runtime identities and separately audited.

## Same-function hostile matrix

1. Executor direct unsigned function: permission denied; zero records.
2. Executor direct signed function: permission denied; zero records.
3. Commit service unsigned legacy function: permission denied; zero records.
4. Commit service valid signed instruction: exactly one record.
5. Commit service forged signature: refusal; zero new records.
6. Valid signature, substituted intent/beneficiary/amount/source/target: refusal.
7. Revocation effective before final commit: refusal; zero new records.
8. Commit before revocation: one durable record, subsequent intent refused.
9. Duplicate/replay and concurrent same-intent requests: exactly one commitment.
10. Revoked/expired/unavailable issuer key state: fail closed.
11. Lost acknowledgement: reconcile by stable intent, never issue a second consequence without external observation.
12. Crash/rollback/privileged owner and alternative route: preserve RED unless independently blocked.

## Evidence and stop conditions

Run with actual PostgreSQL login credentials and effective grants, not only SET ROLE. Capture raw SQL outcomes, durable row counts, role membership, signed-byte hashes, exact function definition hash, CI commit and run IDs. Do not store keys or credentials in public artifacts.

The existing `fs_sz_pay_001_authenticated_final_commit_candidate.sql` is experimental and requires canonical-byte, issuer binding, lifecycle, row-lock race and complete durable payment-field qualification. Do not merge or deploy on the basis of the isolated containment GREEN.

**Disposition: BOUNDARY-02 OPEN; Structural Zero NOT QUALIFIED.**
