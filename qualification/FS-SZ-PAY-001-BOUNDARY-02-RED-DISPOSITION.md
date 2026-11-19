# FS-SZ-PAY-001 — BOUNDARY-02 credential-bypass disposition

Status: **RED CONFIRMED / NOT MERGE READY / NO STRUCTURAL ZERO CLAIM**

## Reproducible finding
- Workflow: https://github.com/grahamb-ai/flowsignal-agentic-payments/actions/runs/44573837948
- Commit: `66530c0e18e4b3cbbb87c1e291e1f0845da850d2`
- Actual `fs_commit_service` PostgreSQL login called `fs_provider.commit_if_current` directly.
- Raw output: `ACTUAL SERVICE LOGIN DIRECT SQL OUTCOME: COMMITTED; durable records: 1`.
- No institutionally signed instruction was presented to the independent verifier.
- A successful signed-payment integration test does **not** counter this finding.

## Required security invariant
For every in-scope payment-commitment route, including direct database connections and compromised runtime credentials, the final authority-enforcing operation must reject a payment unless independently authenticated institutional instruction evidence is bound to the exact intent, mandate, epoch, account, beneficiary, amount, currency, action, target and expiry. Authority standing must be checked atomically with commitment.

## Decision: no cosmetic credential-only remediation
Renaming the executor role, moving the verifier into another HTTP process, rotating passwords or adding a `verified=true` parameter does not meet this invariant. A PostgreSQL `SECURITY DEFINER` function accepting unsigned payment fields is still callable with the granted credential.

Choose and independently review one of:
1. A database-enforced cryptographic verifier that validates the pinned institutional Ed25519 instruction inside the same trusted final-commit boundary and refuses unsigned direct SQL calls. Its key trust material must not be alterable by runtime roles; function grants, owner privileges, extension trust and canonicalisation must be audited.
2. A genuinely isolated commitment authority with non-exportable service identity and enforced ingress/DB connectivity such that the in-scope attacker holding the payment-provider credential cannot invoke the commit function. **This option cannot claim resistance to theft of the commitment authority's own database credential** without additional evidence.

## Next qualification sequence
1. Freeze this RED and the earlier simulated-role RED; do not xfail or relabel.
2. Implement one reviewed final-commit verification design on a separate candidate schema, keeping the old unsigned route revoked for runtime logins.
3. Re-run the exact real-login unsigned £750,000 challenge. It must be refused with zero durable records.
4. Prove a genuine signed instruction commits exactly once through that same final boundary; reject forgery, replay, field substitution, expiry, stale/revoked mandate.
5. Repeat both race orderings, post-commit lost acknowledgement, forced crashes and authoritative reconciliation against the *same* path.
6. Inventory DB owners/superusers, functions, grants, credentials, network routes and break-glass access; explicitly exclude or qualify privileged operators.
7. Freeze code, SQL, CI evidence and claim scope before any merge decision.

## Current disposition
**BOUNDARY-02 RED. BOUNDARY-03 partially GREEN only on the authenticated reference route. BOUNDARY-05..07 OPEN.** No production IAM/KMS, real payment rail or exhaustive route closure qualified.
