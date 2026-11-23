-- IE-W10 direct-function containment candidate, isolated PostgreSQL 16 reference.
-- Run only after fs_sz_pay_001_pg_role_isolation.sql in an ephemeral test DB.
-- This removes executor direct invocation, not a qualified institutional signature path.
\set ON_ERROR_STOP on
REVOKE EXECUTE ON FUNCTION fs_provider.commit_if_current(text,text,bigint,bigint,text) FROM fs_payment_executor;
DO $$
BEGIN
 IF has_function_privilege('fs_payment_executor',
    'fs_provider.commit_if_current(text,text,bigint,bigint,text)','EXECUTE') THEN
   RAISE EXCEPTION 'RED: executor retains direct function invocation';
 END IF;
END $$;
SET ROLE fs_authority_writer;
INSERT INTO fs_provider.mandates(id,epoch,revoked)
VALUES ('MANDATE-CONTAINMENT',1,false);
RESET ROLE;
SET ROLE fs_payment_executor;
DO $$
BEGIN
  BEGIN
    PERFORM fs_provider.commit_if_current(
      'UNSIGNED-DIRECT','MANDATE-CONTAINMENT',1,75000000,'ATTACKER');
    RAISE EXCEPTION 'RED: direct function call unexpectedly succeeded';
  EXCEPTION WHEN insufficient_privilege THEN
    RAISE NOTICE 'GREEN: direct function call denied by PostgreSQL';
  END;
END $$;
SELECT count(*) AS unauthorized_commit_records
FROM fs_provider.commits WHERE intent_id='UNSIGNED-DIRECT';
RESET ROLE;
-- The executor cannot form commits via this function, but no replacement
-- independently authenticated commit path is qualified by this candidate.
