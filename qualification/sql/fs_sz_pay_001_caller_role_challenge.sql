\set ON_ERROR_STOP on
SET ROLE fs_authority_writer;
INSERT INTO fs_provider.mandates(id,epoch,revoked) VALUES ('MANDATE-CALLER',1,false);
RESET ROLE;
SET ROLE fs_payment_caller;
DO $$
BEGIN
 BEGIN
  PERFORM fs_provider.commit_if_current('UNSIGNED-CALLER','MANDATE-CALLER',1,75000000,'ATTACKER');
  RAISE EXCEPTION 'UNTRUSTED CALLER EXECUTED PRIVATE COMMIT FUNCTION';
 EXCEPTION WHEN insufficient_privilege THEN NULL;
 END;
 BEGIN
  INSERT INTO fs_provider.commits(intent_id,mandate_id,epoch,amount_minor,beneficiary)
  VALUES ('UNSIGNED-DIRECT','MANDATE-CALLER',1,75000000,'ATTACKER');
  RAISE EXCEPTION 'UNTRUSTED CALLER INSERTED COMMIT';
 EXCEPTION WHEN insufficient_privilege THEN NULL;
 END;
END $$;
RESET ROLE;
SELECT 1 / CASE WHEN NOT EXISTS (
 SELECT 1 FROM fs_provider.commits WHERE mandate_id='MANDATE-CALLER'
) THEN 1 ELSE 0 END AS untrusted_caller_no_commit;
