# ADR-003: PostgreSQL as the Authoritative Transactional Ledger

- Status: Accepted
- Date: 2026-07-15
- Notion source: https://app.notion.com/p/39d1c1ac5ec0813488b7e9b58c91d563
- Notion page ID: `39d1c1ac-5ec0-8134-88b7-e9b58c91d563`

## Amendment by ADR-015

PostgreSQL is authoritative for transactional memory state and its audit
evidence. Goal, action, budget, approval, lock, dispatch, and external-effect
state belong to external consumers and are not Neural Brain domain state.

## Context

Memory lifecycle, provenance, audit, retention, deletion, and recovery state
require atomicity and crash consistency.

## Decision

PostgreSQL is the authoritative transactional ledger. A protected state mutation
and its audit record commit in the same transaction.

## Consequences

Database roles, migrations, append-only histories, backup, restore, and
reconciliation are release-critical.

## Invariants and Constraints

- Protected state and its audit evidence are changed atomically.
- PostgreSQL is authoritative for transactional domain state.
- Database roles and migrations must preserve the protected-state boundary.
- Backup, restore, and reconciliation evidence is required for release.

## Relationship to the Architecture Directive

This decision provides the transactional authority and crash-consistency basis
for the architecture directive's protected state, ledger, audit, recovery, and
release-stop requirements.
