-- FS-SZ-PAY-001 administrator-controlled institutional issuer trust store.
-- Preparatory schema ONLY. No cryptographic final-commit verifier exists yet.
-- Must run as migration owner in isolated candidate database.
\set ON_ERROR_STOP on
BEGIN;
CREATE TABLE fs_provider.institutional_issuer_keys (
  issuer_id text PRIMARY KEY CHECK (length(issuer_id) > 0),
  public_key bytea NOT NULL CHECK (octet_length(public_key) = 32),
  enabled boolean NOT NULL DEFAULT false,
  valid_from timestamptz NOT NULL,
  valid_until timestamptz,
  CHECK (valid_until IS NULL OR valid_until > valid_from)
);
REVOKE ALL ON fs_provider.institutional_issuer_keys FROM PUBLIC;
REVOKE ALL ON fs_provider.institutional_issuer_keys FROM fs_payment_executor;
REVOKE ALL ON fs_provider.institutional_issuer_keys FROM fs_commit_service;
REVOKE ALL ON fs_provider.institutional_issuer_keys FROM fs_authority_writer;
-- A separate, explicitly administered key steward must be granted access
-- only after identity and lifecycle qualification; no runtime grants here.
COMMIT;
