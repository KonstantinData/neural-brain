# Migrations

This directory contains ordered, reproducible PostgreSQL schema and data
migrations for the authoritative transactional ledger.

Each migration must preserve scope isolation, protected-state ownership, and
safe upgrade and recovery paths. Migration files are added with the feature that
requires them.
