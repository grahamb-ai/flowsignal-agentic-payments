# FS-SZ-PAY-001 — pgsodium PostgreSQL 16 build RED

**Status: BUILD RED / BOUNDARY-02 OPEN / NOT MERGE READY**

First isolated build: https://github.com/grahamb-ai/flowsignal-agentic-payments/actions/runs/44577932987
Commit: `2e367501201433872ba7f5cb9a73bf3f69e80b6e`

The candidate used PostgreSQL 16 Bookworm, pgsodium 3.1.11 from PGXN, and Debian Bookworm `libsodium-dev` / `libsodium23` 1.0.18-1+deb12u1. Compilation failed in `src/ipcrypt.c` with undefined `crypto_ipcrypt_*` symbols (e.g. `crypto_ipcrypt_KEYBYTES`). This is a reproducible dependency/build compatibility failure, not evidence of a payment-authority bypass.

**Do not** edit out IP cryptography source files, stub missing symbols, weaken cryptographic functions, or treat a successful partial build as a qualified verifier. Next action: identify a reviewed compatible pgsodium/libsodium source and dependency combination, pin archive digests, build and load extension, run exact canonical-byte interoperability, then final SQL-boundary hostile tests.

A follow-up workflow run additionally attempts CREATE EXTENSION and the detached Ed25519 catalog gate if the build succeeds; it does not certify source provenance or the payment boundary.

Historical stolen-credential RED remains authoritative; all existing deployment guards remain fail-closed.
