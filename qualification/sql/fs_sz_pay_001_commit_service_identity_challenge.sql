\set ON_ERROR_STOP on
-- Check the replacement permission topology; this does NOT authenticate
-- instructions and must not be counted as BOUNDARY-02.
SELECT 1 / CASE WHEN NOT has_function_privilege(
 'fs_payment_executor','fs_provider.commit_if_current(text,text,bigint,bigint,text)','EXECUTE')
 THEN 1 ELSE 0 END AS provider_denied;
SELECT 1 / CASE WHEN has_function_privilege(
 'fs_commit_service','fs_provider.commit_if_current(text,text,bigint,bigint,text)','EXECUTE')
 THEN 1 ELSE 0 END AS commitment_service_granted;
SELECT 1 / CASE WHEN NOT has_table_privilege(
 'fs_commit_service','fs_provider.mandates','UPDATE')
 THEN 1 ELSE 0 END AS service_cannot_change_mandate;
SELECT 1 / CASE WHEN NOT has_table_privilege(
 'fs_commit_service','fs_provider.commits','INSERT')
 THEN 1 ELSE 0 END AS service_cannot_insert_directly;
SET ROLE fs_authority_writer;
INSERT INTO fs_provider.mandates(id,epoch,revoked)
VALUES ('MANDATE-REPLACEMENT-SKELETON',1,false);
RESET ROLE;
SET ROLE fs_payment_executor;
DO $block$
BEGIN
 BEGIN
  PERFORM fs_provider.commit_if_current('PROVIDER-UNSIGNED','MANDATE-REPLACEMENT-SKELETON',1,75000000,'ATTACKER');
  RAISE EXCEPTION 'RED: provider can still call legacy function';
 EXCEPTION WHEN insufficient_privilege THEN NULL;
 END;
END $block$;
RESET ROLE;
-- Deliberate RED characterization: dedicated service identity still accepts
-- unsigned fields through the SQL function. This is NOT a valid payment.
SET ROLE fs_commit_service;
SELECT fs_provider.commit_if_current(
 'SERVICE-UNSIGNED-RED','MANDATE-REPLACEMENT-SKELETON',1,75000000,'ATTACKER'
) AS service_unsigned_result;
RESET ROLE;
SELECT 1 / CASE WHEN NOT EXISTS (
 SELECT 1 FROM fs_provider.commits WHERE intent_id='PROVIDER-UNSIGNED'
) THEN 1 ELSE 0 END AS provider_cannot_commit;
