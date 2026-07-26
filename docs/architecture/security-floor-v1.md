# Security Floor v1

## Status

Implemented minimum runtime boundary for the early Memory Core. This is not a
general policy engine and does not enable any action, model-promotion, or
Dreaming capability.

## Non-overridable rules

- Only `memory_ingest` and `memory_read` are admitted.
- Every admitted operation requires a trusted `RuntimeContext` with immutable
  actor, Tenant, Area, Project, and Session identifiers.
- Unknown, future, action, promotion, deletion, and caller-invented operations
  are denied. There is no configuration, policy argument, or override hook.
- The floor is defense in depth: OIDC validation, Tenant-bound PostgreSQL
  identity, RLS/FORCE, authority bindings, and Memory Transition Gates remain
  mandatory and independent.

## Traceability

`S1-02.1` is implemented by `neural_brain.security.floor` and enforced before
every currently exposed Memory Core read or ingest call. Unit evidence is in
`tests/unit/test_security_floor.py`; Memory-service integration evidence is in
`tests/unit/test_memory_service.py`.

This artifact implements only the fixed Security Floor required by ADR-018 and
Architecture Directive v4.0. Versioned policy documents, decision records,
approvals, obligations, expiry, and activation workflow remain later backlog
work and must not weaken this floor.
