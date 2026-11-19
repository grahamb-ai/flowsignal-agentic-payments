-- FS-SZ-PAY-001 staged final-boundary migration (NOT production-qualified).
-- This deliberately disables the old unsigned SQL commitment route for the
-- existing executor role. It does NOT itself implement final-boundary signature
-- verification. Apply only to an isolated candidate database, not the current
-- regression environment, until a qualified replacement is implemented.
\set ON_ERROR_STOP on
BEGIN;
REVOKE EXECUTE ON FUNCTION fs_provider.commit_if_current(text,text,bigint,bigint,text)
  FROM fs_payment_executor;
-- PostgreSQL functions grant EXECUTE to PUBLIC by default unless revoked.
REVOKE ALL ON FUNCTION fs_provider.commit_if_current(text,text,bigint,bigint,text)
  FROM PUBLIC;
-- No runtime role is granted this unsigned function by this migration.
-- Database owner and superuser privileges remain outside ordinary role grants.
COMMIT;
