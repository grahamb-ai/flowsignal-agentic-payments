\set ON_ERROR_STOP on
-- Explicit privilege catalog checks: trust material must not be modified
-- or selected by any payment runtime identity.
SELECT 1 / CASE WHEN NOT has_table_privilege(
 'fs_payment_executor','fs_provider.institutional_issuer_keys','SELECT,INSERT,UPDATE,DELETE'
) THEN 1 ELSE 0 END AS executor_trust_denied;
SELECT 1 / CASE WHEN NOT has_table_privilege(
 'fs_commit_service','fs_provider.institutional_issuer_keys','SELECT,INSERT,UPDATE,DELETE'
) THEN 1 ELSE 0 END AS service_trust_denied;
SELECT 1 / CASE WHEN NOT has_table_privilege(
 'fs_authority_writer','fs_provider.institutional_issuer_keys','SELECT,INSERT,UPDATE,DELETE'
) THEN 1 ELSE 0 END AS authority_writer_trust_denied;
-- Real role-execution challenge; a service credential must not plant its own
-- trusted issuer key or enable a disabled key.
SET ROLE fs_commit_service;
DO $challenge$
BEGIN
 BEGIN
  INSERT INTO fs_provider.institutional_issuer_keys(issuer_id,public_key,enabled,valid_from)
  VALUES ('ATTACKER',decode(repeat('ab',32),'hex'),true,now());
  RAISE EXCEPTION 'RED: commitment service planted institutional key';
 EXCEPTION WHEN insufficient_privilege THEN NULL;
 END;
END $challenge$;
RESET ROLE;
SELECT 1 / CASE WHEN NOT EXISTS (
 SELECT 1 FROM fs_provider.institutional_issuer_keys WHERE issuer_id='ATTACKER'
) THEN 1 ELSE 0 END AS no_forged_issuer;
