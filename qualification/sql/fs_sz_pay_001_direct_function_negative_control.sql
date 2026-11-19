-- FS-SZ-PAY-001 hostile negative control: a holder of the payment-executor
-- database credential can invoke the guarded function directly, without
-- institutional signed-instruction verification by the HTTP provider.
-- This demonstrates a credential/route closure gap, not a production exploit.
\set ON_ERROR_STOP on
SET ROLE fs_authority_writer;
INSERT INTO fs_provider.mandates(id,epoch,revoked)
VALUES ('MANDATE-DIRECT-FUNCTION',1,false);
RESET ROLE;
SET ROLE fs_payment_executor;
SELECT fs_provider.commit_if_current(
 'DIRECT-FUNCTION-UNSIGNED', 'MANDATE-DIRECT-FUNCTION',1,75000000,'ATTACKER'
) AS direct_function_outcome;
SELECT count(*) AS unauthorized_commit_records
FROM fs_provider.commits WHERE intent_id='DIRECT-FUNCTION-UNSIGNED';
RESET ROLE;
