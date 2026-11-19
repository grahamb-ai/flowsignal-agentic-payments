-- FS-SZ-PAY-001 reference PostgreSQL role isolation.
-- Run as a dedicated migration administrator in an ephemeral qualification DB.
-- This is a database permission gate, not institutional identity/KMS qualification.
CREATE ROLE fs_authority_writer NOLOGIN;
CREATE ROLE fs_payment_executor NOLOGIN;
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
GRANT SELECT ON fs_provider.commits TO fs_payment_executor;
-- The executor cannot insert a commitment directly; only the guarded function may.
CREATE FUNCTION fs_provider.commit_if_current(
 p_intent text, p_mandate text, p_epoch bigint, p_amount bigint, p_beneficiary text
) RETURNS text LANGUAGE plpgsql SECURITY DEFINER
SET search_path = pg_catalog, fs_provider AS $fn$
DECLARE current_epoch bigint; is_revoked boolean;
BEGIN
 IF p_intent IS NULL OR p_intent = '' OR p_amount <= 0 OR p_beneficiary IS NULL OR p_beneficiary = '' THEN
  RETURN 'REFUSED_INVALID_BINDING';
 END IF;
 SELECT epoch, revoked INTO current_epoch, is_revoked
 FROM fs_provider.mandates WHERE id = p_mandate FOR UPDATE;
 IF NOT FOUND OR is_revoked OR current_epoch <> p_epoch THEN
  RETURN 'REFUSED_AUTHORITY';
 END IF;
 INSERT INTO fs_provider.commits(intent_id,mandate_id,epoch,amount_minor,beneficiary)
 VALUES (p_intent,p_mandate,p_epoch,p_amount,p_beneficiary)
 ON CONFLICT (intent_id) DO NOTHING;
 IF NOT FOUND THEN RETURN 'REFUSED_DUPLICATE_INTENT'; END IF;
 RETURN 'COMMITTED';
END $fn$;
REVOKE ALL ON FUNCTION fs_provider.commit_if_current(text,text,bigint,bigint,text) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION fs_provider.commit_if_current(text,text,bigint,bigint,text) TO fs_payment_executor;
-- Both roles are explicitly denied TRUNCATE/DELETE on mandate state.
-- In production use a qualified single transaction commit function with
-- row locking and no direct table INSERT grant; this is only AUTH-01..04.
