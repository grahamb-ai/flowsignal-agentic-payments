# IE-W10 — GCP deployment-readiness and trust-boundary checklist

Status: PRE-DEPLOYMENT DESIGN ONLY. No GCP resource or IAM inspection has been performed.

## Candidate non-production architecture

1. **Executor:** dedicated Cloud Run service account, invoke-only on replay API. No Firestore data roles, no service account token-creator, no deployment/IAM mutation, no ability to invoke privileged replay maintenance paths.
2. **Replay authority:** separate Cloud Run service account with minimum Firestore permissions to create-if-absent and read replay events. Do not grant database delete, export/import, IAM administration or broad project Editor roles. Note: Firestore IAM alone may not enforce per-document create-only semantics; enforce operation semantics in a narrowly scoped service API, and independently verify effective permissions.
3. **Witness:** distinct project or institution-controlled security boundary, with monotonic high-water state and separate administrator. A second collection in the same project is not independent custody.
4. **Key state:** institution-controlled authoritative issuer/key epoch with authenticated revocation, freshness checks and explicit unavailable-state refusal.
5. **Rail:** independently controlled sandbox/test rail evidence source. Synthetic signed statements remain reference-only.

## Preflight evidence to collect (no secrets)

- GCP project IDs and service account emails for executor, replay authority, witness and key-status reader
- Cloud Run revisions, invoker policies, ingress rules and deployment principals
- Effective IAM policies at project, service, database and service-account scopes; inherited roles and impersonation edges
- Firestore database location, concurrency mode, delete protection and PITR/backup posture
- Cross-project trust and witness custody evidence, including who can roll back or delete records
- Network paths, authentication token audience validation, and unauthorised direct-store access attempts
- Independent signed rail test event source and durable reconciliation semantics

## Qualification stop/go

GO to non-production hostile testing only when each boundary has a named independent operator, auditable effective permissions, a fail-closed outage path and evidence collection.

NO-GO when a common administrator can delete both replay ledger and witness, when a payment executor can impersonate the authority, or when source evidence is simulated but described as real settlement.

## Test order

1. W10-01 executor deletion and impersonation attempts
2. W10-02/03 concurrency and cross-revision restart
3. W10-04 outage
4. W10-05/06 privileged deletion and authentic checkpoint rollback
5. W10-07/08 key revocation and hostile attestation
6. W10-09 lost acknowledgement and recovery
7. W10-10 actual independent non-production rail contradiction

Preserve original REDs and new raw artifacts. Do not modify main or production. No public CI artifact should contain service account credentials, bearer tokens or private signing keys.

**Claim boundary:** IE-W10 NOT RUN; independent administrative custody NOT VERIFIED; Structural Zero NOT QUALIFIED.
