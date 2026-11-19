\set ON_ERROR_STOP on
-- After staged migration, even the private executor identity must be unable
-- to invoke the legacy unsigned function. No payment may be recorded.
SET ROLE fs_authority_writer;
INSERT INTO fs_provider.mandates(id,epoch,revoked)
VALUES ('MANDATE-DISABLED-LEGACY',1,false);
RESET ROLE;
SET ROLE fs_payment_executor;
DO $check$
BEGIN
 BEGIN
  PERFORM fs_provider.commit_if_current(
    'UNSIGNED-LEGACY-DISABLED','MANDATE-DISABLED-LEGACY',1,75000000,'ATTACKER');
  RAISE EXCEPTION 'BOUNDARY-01 RED: unsigned legacy function still executable';
 EXCEPTION WHEN insufficient_privilege THEN
  RAISE NOTICE 'BOUNDARY-01: unsigned function refused by PostgreSQL';
 END;
END
$check$;
RESET ROLE;
SELECT 1 / CASE WHEN NOT EXISTS (
 SELECT 1 FROM fs_provider.commits WHERE intent_id='UNSIGNED-LEGACY-DISABLED'
) THEN 1 ELSE 0 END AS no_unsigned_commit;
