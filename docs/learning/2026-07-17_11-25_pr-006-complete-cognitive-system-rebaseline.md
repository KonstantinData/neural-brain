---
title: "PR #6 - Complete Cognitive-System Rebaseline"
created_at: 2026-07-17T11:25:00+02:00
area: Neural Brain
repository: D:\Git-GitHub\Repositories\condata\neural-brain
task: "Learn PR #6: feat(architecture): rebaseline neural brain as cognitive system"
task_type: per-pr-learning-artifact
domain: Cognitive architecture, two-plane safety, recognition gates
difficulty: advanced
estimated_learning_time: 105 minutes
concepts:
  - complete cognitive-system target
  - Cognitive Plane
  - Protected Control Plane
  - Memory Core subsystem
  - recognition gates
  - evaluation gates
  - stage roadmap
prerequisites:
  - ADR supersession
  - AI evaluation concepts
  - protected state and authority concepts
  - Memory Core boundary from PR #4
related_files:
  - docs/adr/ADR-018-complete-cognitive-system.md
  - docs/architecture/architecture-directive-v4.0.md
  - docs/architecture/neural-brain-recognition-standard.md
  - docs/architecture/evaluation-framework.md
  - docs/architecture/delivery-roadmap.md
  - docs/architecture/contracts/recognition-gates.json
  - docs/architecture/contracts/evaluation-gates.json
  - README.md
related_components:
  - full Neural Brain target architecture
  - Memory Core subsystem
  - Protected Control Plane
  - recognition standard
related_repositories:
  - neural-brain
related_topics:
  - PR #6
  - ADR-018
  - Architecture Directive v4.0
  - NB-0 through NB-8
learning_status: new
tags:
  - Projektbasiert
  - Fortgeschritten
notion_tracker_url: https://app.notion.com/p/3a01c1ac5ec0817db3cadbcbfad52747
---

# PR #6 - Complete Cognitive-System Rebaseline

## 1. Task Summary

PR #6 rebaselined Neural Brain as a complete protected cognitive system. It accepted ADR-018, Architecture Directive v4.0, recognition and evaluation gates, delivery roadmap, capability traceability, and a corrected README maturity boundary.

The learning goal is to understand the target architecture and how it differs from current implementation maturity.

Source PR: https://github.com/KonstantinData/neural-brain/pull/6

## 2. Context

PR #4's memory-only boundary was too narrow for the accepted Neural Brain goal. PR #6 restored the complete cognitive-system target while preserving Memory Core as an internal protected subsystem.

It also superseded PR #5 as a delivery path and corrected its release blocker and Dreaming safety boundary.

## 3. Approach

The PR updated ADRs, architecture directives, machine-readable contracts, threat model, roadmap, traceability, migrations, Memory Core implementation, and documentation. It separated target architecture from implemented state and made recognition claims non-compensatory.

## 4. Key Decisions

The central decision was ADR-018: Neural Brain owns the complete protected perception-cognition-action-learning loop, not only memory.

Another decision was the two-plane architecture. The Cognitive Plane proposes and learns; the Protected Control Plane owns authority, gates, approvals, execution fences, verification, shutdown, and audit.

The PR also decided that "Neural Brain Candidate" is prohibited until later stage and independent recognition evidence.

## 5. Concepts and Methods

Target architecture is not implementation evidence. It defines direction and constraints.

The Protected Control Plane prevents cognitive capability from becoming execution authority.

Recognition gates are non-compensatory: a missing mechanism, safety gate, or evaluation artifact cannot be averaged away.

## 6. Knowledge Prerequisites and Gaps

You should understand why LLM wrappers, RAG-only systems, workflow graphs, and static memory stores are insufficient for this repository's Neural Brain target.

A major gap to study is how to evaluate causal contribution of trainable neural mechanisms across cognitive functions.

## 7. Learning Path

```text
Complete Neural Brain architecture
|-- Memory Core retained
|-- Cognitive Plane defined
|-- Protected Control Plane defined
|-- Recognition standard
|-- Evaluation gates
`-- NB-0 to NB-8 roadmap
```

## 8. Practical Examples

Read ADR-018 first, then Architecture Directive v4.0. ADR-018 is the decision; the directive expands it into operational requirements.

Read the README status section to see how target and current state are separated.

## 9. Exercises

### Beginner

- Objective: Explain Cognitive Plane versus Protected Control Plane.
- Expected result: Two paragraphs.
- Hints: Use Architecture Directive v4.0.
- Validation criteria: Capability does not become authority.

### Intermediate

- Objective: List what Memory Core remains responsible for.
- Expected result: Five retained Memory Core invariants.
- Hints: Compare ADR-015 and ADR-018.
- Validation criteria: You do not re-expand Memory Core into full autonomy.

### Advanced

- Objective: Design a recognition-gate checklist for one future stage.
- Expected result: Gate, evidence, failure condition.
- Hints: Use `recognition-gates.json`.
- Validation criteria: Missing evidence blocks the claim.

## 10. Reflection Questions

1. Why did the memory-only product boundary need supersession?
2. What does the Protected Control Plane own?
3. Why is target architecture not a release claim?
4. Why is NB-6 tied to recognition?
5. How does PR #6 preserve PR #4's useful constraints?

## 11. Common Mistakes and Risks

The main mistake is reading the target architecture as implemented behavior. The repo explicitly says the current state is early Memory Core plus first NB-1 development slice.

Another risk is treating a model, planner, or memory component as authority. PR #6 rejects that.

## 12. Key Takeaways

1. Neural Brain is a complete cognitive-system target.
2. Memory Core is a subsystem, not the whole product.
3. Cognitive capability never creates authority.
4. Recognition claims need independent non-compensatory evidence.
5. Clear maturity language prevents overclaiming.

## 13. Area and Repository Context

PR #6 is the architectural pivot of the current repository. Later NB-1 work depends on this target while remaining claim-bounded.

Related Notion tracker entry: https://app.notion.com/p/3a01c1ac5ec0817db3cadbcbfad52747

## 14. Related Themes

### Cognitive Architecture

- Relationship: Defines integrated perception-cognition-action-learning loop.
- Type: Product architecture.
- Learning value: Establishes what Neural Brain is trying to become.

### Authority Separation

- Relationship: Cognitive Plane cannot execute protected effects.
- Type: Safety architecture.
- Learning value: Prevents unsafe autonomy.

### Evaluation Discipline

- Relationship: Recognition gates govern claims.
- Type: AI evaluation.
- Learning value: Keeps evidence non-compensatory.

## 15. Further Learning Resources

- `docs/adr/ADR-018-complete-cognitive-system.md`
- `docs/architecture/architecture-directive-v4.0.md`
- `docs/architecture/neural-brain-recognition-standard.md`
- `docs/architecture/evaluation-framework.md`

