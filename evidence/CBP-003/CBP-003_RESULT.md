# CBP-003 — Protected External Route/Capability Closure Result

## Classification

**CBP-003 — PROTECTED EXTERNAL ROUTE/CAPABILITY CLOSURE: PASS (BOUNDED TO NAMED TARGET, CAPABILITY AND INTEGRATION)**

## Evidence status

This document records the **first executable result** against the proposition frozen before implementation in `CBP-003_CHALLENGE.md`.

Frozen challenge commit:

`693aa230268142169b8b150757f7191d04fab867`

Frozen base commit:

`cb89c5c4ae1edba4c3c38931ae53e94421d0732d`

The frozen challenge was not changed after the executable result was observed.

## Implementation sequence before first run

External capability target:

`b1452616cb5cdf14b9bdcd9a79cfc1e74e86ae42`

Protected capability adapter:

`1ab35363450c61ccda7bd3f9879af976d5ca4013`

Executable qualification:

`7afcebad3a30ec463297e92adbed563cacf3438d`

Dedicated workflow:

`bc81dfdbe41185111dfcb9143bab951d34d58de6`

Pre-result implementation note:

`ae76f92779190555b99cf4d93515a747e59e8422`

PR head at first executable run:

`6c67317357f5709bb744ddcc16db4194d46cd61e`

## Executed PR state

Pull request: **#18 — CBP-003 — protected route capability closure qualification**

GitHub Actions checked out the PR merge state:

`176f664f008b94683fd9cbe5a13d234e34c74c1a`

Workflow: **CBP-003 Protected Route Capability Closure**

Run ID:

`32339656708`

Job: **Frozen protected route capability seam**

Job ID:

`96336015959`

Python runtime observed in the job:

`3.11.15`

Exact qualification command:

```text
pytest -q tests/test_cbp003_route_capability_closure.py
```

Observed first result:

```text
.                                                                        [100%]
1 passed in 0.24s
```

Workflow conclusion: **success**.

This is an execution in GitHub Actions against the PR state. It is not described as independent verification.

## Named external target and capability

The qualification uses `external_targets/cbp003_capability_service.py`, launched as a **separate OS process** and reached over localhost HTTP.

The target owns its own independently queryable ledger state and its own one-time capability registry.

The protected `/payments` operation does not accept a FlowSignal permit as the payment credential. It requires a target-issued bearer capability.

The target releases such a capability only after it can observe, at the explicit CBP-003 integration seam, both:

- durable consumption of the FlowSignal execution permit signature; and
- an unresolved consequence outcome bound to the same exact action-binding hash.

Those execution-state records are created by the existing FlowSignal protected consequence mechanism after its permit integrity, exact-action binding, expiry, current authority-state, rollback-anchor and one-time permit-consumption checks have succeeded.

The released capability is bound to source account, beneficiary, amount, currency and purpose and is marked used when the target forms the payment consequence.

## Observations exercised by the executable qualification

### 1. Independently observable initial external state — PASS

The target is queried through its own `/state` endpoint before execution. It reports zero transfers, zero issued capabilities and the initial source balance.

### 2. Direct consequence attempt without capability — PASS

An ordinary caller invokes the protected payment endpoint without a target capability.

The target returns `CAPABILITY_REQUIRED` and its independently queried state remains unchanged.

### 3. Valid FlowSignal permit alone cannot directly obtain target capability — PASS

A valid current FlowSignal execution permit is presented directly to the target capability-release endpoint **before** the FlowSignal protected consequence interval has consumed it and created the exact-action unresolved execution state.

The target returns:

`CAPABILITY_RELEASE_NOT_AUTHORISED`

No capability is issued and no external state changes.

This establishes, for the named integration, that possession of a valid FlowSignal permit by itself is not the external consequence-forming capability.

### 4. Current-authority protected-route positive control — PASS

A current exact-action FlowSignal permit enters the protected consequence interval.

Only after the required protected execution state exists does the target issue a one-time capability. The adapter presents that capability to the protected payment endpoint.

The target independently records exactly one intended transfer, one issued capability and one used capability.

### 5. Distinct challenged external state — PASS

The target administrative reset route creates a distinct zero-transfer/zero-capability state for the challenged attempt.

That route is a test-fixture/administrator power and is explicitly outside the bounded route-closure claim.

### 6. Authority changed after historical permit issuance — PASS

A second current exact-action permit is obtained. The authoritative runtime state version is then advanced before capability release or external consequence formation.

The historical permit therefore no longer represents current authority.

### 7. Stale authority refused before capability release — PASS

The historical permit is presented through the same protected capability adapter after the authority-state change.

The protected consequence mechanism returns:

`DENIED_AUTHORITY_STATE_STALE`

The capability-release hook is not reached, no target capability is returned, and the independently queried external state remains unchanged.

### 8. Material action substitution refused before capability release — PASS

The historical attempted consequence is changed to a different beneficiary and amount.

The result is:

`DENIED_ACTION_BINDING_MISMATCH`

No target capability is returned and external state remains unchanged.

### 9. Direct protected-payment bypass without capability — PASS

The target payment endpoint is invoked directly while the historical permit exists but without a released capability.

The target returns `CAPABILITY_REQUIRED` and external state remains unchanged.

### 10. Direct stale capability-release bypass — PASS

The historical FlowSignal permit is presented directly to the target capability-release endpoint after the authority-state change.

Because stale authority never entered the protected consequence interval under current standing, the required durable consumed/unresolved exact-action state does not exist.

The target returns `CAPABILITY_RELEASE_NOT_AUTHORISED`; no capability is issued and external state remains unchanged.

### 11. Current authority reacquisition — PASS

Authority is reacquired for the same intended exact action under the new authority-state version.

The qualification establishes a new authority receipt, a different permit signature and a permit bound to the current authority-state version.

### 12. Historical permit remains unusable after reacquisition — PASS

After current authority is reacquired, the historical permit is presented again through the protected capability adapter.

It remains denied as `DENIED_AUTHORITY_STATE_STALE`, no target capability is returned and external state remains unchanged.

### 13. Fresh current authority forms the external consequence — PASS

The fresh current exact-action permit enters the same protected route.

A target capability is released and exercised; the independently queried target records exactly one intended transfer.

The recorded transaction ID equals the fresh permit signature and the recorded beneficiary and amount match the intended action.

### 14. One-time external capability replay — PASS

The exact target capability that formed the fresh-authority payment is presented to the payment endpoint a second time.

The target returns:

`CAPABILITY_ALREADY_USED`

The target state remains identical to the state after the first successful use. No duplicate external consequence forms.

## Claim/mechanism correspondence earned by this result

Within the **named CBP-003 target, capability mechanism and integration**, the executable evidence establishes that the ordinary caller does not possess the tested external consequence-forming capability merely by holding a FlowSignal execution permit.

For this bounded integration:

- the protected external payment route requires a target-issued capability;
- direct payment without that capability fails;
- direct capability release from a valid but not protected-execution-consumed permit fails;
- stale authority is refused before capability release;
- material action substitution is refused before capability release;
- historical authority remains unusable after current authority reacquisition;
- fresh current exact-action authority can cause capability release and intended consequence formation; and
- replay of the one-time target capability cannot create a duplicate consequence.

This materially extends CBP-002's protected-adapter observation by making the external payment endpoint itself dependent on a distinct one-time target capability at the named integration seam.

## Route-closure boundary

CBP-003 does **not** establish universal route closure.

The target deliberately retains an administrative reset route used by the qualification fixture. A sufficiently privileged administrator, operating-system owner, code maintainer or infrastructure owner could alter the target, modify trusted stores, replace code or create other capabilities outside the ordinary caller path.

The target's read access to the explicitly named FlowSignal permit-consumption and consequence-outcome stores is itself part of the bounded reference integration and trust seam exercised here.

Accordingly, the PASS applies to the named ordinary protected payment/capability route. It does not imply that every possible privileged route in a production deployment is technically dependent on FlowSignal.

## Explicit non-claims

This result does **not** establish:

- universal production non-bypassability;
- control of a real bank settlement rail;
- absence of root, administrator or cloud-provider override power;
- production IAM or process isolation;
- HSM/KMS guarantees;
- resistance to compromise of the capability target/issuer itself;
- cross-provider distributed atomicity;
- production availability or operational fitness; or
- fitness for every deployment architecture.

Those propositions require separate evidence.

## Evidence discipline

The evidence sequence is:

`frozen proposition -> capability target/adapter implementation -> PR state -> first executable GitHub Actions run -> independent external-state and capability assertions -> classification`

The first executable CBP-003 result was a PASS. No failure is being suppressed or replaced for this qualification run.

Test count is not used as the proof claim. The classification is based on the specific route/capability mechanism and independently observable external-state behaviour exercised by `test_cbp003_route_capability_closure.py`.

## Final classification

**CBP-003 — PROTECTED EXTERNAL ROUTE/CAPABILITY CLOSURE: PASS (BOUNDED TO NAMED TARGET, CAPABILITY AND INTEGRATION)**
