# SCB-001 Initial Failure

## Frozen proposition

When invalidity is already knowable from the governing authority topology,
the authority domain must not issue the candidate identity that enables a path
toward protected consequence. The consequential edge must be absent rather
than present and later blocked by runtime adjudication.

The paired liveness requirement is that a valid movement must retain an
authority-issued path.

## Frozen test

`harness/tests/test_scb001_known_invalid_path_nonexistence.py`

The prohibited action is `DELETE_ACCOUNT`, which is not an action in the
authoritative payment mandate. The test presents that fully assembled request
to initial candidate-generation issuance and requires issuance to stop before
an authority-bearing candidate identity is created.

## Initial result

```text
F.                                                                       [100%]
FAILED test_known_invalid_action_has_no_authority_issued_consequential_path
1 failed, 1 passed
```

Observed failure:

```text
Failed: DID NOT RAISE ValueError
```

## Finding

The valid-action liveness control passed. The known-invalid action nevertheless
received an authority-issued candidate generation. Its invalidity would be
discovered later by runtime evaluation, so the current implementation still
contains a present-but-blockable consequential edge for this case.

Classification:

**STRUCTURAL CLOSURE NOT ESTABLISHED — KNOWN-INVALID INITIAL GENERATION WAS
ISSUED**

No runtime remediation was made before recording this result.

## Regression control

The preceding candidate-generation protections remain green:

```text
test_postcandidate_invalid_generation_cannot_regain_execution.py
test_pcg002_unauthorised_successor_generation.py

4 passed
```
