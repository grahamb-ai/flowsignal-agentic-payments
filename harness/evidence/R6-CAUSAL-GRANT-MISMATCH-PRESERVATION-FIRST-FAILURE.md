# R6 Causal Grant Mismatch Preservation — First Failure

## Status

Preserved RED. No authority-formation failure was observed.

## Preceding checkpoint

The branch had a full regression of:

```
116 passed in 0.56s
```

## Challenge

A genuine successful final-bind grant was presented first with deliberately
incorrect decision correspondence. That presentation was correctly rejected.
The same genuine grant was then presented with its exact valid correspondence.

The intended availability property is that a mismatched presentation must not
destroy a still-valid one-shot grant.

## Observed first failure

```
1 failed, 116 passed in 1.84s
```

Failing case:

```
test_r6_wrong_causal_grant_correspondence_does_not_destroy_valid_grant
```

The deliberately mismatched presentation was rejected as expected. The subsequent
correct presentation was also rejected with:

```
ValueError: successful causal final-bind grant required
```

## Root cause

The reference grant consumer currently removes the grant from the process-local
grant store before checking whether the supplied correspondence matches the stored
grant tuple.

A mismatched presentation therefore burns the genuine grant even though no valid
provenance was established.

## Security interpretation

This observed failure is fail-closed with respect to consequence formation. It
does not demonstrate formation of an unauthorised protected consequence.

It demonstrates a bounded availability/denial weakness in the reference grant
consumption semantics: an invalid claim can prevent the subsequent legitimate use
of a genuine unconsumed grant.

## Remediation requirement

Grant consumption should be conditional on exact correspondence. A missing grant
or mismatched correspondence should return false without removing the stored grant.
Only a matching claim should remove the grant and succeed.

The existing one-shot property must remain intact after remediation.


## Remediation

Grant consumption was changed so that the stored grant is inspected and compared
under the existing lock before it is removed. A missing or mismatched claim now
returns false without consuming the grant. Only exact correspondence deletes the
grant and succeeds.

Remediation commit:

- `ef911765ebcf1f756a576742db8d644647a7aac8` — consume causal grant only on exact correspondence.

## Post-remediation verification

The preserved mismatch case now rejects the deliberately incorrect presentation
without destroying the genuine grant. The subsequent exact presentation succeeds,
while the existing single-use regression continues to require that a successfully
consumed grant cannot be reused.

Full regression:

```
117 passed in 0.67s
```

This closes the specific reference-harness availability weakness demonstrated by
this evidence. It does not extend the claim to production persistence,
multi-process coordination, crash recovery, distributed atomicity or external
credential storage.
