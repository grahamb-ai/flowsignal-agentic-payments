# CBP-002 — External Consequence Boundary Result

## Classification

**CBP-002 — EXTERNAL CONSEQUENCE BOUNDARY: PASS (BOUNDED TO NAMED EXTERNAL TARGET AND INTEGRATION)**

## Evidence status

This document records the **first executable result** against the proposition frozen before implementation in `CBP-002_CHALLENGE.md`.

The frozen proposition was committed at:

`fc02a92b1d26e0fdcfe6df2c7a13f387bf49c783`

Frozen base commit:

`cadfaade73867a56c61a4dcc04a5f4434e30d0d5`

The frozen challenge was not changed after the executable result was observed.

## Executed PR state

Pull request: **#17 — CBP-002 — external consequence boundary qualification**

PR head at first run:

`672eec109f39545867913b0104bcd70b62cebd4d`

GitHub Actions checked out the PR merge state:

`cb96ba5953af9cf575b993d3197f363831c1c671`

Workflow: **CBP-002 External Consequence Boundary**

Run ID:

`32337280354`

Job: **Frozen external consequence seam**

Job ID:

`96329163601`

Exact qualification command:

```text
pytest -q tests/test_cbp002_external_consequence_boundary.py
```

Observed result:

```text
.                                                                        [100%]
1 passed in 0.21s
```

Workflow conclusion: **success**.

This is an execution in GitHub Actions against the PR state. It is not described as independent verification.

## Named external target

The qualification uses `external_targets/cbp002_consequence_service.py`, launched as a **separate OS process** and reached over localhost HTTP.

The service owns consequence state outside FlowSignal's protected-consequence state store. Its state is queried through its own HTTP `/state` endpoint.

The external state includes:

- source balance;
- beneficiary balances;
- transfer count; and
- recorded transfers.

FlowSignal's internal `CONSEQUENCE_FORMED` record is therefore not the sole observation used to classify CBP-002.

## Protected integration

`app/engines/external_consequence_adapter.py` maps the exact `ExecutionAttempt` into an external payment request and invokes that external mutation only through the existing protected consequence formation interval.

The external transaction identifier is bound to the execution permit signature. The attempted action binding is recomputed from the actual external action presented to the adapter.

## Observations exercised by the executable qualification

### 1. Independently observable initial external state — PASS

Before FlowSignal attempts consequence formation, the test queries the external service directly and establishes zero transfers and a source balance of `5,000,000.0`.

### 2. Current exact-action authority and bound permit — PASS

The AP-001 authority request evaluates `ALLOW`; the execution gateway validates the exact action and issues an execution permit bound to the current authority-state version and action-binding hash.

### 3. Non-vacuous positive control — PASS

A current valid permit is presented through the protected external adapter.

The protected consequence outcome is `CONSEQUENCE_FORMED` and the external service is queried independently. The external target records exactly one transfer, debits the source balance by the intended amount and credits the intended beneficiary.

### 4. Distinct challenged external state — PASS

The sandbox administrative reset endpoint is used to establish a distinct zero-transfer state for the challenged attempt. The resulting state is queried independently before the challenge begins.

The reset route is an administrative test-fixture route and is explicitly outside the closure claim.

### 5. Authority changed after permit issuance — PASS

A second valid exact-action permit is obtained under the then-current authority state. The authoritative runtime state version is then advanced before external consequence formation.

The test asserts that the new authority-state version differs from the version bound into the historical permit.

### 6. Historical permit attempted at external bind — PASS

The historical permit is presented through the same protected external adapter after the authoritative state change.

The protected consequence mechanism returns:

`DENIED_AUTHORITY_STATE_STALE`

### 7. NO_EXTERNAL_EFFECT under stale authority — PASS

After the stale-authority denial, the test queries the external target itself.

Its complete observable state is equal to the state recorded immediately before the challenged attempt. No transfer was recorded and no external balance changed.

### 8. Denial evidence / non-formation — PASS

The consequence receipt is bound to the historical authority receipt and records:

- `DENIED_AUTHORITY_STATE_STALE`;
- `consequence_formed = false`; and
- valid consequence-receipt integrity.

### 9. Same-route stale retry — PASS

The same historical permit is presented again through the protected external adapter. It is denied as stale and the independently queried external state remains unchanged.

### 10. Material action substitution — PASS

The historical attempt is changed to both a different beneficiary and a different amount.

The result is:

`DENIED_ACTION_BINDING_MISMATCH`

The external state remains unchanged.

### 11. Current authority reacquisition — PASS

Authority is reacquired for the same intended exact action under the new authority-state version.

The test establishes a new authority receipt ID, a different permit signature and a permit bound to the current authority-state version.

### 12. Historical replay after reacquisition — PASS

After current authority has been reacquired, the historical permit is presented again.

It remains denied as:

`DENIED_AUTHORITY_STATE_STALE`

The external state remains unchanged.

### 13. Fresh-authority external consequence — PASS

The fresh current permit is presented through the same protected external adapter.

The result is `CONSEQUENCE_FORMED`.

The external target is then queried independently and records exactly one intended transfer. The recorded transaction ID equals the fresh permit signature, the beneficiary matches the intended action and the amount matches the intended action.

## Claim/mechanism correspondence earned by this result

Within the named CBP-002 integration, the executable evidence establishes that a previously valid exact-action FlowSignal execution permit does **not** cause the independently observable external consequence after the authoritative runtime state on which that permit depends has changed.

It also establishes, within that same integration, that:

- stale-authority attempts leave the external target unchanged;
- repeat stale attempts leave it unchanged;
- a materially substituted action cannot be transferred under the historical permit;
- reacquiring current authority does not rehabilitate the historical permit; and
- a fresh current exact-action permit can form the external consequence, demonstrating that the refusal cases are not explained by a permanently inert target.

## Alternate-route boundary

CBP-002 does **not** establish universal alternate-route closure.

The external sandbox deliberately exposes an administrative reset route used by the qualification fixture. An administrator or holder of separate target credentials/capabilities could therefore exist outside the FlowSignal-protected route.

The PASS classification is bounded to the protected external integration exercised by the qualification. It does not convert the sandbox into a claim that every possible route to the target is technically dependent on FlowSignal.

## Explicit non-claims

This result does **not** establish:

- universal production non-bypassability;
- control of a bank settlement rail;
- universal closure of external administrative or privileged routes;
- production IAM or process isolation;
- HSM/KMS guarantees;
- cross-provider distributed atomicity;
- production availability or operational fitness; or
- fitness for every deployment architecture.

Those propositions require separate evidence.

## Evidence discipline

The evidence sequence is:

`frozen proposition -> implementation -> PR state -> first executable GitHub Actions run -> observed external-state assertions -> classification`

The first executable CBP-002 result was a PASS. No failure is being suppressed or replaced for this qualification run.

Test count is not used as the proof claim. The classification is based on the specific mechanism and external-state observations exercised by `test_cbp002_external_consequence_boundary.py`.

## Final classification

**CBP-002 — EXTERNAL CONSEQUENCE BOUNDARY: PASS (BOUNDED TO NAMED EXTERNAL TARGET AND INTEGRATION)**
