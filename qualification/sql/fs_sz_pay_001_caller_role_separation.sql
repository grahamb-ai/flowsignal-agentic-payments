-- Separate caller identity from provider's private commitment identity.
-- The caller role can neither insert commitments nor invoke commit_if_current.
-- Provider HTTP process retains its private fs_payment_executor credential.
-- IMPORTANT: theft of that private credential still bypasses HTTP signatures.
CREATE ROLE fs_payment_caller NOLOGIN;
GRANT USAGE ON SCHEMA fs_provider TO fs_payment_caller;
GRANT SELECT ON fs_provider.mandates TO fs_payment_caller;
REVOKE ALL ON fs_provider.commits FROM fs_payment_caller;
REVOKE ALL ON FUNCTION fs_provider.commit_if_current(text,text,bigint,bigint,text) FROM fs_payment_caller;
