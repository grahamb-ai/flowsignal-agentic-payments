# R6 Causal Grant / Decision Correspondence — First Failure

## Status

Preserved RED. No remediation is recorded in this document.

## Preceding checkpoint

The branch had a full regression of:

```
115 passed in 0.55s
```

The successful-final-bind causal grant had also been shown to be one-shot.

## Failure-first challenge

A genuine successful final-bind was obtained for a prepared chain. The resulting
one-shot causal grant was then used while keeping the genuine protected operation,
authority exercise and execution attempt, but substituting caller-selected
determination and constraint identifiers.

Those substituted identifiers were carried consistently through the signed permit,
final-bind provenance and RAI execution binding.

## Observed first failure

```
1 failed, 115 passed in 0.68s
```

Failing case:

```
test_r6_genuine_causal_grant_cannot_authorise_substituted_determination_and_constraint
```

Observed protected-boundary result:

```
CONSEQUENCE_FORMED
```

## Root cause

The causal grant emitted by successful final-bind is currently bound to the
protected operation ID, authority exercise ID, execution attempt ID and successful
final-bind reason. It is not bound to the exact determination ID and constraint ID
that were validated by that final-bind.

Provenance establishment consumes the genuine grant by checking only the
operation/exercise/attempt tuple. It therefore accepts substituted determination
and constraint identifiers when the other grant-bound fields match.

Because the signed permit, provenance record and RAI execution registry can then
all carry the same substituted identifiers, the protected boundary sees internally
consistent execution material even though those decision artifacts were not the
ones validated by the successful final-bind.

## Boundary implication

A genuine causal grant proves that successful final-bind occurred for the bound
operation/exercise/attempt, but in this first-failure state it does not prove that
the determination and constraint presented downstream are the exact decision
artifacts that passed that final-bind.

## Remediation requirement

Preserve this failing case unchanged while remediation is developed.

The narrow property required is that successful final-bind must bind its one-shot
causal grant to the exact determination and constraint it validated, and provenance
establishment must require those same identifiers when consuming the grant.

Do not solve this by adding a caller-supplied boolean or another independently
selectable label.


## Remediation

The preserved failure was remediated narrowly by extending the successful
final-bind causal grant correspondence to include the exact:

- determination ID;
- constraint ID;
- protected operation ID;
- authority exercise ID; and
- execution attempt ID.

Provenance establishment now has to present all five exact identifiers when it
consumes the one-shot causal grant.

Relevant remediation commits:

- `1d8ca3efbc672f120c379b39c412f612f282b123` — bind causal grant to exact decision artifacts.
- `09671e40c74bb48e89f51b0b44d532adfc02f4c6` — require exact decision correspondence during provenance establishment.
- `8af1bb072fec2b276bb0a2c9b0446732a653d9df` — retain the original challenge while accepting rejection at provenance establishment as the strengthened defensive outcome.

## Post-remediation verification

The same substituted determination/constraint case no longer reached the protected
consequence boundary. Provenance establishment rejected it with:

```
ValueError: successful causal final-bind grant required
```

The full regression then completed:

```
116 passed in 0.56s
```

This demonstrates closure of the specific decision-artifact substitution route
captured by this evidence. It does not assert global closure of R6 or production
persistence, IAM, concurrency, crash-recovery or distributed-system properties.
