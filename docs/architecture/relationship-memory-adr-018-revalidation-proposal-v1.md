# Relationship Memory ADR-018 Revalidation Proposal v1

- Status: Proposed prerequisite; not accepted and not runtime authorization
- Tasks: REL-MEM-01 through REL-MEM-08; future enforcement package REL-MEM-16
- Governing target: ADR-016, ADR-017, ADR-018, ADR-019, and Architecture Directive v4.0

## Position 1: non-authorizing context only

Relationship Memory is conditionally accepted only as a downstream,
purpose-bound context layer. It is never a Goal, Authority, Gate, policy,
approval, identity, or truth system. It cannot authorize a transition, infer a
permission, mutate protected state, or cause an external effect. The Memory
Transition Gate remains the sole future writer of protected memory state.

Any later NB-1 Planner use is limited to a minimized, approved,
provenance-bound, untrusted read view. It cannot establish truth, create a
profile decision, write Memory, call a tool, or create an external effect.
That use remains blocked pending separately accepted Goal Transition Gate,
historical Goal Gate revalidation, NB-1 Planner/Verification revalidation,
Privacy, and deployment evidence/contracts.

## Position 2: service-operated default after onboarding

After regular tenant onboarding, the future service is default enabled. There
is no customer self-service configuration or disable control. Settings,
parameters, changes, and any tenant-specific decoupling are service operations
performed by the developer/service owner only after a customer request and
documented contract, purpose, and technical checks. Customer requests are
therefore service-handled, not dashboard actions.

Data-subject access, correction, and deletion requests require an auditable
service-managed intake and response path. They are not a direct-store or
dashboard path. Future processing preserves the minimum permitted signals,
purpose limitation, provenance/auditability, tenant isolation, and the rule
that no activity occurs without authenticated tenant context.

## Position 3: future enforcement package

Position 3 is not a separate runtime initiative. It is a separately
authorizable future technical enforcement package derived from Position 2. Its
future scope is schema and Memory Gate design, immutable scope/purpose audit,
deletion propagation, and negative Scope/Purpose tests that enforce and
evidence Position 2. It remains runtime-disabled until separately accepted and
independently verified. Retrieval, Planner, and Dreaming runtimes remain
separately contracted and are not enabled by this package.

## Explicit exclusions

This proposal authorizes no migration, schema, Memory Gate implementation,
runtime component, real personal-data processing, retrieval endpoint, Dreaming
execution, Planner integration, deployment, release, or compliance claim.
