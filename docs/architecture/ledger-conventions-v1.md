# PostgreSQL Ledger Conventions v1

- Status: Normative Foundation convention
- Task: S1-03.1
- Governing decisions: ADR-003, ADR-018, ADR-019
- Applies to: NB-0 through NB-8; all future protected ledger migrations

## Purpose and authority boundary

This convention removes representation choices that could otherwise change protected-key, scope, or ledger semantics. PostgreSQL is the authoritative transactional ledger for protected state and its atomic audit evidence. This document standardizes representation; it neither authorizes a protected state writer nor introduces Goal, Action, approval, budget, resource, fence, or model-promotion tables. Until their owning Gate contracts and migrations are accepted, the current implementation remains the protected Memory Core and its effect-free NB-1 checkpoint path.

## PostgreSQL and migration baseline

The supported migration and CI baseline is PostgreSQL **18**, currently pinned to `postgres:18.4-bookworm` by the migration workflow. A migration must use the repository's immutable, contiguous `NNNN_lowercase_description.sql` plan and the validator-owned transaction. Applied migrations are never edited; a correction is a new migration.

## Identifiers, scope, and names

The existing protected schema uses bounded, non-empty `text` identifiers, not the PostgreSQL `uuid` type. New protected identifiers therefore use `text NOT NULL`, a non-empty check, and a maximum length of 128 unless the identifier is an authenticated external subject, which uses its explicitly justified 512 character bound. A UUID representation is not silently interchangeable with the existing key convention and needs an accepted migration and compatibility decision before introduction.

Identifier columns end in `_id`; request idempotency uses `transition_request_id`; version counters use `*_version` and PostgreSQL `bigint`; timestamps end in `_at`; boolean facts begin with `is_`, `has_`, or `can_`. Database objects use lower-case `snake_case`. Primary and foreign keys preserve typed catalog lineage rather than creating an opaque surrogate key: `tenant_id`, `area_id`, and, where applicable, `project_id` and `session_id` are stored and constrained together. Persistent protected objects always carry immutable `tenant_id` and `area_id`; project-bound objects carry `project_id`. No request, payload, GUC, model output, or consumer metadata defines or expands that scope. ADR-019's database-bound Tenant identity remains anchored to `session_user`; this naming convention does not treat writable context as an identity anchor.

## UTC timestamps and temporal semantics

All persisted instants use `timestamptz`; `timestamp without time zone` is prohibited for protected ledger instants. Database-generated commit and record times use `transaction_timestamp()` so all records in one protected transaction share one authoritative instant. Domain event times supplied to a Gate use `timestamptz` and retain their semantic names (for example `occurred_at` or `valid_until`); they do not replace the authoritative commit time. SQL clients must send offset-bearing UTC instants and application code must not derive ledger order from local wall-clock values.

## Numeric budgets and resource quantities

The current migrations contain no protected budget or resource-claim table; this convention does not imply that one exists. When an accepted owning Goal or Action Gate contract introduces an exact ledger amount, it must use `numeric` (never `real`, `double precision`, or a JSON number) with the fixed database form `numeric(20,6) NOT NULL CHECK (amount >= 0)`, a non-empty explicit unit, and immutable scope, reservation, and audit lineage. Arithmetic, comparison, and exhaustion decisions occur inside the owning Gate transaction. A unit conversion, currency conversion, fractional precision beyond six places, or negative adjustment requires a separate accepted contract and cannot be hidden in a payload.

## Structured payloads and evidence

Structured protected payloads and audit evidence use `jsonb NOT NULL` with a database shape check (`jsonb_typeof(...) = 'object'` or the explicitly required array shape). JSONB stores content and extensible evidence, never an alternative source for trusted identity, scope, authority, lifecycle, version, idempotency, or Gate ownership. Values required for keys, scope joins, authorization, idempotency, versions, retention, or audit correlation are typed columns with constraints and, where applicable, foreign keys.

Opaque consumer metadata remains optional, non-authoritative, and cannot carry a foreign key into a consumer domain or affect scope or actor selection. Large model artifacts remain versioned external artifacts; only their digest, lineage, activation and rollback evidence belong in the transactional ledger. Payload logging, migrations, audit records, examples, and test fixtures must not contain secrets, credentials, tokens, or live personal data.

## Verification obligations

Every new protected migration must prove this convention through migration and architecture tests: typed scope lineage, gate-only writes, atomic audit, idempotency/reconciliation, UTC handling, JSONB shape constraints, and any new exact-amount constraint. A later product-stage table must not mask an earlier evidence, safety, or control gap.
