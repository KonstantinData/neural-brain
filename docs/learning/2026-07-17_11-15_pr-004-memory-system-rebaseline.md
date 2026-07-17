---
title: "PR #4 - Memory-System Rebaseline"
created_at: 2026-07-17T11:15:00+02:00
area: Neural Brain
repository: D:\Git-GitHub\Repositories\condata\neural-brain
task: "Learn PR #4: Rebaseline Neural Brain as a memory system"
task_type: per-pr-learning-artifact
domain: Memory architecture, product boundary correction
difficulty: advanced
estimated_learning_time: 90 minutes
concepts:
  - product boundary correction
  - Memory Core
  - Memory Transition Gate
  - scope and provenance
  - retention and deletion
  - superseded architecture
prerequisites:
  - ADR review
  - protected state concepts
  - memory lifecycle basics
  - architecture refactoring
related_files:
  - docs/adr/ADR-015-memory-system-not-agent-runtime.md
  - docs/architecture/architecture-directive-v2.0.md
  - docs/architecture/contracts/memory-lifecycle.json
  - docs/architecture/contracts/system-boundary.json
  - docs/architecture/threat-model.md
  - tests/architecture/test_memory_lifecycle_contract.py
related_components:
  - Memory Core
  - Memory Transition Gate
  - memory lifecycle contracts
related_repositories:
  - neural-brain
related_topics:
  - PR #4
  - ADR-015
  - memory-only boundary
  - agent-runtime exclusion
learning_status: new
tags:
  - Projektbasiert
  - Fortgeschritten
notion_tracker_url: https://app.notion.com/p/3a01c1ac5ec08130a61bd65167cd81c8
---

# PR #4 - Memory-System Rebaseline

## 1. Task Summary

PR #4 corrected Neural Brain away from an agent-runtime framing and rebaselined it as a protected memory system. It added ADR-015, Architecture Directive v2.0, memory lifecycle contracts, and removed Goal/Action runtime contracts from the active product boundary.

The learning goal is to understand architectural correction: how to narrow scope when a repository is claiming too much.

Source PR: https://github.com/KonstantinData/neural-brain/pull/4

## 2. Context

The Foundation baseline had combined memory with external agent responsibilities. PR #4 separated them: Neural Brain would store, govern, retrieve, evaluate, consolidate, and forget memory; consumers would own goals, tools, actions, scheduling, and autonomy.

This was later superseded by PR #6 as the product boundary, but it remains important because it protected the Memory Core concept.

## 3. Approach

The PR rewrote README, AGENTS, threat model, runbooks, traceability, ADRs, and contracts. It deleted active Goal and Action contracts and replaced them with memory-system boundary and memory-lifecycle contracts.

Tests were updated so architecture consistency matched the new memory-only boundary.

## 4. Key Decisions

The main decision was to say: memory is not an agent runtime. Memory content, retrieval, consolidation, and procedural hints do not authorize tools or external effects.

Another decision was to keep unresolved Tenant-root versus mandatory Area scope conflict explicit and fail-closed instead of inventing a manual workaround.

## 5. Concepts and Methods

Boundary correction is a real architecture task. It removes or supersedes prior surfaces that no longer match the accepted product definition.

Memory lifecycle means memory has provenance, freshness, retention, deletion, quarantine, rollback, and scope rules.

Fail-closed unresolved conflict means a known design conflict blocks dependent implementation.

## 6. Knowledge Prerequisites and Gaps

You should understand the difference between memory, goals, planning, execution, and autonomy. A useful gap is learning when a correction is too narrow and later needs a broader superseding ADR.

## 7. Learning Path

```text
Architecture correction
|-- Identify overclaim
|-- Remove wrong active contracts
|-- Preserve useful invariants
|-- Add new boundary
`-- Mark unresolved conflicts fail-closed
```

## 8. Practical Examples

Read ADR-015 and then compare it to ADR-018. ADR-015 is not "wrong" in every part; it is superseded as product boundary while retained for Memory Core constraints.

Review `memory-lifecycle.json` to see which memory semantics survived later architecture changes.

## 9. Exercises

### Beginner

- Objective: List what PR #4 excludes from Neural Brain.
- Expected result: A boundary list.
- Hints: Focus on goals, planning, tools, actions, and autonomy.
- Validation criteria: You separate consumer behavior from memory behavior.

### Intermediate

- Objective: Identify invariants preserved after PR #6.
- Expected result: Three Memory Core rules that remain valid.
- Hints: Use ADR-015 and ADR-018.
- Validation criteria: You distinguish superseded boundary from retained subsystem constraints.

### Advanced

- Objective: Write a supersession note for an ADR.
- Expected result: One paragraph explaining what is superseded and what remains.
- Hints: Use ADR-015 as the example.
- Validation criteria: The note does not erase historical traceability.

## 10. Reflection Questions

1. Why was a memory-only correction attractive?
2. Why did it later become insufficient?
3. What is still valuable in ADR-015?
4. How does fail-closed conflict handling protect implementation?
5. What does Memory Core not authorize?

## 11. Common Mistakes and Risks

The main mistake is treating a superseded decision as useless. ADR-015 remains important subsystem history.

Another mistake is hiding unresolved architecture conflict. The repo instead names the conflict and blocks unsafe dependent work.

## 12. Key Takeaways

1. Scope correction is valuable even when later superseded.
2. Memory does not equal agency.
3. Procedural memory can inform cognition but not authorize effects.
4. Historical ADRs preserve why the system changed.
5. Explicit unresolved conflicts are safer than invented defaults.

## 13. Area and Repository Context

PR #4 is the bridge from broad agent-like architecture to protected Memory Core. It prepared the memory subsystem that PR #6 later retained inside a larger complete cognitive-system target.

Related Notion tracker entry: https://app.notion.com/p/3a01c1ac5ec08130a61bd65167cd81c8

## 14. Related Themes

### Product Boundary

- Relationship: Defines what the repository owns.
- Type: Architecture strategy.
- Learning value: Prevents unclear responsibility.

### Memory Governance

- Relationship: Memory lifecycle rules become central.
- Type: Data and safety architecture.
- Learning value: Teaches protected memory semantics.

### Supersession

- Relationship: Later PRs change authority without deleting history.
- Type: Documentation governance.
- Learning value: Shows mature architecture evolution.

## 15. Further Learning Resources

- `docs/adr/ADR-015-memory-system-not-agent-runtime.md`
- `docs/architecture/architecture-directive-v2.0.md`
- `docs/architecture/contracts/memory-lifecycle.json`

