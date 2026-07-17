---
title: "PR #5 - Superseded Stage 1 Memory Kernel Path"
created_at: 2026-07-17T11:20:00+02:00
area: Neural Brain
repository: D:\Git-GitHub\Repositories\condata\neural-brain
task: "Learn PR #5: feat(memory): add scoped Stage 1 kernel and Dreaming baseline"
task_type: per-pr-learning-artifact
domain: Superseded implementation path, Memory Kernel, Dreaming safety
difficulty: advanced
estimated_learning_time: 75 minutes
concepts:
  - superseded PR handling
  - scoped memory kernel
  - Dreaming dry run
  - database role bootstrap
  - release blocker diagnosis
prerequisites:
  - pull request lifecycle
  - PostgreSQL role and migration basics
  - fail-closed design
  - Memory Core architecture
related_files:
  - docs/adr/ADR-016-hierarchy-catalog-and-operational-memory-scope.md
  - docs/adr/ADR-017-governed-area-local-dreaming.md
  - docs/architecture/architecture-directive-v3.0.md
  - migrations/0001_scope_catalog.sql
  - migrations/0002_stage1_memory_kernel.sql
  - migrations/0003_dreaming_dry_run.sql
  - src/neural_brain/memory/service.py
  - src/neural_brain/postgres/memory_repository.py
related_components:
  - Stage 1 Memory Kernel
  - scope catalog
  - governed Dreaming baseline
related_repositories:
  - neural-brain
related_topics:
  - PR #5
  - closed without merge
  - superseded by PR #6
  - Dreaming unavailable boundary
learning_status: new
tags:
  - Projektbasiert
  - Fortgeschritten
notion_tracker_url: https://app.notion.com/p/3a01c1ac5ec0814f8b21c88f0fcff32f
---

# PR #5 - Superseded Stage 1 Memory Kernel Path

## 1. Task Summary

PR #5 added a scoped Stage 1 memory kernel and Dreaming baseline, but it was closed without merge. PR #6 later included the useful baseline, fixed its release path, and removed unsafe executable Dreaming behavior.

The learning goal is to understand how a closed PR can still teach architecture, safety, and delivery lessons.

Source PR: https://github.com/KonstantinData/neural-brain/pull/5

## 2. Context

PR #5 followed the memory-system boundary from PR #4. It introduced ADR-016 for Brain/Tenant/Area lineage and ADR-017 for governed Area-local Dreaming. It also added PostgreSQL gates for observations, Working Memory, checkpoints, audit, replay protection, and inactive Dreaming candidates.

It did not merge because its path was superseded by the broader PR #6 cognitive-system rebaseline.

## 3. Approach

The PR implemented memory kernel surfaces, migrations, repository adapter, tests, and runbook updates. It verified scope, audit, cross-Area failure, database roles, and migration digests.

The important review result was not "throw it away"; it was "carry forward the safe parts through a corrected product-boundary PR."

## 4. Key Decisions

The main decision was supersession. Rather than force-merge a blocked path, the work was closed and absorbed into PR #6 with corrections.

Another decision was that Dreaming must remain governed and unable to promote candidates or mutate active pointers. PR #6 tightened this by making supported Dreaming execution fail closed.

## 5. Concepts and Methods

Supersession is when a later change replaces the delivery authority of an earlier PR. It should preserve useful code and evidence while avoiding unsafe merge history.

Dreaming is offline candidate production. It is not active learning, not tool execution, and not protected-state mutation.

## 6. Knowledge Prerequisites and Gaps

You should understand PR lifecycle states, especially the difference between closed and merged. You should also study how a blocked PR can be mined for reusable implementation without accepting its full risk.

## 7. Learning Path

```text
Superseded implementation path
|-- Useful implementation
|-- Release blocker
|-- Product-boundary correction
|-- Replacement PR
`-- Historical learning retained
```

## 8. Practical Examples

PR #5's memory service and PostgreSQL repository concepts appear in the later repository state, but the accepted authority flows through PR #6.

Review ADR-016 and ADR-017 as concepts that survive beyond the closed PR.

## 9. Exercises

### Beginner

- Objective: Explain why PR #5 is included in the learning sequence.
- Expected result: A paragraph about closed-but-useful work.
- Hints: Mention PR #6 supersession.
- Validation criteria: You do not call PR #5 merged.

### Intermediate

- Objective: Identify one safe idea and one unsafe or blocked delivery aspect.
- Expected result: Two-column table.
- Hints: Scope catalog versus executable Dreaming path.
- Validation criteria: The delivery conclusion is "supersede", not "ignore".

### Advanced

- Objective: Write a handover note for a superseded PR.
- Expected result: What to preserve, what to reject, and why.
- Hints: Use PR #5 to PR #6 relationship.
- Validation criteria: The note avoids duplicate implementation work.

## 10. Reflection Questions

1. Why can a closed PR still be valuable?
2. What makes Dreaming unsafe if activated too early?
3. How should superseded work be documented?
4. What evidence should move forward?
5. What evidence should not move forward?

## 11. Common Mistakes and Risks

The main mistake is equating "closed without merge" with failure. PR #5 carried useful implementation ideas but lost delivery authority.

Another risk is silently copying superseded behavior without its safety corrections.

## 12. Key Takeaways

1. Superseded PRs can be learning artifacts.
2. Delivery authority matters as much as code content.
3. Dreaming must not mutate protected state early.
4. Replacement PRs should explain what they absorb and correct.
5. Closed PRs should not be represented as merged evidence.

## 13. Area and Repository Context

PR #5 sits between the memory-only boundary and complete cognitive-system rebaseline. It teaches how Neural Brain handled a blocked implementation path without losing traceability.

Related Notion tracker entry: https://app.notion.com/p/3a01c1ac5ec0814f8b21c88f0fcff32f

## 14. Related Themes

### Delivery Governance

- Relationship: Closed PRs need explicit interpretation.
- Type: Process.
- Learning value: Prevents stale or misleading evidence.

### Dreaming Safety

- Relationship: Candidate production must remain offline and bounded.
- Type: AI safety.
- Learning value: Avoids premature learning activation.

### Scope Catalog

- Relationship: Brain/Tenant/Area lineage underpins later work.
- Type: Data architecture.
- Learning value: Shows identity foundations.

## 15. Further Learning Resources

- `docs/adr/ADR-016-hierarchy-catalog-and-operational-memory-scope.md`
- `docs/adr/ADR-017-governed-area-local-dreaming.md`
- `docs/architecture/architecture-directive-v3.0.md`

