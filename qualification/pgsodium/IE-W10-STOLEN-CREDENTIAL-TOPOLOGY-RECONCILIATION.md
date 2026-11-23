# BOUNDARY-02 stolen-credential RED — topology reconciliation (2026-11-23)

## Confirmed root cause of historical negative-control RED

GitHub Actions run 45178516766 fails with `BOUNDARY-02 RED: stolen service DB credential formed unsigned commitment`.

The workflow first runs `fs_sz_pay_001_disable_unsigned_commit_candidate.sql`, which revokes the old function's EXECUTE grant from `fs_payment_executor` and PUBLIC. It then runs `fs_sz_pay_001_commit_service_identity_candidate.sql`, which **explicitly GRANTs EXECUTE on `fs_provider.commit_if_current` to `fs_commit_service`**. The actual-login hostile test `fs_sz_pay_001_stolen_commit_credential_negative.py` connects as that service and invokes the old unsigned function, successfully committing.

This is an intentionally vulnerable intermediate identity skeleton, **not** the frozen signed-final-commit topology. Preserve original RED and raw artifact; do not relabel it GREEN or delete the test.

## Distinct candidate evidence

PostgreSQL 16 pgsodium experiment run 45178517001 passed the actual-login signed-function positive control, unsigned signed-function refusal, old unsigned function denied, revocation and stale-epoch refusal, row-lock revocation ordering, duplicate/lost-ack, and noncanonical wire refusal. This run is isolated reference evidence, not independent deployment qualification.

## Next integrated qualification

Run the **same stolen actual-login credential** against a frozen schema with `fs_sz_pay_001_authenticated_final_commit_candidate.sql` installed:
- `fs_commit_service` can execute only `commit_signed_if_current`, not `commit_if_current`;
- direct table insert and other legacy routes denied;
- unsigned/forged signed-function invocation refuses with zero durable rows;
- valid signed instruction commits exactly once;
- same identity with revoked mandate or stale epoch refuses;
- capture real-login `current_user`, effective privileges, role membership, function owner and durable counts.

Keep the intentionally RED intermediate workflow unchanged. Do not treat its failure as evidence the final signed candidate fails, nor treat the isolated GREEN as production qualification.

**Structural Zero NOT QUALIFIED; no production or main changes.**
