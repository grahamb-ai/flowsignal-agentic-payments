# FS-SZ-PAY-001 — Experimental final-commit qualification review

Status: **IMPLEMENTED EXPERIMENT / NOT INDEPENDENTLY QUALIFIED / NOT MERGE READY**.

The candidate function `fs_provider.commit_signed_if_current` verifies a pinned issuer's Ed25519 signature, checks supplied fields against decoded JSON, locks the mandate and inserts a unique intent. The old unsigned function's runtime EXECUTE grants are revoked in the candidate migration.

## Review blockers before BOUNDARY-02 closure

1. **Canonical bytes:** the candidate parses caller-supplied UTF-8 JSON as `jsonb`, but does not require the raw bytes to equal the institution's exact canonical JSON encoding. Duplicate JSON keys, extra properties, Unicode escapes, alternative numeric syntax and whitespace need explicit hostile tests and a documented canonical-byte acceptance policy. Never claim canonical format qualification based on signed JSON parsing alone.
2. **Issuer identity binding:** `p_issuer` is used to look up the trusted key but is not itself inside the signed canonical instruction. This may be acceptable for a single pinned trust key; multiple issuers and rotation need unambiguous policy and anti-confusion tests.
3. **Trust lifecycle:** key-steward separation is tested, but rotation timing, revocation race, key validity at commit time, and absent/unavailable trust state need integrated tests.
4. **Execution identity:** the new function grants EXECUTE only to `fs_commit_service`; test with a real login, not only `SET ROLE`. Ensure no direct INSERT or legacy unsigned-function access remains. Inspect `PUBLIC`, inherited grants, function owner and other privileged routes.
5. **Atomicity:** signed verification and mandate row lock are in one function, but both race orderings, revocation, duplicate, crash, lost-ack and authoritative reconciliation must run through this exact function.
6. **Supply chain:** pgsodium 3.1.8 builds and verifies signatures in the isolated reference, but its source archive is not digest-pinned or independently reviewed. Production deployment, IAM/KMS and real payment rail remain out of scope.
7. **Payment fields:** the reference commitment table stores intent, mandate, epoch, amount and beneficiary, not source account, currency, action or target. Their verification occurs at commit time but durable evidence is incomplete; full binding/receipt persistence needs a design decision.
8. **Deployment guard:** existing guard is deliberately hard-coded to refuse deployment. Do not relax it merely because a candidate function passes reference tests.

## Exit criteria
The original actual-login unsigned £750,000 bypass must be rerun against the *new signed function* and refuse with zero durable records. A valid signed instruction must commit exactly once, and all hostile/race/recovery cases must pass on the same frozen function and credentials. Preserve the historical original RED and every new RED.

**Disposition: BOUNDARY-02 OPEN until all gates are evidenced.**
