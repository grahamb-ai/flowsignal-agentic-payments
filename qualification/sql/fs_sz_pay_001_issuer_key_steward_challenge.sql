\set ON_ERROR_STOP on
SELECT 1 / CASE WHEN NOT has_table_privilege(
 'fs_issuer_key_steward','fs_provider.mandates','INSERT,UPDATE,DELETE'
) THEN 1 ELSE 0 END AS steward_cannot_mutate_mandates;
SELECT 1 / CASE WHEN NOT has_table_privilege(
 'fs_issuer_key_steward','fs_provider.commits','INSERT,UPDATE,DELETE'
) THEN 1 ELSE 0 END AS steward_cannot_mutate_commits;
SET ROLE fs_issuer_key_steward;
INSERT INTO fs_provider.institutional_issuer_keys(issuer_id,public_key,enabled,valid_from)
VALUES ('INSTITUTION-A-V1',decode(repeat('11',32),'hex'),true,now()-interval '1 minute');
UPDATE fs_provider.institutional_issuer_keys SET enabled=false
 WHERE issuer_id='INSTITUTION-A-V1';
INSERT INTO fs_provider.institutional_issuer_keys(issuer_id,public_key,enabled,valid_from)
VALUES ('INSTITUTION-A-V2',decode(repeat('22',32),'hex'),true,now());
DO $challenge$
BEGIN
 BEGIN
  DELETE FROM fs_provider.institutional_issuer_keys WHERE issuer_id='INSTITUTION-A-V1';
  RAISE EXCEPTION 'RED: steward deleted historical issuer key';
 EXCEPTION WHEN insufficient_privilege THEN NULL;
 END;
 BEGIN
  INSERT INTO fs_provider.mandates(id,epoch,revoked)
  VALUES ('FORGED-STEWARDSHIP',1,false);
  RAISE EXCEPTION 'RED: steward forged mandate';
 EXCEPTION WHEN insufficient_privilege THEN NULL;
 END;
END $challenge$;
RESET ROLE;
SELECT 1 / CASE WHEN
 (SELECT count(*) FROM fs_provider.institutional_issuer_keys
  WHERE issuer_id='INSTITUTION-A-V1' AND NOT enabled)=1
 AND (SELECT count(*) FROM fs_provider.institutional_issuer_keys
  WHERE issuer_id='INSTITUTION-A-V2' AND enabled)=1
 AND NOT EXISTS(SELECT 1 FROM fs_provider.mandates WHERE id='FORGED-STEWARDSHIP')
 THEN 1 ELSE 0 END AS retirement_and_rotation_preserved;
