# FS-SZ-PAY-001 — Privileged route disposition and trust boundary

**Disposition: PRESERVED RED / BOUNDARY-02 OPEN / STRUCTURAL ZERO NOT QUALIFIED.**

## Observed hostile evidence

- GitHub Actions run `45150627886`, candidate commit `8456ddb84fed0e3452b70afd4018bdb7765aafde`.
- Isolated PostgreSQL administrator identity `postgres` executed a direct `INSERT` into `fs_provider.commits` without a signed instruction.
- Raw result: `INSERT 0 1`; `privileged_bypass_durable_count = 1`.
- This is an actual durable bypass in the qualification database, not a theoretical privilege concern.
- In contrast, real runtime login `fs_commit_service` direct INSERT was denied with zero durable records (run `45149549951`).

## Scope of the claim

The tested signed final-commit function constrains the designated runtime service login. It **does not** constrain a superuser, schema/table owner or any actor holding equivalent privileges. A database superuser can directly write or modify rows, alter functions and grants, and interfere with evidence.

Therefore the phrase *non-bypassable* must be scoped to a declared threat model and runtime principal set. Do not claim universal structural zero while privileged direct writes remain possible.

## Qualification work required

1. Document every privileged principal capable of altering authority, issuer keys, signed functions, commitment records or their evidence; include migrations, backups, replication, break-glass and automation identities.
2. Keep privileged database credentials inaccessible to runtime agents and payment executors. Establish institutional ownership, independent approval, time-limited access and monitored break-glass procedures.
3. Test privilege inheritance, `SET ROLE`, ownership changes, `SECURITY DEFINER` ownership, migration paths and alternative application connections. Verify the inventory against the intended deployment, not just this isolated container.
4. Decide whether a separate independent execution/claim authority and tamper-evident external receipt is required so that database administrator intervention cannot silently manufacture a legitimate consequence.
5. Run hostile direct-write and evidence-manipulation tests under each admitted privileged principal. Preserve every RED and do not relabel an administrative bypass as GREEN merely because it was expected.
6. Freeze the final SQL, source archive digest, deployment role map and threat model before external qualification. Production and `main` are out of scope.

## Decision gate

**Do not close BOUNDARY-02 or advertise Structural Zero** until the approved institutional threat model explicitly defines privileged actors, their technical containment or independent detection, and all consequence-forming routes. A procedural control alone does not prove cryptographic impossibility.

Historical RED artifact: https://github.com/grahamb-ai/flowsignal-agentic-payments/actions/runs/45150627886
