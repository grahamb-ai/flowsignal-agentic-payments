# FS-SZ-PAY-001 — Consolidated candidate qualification checkpoint

## Verified evidence
- Commit `54ec19127e806c29bcbb64c81ba1c4c848aa26a0`
- CI run: https://github.com/grahamb-ai/flowsignal-agentic-payments/actions/runs/44503567857
- Focused: **20 passed**; full: **88 passed, 1 failed**.
- The sole reported full-suite failure is the preserved T23 unfenced-provider challenge. Do not treat a workflow marked failure as a complete GREEN.
- This is a bounded local/reference integration, not production certification or universal route closure.

## Code-level review observations
1. `protected_consequence.py` now invokes `consume_permit_begin_outcome_and_claim_intent_once` for permits with signed business-intent ID. This is integrated, unlike the original T22 component.
2. `permit_consumption_store.py` creates the intent claim, consumed permit and initial unresolved outcome in one local attached-SQLite transaction.
3. `external_consequence_adapter.py` sends signed permit-derived business intent, mandate and provider epoch; an empty provider response is not commitment evidence.
4. `ProviderCommitFence.commit_transfer` checks mandate epoch and revocation in the same transaction as the simulated transfer record.
5. **Residual boundary:** the provider HTTP service compares request mandate/epoch to configured values, but does not independently authenticate a signed execution permit or cryptographically bind all payment fields to a trusted institution mandate. A caller with direct access to a configured provider route may still supply fields. Do not claim provider-side independent authority authentication.
6. **Residual boundary:** legacy test mode exists outside the declared protected boundary; no demonstrated production IAM isolation prevents access.
7. **Residual boundary:** local intent claim is not a distributed consensus or live-rail idempotency mechanism; unknown-outcome reconciliation remains a separate gate.
8. **Code hygiene:** the T22 function docstring still says it is not wired to adapters, which is stale after this integration; fix documentation without weakening any test.

## Acceptance before merging to main
- Verify the exact latest candidate commit and rerun focused and full regression on that SHA.
- Preserve the original T23 RED as a separately labelled historical test; do not silently delete or xfail it to manufacture all-green.
- Prove provider-side independently verified binding of the exact payment consequence, intent and authoritative epoch; demonstrate a hostile direct-route caller cannot substitute another mandate.
- Exercise restart and ambiguous provider acknowledgement with a fresh permit for the same intent and verify at most one provider commitment.
- Identify all protected route credentials and demonstrate the legacy/unfenced mode is inaccessible to them.
- Review for migration/compatibility of permit signature payload and database schema before production consideration.

**Decision: CONSOLIDATED REFERENCE CANDIDATE — NOT MERGE-READY.**
