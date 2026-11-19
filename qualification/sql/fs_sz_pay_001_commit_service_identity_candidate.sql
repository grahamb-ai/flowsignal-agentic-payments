-- FS-SZ-PAY-001 isolated replacement identity: permission skeleton only.
-- Apply AFTER base schema and unsigned-function shutdown in an ephemeral DB.
-- This is NOT a cryptographic final-boundary implementation.
\set ON_ERROR_STOP on
BEGIN;
CREATE ROLE fs_commit_service NOLOGIN;
GRANT USAGE ON SCHEMA fs_provider TO fs_commit_service;
GRANT SELECT ON fs_provider.mandates TO fs_commit_service;
GRANT SELECT ON fs_provider.commits TO fs_commit_service;
GRANT EXECUTE ON FUNCTION fs_provider.commit_if_current(text,text,bigint,bigint,text)
  TO fs_commit_service;
-- The HTTP provider and other runtime roles retain no EXECUTE permission.
COMMIT;
