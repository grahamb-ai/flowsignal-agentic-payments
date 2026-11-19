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
-- Assert unchanged state using SQL arithmetic to make unexpected state fatal.
SELECT 1 / CASE WHEN EXISTS (
 SELECT 1 FROM fs_provider.mandates WHERE id='MANDATE-A' AND epoch=1 AND NOT revoked
) AND NOT EXISTS (
 SELECT 1 FROM fs_provider.mandates WHERE id='FORGED'
) THEN 1 ELSE 0 END AS authority_state_unchanged;
RESET ROLE;

-- Guarded commitment path; direct INSERT must be denied.
SET ROLE fs_payment_executor;
DO $$
BEGIN
 BEGIN
  INSERT INTO fs_provider.commits(intent_id,mandate_id,epoch,amount_minor,beneficiary)
  VALUES ('DIRECT','MANDATE-A',1,100,'ATTACKER');
  RAISE EXCEPTION 'AUTH-COMMIT: direct executor INSERT succeeded';
 EXCEPTION WHEN insufficient_privilege THEN NULL;
 END;
END $$;
SELECT 1 / CASE WHEN fs_provider.commit_if_current('INTENT-1','MANDATE-A',1,100,'BENEFICIARY')='COMMITTED' THEN 1 ELSE 0 END AS initial_commit_allowed;
SELECT 1 / CASE WHEN fs_provider.commit_if_current('INTENT-1','MANDATE-A',1,100,'BENEFICIARY')='REFUSED_DUPLICATE_INTENT' THEN 1 ELSE 0 END AS duplicate_refused;
RESET ROLE;
SET ROLE fs_authority_writer;
UPDATE fs_provider.mandates SET revoked=true,epoch=epoch+1 WHERE id='MANDATE-A' AND epoch=1;
RESET ROLE;
SET ROLE fs_payment_executor;
SELECT 1 / CASE WHEN fs_provider.commit_if_current('INTENT-2','MANDATE-A',1,100,'BENEFICIARY')='REFUSED_AUTHORITY' THEN 1 ELSE 0 END AS post_revocation_refused;
SELECT 1 / CASE WHEN (SELECT COUNT(*) FROM fs_provider.commits)=1 THEN 1 ELSE 0 END AS no_extra_commit;
RESET ROLE;

-- Hostile alternate executor: direct commitment writes must be denied even
-- with a valid mandate ID and epoch; forged executor role cannot mutate state.
SET ROLE fs_payment_executor;
DO $$
BEGIN
 BEGIN
  INSERT INTO fs_provider.commits(intent_id,mandate_id,epoch,amount_minor,beneficiary)
  VALUES ('ALTERNATE-EXECUTOR-BYPASS','MANDATE-A',1,75000000,'ATTACKER');
  RAISE EXCEPTION 'ALTERNATE_EXECUTOR_RED: direct INSERT succeeded';
 EXCEPTION WHEN insufficient_privilege THEN NULL;
 END;
END $$;
SELECT 1 / CASE WHEN NOT EXISTS (
 SELECT 1 FROM fs_provider.commits WHERE intent_id='ALTERNATE-EXECUTOR-BYPASS'
) THEN 1 ELSE 0 END AS alternate_direct_commit_refused;
RESET ROLE;
