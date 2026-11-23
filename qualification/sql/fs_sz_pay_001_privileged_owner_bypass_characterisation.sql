-- FS-SZ-PAY-001 privileged-owner hostile characterisation.
-- This is intentionally executed by the ephemeral qualification postgres owner.
-- It demonstrates an administrative bypass, NOT a production control.
\set ON_ERROR_STOP on
SELECT current_user AS privileged_identity;
INSERT INTO fs_provider.commits(intent_id,mandate_id,epoch,amount_minor,beneficiary)
VALUES ('PRIVILEGED-OWNER-BYPASS-001','MANDATE-VECTOR',8,75000000,'ATTACKER');
SELECT count(*) AS privileged_bypass_durable_count
FROM fs_provider.commits WHERE intent_id='PRIVILEGED-OWNER-BYPASS-001';
