# IE-W18 — Independent custody entry gate

Date: 2026-11-23
Status: DESIGN / NO DEPLOYMENT / NOT QUALIFIED

## Entry evidence
- IE-W17 first run 45192315639 failed at Python parse time (literal newline source error), retained.
- Corrected run 45192592832 succeeded: forged, substituted, expired and wrong-key approvals refused; valid signed recovery once; stale replay refused.
- This proves only the local reference. Its signing key and witness data remain within one administrator's control.
- GCP console review found common organisational control across Structural Zero Lab, Gateway Evidence and Issuer Research; organisation Deny policy visibility unavailable. No independent witness administrator verified.

## Required custody decision before further deployment
1. Identify an institutional or third-party operator who controls the witness project/account, KMS signing key, audit log retention, service deployment and high-water storage. They must not share an effective administrator or impersonation chain with FlowSignal's execution environment.
2. Obtain an effective-access inventory covering organisation inheritance, project/resource IAM, service-account impersonation, CI/deploy identities, KMS signing, key disable/delete, data rollback/delete and policy administration. Record unavailable policy visibility as UNKNOWN.
3. Define signed recovery approval provenance: independent issuer key, exact instruction/event and prior/proposed checkpoint binding, expiry, nonce/approval ID, revocation, sequence CAS, and one-time consumption. A valid signature without current high-water confirmation is not sufficient.
4. Define outage/ambiguity handling: witness unavailable -> no new finalisation; after provider may have committed -> UNRESOLVED and independently reconcile before retry. Never infer non-payment from absent witness receipt.
5. Independent operator witnesses hostile tests: compromised FlowSignal Owner, impersonation, direct store write/delete, old authentic checkpoint, stale/forged approval, concurrent recovery, crash between stores, issuer key withdrawal, provider outcome contradiction.

## Explicit no-go
- A second GCP project under the same effective organisation administrator is a SAME-ADMIN PROTOTYPE, not independent custody.
- No credential, IAM, KMS, Firestore, Cloud Run or production change is authorised by this design.
- No Structural Zero claim until a separately controlled execution boundary and actual independently observed consequence are qualified.

**Disposition: IE-W18 WAITING FOR INDEPENDENT CUSTODY / Structural Zero NOT QUALIFIED.**
