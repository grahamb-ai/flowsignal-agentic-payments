# IE-W10 revocation evidence reconciliation — 2026-11-23

Status: REVIEW ONLY; no new GCP execution or independent-domain qualification.

## Historical GCP observations supplied from Cloud Console

- Firestore database `flowsignal-sz-claims-lab` contains `sz_authority_standing_fenced_v1/BANK-REVOKE-d9966fd663544bd4` with `active=false`, `epoch=4`, `version=2`, `synthetic=true`. The screenshot does not show revocation event time or transition history.
- A separate issuer `BANK-CLAIM-1c6026157d0a4167` has a corresponding `sz_claims_fenced_v1` document with matching `issuer_id`, `status=PENDING`, synthetic fields, digest and signature strings. No signature verification or atomic authority check is evidenced by these screenshots.
- Earlier Cloud Run `flowsignal-sz-live-test` logs show `CLAIM_ACCEPTED` (201) and `DUPLICATE_REFUSED` (409) for a different synthetic operation; replay job logs also show 409. These are NOT a post-revocation final-commit test.
- Earlier historical job REDs: two 404 routing failures and identity-inspection missing `requests` dependency. Retain raw logs and distinguish from authority bypasses.
- Project-level Test Caller IAM permission evaluations for datastore create/update/delete show `Cannot access`; exact Claim Authority service-account evaluations for `getAccessToken` and `actAs` show `Cannot access`. IAM Deny policy visibility was incomplete. This does not prove independent administrator resistance.

## Source review on qualification branch

- `harness/tests/test_fs_sz_pay_001_t23_provider_commitment_fence.py`: deliberate failure-first provider that revokes after local check and still commits without authoritative provider-side fence. Preserve RED.
- `harness/tests/test_fs_sz_pay_001_t24_provider_fence.py`: cooperative SQLite reference tests serial revocation-first refusal, commit-first ordering, duplicate intent and process race.
- `harness/app/engines/t24_provider_commit_fence_reference.py`: SQLite `BEGIN IMMEDIATE` serialises mandate state check with commitment; reference is not actual rail.
- `harness/tests/test_fs_sz_pay_001_t22_atomic_claim.py`: bounded local claim and unresolved outcome records; explicitly not external execution.

## Next evidence requirement (do not infer from record fields)

Find an executed test with authoritative revocation timestamp/epoch, attempt timestamp, exact execution target and binding, final-boundary decision, durable consequence count and separately controlled provider outcome. A revoked record alone is insufficient.

## Disposition

T23 preserved RED; T24 local reference behaviour demonstrated by code (CI status not independently established in this review); GCP historical synthetic replay GREEN for observed logs; GCP post-revocation final-boundary consequence test NOT VERIFIED; independent witness/rail NOT QUALIFIED; STRUCTURAL ZERO NOT QUALIFIED.

No changes to `main`, GCP resources, IAM or production.
