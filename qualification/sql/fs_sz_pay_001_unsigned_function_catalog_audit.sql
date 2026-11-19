\set ON_ERROR_STOP on
-- BOUNDARY-01 catalog audit after fail-closed migration.
-- Verify no runtime identity inherits the legacy function privilege.
SELECT 1 / CASE WHEN NOT has_function_privilege(
 'fs_payment_executor',
 'fs_provider.commit_if_current(text,text,bigint,bigint,text)', 'EXECUTE'
) THEN 1 ELSE 0 END AS executor_denied;
SELECT 1 / CASE WHEN NOT has_function_privilege(
 'fs_payment_caller',
 'fs_provider.commit_if_current(text,text,bigint,bigint,text)', 'EXECUTE'
) THEN 1 ELSE 0 END AS caller_denied;
SELECT 1 / CASE WHEN NOT has_function_privilege(
 'fs_authority_writer',
 'fs_provider.commit_if_current(text,text,bigint,bigint,text)', 'EXECUTE'
) THEN 1 ELSE 0 END AS writer_denied;
-- Explicitly fail if any runtime role is a member of the function owner role.
SELECT 1 / CASE WHEN NOT pg_has_role(
 'fs_payment_executor', (SELECT proowner FROM pg_proc
 WHERE oid='fs_provider.commit_if_current(text,text,bigint,bigint,text)'::regprocedure),
 'MEMBER'
) THEN 1 ELSE 0 END AS executor_not_owner_member;
-- Function remains available to DB owner/superuser; that is a separate trust boundary.
