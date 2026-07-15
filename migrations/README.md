# Migrations

This directory contains ordered, reproducible PostgreSQL schema and data
migrations for the authoritative transactional ledger.

Each migration must preserve scope isolation, protected-state ownership, and
safe upgrade and recovery paths. Migration files are added with the feature that
requires them.

## Foundation contract

FND-03 establishes the migration validation mechanism but deliberately does not
introduce the Stage 1 domain schema. Until the first authorized schema slice is
implemented, this directory contains no SQL migration and validation requires
the explicit `--allow-empty` flag.

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
  --migrations-dir migrations \
  --allow-empty
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
`N-1` upgrade path before any product schema exists and is never applied outside
disposable migration-validation databases.
