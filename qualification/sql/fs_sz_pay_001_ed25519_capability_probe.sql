-- FS-SZ-PAY-001: inventory database cryptographic primitives, no assumptions.
-- PostgreSQL 16 pgcrypto supports digest/HMAC and PGP operations, not
-- a qualified Ed25519 verification function for our canonical envelope.
-- This probe records actual installed functions and privileges; it must
-- never grant a runtime commit permission.
\set ON_ERROR_STOP on
CREATE EXTENSION IF NOT EXISTS pgcrypto;
SELECT extname, extversion FROM pg_extension WHERE extname='pgcrypto';
SELECT n.nspname AS schema_name, p.proname AS function_name,
       pg_get_function_identity_arguments(p.oid) AS arguments
FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace
WHERE p.proname ~* '(ed25519|crypto_sign_verify|verify_signature)'
ORDER BY 1,2,3;
-- The expected absence of Ed25519 verification is not evidence of a
-- secure replacement; it is an implementation blocker.
