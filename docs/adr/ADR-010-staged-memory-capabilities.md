# ADR-010: Staged Memory Capabilities

- Status: Superseded as product delivery model by ADR-018; retained for the Memory Core
- Date: 2026-07-15
- Notion source: https://app.notion.com/p/39d1c1ac5ec081b7953ec18893f35c35
- Notion page ID: `39d1c1ac-5ec0-81b7-953e-c18893f35c35`
- Authority: retained_subsystem
- Theme: memory_lifecycle
- Applies to stages: MS-0, MS-1, MS-2, MS-3, MS-4
- Supersedes: none
- Superseded by: ADR-018
- Amends: none
- Amended by: ADR-015, ADR-017, ADR-018

## Supersession by ADR-018

ADR-018 replaces these product-wide stages with NB-0 through NB-8. The
memory-specific ordering below is now explicitly namespaced as MS-0 through
MS-4, remains binding inside the Memory Core, and maps primarily to NB-3 and
NB-4. An MS stage is not an NB stage and does not advance product maturity by
itself. The subsystem exclusion of cognition, goals, planning, action, and
feedback no longer applies to Neural Brain as a whole.

## Amendment by ADR-015 and ADR-017

All stages are memory-only. Stage 1 adds governed intake, observations,
Working Memory, checkpoints, inactive candidates, Dreaming dry runs, and their
safety foundations. Stage 2 adds sources, episodic and semantic memory, retrieval,
freshness, dependency-aware deletion, and inactive Dreaming analysis. Stage 3
adds controlled Dreaming consolidation, re-evaluation, procedural memory,
quarantine, authorized promotion, and rollback. Stage 4 may add explicit
audited cross-area knowledge transfer and scalable memory coordination. No
stage adds agent goals, planning, tools, execution, completion, or autonomy.

## Context

Memory types have different truth, safety, and lifecycle requirements. Enabling
them without stage boundaries would combine temporary context, durable
knowledge, and learned procedure prematurely.

## Decision

Stage 1 contains working memory, checkpoints, observations, inactive memory
candidates, and Dreaming dry runs. Stage 2 introduces episodic and semantic
storage, retrieval, and inactive Dreaming analysis. Stage 3 introduces
controlled Dreaming consolidation, promotion, and procedural learning.

## Invariants and Constraints

- Stage 1 memory candidates remain inactive.
- Stage 1 schemas cannot represent promoted candidates.
- Stage 1 Dreaming cannot create or activate a successor memory version or
  change an active-version pointer.
- Episodic and semantic storage and retrieval are Stage 2 capabilities.
- Stage 2 Dreaming analysis remains inactive and cannot promote candidates.
- Controlled promotion and procedural learning are Stage 3 capabilities.
- Later-stage memory capabilities require explicit migrations and cannot be
  enabled through Stage 1 configuration.

## Consequences

Each later memory capability requires an explicit migration and its owning
delivery stage. Stage 1 cannot accidentally persist or activate promoted memory
candidates.

## Relationship to the Architecture Directive

This decision specializes the architecture directive's staged memory model. It
keeps the directive's Stage 1, Stage 2, and Stage 3 capability boundaries
explicit in schemas and runtime activation.
