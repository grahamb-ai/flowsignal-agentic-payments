-- FS-SZ-PAY-001 fail-closed cutover gate.
-- Until final-boundary instruction authentication is independently qualified,
-- no runtime role (including the proposed service identity) may call the
-- unsigned legacy commit function. Apply only in isolated qualification DB.
\set ON_ERROR_STOP on
BEGIN;
REVOKE EXECUTE ON FUNCTION fs_provider.commit_if_current(text,text,bigint,bigint,text)
 FROM fs_commit_service;
REVOKE EXECUTE ON FUNCTION fs_provider.commit_if_current(text,text,bigint,bigint,text)
 FROM fs_payment_executor;
REVOKE EXECUTE ON FUNCTION fs_provider.commit_if_current(text,text,bigint,bigint,text)
 FROM PUBLIC;
COMMIT;
SELECT 1 / CASE WHEN NOT has_function_privilege(
 'fs_commit_service','fs_provider.commit_if_current(text,text,bigint,bigint,text)','EXECUTE'
) THEN 1 ELSE 0 END AS service_unsigned_route_closed;
SELECT 1 / CASE WHEN NOT has_function_privilege(
 'fs_payment_executor','fs_provider.commit_if_current(text,text,bigint,bigint,text)','EXECUTE'
) THEN 1 ELSE 0 END AS provider_unsigned_route_closed;
