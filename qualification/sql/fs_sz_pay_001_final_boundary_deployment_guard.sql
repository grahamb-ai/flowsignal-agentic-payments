-- FS-SZ-PAY-001 final-boundary deployment guard.
-- Deliberately fail closed until a reviewed DB-enforced Ed25519 verifier is
-- installed and explicitly qualified. Merely having an extension installed
-- is NOT proof that it enforces the canonical institutional instruction.
-- This guard must NOT be removed to make CI green.
\set ON_ERROR_STOP on
DO $guard$
DECLARE
  unsigned_executor boolean;
  unsigned_service boolean;
  qualified_verifier boolean;
BEGIN
  unsigned_executor := has_function_privilege(
    'fs_payment_executor',
    'fs_provider.commit_if_current(text,text,bigint,bigint,text)', 'EXECUTE');
  unsigned_service := has_function_privilege(
    'fs_commit_service',
    'fs_provider.commit_if_current(text,text,bigint,bigint,text)', 'EXECUTE');
  IF unsigned_executor OR unsigned_service THEN
    RAISE EXCEPTION 'BOUNDARY-02 REFUSE: unsigned legacy commitment route remains executable';
  END IF;
  -- The reviewed verifier must expose an independently versioned,
  -- qualified final-commit contract. No such implementation exists yet.
  qualified_verifier := false;
  IF NOT qualified_verifier THEN
    RAISE EXCEPTION 'BOUNDARY-02 REFUSE: no qualified DB-enforced institutional Ed25519 final commit';
  END IF;
END $guard$;
