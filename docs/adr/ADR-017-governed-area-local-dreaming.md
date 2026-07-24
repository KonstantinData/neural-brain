# ADR-017: Governed Area-Local Dreaming

- Status: Accepted
- Date: 2026-07-15
- Decision owner: Konstantin Milonas
- Notion source: https://app.notion.com/p/39e1c1ac5ec081c1b2d4e1f86d8c7061
- Notion page ID: `39e1c1ac-5ec0-81c1-b2d4-e1f86d8c7061`
- Authority: current
- Theme: memory_lifecycle
- Applies to stages: MS-1, MS-2, MS-3, MS-4
- Supersedes: none
- Superseded by: none
- Amends: ADR-010, ADR-012, ADR-014, ADR-015
- Amended by: ADR-018

## Amendment by ADR-018

ADR-018 retains this decision as Memory Core authority. Its historical Stage 1
through Stage 4 terms map to the namespaced MS-1 through MS-4 subsystem stages;
they do not define or advance NB product stages.

## Context

Neural Brain needs an offline process analogous to biological memory
consolidation: replay recent evidence, identify duplication and contradiction,
assess freshness, propose abstractions, and prepare controlled successor memory.
Calling that process Dreaming does not make Neural Brain an agent. It must not
pursue goals, execute actions, invent authority, or silently rewrite memory.

An unconstrained background model or maintenance job could poison active
memory, mix Areas, race with live sessions, self-promote its conclusions, or
make rollback impossible. Dreaming therefore requires its own governed contract.

## Decision

Dreaming is an Area-local, offline, snapshot-based memory-analysis process. A
run uses this guarded sequence:

```text
trusted schedule or operator request
-> authenticated Area scope
-> active-session and activity guard
-> exclusive Area Dreaming lease
-> immutable versioned snapshot
-> bounded replay and analysis
-> inactive candidate proposals and findings
-> immutable decision package
-> independent validation
-> separately authorized Memory Gate transition
```

The run stops or records a protected skip when the Area is active, the lease is
unavailable, the snapshot is stale or incomplete, provenance is missing, or any
security-relevant state is unknown. The lease and activity guard close the race
between the inactivity check and snapshot capture. A run never expands beyond
its authenticated Area.

Stage 1 permits only a Dreaming dry run. It may create an immutable snapshot,
analysis report, findings, and inactive non-retrievable candidates through the
Memory Transition Gate. It cannot create or activate a successor memory version
and cannot change an active-version pointer.

Stage 2 may analyze governed episodes, claims, assessments, freshness, and
retrieval evidence, but its outputs remain inactive. Stage 3 may independently
assess candidates and perform controlled consolidation, re-evaluation,
promotion, quarantine, or rollback through separately authorized Memory Gate
transitions. Stage 4 may propose minimized cross-Area abstractions only through
the explicit dual-scope transfer contract; raw cross-Area Dreaming is forbidden.

Local model output is untrusted analysis input. It cannot establish scope,
classify itself as authoritative, approve a candidate, activate memory, change a
pointer, or suppress contradictory evidence.

## Consequences

- Dreaming is a governed memory function, not an autonomous task runtime.
- Active memory is never rewritten in place; promotion creates a versioned
  successor with provenance and a rollback target.
- Every run, protected skip, finding, candidate, decision package, validation,
  promotion, quarantine, and rollback is traceable without logging secrets or
  reconstructive sensitive payloads unnecessarily.
- Failed or interrupted runs leave active memory unchanged and are reconciled
  before the Dreaming capability reports ready.
- Scheduling, capacity limits, model choice, and run frequency remain trusted
  deployment policy, never memory content or consumer-controlled input.

## Invariants and Constraints

- Dreaming runs against exactly one authenticated Tenant and Area.
- Dreaming does not run while the Area has active sessions or admitted live
  memory activity.
- One Area has at most one valid Dreaming lease and snapshot epoch at a time.
- Snapshots, reports, candidates, and decision packages preserve immutable
  source provenance and policy context.
- A Dreaming worker cannot write protected memory or active pointers directly.
- Stage 1 and Stage 2 Dreaming outputs remain inactive and excluded from normal
  retrieval.
- Sensitive or risky candidates cannot be promoted solely by their producer.
- Unknown, stale, incomplete, cross-scope, unclassified, or unauditable state
  fails closed.
- Every activation is versioned, independently validated, auditable, and
  rollback-capable.
- Dreaming never creates agent goals, plans, actions, tool calls, external
  effects, approvals, or consumer authority.

## Relationship to Earlier Decisions

ADR-010 continues to define the delivery-stage boundary. ADR-015 defines Neural
Brain as a memory system. This decision specializes their candidate,
consolidation, promotion, quarantine, rollback, and Area-isolation requirements
for Dreaming.

## Relationship to the Architecture Directive

Architecture Directive v3.0 incorporates Dreaming as a governed memory process
and makes its stage limits, protected transitions, and release stops normative.
