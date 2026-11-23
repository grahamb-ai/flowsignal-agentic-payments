# IE-W10 signed final-commit evidence review — 2026-11-23

**Disposition: isolated PostgreSQL signed-commit reference GREEN for observed cases; BOUNDARY-02 OPEN; Structural Zero NOT QUALIFIED.**

## Evidence
- GitHub Actions run 45178517001, commit 0b9c11907f468212b67592a1140b08f245142ca9, pgsodium PostgreSQL 16 compatibility experiment: completed SUCCESS.
- Raw job log confirms actual-login signed positive control and durable once; unsigned, substituted beneficiary/intent and mutated signed bytes refused.
- Revoked mandate and stale epoch refused.
- Revocation-first row-lock test: REFUSED_AUTHORITY, durable_commit_count=0; two row-lock orderings passed.
- Lost-ack retry: first COMMITTED, retry REFUSED_DUPLICATE_INTENT, durable_count=1.
- Reconciliation and noncanonical wire refusal passed.
- Separate direct-function containment run 45178144099 passed; historical direct-function RED preserved in run 45178143650.

## Boundaries and unresolved RED
- Privileged PostgreSQL owner can still insert directly; recorded privileged bypass remains RED.
- Authentic old signed anchor plus rolled-back ledger can be accepted absent independently protected monotonic witness.
- Deletion of locally controlled witness/replay store reopens old-state/replay vulnerabilities.
- Consolidated regression and stolen-credential negative-control workflows remain RED. Do not describe the entire branch as GREEN.
- pgsodium compatibility across versions remains unqualified (version matrix failure).
- No independent institutional key custody, GCP separate-admin replay witness, or actual payment rail observation.
- No production deployment approval; existing deployment guard remains refusal.

## Next focused work
1. Inspect exact failed consolidated tests and stolen-credential evidence before changing code.
2. Verify role membership and all alternative commit paths with a real non-owner login against a frozen schema.
3. Establish independent trust anchor/replay store administrative custody before claiming privileged-rollback resistance.
4. Validate externally observed non-production payment outcomes and refusal at actual consequence boundary.

No production, GCP IAM or main-branch modifications.
