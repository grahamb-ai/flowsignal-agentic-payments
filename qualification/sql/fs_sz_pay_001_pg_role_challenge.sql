\set ON_ERROR_STOP on
-- Exercise actual PostgreSQL privileges, not an in-process Python guard.
SET ROLE fs_authority_writer;
INSERT INTO fs_provider.mandates(id, epoch, revoked) VALUES ('MANDATE-A', 1, false);
RESET ROLE;
SET ROLE fs_payment_executor;
DO $$
BEGIN
  BEGIN
    INSERT INTO fs_provider.mandates(id,epoch,revoked) VALUES ('FORGED',1,false);
    RAISE EXCEPTION 'AUTH-01: executor created mandate';
  EXCEPTION WHEN insufficient_privilege THEN NULL;
  END;
  BEGIN
    UPDATE fs_provider.mandates SET revoked=true WHERE id='MANDATE-A';
    RAISE EXCEPTION 'AUTH-02: executor revoked mandate';
  EXCEPTION WHEN insufficient_privilege THEN NULL;
  END;
  BEGIN
    UPDATE fs_provider.mandates SET revoked=true, epoch=epoch+1
      WHERE id='MANDATE-A' AND epoch=1;
    RAISE EXCEPTION 'AUTH-03: executor changed epoch';
  EXCEPTION WHEN insufficient_privilege THEN NULL;
  END;
  BEGIN
    DELETE FROM fs_provider.mandates WHERE id='MANDATE-A';
    RAISE EXCEPTION 'AUTH-04: executor deleted mandate';
  EXCEPTION WHEN insufficient_privilege THEN NULL;
  END;
END $$;
SELECT CASE WHEN (SELECT epoch=1 AND NOT revoked FROM fs_provider.mandates WHERE id='MANDATE-A')
 THEN 'AUTH-01..04 PASS: mandate unchanged' ELSE 1/0::text END;
RESET ROLE;
