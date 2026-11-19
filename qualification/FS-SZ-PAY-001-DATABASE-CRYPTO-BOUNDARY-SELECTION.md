# FS-SZ-PAY-001 — Database cryptographic boundary selection

Status: **CAPABILITY GAP VERIFIED / DESIGN GATE OPEN / NOT MERGE READY**

## Evidence
The PostgreSQL 16 + pgcrypto 1.3 probe at
https://github.com/grahamb-ai/flowsignal-agentic-payments/actions/runs/44574997863
returned zero matching Ed25519 verification functions in its queried catalog.
This is a bounded capability inventory, **not** proof that no reviewed
PostgreSQL extension can support Ed25519.

The actual-login stolen commitment-service credential challenge at
https://github.com/grahamb-ai/flowsignal-agentic-payments/actions/runs/44573837948
recorded an unsigned £750,000 commitment through the existing SQL function.

## Required final-boundary architecture
Select and independently review a PostgreSQL-compatible, trusted Ed25519
verification implementation that can validate the existing exact canonical
institutional instruction within the final commit operation. The final
operation must:
1. Obtain pinned institutional public trust material from an administrator-
   controlled relation or equally protected configuration, not the caller.
2. Parse and validate exact canonical signed fields and expiry with
   unambiguous byte encoding and integer minor-unit amounts.
3. Reject unknown issuer, missing signature, replay, wrong action/target,
   altered intent/mandate/epoch/account/beneficiary/amount/currency, expired
   instruction and unavailable trust state.
4. Lock authoritative mandate state and insert a unique intent in the same
   serialised transaction *after* signature verification.
5. Revoke all runtime EXECUTE grants on the legacy unsigned function, and
   ensure the authenticated function cannot be bypassed through direct INSERT,
   alternate functions, owners or other runtime credentials.
6. Re-run the exact stolen-service-credential direct SQL challenge with no
   signed instruction and require zero durable commits.
7. Run valid signed, revocation ordering, duplicate, crash and reconciliation
   tests through the **same** final authenticated function.

## Implementation decision gate
No reviewed Ed25519-capable PostgreSQL extension has been selected or qualified
in this candidate. Do not invent a production-grade cryptographic primitive or
enable a privileged function that merely trusts an upstream verifier.

The existing independent Python verifier is useful for defence-in-depth but
does not close the final SQL route when the database credential is stolen.

**Disposition: BOUNDARY-02 RED / Structural Zero NOT QUALIFIED.**
