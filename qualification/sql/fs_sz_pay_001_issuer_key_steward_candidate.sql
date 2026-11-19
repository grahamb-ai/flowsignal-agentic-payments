-- FS-SZ-PAY-001 trust stewardship candidate (isolated qualification DB only).
-- Separate issuer-key stewardship from mandate writers and payment executors.
\set ON_ERROR_STOP on
BEGIN;
CREATE ROLE fs_issuer_key_steward NOLOGIN;
GRANT USAGE ON SCHEMA fs_provider TO fs_issuer_key_steward;
GRANT SELECT, INSERT, UPDATE ON fs_provider.institutional_issuer_keys TO fs_issuer_key_steward;
-- No DELETE: retire keys by disabling, preserving lineage.
-- No mandate or commitment table permissions granted.
COMMIT;
