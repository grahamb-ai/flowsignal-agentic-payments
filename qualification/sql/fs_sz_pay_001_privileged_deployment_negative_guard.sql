-- FS-SZ-PAY-001 privileged-route deployment guard (negative control).
-- Intentionally REFUSE the present reference deployment. A superuser owning
-- consequence state and signing boundary is a declared uncontained bypass.
-- This does not purport to make superusers cryptographically powerless.
\set ON_ERROR_STOP on
DO $guard$
DECLARE
  schema_owner name;
  commit_owner name;
  mandate_owner name;
  issuer_owner name;
  function_owner name;
  privileged_owners text;
BEGIN
  SELECT pg_get_userbyid(nspowner) INTO schema_owner
  FROM pg_namespace WHERE nspname='fs_provider';
  SELECT pg_get_userbyid(relowner) INTO commit_owner
  FROM pg_class WHERE oid='fs_provider.commits'::regclass;
  SELECT pg_get_userbyid(relowner) INTO mandate_owner
  FROM pg_class WHERE oid='fs_provider.mandates'::regclass;
  SELECT pg_get_userbyid(relowner) INTO issuer_owner
  FROM pg_class WHERE oid='fs_provider.institutional_issuer_keys'::regclass;
  SELECT pg_get_userbyid(proowner) INTO function_owner
  FROM pg_proc WHERE oid='fs_provider.commit_signed_if_current(text,bytea,bytea,text,text,bigint,text,text,bigint,text,text,text)'::regprocedure;
  SELECT string_agg(rolname, ', ' ORDER BY rolname) INTO privileged_owners
  FROM pg_roles WHERE rolname IN (schema_owner,commit_owner,mandate_owner,issuer_owner,function_owner)
    AND (rolsuper OR rolcreaterole OR rolbypassrls);
  IF privileged_owners IS NOT NULL THEN
    RAISE EXCEPTION 'FS-SZ-PAY-001 PRIVILEGED_ROUTE_REFUSE: uncontained privileged owner(s): %',privileged_owners;
  END IF;
  -- A clean owner check is NOT enough to certify route closure. Require
  -- independent external verification, complete principal inventory and review.
  RAISE EXCEPTION 'FS-SZ-PAY-001 PRIVILEGED_ROUTE_REFUSE: independent evidence and deployment trust boundary not qualified';
END $guard$;
