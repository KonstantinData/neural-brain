# ADR-015: Neural Brain Is a Memory System, Not an Agent Runtime

- Status: Superseded as product boundary by ADR-018; retained for the Memory Core
- Date: 2026-07-15
- Decision owner: Konstantin Milonas
- Notion source: https://app.notion.com/p/39e1c1ac5ec081c28b2af5439d510529
- Notion page ID: `39e1c1ac-5ec0-81c2-8b2a-f5439d510529`

## Supersession by ADR-018

ADR-018 restores Neural Brain as the complete protected cognitive system. This
ADR remains authoritative only for the governed Memory Core subsystem and its
memory-specific trust, lifecycle, isolation, privacy, and audit boundary. Its
exclusion of goals, planning, action, feedback, and autonomy no longer applies
to Neural Brain as a whole.

The remaining decision text is retained as accepted historical evidence.
Present-tense and `current` statements below describe the 2026-07-15
memory-system baseline, not the authority after ADR-018.

## Context

The Foundation baseline described Neural Brain as a biologically inspired agent
system and assigned it goals, planning, action execution, tool use, completion,
and autonomy. That boundary is incorrect. Neural Brain is the governed memory
system used by people, agents, and other authorized consumers. An agent can use
the brain, but the brain is not itself an agent.

Leaving the two responsibilities combined would give a memory component
authority over the consumers whose context it stores. It would also make agent
lifecycle and external-effect controls appear to be intrinsic memory
capabilities.

## Decision

Neural Brain is a product- and domain-neutral memory system. It owns governed
memory intake, provenance, scope isolation, working context, durable memory,
retrieval, freshness, consolidation, controlled learning, retention, deletion,
and audit evidence.

Goals, plans, action intents, tools, execution, completion decisions, and
autonomy belong to external consumers. Neural Brain MUST NOT own, schedule, or
execute them. External agents and applications interact with Neural Brain only
through authenticated, scoped, typed ports. Consumer input remains untrusted
until validated, and retrieved memory is contextual evidence rather than
authority, policy, approval, or instruction.

The memory capability sequence is:

1. Foundation: repository governance, normative memory contracts, and quality
   controls.
2. Stage 1: authenticated scope, governed memory intake, observations, Working
   Memory, checkpoints, inactive memory candidates, audit, retention
   foundations, and deterministic verification.
3. Stage 2: source registry, episodic memory, semantic claims and assessments,
   retrieval, freshness, and dependency-aware deletion.
4. Stage 3: controlled consolidation, re-evaluation, procedural memory,
   quarantine, authorized promotion, and rollback.
5. Stage 4: explicit audited cross-area knowledge transfer and scalable memory
   coordination. Stage 4 does not add agent execution or autonomy.

The following earlier decisions are superseded because they define agent-only
runtime concerns: ADR-004, ADR-006, ADR-007, ADR-008, ADR-009, and ADR-011.
Their files remain as historical records. ADR-001, ADR-002, ADR-003, ADR-005,
ADR-010, ADR-012, ADR-013, and ADR-014 remain accepted as amended by this ADR.

Architecture Directive v1.1 is superseded by Architecture Directive v2.0,
which is in turn superseded by Architecture Directive v3.0.

## Resolution by ADR-016

At the time of acceptance, this ADR left the persistent Tenant-root rule open.
ADR-016 now resolves it through typed catalog objects with explicit required
parent lineage, while operational memory always carries `tenant_id` and
`area_id`. No sentinel Area, nullable exception, or implicit root scope is
authorized.

## Consequences

- Agent runtime contracts are removed from the current architecture baseline.
- Memory transition ownership, provenance, isolation, retention, and promotion
  remain protected system concerns.
- External consumers retain responsibility for their own goals, actions,
  authorization, execution, verification, and completion.
- Existing machine-readable agent contracts require separate archival or
  replacement work and are not current implementation authority.
- Backlog, tests, documentation, and schemas must use memory-system terminology
  and reject accidental agent-runtime capabilities.

## Invariants and Constraints

- Neural Brain MUST NOT plan, execute tools, perform external actions, or decide
  that a consumer goal is complete.
- Memory never creates consumer authority, policy, approval, identity, or scope.
- Scope and actor identity come only from authenticated runtime context.
- Cross-area memory use is denied unless an explicit audited transfer contract
  authorizes a minimized, provenance-preserving representation.
- Inactive memory candidates are not retrievable as accepted memory.
- Promotion and consolidation are controlled, reversible, and auditable.
- Retention, lawful deletion, and deletion of derivatives remain mandatory.

## Relationship to the Architecture Directive

Architecture Directive v3.0 is the current normative consolidation of this
decision together with ADR-016 and ADR-017. It retains the memory-system
boundary, resolves the Tenant-root conflict, and adds governed Dreaming.
