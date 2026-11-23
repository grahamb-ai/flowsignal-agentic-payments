-- Real-login negative control: deliberately attempt forbidden direct write.
-- The harness expects psql exit NONZERO and zero matching durable records.
\set ON_ERROR_STOP on
SELECT current_user AS attack_login;
INSERT INTO fs_provider.commits(intent_id,mandate_id,epoch,amount_minor,beneficiary)
VALUES ('PRIVILEGE-DIRECT-BYPASS-001','MANDATE-VECTOR',8,75000000,'ATTACKER');
