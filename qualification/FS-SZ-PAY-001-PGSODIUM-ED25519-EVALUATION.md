# FS-SZ-PAY-001 — pgsodium Ed25519 final-boundary evaluation

**Status: CANDIDATE IDENTIFIED / NOT INSTALLED / NOT QUALIFIED / BOUNDARY-02 RED.**

## Candidate and source
The PGXN pgsodium documentation describes `crypto_sign_verify_detached(sig bytea, message bytea, key bytea) -> boolean` backed by libsodium's single-part Ed25519 signature verification. References:
- https://pgxn.org/dist/pgsodium/
- https://doc.libsodium.org/public-key_cryptography/public-key_signatures

This is not available in the previously tested stock PostgreSQL 16 + pgcrypto 1.3 image. We must select, pin, build and review a PostgreSQL-16-compatible pgsodium version; do not infer compatibility or production security from documentation alone.

## Blocking implementation gates
1. Verify actual installed extension version, library provenance, build reproducibility, function schema, ownership, search path, grants and PostgreSQL 16 compatibility. Use only reviewed immutable source/build.
2. Test **exact bytes** signed by the existing Python `provider_instruction_verifier`: `json.dumps({"instruction": canonical_instruction(payload), "expires_at": expires_at}, sort_keys=True, separators=(",", ":")).encode()`. Avoid PostgreSQL JSONB reserialization without independent byte-for-byte comparison; key order, Unicode escaping and numeric representation can differ.
3. Derive the canonical instruction **inside the trusted final SQL boundary** from validated typed fields; never accept arbitrary caller-supplied message bytes as proof of the transaction fields to be committed. Compare every signed field with committed values.
4. Read an administrator-controlled, enabled, time-valid issuer public key from the protected trust registry. Reject missing/disabled/expired keys and unrecognised issuer identity. Runtime roles must not modify the registry.
5. Validate signature size (64 bytes), key size (32 bytes), expiry with UTC timezone, action/target/source/beneficiary/currency, positive integer minor units, intent and mandate/epoch. Check authoritative mandate standing under lock and insert unique intent atomically.
6. Revoke legacy unsigned-function EXECUTE from all runtime identities. The only accessible final function must perform cryptographic verification itself. Audit alternate functions, direct INSERT, role membership, owners and superusers.
7. Rerun the exact actual-login stolen-service-credential £750,000 unsigned direct SQL attack. Require refusal and zero durable records. Then valid signed, tamper, replay, expiry, revocation ordering, forced-crash and reconciliation tests through the same function.
8. Independently review extension trust, key administration, DB privileged access and network routes. A database owner/superuser is outside ordinary role-grant containment.

## Current decision
**Proceed to an isolated pgsodium compatibility and canonical-byte interoperability experiment. Do not grant any runtime payment-commit privilege or enable payment execution during that experiment.** A function inventory alone is not BOUNDARY-02 closure.
