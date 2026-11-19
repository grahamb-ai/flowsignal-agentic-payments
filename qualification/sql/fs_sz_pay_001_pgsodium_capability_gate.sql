-- FS-SZ-PAY-001 pgsodium capability gate.
-- Run only in an isolated, independently provisioned PostgreSQL instance.
-- No extension is installed by this probe; absence must fail the gate.
\set ON_ERROR_STOP on
DO $gate$
DECLARE ext_schema text; fn_count integer;
BEGIN
 SELECT n.nspname INTO ext_schema
 FROM pg_extension e JOIN pg_namespace n ON n.oid=e.extnamespace
 WHERE e.extname='pgsodium';
 IF ext_schema IS NULL THEN
  RAISE EXCEPTION 'PGSODIUM NOT INSTALLED: BOUNDARY-02 remains RED';
 END IF;
 SELECT count(*) INTO fn_count
 FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace
 WHERE n.nspname=ext_schema
 AND p.proname='crypto_sign_verify_detached'
 AND pg_get_function_identity_arguments(p.oid)='sig bytea, message bytea, key bytea'
 AND p.prorettype='boolean'::regtype;
 IF fn_count <> 1 THEN
  RAISE EXCEPTION 'PGSODIUM DETACHED ED25519 VERIFIER SIGNATURE NOT QUALIFIED: count=%',fn_count;
 END IF;
 RAISE NOTICE 'PGSODIUM FUNCTION FOUND: cryptographic interoperability and privileges NOT QUALIFIED';
END $gate$;
