\set ON_ERROR_STOP on
SET ROLE fs_authority_writer;
INSERT INTO fs_provider.mandates(id,epoch,revoked) VALUES ('MANDATE-CUTOVER-GATE',1,false);
RESET ROLE;
SET ROLE fs_commit_service;
DO $test$
BEGIN
 BEGIN
  PERFORM fs_provider.commit_if_current('SERVICE-UNSIGNED-BLOCKED','MANDATE-CUTOVER-GATE',1,75000000,'ATTACKER');
  RAISE EXCEPTION 'RED: service credential still executes unsigned commit';
 EXCEPTION WHEN insufficient_privilege THEN
  RAISE NOTICE 'service unsigned commit denied';
 END;
END $test$;
RESET ROLE;
SET ROLE fs_payment_executor;
DO $test$
BEGIN
 BEGIN
  PERFORM fs_provider.commit_if_current('PROVIDER-UNSIGNED-BLOCKED','MANDATE-CUTOVER-GATE',1,75000000,'ATTACKER');
  RAISE EXCEPTION 'RED: provider credential still executes unsigned commit';
 EXCEPTION WHEN insufficient_privilege THEN
  RAISE NOTICE 'provider unsigned commit denied';
 END;
END $test$;
RESET ROLE;
SELECT 1 / CASE WHEN NOT EXISTS (
 SELECT 1 FROM fs_provider.commits WHERE mandate_id='MANDATE-CUTOVER-GATE'
) THEN 1 ELSE 0 END AS zero_unsigned_commitments;
