# ADR-016: Hierarchy Catalog and Operational Memory Scope

- Status: Accepted
- Date: 2026-07-15
- Decision owner: Konstantin Milonas
- Notion source: https://app.notion.com/p/39e1c1ac5ec0810e862de4ffe00a0acb
- Notion page ID: `39e1c1ac-5ec0-810e-862d-e4ffe00a0acb`
- Authority: current
- Theme: scope_and_isolation
- Applies to stages: NB-0, NB-1, NB-2, NB-3, NB-4, NB-5, NB-6, NB-7, NB-8
- Supersedes: none
- Superseded by: none
- Amends: ADR-002, ADR-015
- Amended by: ADR-018

## Amendment by ADR-018

ADR-018 adds complete-system Goal state as a session-bound protected aggregate
while retaining this ADR's catalog hierarchy and authenticated isolation scope
through Session. Goal is not a catalog entry or isolation dimension. The
original decision below remains the accepted historical scope record for the
Memory Core.

## Context

ADR-002 required every persistent domain object to carry `tenant_id` and
`area_id`. Applied literally to the hierarchy catalog, that rule is circular:
an Area is a child of Tenant, so a Tenant cannot truthfully carry the identifier
of an Area below it. Sentinel Areas, nullable exceptions, and implicit root
scope would weaken isolation and make audit evidence ambiguous.

The hierarchy catalog and operational memory have different responsibilities.
Catalog objects establish lineage. Operational memory objects are read, written,
and retrieved inside an authenticated isolation scope.

## Decision

The persistent hierarchy is a typed catalog:

```text
Brain
└── Tenant
    └── Area
        └── Project
            └── Session
```

Each Neural Brain deployment persists exactly one Brain catalog row. The Brain
is the singleton root of every Tenant lineage; it is not operational memory and
does not carry Tenant or Area identifiers.

Each catalog object carries its own immutable identifier and its required
immutable parent lineage, never identifiers of descendants. Brain ancestry
below Tenant is resolved transitively through the authoritative Tenant row:

- The singleton Brain carries `brain_id`.
- Tenant carries `brain_id` and `tenant_id`; it does not carry `area_id`.
- Area carries `tenant_id` and `area_id`; its Brain is resolved through Tenant.
- Project carries `tenant_id`, `area_id`, and `project_id`.
- Session carries `tenant_id`, `area_id`, `project_id`, and `session_id`.

Every operational memory object carries immutable `tenant_id` and `area_id`.
Project-bound memory also carries immutable `project_id`; session-bound memory
also carries immutable `session_id` and its ancestor `project_id`. Scope and
lineage come only from authenticated runtime context and authoritative catalog
resolution.

External goal, task, or session identifiers may be stored only as optional,
opaque, non-authoritative correlation metadata. They are not catalog scope and
cannot confer authority or drive a memory transition.

## Consequences

- Tenant roots can be persisted without circular scope or synthetic Areas.
- Catalog lineage and operational isolation are explicit, separately testable
  contracts.
- Operational memory remains strictly tenant- and Area-isolated.
- Moving a catalog object to another parent is not an in-place scope update; it
  requires an explicit governed replacement or migration contract.
- Concrete memory remains in its origin Area. Cross-Area reuse requires the
  separately governed Stage 4 abstraction and handover contract.

## Invariants and Constraints

- Catalog identifiers and required parent-lineage identifiers are immutable
  after persistence.
- The catalog contains exactly one Brain root.
- A catalog object cannot contain a descendant identifier or omit required
  parent lineage.
- Operational memory cannot exist without authenticated `tenant_id` and
  `area_id`.
- A project- or session-bound object cannot omit any required parent identifier.
- No sentinel Area, nullable required identifier, implicit root scope, or
  payload-derived scope is permitted.
- Catalog existence does not authorize access to operational memory.
- Database constraints, row-level security, application guards, audit records,
  indexes, caches, and derived records enforce equivalent scope semantics.

## Relationship to Earlier Decisions

This decision resolves the open Tenant-root question recorded by ADR-002 and
ADR-015. It narrows ADR-002's universal field rule to operational memory objects
and replaces it with typed lineage rules for hierarchy catalog objects. ADR-015
continues to govern the memory-system boundary.

## Relationship to the Architecture Directive

Architecture Directive v3.0 incorporates this typed catalog rule and removes
the Tenant-root release blocker from the current normative baseline.
