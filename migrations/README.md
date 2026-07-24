# Migrations

This directory contains ordered, reproducible PostgreSQL schema and data
migrations for the authoritative transactional memory ledger.

Each migration must preserve scope isolation, source provenance, protected
memory-state ownership, retention and deletion semantics, and safe upgrade and
recovery paths. Migration files are added with the memory capability that
requires them.

## Foundation contract

FND-03 established the migration validation mechanism. The current ordered plan
contains the MS-1 hierarchy, scoped memory kernel, reserved Dreaming schema,
protected NB-1 cognitive checkpoint evidence, the fixed local administrative
provisioning gate, and OIDC Consumer read gates in migrations `0001` through
`0006`. Migration `0003` deliberately grants no
productive Dreaming execute capability and its function fails closed until the
persistent lease, immutable snapshot, and independent validation prerequisites
exist. Migration `0004` adds scope-bound immutable cognitive transition evidence
and dedicated Memory Transition Gate functions; it does not grant table-write
access or create a second protected-state writer. Empty migration plans are no
longer accepted by repository CI or release evidence.

Migration `0005` adds only the fixed local demo provisioning function. It runs
with the authenticated administrative invoker's authority, accepts no scope or
principal input, verifies the complete fixed hierarchy, records the database
administrator as actor and the runtime Principal as subject, and has no runtime
role grant. It is not a general production provisioning API.

Migration `0006` adds protected OIDC principal resolution and direct scoped
Observation and current Working Memory read gates. It grants no table access and
does not accept identity or scope through an untrusted memory request.

Migration files use the exact format `NNNN_lowercase_description.sql`, begin at
`0001`, and remain contiguous. Files are immutable after merge. Corrections use
a new migration rather than changing an applied file. A migration must not
contain `BEGIN`, `COMMIT`, `ROLLBACK`, or savepoint control because the validator
owns one explicit transaction per file.

## Validation

The validator requires an administrative DSN for a disposable PostgreSQL 18
instance. It never logs the DSN or migration payloads.

```text
python tools/validate_migrations.py \
  --admin-dsn <postgresql-18-admin-dsn> \
  --migrations-dir migrations
```

For each run it creates two randomly named databases inside the guarded
`neural_brain_migration_validation_*` namespace:

1. apply every migration to an empty database;
2. apply migrations through `N-1`, then apply `N` as the forward-upgrade path;
3. compute deterministic catalog digests for both final schemas;
4. require the digests to match exactly;
5. forcibly remove only the two databases created by that run.

Unknown filenames, sequence gaps, transaction control, a PostgreSQL major other
than 18, schema divergence, or unprovable cleanup ownership fail closed. Cleanup
failure also fails the validation. The digest covers user schemas, relations,
columns, constraints, indexes, views, routines, triggers, row-level policies,
sequences, enums, and non-default extensions.

CI additionally runs a two-migration test-only fixture. The fixture proves the
`N-1` upgrade path and is never applied outside disposable
migration-validation databases.
