# EC-002 — Capability Isolation Challenge

**Status:** FROZEN BEFORE EC-002 V2 REMEDIATION  
**Date:** 18 August 2026

## Proposition

Code acting only as the represented execution component must not possess an independent usable capability to mint a consequence-authorising execution permit.

## Attack surface

The unchanged challenge checks whether the execution-side module:

1. exposes a callable permit issuer;
2. contains permit-signing key material;
3. exposes a permit-signing primitive; or
4. embeds the reference permit secret in executor source.

## Required property

The represented execution component may verify and consume a permit, but it must not itself contain the capability required to mint a new consequence-authorising permit.

## Classification discipline

A PASS can apply only to the exact reference-component boundary exercised by the tests. Even if the module boundary passes, production process/IAM/KMS/HSM capability isolation remains NOT DEMONSTRATED until a real deployment trust boundary is exercised.

The proposition will not be narrowed after observing the initial result.