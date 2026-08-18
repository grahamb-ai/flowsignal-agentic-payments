# EC-002 — Initial Capability-Isolation Failure

**Status:** PRESERVED FAILURE  
**Date:** 18 August 2026  
**GitHub Actions run:** `32102086782` (run #73)  
**Head commit under test:** `e9fb298189566ede3aadce940e09a527cffad510`

## Frozen proposition

Code acting only as the represented execution component must not possess an independent usable capability to mint a consequence-authorising execution permit.

## Observed result

All four frozen execution-component isolation checks failed:

- callable permit issuer exposed;
- permit-signing key material present;
- signing primitive exposed;
- embedded reference permit secret present in executor source.

Full suite result:

```text
4 failed, 38 passed in 0.59s
```

## Classification at this point

**FAIL — capability isolation not demonstrated at the represented execution-component/module boundary.**

## Scope

This is a bounded reference-harness failure. It confirms the known EC-001.4 gap in executable form. It is not a claim about a production IAM/KMS/HSM deployment because no such deployment boundary exists in this harness.

## Remediation constraint

The four frozen tests remain unchanged. Remediation may move permit issuance/signing into a separate reference component, but a later PASS must still be described only as reference component/module isolation unless a genuine production trust boundary is exercised.