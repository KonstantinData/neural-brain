---
title: "PR #8 - NB-1 Evidence Foundation"
created_at: 2026-07-17T11:35:00+02:00
area: Neural Brain
repository: D:\Git-GitHub\Repositories\condata\neural-brain
task: "Learn PR #8: feat: add NB-1 evidence foundation"
task_type: per-pr-learning-artifact
domain: Training provenance, hidden evaluation boundary, protected persistence
difficulty: advanced
estimated_learning_time: 105 minutes
concepts:
  - deterministic offline training
  - self-verifying evidence bundle
  - hidden evaluator interface
  - PostgreSQL cognitive checkpoints
  - compare-and-set recovery
  - claim boundary
prerequisites:
  - PR #7 safe serial cognition
  - training/evaluation split concepts
  - hashing and artifact provenance
  - PostgreSQL transaction concepts
related_files:
  - src/neural_brain/cognition/training.py
  - src/neural_brain/postgres/cognitive_repository.py
  - tools/train_nb1_workspace.py
  - migrations/0004_nb1_cognitive_checkpoints.sql
  - docs/architecture/evaluations/artifacts/nb1-v1-offline-training-bundle.json
  - tests/unit/test_nb1_training.py
  - tests/evaluation/test_nb1_hidden_evaluator.py
  - tests/database/test_postgres_cognitive_repository.py
related_components:
  - offline training bundle
  - hidden evaluator interface
  - PostgresCognitiveRepository
  - NB-1 evidence foundation
related_repositories:
  - neural-brain
related_topics:
  - PR #8
  - deterministic training
  - model provenance
  - no promotion claim
learning_status: new
tags:
  - Projektbasiert
  - Fortgeschritten
notion_tracker_url: https://app.notion.com/p/3a01c1ac5ec0818d9869f065592b8f33
---

# PR #8 - NB-1 Evidence Foundation

## 1. Task Summary

PR #8 closed implementation and evidence-foundation gaps left by PR #7. It added deterministic offline training, a self-verifying non-promoted bundle, a hidden evaluator interface, migration 0004, and a PostgreSQL cognitive checkpoint adapter that commits transition evidence, provenance, receipt, and audit inside the existing Memory Transition Gate transaction.

The learning goal is to understand how evidence can be stored without becoming a release, promotion, or recognition claim.

Source PR: https://github.com/KonstantinData/neural-brain/pull/8

## 2. Context

PR #7 implemented a safe serial cognition slice but still needed stronger training provenance and live PostgreSQL cognition/recovery evidence. PR #8 added those foundations while explicitly making no hidden-test, NB-1 release, model promotion, or Neural Brain Candidate claim.

## 3. Approach

The PR generated a deterministic train-only dataset, bounded candidate grid, selected parameters by a preregistered rule, and wrote a self-validating bundle. It also introduced a hidden evaluator interface without storing hidden data.

On the database side, it added protected cognitive checkpoint persistence with stale-version, cross-scope, corruption, restart, replay, tamper, audit-failure rollback, and no-claim tests.

## 4. Key Decisions

One decision was that training is offline-only and deterministic. Runtime training remains unavailable.

Another decision was that the bundle is non-promoted. It can prove provenance consistency, not stage release.

The hidden evaluator interface stores no hidden dataset and cannot invent hidden results.

The database adapter validates returned transition and audit evidence instead of trusting SQL success alone.

## 5. Concepts and Methods

Training provenance binds dataset role, generator, seed, candidate grid, selection rule, code digest, contract digest, environment digest, parameter digest, and manifest digest.

Compare-and-set checkpointing prevents stale writers from overwriting newer cognitive state.

Hidden evaluation boundary means public code can define how to accept an independent hidden artifact, but the hidden data itself is not checked into the repo.

## 6. Knowledge Prerequisites and Gaps

You should understand training/test separation, deterministic hashing, model manifests, PostgreSQL transactions, and rollback tests.

A key gap is how to operationalize independent hidden evaluation later without contaminating hidden data.

## 7. Learning Path

```text
NB-1 evidence foundation
|-- Deterministic train-only data
|-- Bounded grid search
|-- Self-verifying model bundle
|-- Hidden evaluator interface
|-- Protected PostgreSQL checkpoint
`-- No release or promotion claim
```

## 8. Practical Examples

Read `src/neural_brain/cognition/training.py`. The validators reject tampered datasets, candidate indexes, selected candidate rules, parameter digests, and manifest digests.

Read `src/neural_brain/postgres/cognitive_repository.py`. The adapter checks transition identity, version, trusted training provenance, returned checkpoint identity, and audit evidence.

## 9. Exercises

### Beginner

- Objective: Explain why the bundle is non-promoted.
- Expected result: A short paragraph.
- Hints: Look for `stage_release_authorized` and `active_model_promoted`.
- Validation criteria: You do not call it a released model.

### Intermediate

- Objective: Trace the digest chain in the training artifact.
- Expected result: Dataset to provenance to parameters to manifest.
- Hints: Follow validators in `training.py`.
- Validation criteria: You can name what each digest protects.

### Advanced

- Objective: Design hidden evaluator intake.
- Expected result: Required fields, contamination report, independent actor, failure criteria.
- Hints: Use `test_nb1_hidden_evaluator.py`.
- Validation criteria: Hidden data is not stored or reconstructed in repo.

## 10. Reflection Questions

1. Why is training deterministic here?
2. What does a self-verifying bundle prove?
3. What does it not prove?
4. Why does SQL success need application-level validation?
5. What remains before NB-1 can be released?

## 11. Common Mistakes and Risks

The main mistake is treating training provenance as evaluation success. It is only evidence that the training artifact is consistent and bounded.

Another risk is leaking hidden test data. PR #8 avoids that by defining an interface rather than storing hidden artifacts.

## 12. Key Takeaways

1. Evidence artifacts must validate themselves.
2. Offline training is not runtime learning.
3. Hidden evaluation must stay independent.
4. Protected checkpoint persistence needs rollback and tamper tests.
5. No-claim fields are part of safety documentation.

## 13. Area and Repository Context

PR #8 builds on PR #7 and makes NB-1 evidence more credible, but it still leaves independent hidden artifact execution, complete EVAL report fields, and release review open.

Related Notion tracker entry: https://app.notion.com/p/3a01c1ac5ec0818d9869f065592b8f33

## 14. Related Themes

### Provenance

- Relationship: Every artifact is tied to inputs, code, environment, and contract.
- Type: Evidence engineering.
- Learning value: Prevents unverifiable model claims.

### Hidden Evaluation

- Relationship: Interface exists, hidden data does not.
- Type: AI evaluation.
- Learning value: Protects test integrity.

### Protected Persistence

- Relationship: Cognitive checkpoints commit through Memory Gate transaction.
- Type: Backend safety.
- Learning value: Keeps cognition evidence atomic.

## 15. Further Learning Resources

- `src/neural_brain/cognition/training.py`
- `src/neural_brain/postgres/cognitive_repository.py`
- `tools/train_nb1_workspace.py`
- `tests/evaluation/test_nb1_hidden_evaluator.py`
