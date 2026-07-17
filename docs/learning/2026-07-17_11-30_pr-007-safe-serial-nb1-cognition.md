---
title: "PR #7 - Safe Serial NB-1 Cognition Slice"
created_at: 2026-07-17T11:30:00+02:00
area: Neural Brain
repository: D:\Git-GitHub\Repositories\condata\neural-brain
task: "Learn PR #7: feat: add first safe serial NB-1 cognition slice"
task_type: per-pr-learning-artifact
domain: Safe neural cognition, evaluation, checkpointing
difficulty: advanced
estimated_learning_time: 105 minutes
concepts:
  - NB-1 safe serial cognition
  - recurrent neural workspace
  - effect-free cognitive cycle
  - internal goal and plan proposals
  - metacognitive ask/continue
  - baselines and ablations
prerequisites:
  - PR #6 architecture boundary
  - Python service patterns
  - basic recurrent model concepts
  - evaluation baseline and ablation concepts
related_files:
  - docs/architecture/contracts/nb1-safe-serial-cognition.json
  - docs/architecture/evaluations/nb1-safe-serial-cognition-v3.json
  - docs/architecture/nb1-work-packages.md
  - src/neural_brain/cognition/service.py
  - src/neural_brain/cognition/workspace.py
  - src/neural_brain/cognition/evaluation.py
  - tests/unit/test_cognition_service.py
  - tests/evaluation/test_nb1_safe_serial_cognition.py
related_components:
  - CognitiveCycleService
  - Neural Cognitive Workspace
  - NB-1 evaluation harness
related_repositories:
  - neural-brain
related_topics:
  - PR #7
  - EVAL-01 v3
  - effect-free cognition
  - no NB-1 release claim
learning_status: new
tags:
  - Projektbasiert
  - Fortgeschritten
notion_tracker_url: https://app.notion.com/p/3a01c1ac5ec08121890cdb03673ee2ff
---

# PR #7 - Safe Serial NB-1 Cognition Slice

## 1. Task Summary

PR #7 added the first effect-free NB-1 vertical slice. It froze corrected EVAL-01 v3, added a serial recurrent cognitive workspace, persisted transition evidence atomically, bound context providers, measured baselines and ablations, and updated docs without claiming NB-1 completion.

The learning goal is to understand how to implement a narrow cognitive slice without accidentally adding autonomy or external effects.

Source PR: https://github.com/KonstantinData/neural-brain/pull/7

## 2. Context

PR #6 defined the complete cognitive-system target. PR #7 began NB-1 implementation under strict limits: recorded or synthetic observations only, no tools, no executor, no Action Intent, no external effects, no online training, and no active model mutation.

## 3. Approach

The implementation added typed cognition models, ports, adapters, workspace, service, evaluation harness, and tests. The service takes authenticated runtime context, checks checkpoint version and scope, runs one fixed model step, produces internal proposals, and commits evidence through the memory gate.

## 4. Key Decisions

The key decision was to keep the slice serial and effect-free. The system can propose internal goals and plans, but it cannot act.

Another decision was to retain rejected evaluation v1/v2 history and freeze corrected v3. This preserves learning from flawed specifications.

The fix commit atomically persisted transition evidence, reinforcing that cognitive state and audit must not diverge.

## 5. Concepts and Methods

An effect-free cognitive cycle can observe, attend, update hidden state, propose internal goals/plans, and emit metacognitive decisions without touching the external world.

A recurrent workspace keeps state across observations. In this PR it is intentionally small and bounded.

Ablation checks whether a mechanism matters by disabling or altering it and measuring expected impairment.

## 6. Knowledge Prerequisites and Gaps

You should understand service boundaries, typed models, recurrence, confidence versus uncertainty, and baseline comparisons.

A key gap is that `ask` and `continue` are heuristic here; they are not yet calibrated metacognition.

## 7. Learning Path

```text
NB-1 implementation slice
|-- Frozen evaluation contract
|-- Recurrent workspace
|-- Authenticated scope
|-- Internal proposals
|-- Memory-gate checkpoint
`-- Baseline and ablation evidence
```

## 8. Practical Examples

Read `src/neural_brain/cognition/service.py`. The important sequence is context, scope, checkpoint version, fixed model, internal proposals, transition envelope, and Memory Gate commit.

Read `tests/unit/test_cognition_service.py` to see no-effect-surface and failure tests.

## 9. Exercises

### Beginner

- Objective: Trace one `run_cycle` call.
- Expected result: Ordered steps from request to result.
- Hints: Follow `CognitiveCycleService.run_cycle`.
- Validation criteria: No step executes an external effect.

### Intermediate

- Objective: Explain why v1/v2 evaluation specs remain in the repo.
- Expected result: A short history note.
- Hints: Look at evaluation files.
- Validation criteria: You mention rejected history and traceability.

### Advanced

- Objective: Propose a stronger metacognition test.
- Expected result: Scenario, expected decision, and calibration evidence.
- Hints: Current behavior only covers `ask` and `continue`.
- Validation criteria: The test does not claim full metacognition.

## 10. Reflection Questions

1. Why is effect-free cognition useful?
2. What is still missing for NB-1 completion?
3. Why does the service reject stale checkpoints?
4. Why are internal plans not actions?
5. What does ablation prove and not prove?

## 11. Common Mistakes and Risks

The main mistake is overclaiming. PR #7 is a first vertical slice, not NB-1 release evidence.

Another risk is treating internal goal proposals as protected Goal Runtime state. They are proposals only.

## 12. Key Takeaways

1. A narrow cognitive slice can be valuable if it is claim-bounded.
2. Internal proposals are not external effects.
3. Checkpoint state must be scoped and versioned.
4. Evaluation history should preserve rejected specs.
5. Ablations are necessary but not complete recognition evidence.

## 13. Area and Repository Context

PR #7 is the first implementation step after the complete-system rebaseline. It begins NB-1 but explicitly leaves release evidence incomplete.

Related Notion tracker entry: https://app.notion.com/p/3a01c1ac5ec08121890cdb03673ee2ff

## 14. Related Themes

### Neural Workspace

- Relationship: Implements a minimal recurrent cognitive mechanism.
- Type: AI implementation.
- Learning value: Demonstrates bounded stateful cognition.

### Safe Scope

- Relationship: Every cycle runs in authenticated session scope.
- Type: Safety architecture.
- Learning value: Prevents payload-defined authority.

### Evaluation History

- Relationship: v1/v2 rejected specs remain visible.
- Type: Evidence governance.
- Learning value: Shows how evaluation improves over time.

## 15. Further Learning Resources

- `src/neural_brain/cognition/service.py`
- `docs/architecture/evaluations/nb1-safe-serial-cognition-v3.json`
- `tests/evaluation/test_nb1_safe_serial_cognition.py`

