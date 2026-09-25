# FS-RAI-IC-001-CL-004 — Coherent Multi-Source Authority Compatibility Cut

**Status:** CLOSED — TESTED R1 REFERENCE PATH

## Baseline failure

FS-RAI-IC-001-BL-001 preserved IC-FAIL-004: the baseline implementation exposed a local monotonic authority-state version but did not establish that all authority-material inputs were read from one authoritative compatible cut.

## Failure-first reproduction

After the R2 remediation introduced proposition evidence, source versions and a source-version-vector identity, a direct second-order test independently advanced otherwise competent actor and operational authority sources:

- actor source: `ACTOR-GEN-200`
- operational source: `OPERATION-GEN-900`
- mandate source: current authoritative snapshot

No compatibility relation had been established between those generations.

**Observed result:** authority resolution succeeded.

**Regression result:** 88 passed / 1 failed.

This reproduced the substantive baseline defect at the newer architecture level: a version vector could describe which generations were used, but did not prove that those generations were permitted to coexist in one authority-resolution cut.

## Remediation

The reference institutional-authority model now represents an explicit `AuthorityCompatibilityCut`.

Authority resolution now requires:

1. required proposition evidence is complete;
2. source generations are individually identified;
3. an explicit compatibility relation exists for the relevant source generations;
4. only then may the authority context be constructed.

The compatibility-cut identity participates in resolution-context derivation.

An intermediate regression exposed an ordering defect: compatibility lookup occurred before evidence completeness, producing `KeyError` for unknown actor/beneficiary evidence. This was not classified as two new authority failures. The resolver was corrected so missing required propositions remain fail-closed as unresolved before compatibility is evaluated.

Post-remediation regression: **89/89 GREEN**.

## Positive mirror

A second test established newer source generations:

- actor source: `ACTOR-GEN-201`
- operational source: `OPERATION-GEN-901`

Those versions remained insufficient merely by existing. A bounded authoritative compatibility-cut registration was then explicitly established. Authority resolution succeeded using the newer generations.

Final regression: **90/90 GREEN**.

This defeats the vacuous alternative in which the remediation simply permits the frozen baseline generation forever and rejects every future generation.

## Demonstrated property

For the tested R1 reference path:

> Individually competent/current-looking authority propositions from independently versioned sources cannot form one sufficient AuthorityResolutionContext merely because their versions can be recorded or hashed together. Their cross-source compatibility must itself be independently established.

Positive mirror:

> Newer source generations may participate when an authoritative compatibility relation has been explicitly established.

## Architectural distinction

**Version-vector identity != compatibility proof.**

A version vector answers:

> Which source generations were used?

The compatibility cut answers:

> Are these source generations authorised to coexist for this authority resolution?

Both are needed in the tested multi-source model.

## Boundaries and nonclaims

The compatibility registry and registration capability are process-local reference-harness mechanisms. They do not constitute a production distributed snapshot protocol, consensus mechanism, external attestation system, durable provenance store, or proof of legal/institutional validity.

This closure is bounded to the tested R1 reference path and the represented reference sources. Route-wide compatibility, durable source-transition provenance, production source synchronisation, environment identity and dependency locking remain separate campaign concerns.

## Closure

IC-FAIL-004 is **CLOSED for the tested R1 reference path**.

It is not promoted to route-wide or production implementation conformance by this record.
