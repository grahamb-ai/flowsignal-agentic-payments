-- FS-SZ-PAY-001: real-login privilege boundary inventory and fail-closed assertions.
-- Run as fs_commit_service over TCP with its qualification password.
\set ON_ERROR_STOP on
SELECT current_user AS real_login;
SELECT 1 / CASE WHEN
  has_function_privilege(current_user,
    'fs_provider.commit_signed_if_current(text,bytea,bytea,text,text,bigint,text,text,bigint,text,text,text)',
    'EXECUTE')
  THEN 1 ELSE 0 END AS signed_function_available;
SELECT 1 / CASE WHEN NOT has_function_privilege(current_user,
  'fs_provider.commit_if_current(text,text,bigint,bigint,text)','EXECUTE')
  THEN 1 ELSE 0 END AS legacy_unsigned_function_denied;
SELECT 1 / CASE WHEN NOT has_table_privilege(current_user,'fs_provider.commits','INSERT')
 AND NOT has_table_privilege(current_user,'fs_provider.commits','UPDATE')
 AND NOT has_table_privilege(current_user,'fs_provider.commits','DELETE')
 AND NOT has_table_privilege(current_user,'fs_provider.commits','TRUNCATE')
 THEN 1 ELSE 0 END AS direct_commit_writes_denied;
SELECT 1 / CASE WHEN NOT has_table_privilege(current_user,'fs_provider.mandates','INSERT')
 AND NOT has_table_privilege(current_user,'fs_provider.mandates','UPDATE')
 AND NOT has_table_privilege(current_user,'fs_provider.mandates','DELETE')
 THEN 1 ELSE 0 END AS authority_mutation_denied;
SELECT 1 / CASE WHEN NOT has_table_privilege(current_user,'fs_provider.institutional_issuer_keys','SELECT')
 AND NOT has_table_privilege(current_user,'fs_provider.institutional_issuer_keys','INSERT')
 AND NOT has_table_privilege(current_user,'fs_provider.institutional_issuer_keys','UPDATE')
 AND NOT has_table_privilege(current_user,'fs_provider.institutional_issuer_keys','DELETE')
 THEN 1 ELSE 0 END AS issuer_key_table_denied;
SELECT 1 / CASE WHEN NOT has_schema_privilege(current_user,'fs_provider','CREATE')
 THEN 1 ELSE 0 END AS provider_schema_create_denied;
SELECT 1 / CASE WHEN NOT EXISTS (
 SELECT 1 FROM pg_roles WHERE rolname=current_user
 AND (rolsuper OR rolcreaterole OR rolcreatedb OR rolreplication OR rolbypassrls)
) THEN 1 ELSE 0 END AS privileged_role_flags_denied;
