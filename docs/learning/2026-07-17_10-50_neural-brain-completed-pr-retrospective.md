---
title: Neural Brain Completed Pull Request Retrospective
created_at: 2026-07-17T10:50:00+02:00
area: Neural Brain
repository: D:\Git-GitHub\Repositories\condata\neural-brain
task: Retrospective learning artifact for completed Neural Brain pull requests
task_type: retrospective-learning-artifact
domain: Cognitive architecture, protected state, evidence-driven AI engineering
difficulty: advanced
estimated_learning_time: 180 minutes
concepts:
  - repository foundation and governance
  - architecture decision records
  - protected control plane
  - PostgreSQL transition gates
  - fail-closed safety design
  - NB-1 safe serial neural cognition
  - deterministic offline training provenance
  - non-compensatory evaluation gates
prerequisites:
  - Python strict typing and pytest
  - PostgreSQL transactional design
  - ADR-based architecture governance
  - basic neural network and evaluation concepts
  - GitHub pull request review workflow
related_files:
  - README.md
  - AGENTS.md
  - docs/adr/ADR-013-python-runtime-and-toolchain.md
  - docs/adr/ADR-015-memory-system-not-agent-runtime.md
  - docs/adr/ADR-016-hierarchy-catalog-and-operational-memory-scope.md
  - docs/adr/ADR-017-governed-area-local-dreaming.md
  - docs/adr/ADR-018-complete-cognitive-system.md
  - docs/architecture/architecture-directive-v4.0.md
  - docs/architecture/nb1-work-packages.md
  - docs/architecture/evaluation-framework.md
  - src/neural_brain/memory/service.py
  - src/neural_brain/cognition/service.py
  - src/neural_brain/cognition/training.py
  - src/neural_brain/postgres/cognitive_repository.py
related_components:
  - Foundation governance baseline
  - Memory Core
  - Protected Control Plane
  - NB-1 CognitiveCycleService
  - PostgreSQL Memory Transition Gate
  - offline training and evidence bundle
related_repositories:
  - neural-brain
related_topics:
  - PR #1 FND-01 repository baseline
  - PR #2 FND-02 executable architecture baseline
  - PR #3 FND-03 quality and CI baseline
  - PR #4 memory-system rebaseline
  - PR #5 superseded Stage 1 memory kernel and Dreaming baseline
  - PR #6 complete cognitive-system rebaseline
  - PR #7 first safe serial NB-1 cognition slice
  - PR #8 NB-1 evidence foundation
learning_status: new
tags:
  - Projektbasiert
  - Fortgeschritten
notion_tracker_url: https://app.notion.com/p/3a01c1ac5ec081329086c3b6135de903
---

# Neural Brain Completed Pull Request Retrospective

## 1. Task Summary

This artifact turns the completed Neural Brain pull request sequence into reusable study material. The reviewed scope covers merged PRs #1, #2, #3, #4, #6, #7, and #8. Closed unmerged PR #5 is included as superseded context because PR #6 explicitly absorbed and corrected its delivery path.

The main outcome to learn is how the repository moved from a guarded foundation into an early Memory Core and then into a complete cognitive-system target with a first effect-free NB-1 implementation slice. The sequence is not evidence that Neural Brain is released, autonomous, or a Neural Brain Candidate. It is evidence of disciplined architecture, protected state design, and claim-bounded implementation.

Primary PR sources:

- PR #1: https://github.com/KonstantinData/neural-brain/pull/1
- PR #2: https://github.com/KonstantinData/neural-brain/pull/2
- PR #3: https://github.com/KonstantinData/neural-brain/pull/3
- PR #4: https://github.com/KonstantinData/neural-brain/pull/4
- PR #5: https://github.com/KonstantinData/neural-brain/pull/5
- PR #6: https://github.com/KonstantinData/neural-brain/pull/6
- PR #7: https://github.com/KonstantinData/neural-brain/pull/7
- PR #8: https://github.com/KonstantinData/neural-brain/pull/8

## 2. Context

Neural Brain is a product- and domain-neutral cognitive architecture repository. Its target is an integrated perception-cognition-action-learning system, but its current implementation remains early: Foundation, Memory Core prerequisites, and a first effect-free NB-1 development slice.

The completed PRs form a staged learning path:

1. Build a reproducible repository and quality baseline.
2. Convert architecture claims into testable ADRs, contracts, and release stops.
3. Add CI, migration, security, and release evidence gates.
4. Correct a wrong product boundary when the architecture drifted toward memory-only or agent-only interpretations.
5. Preserve useful Memory Core work while re-establishing Neural Brain as a complete cognitive system.
6. Implement a bounded serial neural cognition slice without external effects.
7. Add deterministic offline training provenance and protected PostgreSQL cognition persistence without claiming stage release.

The central constraint is claim discipline: every capability must be separated into target, implemented behavior, and verified release evidence.

## 3. Approach

The PR sequence used an evidence-first architecture approach:

- ADRs recorded durable decisions before dependent implementation.
- Machine-readable contracts made architecture testable.
- PostgreSQL was treated as the authoritative ledger for protected state.
- Runtime services attached trusted context instead of accepting scope from payloads.
- CI and local tooling checked formatting, linting, strict typing, type-exception policy, migration safety, security policy, and tests.
- Evaluation work was preregistered and separated from hidden-test claims.
- Closed or superseded work was not hidden; PR #5 remained useful context but PR #6 became the accepted delivery path.

This is the key method to transfer: make architecture falsifiable before implementation, and make implementation unable to exceed its evidence.

## 4. Key Decisions

The first decision was to make the repository itself a governed product artifact. PR #1 established AGENTS.md, README maturity language, ADR-013, locked Python and uv tooling, local PostgreSQL dev/test setup, and fail-closed database reset guards. The rejected alternative was to start with feature code and add governance later. That would have made later safety claims much weaker.

The second decision was to encode architecture as contracts. PR #2 added ADR-001 through ADR-014, architecture directive v1.1, Goal and Action state machine contracts, ledger invariants, threat model, release stops, and property tests. The important lesson is that architecture documents become stronger when tests can fail if they drift.

The third decision was to treat quality and release evidence as product behavior. PR #3 added CODEOWNERS, pinned GitHub Actions, workflow policy, migration validation, SBOM and release evidence tooling, secret scanning, dependency checks, and governance tests. This made delivery gates part of the system, not an afterthought.

The fourth decision was to correct the product boundary when it became wrong. PR #4 rebaselined Neural Brain as a memory system under ADR-015. That was useful for isolating Memory Core responsibilities, but it also overcorrected by excluding cognition. The later lesson from PR #6 is that a good intermediate correction can still be superseded when it no longer satisfies the product recognition standard.

The fifth decision was to keep Memory Core as a protected subsystem rather than discard it. PR #6 accepted ADR-018 and Architecture Directive v4.0, restoring Neural Brain as a complete cognitive system while retaining Memory Core invariants from ADR-015 through ADR-017. The rejected alternatives were a memory-only product, a fragmented separate orchestrator, or restoring the older agent architecture unchanged.

The sixth decision was to implement NB-1 as effect-free internal cognition. PR #7 added CognitiveCycleService, a fixed-version neural workspace, internal goal and plan proposals, metacognitive continue/ask behavior, and evaluation baselines. It deliberately avoided actions, tools, executors, online training, and active model mutation.

The seventh decision was to make training and persistence evidence tamper-resistant. PR #8 added deterministic offline training, a self-verifying non-promoted bundle, hidden-evaluator interface, migration 0004, and a PostgreSQL cognitive repository that commits transition envelope, checkpoint, receipt, provenance, and audit inside the existing Memory Transition Gate transaction.

## 5. Concepts and Methods

Protected state means that important state can only be written through its owning transition gate. In this repository, memory and cognition persistence are designed so application code submits typed requests, while the protected database gate commits or rejects the change atomically.

Fail-closed design means unknown or incomplete conditions stop progress. Examples include unsafe database reset names, missing authenticated project/session scope, Dreaming execution before its lease and snapshot prerequisites, stale cognitive checkpoint versions, and missing hidden evaluation artifacts.

The two-plane architecture separates capability from authority. The Cognitive Plane can infer, propose, plan, and learn. The Protected Control Plane owns identity, scope, policy, approvals, execution fences, verification, kill switch, promotion, reconciliation, and audit. Cognitive capability never creates authority.

Non-compensatory evaluation means one strong result cannot make up for a missing safety, mechanism, privacy, or authority gate. NB-1 development evidence is useful, but it does not release NB-1 or authorize the Neural Brain Candidate label.

Deterministic offline training provenance means that training data role, generator seed, candidate grid, selection rule, code digest, contract digest, environment digest, parameters, and model manifest are bound by hashes and validation. That makes the artifact inspectable without turning it into a promoted model.

## 6. Knowledge Prerequisites and Gaps

Helpful prerequisites:

- Understand why ADRs exist and when they should supersede older decisions.
- Understand PostgreSQL transactions, row-level authority patterns, and migration validation.
- Understand strict typing with Pydantic boundaries and mypy.
- Understand baseline, ablation, confidence interval, held-out evaluation, and contamination risk.
- Understand why tool success, model self-report, or PR merge success is not the same as capability success.

Current gaps to study further:

- How to design hidden evaluation artifacts without leaking test data.
- How to prove causal contribution of a neural mechanism beyond a simple development slice.
- How to implement calibrated uncertainty rather than a heuristic ambiguity score.
- How to move from effect-free cognition to later closed-loop simulation without weakening the authority model.

## 7. Learning Path

```text
Evidence-driven cognitive system engineering
|-- Repository foundation
|   |-- locked toolchain
|   |-- CI and release evidence
|   `-- governance and traceability
|-- Protected architecture
|   |-- ADRs and contracts
|   |-- transition gates
|   `-- fail-closed release stops
|-- Memory Core
|   |-- scope and provenance
|   |-- PostgreSQL atomicity
|   `-- Dreaming disabled until safe prerequisites exist
|-- NB-1 safe serial cognition
|   |-- fixed-version neural workspace
|   |-- bounded internal proposals
|   |-- checkpoint recovery
|   `-- no external effects
|-- Evaluation and learning evidence
|   |-- baselines and ablations
|   |-- deterministic training provenance
|   `-- independent hidden evaluation
`-- Later Neural Brain stages
    |-- perception and world model
    |-- differentiated memory
    |-- continual learning
    `-- closed-loop action with independent verification
```

## 8. Practical Examples

In `src/neural_brain/memory/service.py`, the service rejects memory cycles when Working Memory does not reference the admitted observation. It also requires authenticated project and session scope before committing. That is a small but important pattern: validate the cycle relationship before the gate writes protected state.

In `src/neural_brain/cognition/service.py`, the cognitive cycle loads trusted context, validates the expected checkpoint version, rejects model-version changes in place, runs one fixed workspace step, produces internal proposals, and commits through a memory gate. The service has no tool or external-effect surface.

In `src/neural_brain/cognition/training.py`, the offline training bundle validates its own dataset digest, candidate ordering, selection rule, parameter digest, manifest digest, and no-claim status. That teaches how to store training evidence without implying model promotion.

In `src/neural_brain/postgres/cognitive_repository.py`, the repository validates that committed transition evidence matches the request and that audit evidence is complete. This prevents the database operation from being treated as trustworthy merely because it returned successfully.

## 9. Exercises

### Beginner

- Objective: Map PR #1 through PR #8 to the repository maturity timeline.
- Expected result: A one-page timeline that separates Foundation, Memory Core, complete cognitive-system target, NB-1 implementation slice, and evidence foundation.
- Hints: Use PR titles, README status, ADR-018, and `docs/architecture/nb1-work-packages.md`.
- Validation criteria: The timeline does not claim NB-1 release, production readiness, or Neural Brain Candidate status.

### Intermediate

- Objective: Trace one protected cognitive cycle from request to audit.
- Expected result: A short diagram or bullet flow covering `CognitiveCycleService.run_cycle`, `PostgresCognitiveRepository.commit_checkpoint`, Memory Transition Gate persistence, and audit validation.
- Hints: Look for scope construction, checkpoint version checks, active model evidence, transition envelope, and audit evidence.
- Validation criteria: The flow identifies where stale checkpoint, scope crossing, model mismatch, and incomplete audit are rejected.

### Advanced

- Objective: Design the next evidence gate for NB-1 without weakening claim boundaries.
- Expected result: A proposal for hidden evaluation artifact intake, contamination controls, independent execution, result schema, and failure criteria.
- Hints: Start from EVAL-01 v3, PR #8 hidden-evaluator interface, and the non-compensatory recognition standard.
- Validation criteria: The proposal stores no hidden data in the repo, makes no release claim before independent review, and keeps training, evaluation, and promotion separated.

## 10. Reflection Questions

1. Why was the memory-only rebaseline useful even though it was later superseded as the product boundary?
2. Which parts of the current implementation are target architecture, and which parts are executable behavior?
3. Where does the repository prevent untrusted content from becoming trusted scope or authority?
4. Why is deterministic offline training evidence not the same as model promotion?
5. Which additional evidence would be needed before saying NB-1 is complete?

## 11. Common Mistakes and Risks

The first common mistake is overclaiming. A merged PR, passing tests, or a strong development metric can make the system better, but it does not automatically complete a stage or pass recognition gates.

The second mistake is letting cognitive code write protected state directly. The repository avoids this by routing state changes through services, repositories, PostgreSQL gate functions, and audit checks.

The third mistake is accepting scope from request payloads. The correct pattern is to attach trusted runtime context and then verify that returned records stayed inside that authenticated scope.

The fourth mistake is treating Dreaming as active because a schema exists. In the accepted design, Dreaming is reserved but unavailable until lease, snapshot, and independent validation prerequisites are implemented.

The fifth mistake is confusing training evidence with learning. Learning activation needs isolated evaluation, promotion, canary, retention, rollback, and safety evidence. PR #8 deliberately stores a non-promoted development bundle.

## 12. Key Takeaways

1. Architecture claims should be versioned, testable, and allowed to fail.
2. Product boundary corrections are legitimate engineering work when they preserve traceability.
3. Protected state needs explicit writer ownership, trusted context, atomic commit, and audit evidence.
4. NB-1 can begin as an effect-free cognitive slice without implying autonomy or external effects.
5. Evidence must be staged: development evidence, hidden evaluation, release gates, and recognition claims are different layers.

## 13. Area and Repository Context

This learning belongs to the Neural Brain area and the `neural-brain` repository. It should not import product behavior from other business areas. The repository is the durable technical source of truth; Notion coordinates work state, decisions, backlog, and learning records.

The completed PRs establish that Neural Brain is no longer just a memory database or agent workflow. It is defined as a protected cognitive-system target with an early Memory Core and a first effect-free NB-1 development slice. The next work should preserve the separation between target architecture, implemented code, and accepted evidence.

Related Notion tracker entry:
https://app.notion.com/p/3a01c1ac5ec081329086c3b6135de903

## 14. Related Themes

### Architecture governance

- Relationship: ADRs and directives define durable authority and supersession.
- Type: Technical leadership and repository governance.
- Learning value: Teaches when to preserve history and when to change implementation authority.

### Safety-critical state management

- Relationship: Memory and cognition commits are protected by authenticated scope, transaction boundaries, and audit validation.
- Type: Backend architecture and reliability.
- Learning value: Teaches how to design systems that deny unknown or ambiguous state transitions.

### Evaluation-driven AI implementation

- Relationship: NB-1 work separates baselines, ablations, training provenance, hidden evaluation, and release claims.
- Type: AI engineering and evidence design.
- Learning value: Teaches how to avoid unearned AI capability claims.

## 15. Further Learning Resources

- Repository README: `README.md`
- ADR-018 complete cognitive system: `docs/adr/ADR-018-complete-cognitive-system.md`
- Architecture Directive v4.0: `docs/architecture/architecture-directive-v4.0.md`
- Evaluation framework: `docs/architecture/evaluation-framework.md`
- NB-1 work packages: `docs/architecture/nb1-work-packages.md`
- PostgreSQL documentation for transactions and isolation: not reverified during this retrospective.
- Pydantic v2 documentation for model validation: not reverified during this retrospective.
- Hypothesis documentation for property-based tests: not reverified during this retrospective.
