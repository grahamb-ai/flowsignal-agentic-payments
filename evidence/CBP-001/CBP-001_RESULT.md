# CBP-001 — Consequence Boundary Proof Result

**Status:** PASS  
**Scope:** Represented protected-consequence boundary in the FlowSignal reference harness  
**Merged to main:** 2026-08-19  
**Merge commit:** `1ef1852512defaeed0c2efbd305efaa9628a98ff`

## Frozen proposition

The challenge proposition was committed before the executable test was added.

Frozen seam:

`real represented protected consequence -> current standing -> changed condition -> attempted bind -> NO_BIND -> bypass failure -> receipt -> replay/current-state separation`

Frozen challenge commit:

`d03ecaed13b0ed419283d086bf32e7594549d3f4`

Executable test commit:

`fdb01766784d481e324a8ac39e442d37e8986e95`

PR head tested:

`db56640c0554381498a0106cbe0d40d9c351cec7`

Pull request:

`#14 — CBP-001 — frozen consequence-boundary proof`

## Executed result

GitHub Actions workflow:

`CBP-001 Consequence Boundary Proof`

Run ID:

`32275844799`

Job:

`Frozen consequence-boundary seam`

Command executed by GitHub Actions:

```text
pytest -q tests/test_cbp001_consequence_boundary_proof.py
```

Observed result:

```text
.                                                                        [100%]
1 passed in 0.09s
```

Workflow conclusion: **success**.

The accompanying `EC-001 and Regression Tests` workflow also completed with conclusion **success** against the same PR state.

## What CBP-001 exercised

1. A fresh current authority determination produced an ALLOW and a bound execution permit.
2. The represented protected consequence formed under that fresh/current permit as a positive control.
3. A second valid permit was obtained under the then-current authority state.
4. Authority state was advanced before that permit could be used for consequence formation.
5. Direct presentation of the stale permit to the protected-consequence boundary returned `DENIED_AUTHORITY_STATE_STALE`.
6. A signed consequence outcome receipt recorded that the consequence did not form.
7. Re-presenting the stale permit through the direct protected-consequence route remained denied.
8. Substitution of the beneficiary was denied with `DENIED_ACTION_BINDING_MISMATCH`.
9. Substitution of the amount was denied with `DENIED_ACTION_BINDING_MISMATCH`.
10. Current authority was reacquired, producing a new authority receipt and new execution permit for the same intended consequence.
11. The historical stale permit remained denied after reacquisition.
12. The fresh/current permit formed the represented protected consequence.

## Evidence interpretation

CBP-001 demonstrates, within the reference harness, that a prior ALLOW/permit is insufficient to form the represented consequence after the authority state has changed. The protected-consequence boundary requires current authority and exact action binding at the point of formation. Stale replay and tested beneficiary/amount substitutions do not form the represented consequence.

The PASS is evidence for this bounded proposition. It is not evidence for every possible execution environment or bypass route.

## What this result does not claim

CBP-001 does **not** claim:

- control of an external bank or payment settlement rail;
- production-grade distributed transactionality;
- production IAM/process isolation;
- HSM/KMS-backed production key isolation;
- proof that every possible external or infrastructure bypass route has been eliminated;
- that the reference harness itself is a production deployment.

Those require separate integration and production-environment evidence.

## Evidence discipline

The challenge was frozen before the executable test was committed. The protected-consequence implementation was not modified between freezing the proposition and the first executable CBP-001 run in order to manufacture the result.

Historical failures elsewhere in the repository remain part of the evidence record rather than being removed when remediated.

---

**FlowSignal™**  
**Execute with Authority. Defend with Evidence.**
