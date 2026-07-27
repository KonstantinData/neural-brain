# Protected Control Plane Kill-Switch Scope Resolution Decision v1

- Status: Unaccepted decision preparation; not runtime authorization
- Parent task: `S1-02.5`
- Governing context: ADR-018, ADR-019, Architecture Directive v4.0
- Decision owner: Neural Brain architecture decision owner
- Required reviewers: Protected Control Plane architecture owner; independent security/safety reviewer; qualified recovery owner

## Purpose

This document isolates decisions that must be accepted before a future
Protected Control Plane kill-switch implementation can define a concrete scope
model. It does not choose an option, establish authority, bind a deployment,
or permit a state writer, API, credential operation, recovery, or external
effect. Every unresolved option remains fail-closed.

## Fixed non-negotiable boundary

All options must bind the immutable authenticated lineage
`Brain -> Tenant -> Area -> Project -> Session`. `tenant_id` and `area_id` are
immutable on persistent operational objects; project-bound objects also carry
`project_id`. A goal remains a session-bound aggregate, not an isolation
dimension. Untrusted content, cached state, and request payloads never define
or repair scope.

## Decision matrix

| Decision | Options needing explicit acceptance | Evidence needed | Consequence while unresolved |
| --- | --- | --- | --- |
| Control-scope granularity | (A) exact Session; (B) a named authenticated ancestor scope with an explicit descendant-enforcement rule; (C) another ADR-018-conformant hierarchy rule | Threat model, cross-scope isolation proof, gate/interface design, operational recovery analysis | Deny transitions and do not implement persistence or routing. |
| State ownership and persistence | (A) dedicated PostgreSQL protected state/ledger; (B) another independently authorized protected ledger; (C) explicitly rejected | Data model, role/RLS/FORCE model, atomic audit/CAS design, backup/restore evidence | No state table, migration, writer, cache, or restoration behavior. |
| Credential-revocation binding | (A) exact scope plus credential revision; (B) ancestor revocation with bounded descendant mapping; (C) separate credential domain with verified linkage | Credential authority model, expiry/fence behavior, revocation propagation and recovery tests | Credentials are not issued, revoked, or considered valid for future control. |
| Recovery authority and quorum | (A) named separated roles with a specified quorum; (B) independently verified workflow with a different quorum; (C) explicitly no re-enable scope | Separation-of-duties matrix, incident ownership, evidence retention, anti-rollback tests | Recovery never reaches enabled. |
| Scope-wide effect containment | (A) Session-local only; (B) bounded ancestor containment with descendant fence proof; (C) explicitly deferred | Executor/sandbox routing, in-flight effect inventory, partition and reconciliation tests | No runtime containment or dispatch behavior is implemented. |
| Audit and lineage representation | (A) explicit immutable fields plus lineage hash; (B) immutable normalized parent references plus verified reconstruction; (C) another equivalent tamper-evident representation | Audit schema, query/reconstruction proof, retention and independent review | No audit format is accepted; missing/mismatched lineage denies. |

## Required decision record

An accepted ADR-018-conformant successor must select or replace every matrix
row, name the accountable owners, define interfaces and persistence, and
preregister positive, negative, concurrency, crash, partition, revocation,
rollback, and recovery evidence. It must explain why selected scope does not
weaken Tenant/Area isolation or permit a Brain, cache, or untrusted request to
broaden authority.

## Review and failure boundary

The independent security/safety reviewer must reject a decision that lacks
complete lineage, monotonic revision/CAS semantics, atomic audit, fail-closed
recovery, or a defensible cross-scope containment proof. The qualified recovery
owner must reject a decision with no operator handover, reconciliation, or
evidence-retention path. Until those reviews and the ADR decision are accepted,
the contract remains a non-authorizing preparation artifact.
