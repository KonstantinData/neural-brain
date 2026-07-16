# ADR-002: Immutable Scope on Persistent Objects

- Status: Accepted
- Date: 2026-07-15
- Notion source: https://app.notion.com/p/39d1c1ac5ec0817cb442c04a40a6cffd
- Notion page ID: `39d1c1ac-5ec0-817c-b442-c04a40a6cffd`

## Amendment by ADR-015 and ADR-016

This decision applies to operational memory objects. ADR-016 resolves its
literal conflict at the persistent Tenant root by defining hierarchy entries as
typed catalog objects with explicit required parent lineage and no descendant
identifiers. Tenant therefore carries `brain_id` and `tenant_id` but no
`area_id`; operational memory still requires `tenant_id` and `area_id`.

## Context

Retrofitting scope fields is high-risk and can invalidate audit evidence.

## Decision

Every operational memory object carries immutable `tenant_id` and `area_id`.
Project-bound objects also carry immutable `project_id`. Hierarchy catalog
objects follow ADR-016. Scope comes only from authenticated runtime context.

## Consequences

Memory Core MS-1 may operate with a single configured scope, but its schemas and guards
must be ready for multiple scopes.

## Invariants and Constraints

- Operational-memory `tenant_id` and `area_id` values are mandatory and
  immutable.
- Hierarchy catalog objects carry their own immutable identifier and required
  parent lineage, but no descendant identifier. Brain ancestry below Tenant is
  resolved transitively through the authoritative Tenant entry.
- Persistent project-bound objects also have an immutable `project_id`.
- Requests, prompts, model responses, and tool outputs do not determine scope.
- An MS-1 single-scope configuration does not permit single-scope schemas or
  transition guards.

## Relationship to the Architecture Directive

This decision fixes the persistent scope contract behind the architecture
directive's Brain-to-Session hierarchy and its authenticated-runtime-context
boundary.
