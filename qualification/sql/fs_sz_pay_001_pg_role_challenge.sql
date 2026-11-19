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
DO $ BEGIN
 IF NOT EXISTS (SELECT 1 FROM fs_provider.mandates WHERE id='MANDATE-A' AND epoch=1 AND NOT revoked) THEN
  RAISE EXCEPTION 'AUTH-01..04: mandate state changed';
 END IF;
 IF EXISTS (SELECT 1 FROM fs_provider.mandates WHERE id='FORGED') THEN
  RAISE EXCEPTION 'AUTH-01: forged mandate exists';
 END IF;
 RAISE NOTICE 'AUTH-01..04 PASS: database permissions denied mutations';
END $;
RESET ROLE;
