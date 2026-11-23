-- FS-SZ-PAY-001 experimental authenticated final-commit function.
-- PostgreSQL 16 + pgsodium 3.1.8 qualification environment ONLY.
-- NOT production-qualified: canonical JSON parser, issuer lifecycle,
-- extension trust, privileged owners and full route closure require review.
\set ON_ERROR_STOP on
BEGIN;
CREATE FUNCTION fs_provider.commit_signed_if_current(
 p_issuer text, p_signed_bytes bytea, p_signature bytea,
 p_intent text, p_mandate text, p_epoch bigint, p_source text,
 p_beneficiary text, p_amount_minor bigint, p_currency text,
 p_action text, p_target text
) RETURNS text LANGUAGE plpgsql SECURITY DEFINER
SET search_path = pg_catalog, fs_provider, pgsodium AS $fn$
DECLARE
  proof jsonb;
  ins jsonb;
  expiry timestamptz;
  reconstructed bytea;
  trusted_key bytea;
  current_epoch bigint;
  is_revoked boolean;
BEGIN
  IF p_signed_bytes IS NULL OR p_signature IS NULL OR octet_length(p_signature) <> 64
     OR p_issuer IS NULL OR p_intent IS NULL OR p_intent = ''
     OR p_mandate IS NULL OR p_mandate = '' OR p_epoch IS NULL OR p_epoch <= 0
     OR p_source IS NULL OR p_source = '' OR p_beneficiary IS NULL OR p_beneficiary = ''
     OR p_amount_minor IS NULL OR p_amount_minor <= 0
     OR p_currency <> 'GBP' OR p_action <> 'transfer' OR p_target <> 'protected-provider'
  THEN RETURN 'REFUSED_INVALID_BINDING'; END IF;

  BEGIN
    proof := convert_from(p_signed_bytes, 'UTF8')::jsonb;
    ins := proof->'instruction';
    IF jsonb_typeof(proof) <> 'object'
       OR jsonb_typeof(ins) <> 'object'
       OR jsonb_typeof(proof->'expires_at') <> 'string'
       OR jsonb_typeof(ins->'authority_epoch') <> 'number'
       OR jsonb_typeof(ins->'amount_minor') <> 'number'
       OR (proof->>'expires_at')::timestamptz <= clock_timestamp()
       OR (proof->>'expires_at')::timestamptz > clock_timestamp() + interval '1 day'
       OR ins->>'payment_intent_id' IS DISTINCT FROM p_intent
       OR ins->>'mandate_id' IS DISTINCT FROM p_mandate
       OR (ins->>'authority_epoch')::bigint IS DISTINCT FROM p_epoch
       OR ins->>'source_account' IS DISTINCT FROM p_source
       OR ins->>'beneficiary' IS DISTINCT FROM p_beneficiary
       OR (ins->>'amount_minor')::bigint IS DISTINCT FROM p_amount_minor
       OR ins->>'currency' IS DISTINCT FROM p_currency
       OR ins->>'action' IS DISTINCT FROM p_action
       OR ins->>'target' IS DISTINCT FROM p_target
    THEN RETURN 'REFUSED_INVALID_BINDING'; END IF;
  EXCEPTION WHEN others THEN
    RETURN 'REFUSED_INVALID_BINDING';
  END;

  -- Exact supported canonical JSON byte protocol, not merely parsed equivalence.
  -- Fail closed for unexpected keys and unsupported textual characters.
  IF (SELECT count(*) FROM jsonb_object_keys(proof)) <> 2
     OR (SELECT count(*) FROM jsonb_object_keys(ins)) <> 9
     OR (proof->>'expires_at') !~ '^[0-9T:+.Z-]+
    FROM fs_provider.institutional_issuer_keys
   WHERE issuer_id = p_issuer AND enabled
     AND valid_from <= clock_timestamp()
     AND (valid_until IS NULL OR valid_until > clock_timestamp());
  IF trusted_key IS NULL THEN RETURN 'REFUSED_UNTRUSTED_ISSUER'; END IF;
  BEGIN
    IF pgsodium.crypto_sign_verify_detached(p_signature,p_signed_bytes,trusted_key) IS DISTINCT FROM TRUE
    THEN RETURN 'REFUSED_UNAUTHENTICATED_INSTRUCTION'; END IF;
  EXCEPTION WHEN others THEN
    -- Invalid signatures may raise rather than return false. Never let
    -- a cryptographic exception become an authority grant.
    RETURN 'REFUSED_UNAUTHENTICATED_INSTRUCTION';
  END;

  SELECT epoch,revoked INTO current_epoch,is_revoked
    FROM fs_provider.mandates WHERE id=p_mandate FOR UPDATE;
  IF NOT FOUND OR is_revoked OR current_epoch <> p_epoch
  THEN RETURN 'REFUSED_AUTHORITY'; END IF;
  INSERT INTO fs_provider.commits(intent_id,mandate_id,epoch,amount_minor,beneficiary)
  VALUES (p_intent,p_mandate,p_epoch,p_amount_minor,p_beneficiary)
  ON CONFLICT (intent_id) DO NOTHING;
  IF NOT FOUND THEN RETURN 'REFUSED_DUPLICATE_INTENT'; END IF;
  RETURN 'COMMITTED';
END $fn$;
REVOKE ALL ON FUNCTION fs_provider.commit_signed_if_current(
 text,bytea,bytea,text,text,bigint,text,text,bigint,text,text,text) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION fs_provider.commit_signed_if_current(
 text,bytea,bytea,text,text,bigint,text,text,bigint,text,text,text) TO fs_commit_service;
REVOKE EXECUTE ON FUNCTION fs_provider.commit_if_current(
 text,text,bigint,bigint,text) FROM fs_commit_service,fs_payment_executor,PUBLIC;
COMMIT;

     OR p_intent !~ '^[A-Za-z0-9_-]+
    FROM fs_provider.institutional_issuer_keys
   WHERE issuer_id = p_issuer AND enabled
     AND valid_from <= clock_timestamp()
     AND (valid_until IS NULL OR valid_until > clock_timestamp());
  IF trusted_key IS NULL THEN RETURN 'REFUSED_UNTRUSTED_ISSUER'; END IF;
  BEGIN
    IF pgsodium.crypto_sign_verify_detached(p_signature,p_signed_bytes,trusted_key) IS DISTINCT FROM TRUE
    THEN RETURN 'REFUSED_UNAUTHENTICATED_INSTRUCTION'; END IF;
  EXCEPTION WHEN others THEN
    -- Invalid signatures may raise rather than return false. Never let
    -- a cryptographic exception become an authority grant.
    RETURN 'REFUSED_UNAUTHENTICATED_INSTRUCTION';
  END;

  SELECT epoch,revoked INTO current_epoch,is_revoked
    FROM fs_provider.mandates WHERE id=p_mandate FOR UPDATE;
  IF NOT FOUND OR is_revoked OR current_epoch <> p_epoch
  THEN RETURN 'REFUSED_AUTHORITY'; END IF;
  INSERT INTO fs_provider.commits(intent_id,mandate_id,epoch,amount_minor,beneficiary)
  VALUES (p_intent,p_mandate,p_epoch,p_amount_minor,p_beneficiary)
  ON CONFLICT (intent_id) DO NOTHING;
  IF NOT FOUND THEN RETURN 'REFUSED_DUPLICATE_INTENT'; END IF;
  RETURN 'COMMITTED';
END $fn$;
REVOKE ALL ON FUNCTION fs_provider.commit_signed_if_current(
 text,bytea,bytea,text,text,bigint,text,text,bigint,text,text,text) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION fs_provider.commit_signed_if_current(
 text,bytea,bytea,text,text,bigint,text,text,bigint,text,text,text) TO fs_commit_service;
REVOKE EXECUTE ON FUNCTION fs_provider.commit_if_current(
 text,text,bigint,bigint,text) FROM fs_commit_service,fs_payment_executor,PUBLIC;
COMMIT;

     OR p_mandate !~ '^[A-Za-z0-9_-]+
    FROM fs_provider.institutional_issuer_keys
   WHERE issuer_id = p_issuer AND enabled
     AND valid_from <= clock_timestamp()
     AND (valid_until IS NULL OR valid_until > clock_timestamp());
  IF trusted_key IS NULL THEN RETURN 'REFUSED_UNTRUSTED_ISSUER'; END IF;
  BEGIN
    IF pgsodium.crypto_sign_verify_detached(p_signature,p_signed_bytes,trusted_key) IS DISTINCT FROM TRUE
    THEN RETURN 'REFUSED_UNAUTHENTICATED_INSTRUCTION'; END IF;
  EXCEPTION WHEN others THEN
    -- Invalid signatures may raise rather than return false. Never let
    -- a cryptographic exception become an authority grant.
    RETURN 'REFUSED_UNAUTHENTICATED_INSTRUCTION';
  END;

  SELECT epoch,revoked INTO current_epoch,is_revoked
    FROM fs_provider.mandates WHERE id=p_mandate FOR UPDATE;
  IF NOT FOUND OR is_revoked OR current_epoch <> p_epoch
  THEN RETURN 'REFUSED_AUTHORITY'; END IF;
  INSERT INTO fs_provider.commits(intent_id,mandate_id,epoch,amount_minor,beneficiary)
  VALUES (p_intent,p_mandate,p_epoch,p_amount_minor,p_beneficiary)
  ON CONFLICT (intent_id) DO NOTHING;
  IF NOT FOUND THEN RETURN 'REFUSED_DUPLICATE_INTENT'; END IF;
  RETURN 'COMMITTED';
END $fn$;
REVOKE ALL ON FUNCTION fs_provider.commit_signed_if_current(
 text,bytea,bytea,text,text,bigint,text,text,bigint,text,text,text) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION fs_provider.commit_signed_if_current(
 text,bytea,bytea,text,text,bigint,text,text,bigint,text,text,text) TO fs_commit_service;
REVOKE EXECUTE ON FUNCTION fs_provider.commit_if_current(
 text,text,bigint,bigint,text) FROM fs_commit_service,fs_payment_executor,PUBLIC;
COMMIT;

     OR p_source !~ '^[A-Za-z0-9_-]+
    FROM fs_provider.institutional_issuer_keys
   WHERE issuer_id = p_issuer AND enabled
     AND valid_from <= clock_timestamp()
     AND (valid_until IS NULL OR valid_until > clock_timestamp());
  IF trusted_key IS NULL THEN RETURN 'REFUSED_UNTRUSTED_ISSUER'; END IF;
  BEGIN
    IF pgsodium.crypto_sign_verify_detached(p_signature,p_signed_bytes,trusted_key) IS DISTINCT FROM TRUE
    THEN RETURN 'REFUSED_UNAUTHENTICATED_INSTRUCTION'; END IF;
  EXCEPTION WHEN others THEN
    -- Invalid signatures may raise rather than return false. Never let
    -- a cryptographic exception become an authority grant.
    RETURN 'REFUSED_UNAUTHENTICATED_INSTRUCTION';
  END;

  SELECT epoch,revoked INTO current_epoch,is_revoked
    FROM fs_provider.mandates WHERE id=p_mandate FOR UPDATE;
  IF NOT FOUND OR is_revoked OR current_epoch <> p_epoch
  THEN RETURN 'REFUSED_AUTHORITY'; END IF;
  INSERT INTO fs_provider.commits(intent_id,mandate_id,epoch,amount_minor,beneficiary)
  VALUES (p_intent,p_mandate,p_epoch,p_amount_minor,p_beneficiary)
  ON CONFLICT (intent_id) DO NOTHING;
  IF NOT FOUND THEN RETURN 'REFUSED_DUPLICATE_INTENT'; END IF;
  RETURN 'COMMITTED';
END $fn$;
REVOKE ALL ON FUNCTION fs_provider.commit_signed_if_current(
 text,bytea,bytea,text,text,bigint,text,text,bigint,text,text,text) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION fs_provider.commit_signed_if_current(
 text,bytea,bytea,text,text,bigint,text,text,bigint,text,text,text) TO fs_commit_service;
REVOKE EXECUTE ON FUNCTION fs_provider.commit_if_current(
 text,text,bigint,bigint,text) FROM fs_commit_service,fs_payment_executor,PUBLIC;
COMMIT;

     OR p_beneficiary !~ '^[A-Za-z0-9_-]+
    FROM fs_provider.institutional_issuer_keys
   WHERE issuer_id = p_issuer AND enabled
     AND valid_from <= clock_timestamp()
     AND (valid_until IS NULL OR valid_until > clock_timestamp());
  IF trusted_key IS NULL THEN RETURN 'REFUSED_UNTRUSTED_ISSUER'; END IF;
  BEGIN
    IF pgsodium.crypto_sign_verify_detached(p_signature,p_signed_bytes,trusted_key) IS DISTINCT FROM TRUE
    THEN RETURN 'REFUSED_UNAUTHENTICATED_INSTRUCTION'; END IF;
  EXCEPTION WHEN others THEN
    -- Invalid signatures may raise rather than return false. Never let
    -- a cryptographic exception become an authority grant.
    RETURN 'REFUSED_UNAUTHENTICATED_INSTRUCTION';
  END;

  SELECT epoch,revoked INTO current_epoch,is_revoked
    FROM fs_provider.mandates WHERE id=p_mandate FOR UPDATE;
  IF NOT FOUND OR is_revoked OR current_epoch <> p_epoch
  THEN RETURN 'REFUSED_AUTHORITY'; END IF;
  INSERT INTO fs_provider.commits(intent_id,mandate_id,epoch,amount_minor,beneficiary)
  VALUES (p_intent,p_mandate,p_epoch,p_amount_minor,p_beneficiary)
  ON CONFLICT (intent_id) DO NOTHING;
  IF NOT FOUND THEN RETURN 'REFUSED_DUPLICATE_INTENT'; END IF;
  RETURN 'COMMITTED';
END $fn$;
REVOKE ALL ON FUNCTION fs_provider.commit_signed_if_current(
 text,bytea,bytea,text,text,bigint,text,text,bigint,text,text,text) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION fs_provider.commit_signed_if_current(
 text,bytea,bytea,text,text,bigint,text,text,bigint,text,text,text) TO fs_commit_service;
REVOKE EXECUTE ON FUNCTION fs_provider.commit_if_current(
 text,text,bigint,bigint,text) FROM fs_commit_service,fs_payment_executor,PUBLIC;
COMMIT;

  THEN RETURN 'REFUSED_NONCANONICAL_WIRE'; END IF;
  reconstructed := convert_to(
    '{"expires_at":' || to_json(proof->>'expires_at')::text ||
    ',"instruction":{"action":' || to_json(p_action)::text ||
    ',"amount_minor":' || p_amount_minor::text ||
    ',"authority_epoch":' || p_epoch::text ||
    ',"beneficiary":' || to_json(p_beneficiary)::text ||
    ',"currency":' || to_json(p_currency)::text ||
    ',"mandate_id":' || to_json(p_mandate)::text ||
    ',"payment_intent_id":' || to_json(p_intent)::text ||
    ',"source_account":' || to_json(p_source)::text ||
    ',"target":' || to_json(p_target)::text || '}}', 'UTF8');
  IF reconstructed IS DISTINCT FROM p_signed_bytes
  THEN RETURN 'REFUSED_NONCANONICAL_WIRE'; END IF;

  SELECT public_key INTO trusted_key
    FROM fs_provider.institutional_issuer_keys
   WHERE issuer_id = p_issuer AND enabled
     AND valid_from <= clock_timestamp()
     AND (valid_until IS NULL OR valid_until > clock_timestamp());
  IF trusted_key IS NULL THEN RETURN 'REFUSED_UNTRUSTED_ISSUER'; END IF;
  BEGIN
    IF pgsodium.crypto_sign_verify_detached(p_signature,p_signed_bytes,trusted_key) IS DISTINCT FROM TRUE
    THEN RETURN 'REFUSED_UNAUTHENTICATED_INSTRUCTION'; END IF;
  EXCEPTION WHEN others THEN
    -- Invalid signatures may raise rather than return false. Never let
    -- a cryptographic exception become an authority grant.
    RETURN 'REFUSED_UNAUTHENTICATED_INSTRUCTION';
  END;

  SELECT epoch,revoked INTO current_epoch,is_revoked
    FROM fs_provider.mandates WHERE id=p_mandate FOR UPDATE;
  IF NOT FOUND OR is_revoked OR current_epoch <> p_epoch
  THEN RETURN 'REFUSED_AUTHORITY'; END IF;
  INSERT INTO fs_provider.commits(intent_id,mandate_id,epoch,amount_minor,beneficiary)
  VALUES (p_intent,p_mandate,p_epoch,p_amount_minor,p_beneficiary)
  ON CONFLICT (intent_id) DO NOTHING;
  IF NOT FOUND THEN RETURN 'REFUSED_DUPLICATE_INTENT'; END IF;
  RETURN 'COMMITTED';
END $fn$;
REVOKE ALL ON FUNCTION fs_provider.commit_signed_if_current(
 text,bytea,bytea,text,text,bigint,text,text,bigint,text,text,text) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION fs_provider.commit_signed_if_current(
 text,bytea,bytea,text,text,bigint,text,text,bigint,text,text,text) TO fs_commit_service;
REVOKE EXECUTE ON FUNCTION fs_provider.commit_if_current(
 text,text,bigint,bigint,text) FROM fs_commit_service,fs_payment_executor,PUBLIC;
COMMIT;
