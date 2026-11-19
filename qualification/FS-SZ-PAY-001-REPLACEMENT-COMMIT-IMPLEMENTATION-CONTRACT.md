# FS-SZ-PAY-001 — Replacement commitment boundary implementation contract

Status: **DESIGN ONLY / NOT QUALIFIED / NOT MERGE READY**. Historical direct-function RED remains the controlling negative evidence.

## Selected implementation direction
Use a **separately isolated commitment service** as the only holder of a database credential permitted to invoke the final guarded commitment transaction. The FlowSignal gateway and HTTP payment provider must have **no database EXECUTE grant** on any commit function and **no direct INSERT grant** on the commitment table.

The commitment service must verify the existing canonical Ed25519 institutional instruction *inside its own trusted process*, using independently provisioned public trust material, and only then execute the PostgreSQL row-locked mandate check and durable commit. The service must not accept an upstream `verified=true` flag, a caller-supplied public key, or a caller-supplied mandate standing assertion.

**Security limitation:** a stolen commitment-service database credential can still bypass the service and call its guarded SQL function. Therefore this design is NOT BOUNDARY-02 closed without independently evidenced credential custody and database network isolation that make direct invocation unavailable to the in-scope attacker. If the threat model includes possession of that credential, use a reviewed final-boundary cryptographic verifier in the database or an equivalent stronger enforcement mechanism. Neither has been implemented.

## Interface contract
- Input: signed payment instruction with intent ID, mandate ID, epoch, source account, beneficiary, integer minor-unit amount, currency, action, execution target, expiry, issuer identity and signature.
- Verify: pinned institutional issuer trust, canonical exact-field Ed25519 signature, expiry, permitted action and target, allowed currency, positive integer minor units, mandate identity and epoch.
- Commit: one serialised database transaction checks authoritative mandate state under row lock, inserts unique intent, returns a durable commitment identity.
- Retry: same intent cannot form another commitment; ambiguous transport errors remain UNKNOWN until reconciliation against durable authoritative records.
- Reject: unsigned, forged, stale, wrong target, altered fields, duplicate, revoked, unavailable trust state, and direct untrusted SQL invocation.
- Operational trust: separate credentials, secrets distribution, ingress authentication, egress restrictions, rotation, break-glass privilege inventory, and owner/superuser exclusions must be documented and independently challenged.

## Cutover sequence (no production changes)
1. Preserve baseline RED and freeze its commit, raw logs and test fixture.
2. Create an isolated candidate database; revoke the old unsigned function from **all runtime logins**.
3. Create a dedicated commitment-service identity, without granting it mandate-write privileges.
4. Deploy independent signed-instruction verifier and its trusted key material; do not give the HTTP provider the commitment credential.
5. Prove a valid signed instruction commits exactly once through the new service.
6. Attempt direct SQL commit using gateway, HTTP provider, untrusted caller, and compromised *provider* credentials; all must fail.
7. Explicitly challenge the dedicated commitment-service credential; if direct SQL can still commit without a signature, preserve RED and narrow the claim or redesign.
8. Rerun both race orderings, precommit revocation, postcommit persistence, session restart, lost acknowledgement and forced-crash cases through the **same replacement path**.
9. Inventory all functions, roles, grants, network ingress, privileged operators and execution routes; reconcile each to test evidence.

## Exit criteria
No Structural Zero claim until BOUNDARY-01..07 are independently evidenced on one frozen integrated candidate. Existing reference HTTP GREEN and staged function-shutdown GREEN are necessary but insufficient. The historical full regression suite and direct-function RED are not to be relabelled or suppressed.
