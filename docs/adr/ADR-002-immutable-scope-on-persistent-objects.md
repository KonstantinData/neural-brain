# ADR-002: Immutable Scope on Persistent Objects

- Status: Accepted
- Date: 2026-07-15
- Notion source: https://app.notion.com/p/39d1c1ac5ec0817cb442c04a40a6cffd
- Notion page ID: `39d1c1ac-5ec0-817c-b442-c04a40a6cffd`

## Amendment by ADR-015

This decision applies to operational memory objects. Its literal application to
the persistent Tenant root is unresolved because Area is below Tenant in the
fixed hierarchy. ADR-015 authorizes no sentinel Area, nullable exception, or
implicit root scope. Tenant-root persistence and dependent implementation
remain blocked until a separate accepted decision resolves the conflict.

## Context

Retrofitting scope fields is high-risk and can invalidate audit evidence.

## Decision

Every persistent domain object carries immutable `tenant_id` and `area_id`.
Project-bound objects also carry immutable `project_id`. Scope comes only from
authenticated runtime context.

## Consequences

Stage 1 may operate with a single configured scope, but its schemas and guards
must be ready for multiple scopes.

## Invariants and Constraints

- Persistent `tenant_id` and `area_id` values are mandatory and immutable.
- Persistent project-bound objects also have an immutable `project_id`.
- Requests, prompts, model responses, and tool outputs do not determine scope.
- A Stage 1 single-scope configuration does not permit single-scope schemas or
  transition guards.

## Relationship to the Architecture Directive

This decision fixes the persistent scope contract behind the architecture
directive's Brain-to-Session hierarchy and its authenticated-runtime-context
boundary.
