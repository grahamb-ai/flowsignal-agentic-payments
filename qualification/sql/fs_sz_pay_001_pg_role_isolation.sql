-- FS-SZ-PAY-001 reference PostgreSQL role isolation.
-- Run as a dedicated migration administrator in an ephemeral qualification DB.
-- This is a database permission gate, not institutional identity/KMS qualification.
CREATE ROLE fs_authority_writer LOGIN PASSWORD 'ephemeral-writer-only';
CREATE ROLE fs_payment_executor LOGIN PASSWORD 'ephemeral-executor-only';
CREATE SCHEMA fs_provider;
REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA fs_provider FROM PUBLIC;
GRANT USAGE ON SCHEMA fs_provider TO fs_authority_writer, fs_payment_executor;
CREATE TABLE fs_provider.mandates (
    id text PRIMARY KEY,
    epoch bigint NOT NULL CHECK (epoch > 0),
    revoked boolean NOT NULL DEFAULT false
);
CREATE TABLE fs_provider.commits (
    intent_id text PRIMARY KEY,
    mandate_id text NOT NULL REFERENCES fs_provider.mandates(id),
    epoch bigint NOT NULL,
    amount_minor bigint NOT NULL CHECK (amount_minor > 0),
    beneficiary text NOT NULL
);
REVOKE ALL ON ALL TABLES IN SCHEMA fs_provider FROM PUBLIC;
GRANT SELECT, INSERT, UPDATE ON fs_provider.mandates TO fs_authority_writer;
GRANT SELECT ON fs_provider.mandates TO fs_payment_executor;
GRANT SELECT, INSERT ON fs_provider.commits TO fs_payment_executor;
-- Both roles are explicitly denied TRUNCATE/DELETE on mandate state.
-- In production use a qualified single transaction commit function with
-- row locking and no direct table INSERT grant; this is only AUTH-01..04.
