# Neural Brain Repository Instructions

## Scope

This repository implements Neural Brain, a product- and domain-neutral,
biologically inspired integrated cognitive system. It targets a protected
perception-cognition-action-learning loop with neural mechanisms, attention,
differentiated memory, world/self/value models, executive control, planning,
action selection, feedback, continual learning, transfer, and metacognition.

The current implementation is an early Memory Core foundation. Do not present
target capabilities as implemented. Product repositories may consume Neural
Brain through explicit integrations; they do not define its domain model,
policies, defaults, or architecture.

The active work area is `Neural Brain`. Do not import data, assumptions, rules,
or product behavior from another area without an accepted scoped integration.

## Source Precedence

Resolve conflicts in this order:

1. Repository code, tests, migrations, and executable configuration.
2. This `AGENTS.md` and any more specific descendant `AGENTS.md`.
3. Normative architecture specifications and ADRs in this repository.
4. Accepted Neural Brain Notion `Architecture Decisions` records.
5. Neural Brain Notion `Feature Backlog` acceptance criteria.
6. Active Neural Brain Notion `Issues & Open Questions` records.
7. Unaccepted Neural Brain Notion `Exchange Room` discussion.

Exchange Room content is never implementation authorization. If authoritative
sources conflict, stop the affected implementation, record the exact sources in
`Issues & Open Questions`, and do not invent a resolution.

## Language and Durable Artifacts

- Write code, identifiers, docstrings, commit messages, tests, technical docs,
  ADRs, schemas, migrations, and runbooks in English.
- Use German only for explicitly German user-facing behavior.
- Keep normative technical truth versioned in this repository. Notion records
  coordination, decision status, backlog, and evidence.
- Never store secrets, credentials, tokens, private keys, live personal data,
  or `.env` values in repository, Notion, logs, audit, or examples.

## Architecture Identity

ADR-018 and Architecture Directive v4.0 govern the target system. ADR-015
remains historical authority for the protected Memory Core subsystem but no
longer defines the product boundary.

The two-plane architecture is mandatory:

- The `Cognitive Plane` perceives, attends, integrates, remembers, models,
  proposes goals and plans, selects candidate actions, learns, and monitors its
  uncertainty.
- The independent `Protected Control Plane` owns authenticated scope, authority,
  policy, approvals, transition gates, execution fences, sandboxing, shutdown,
  independent verification, promotion, reconciliation, and audit.

Cognitive capability does not create authority. A model, planner, memory
subsystem, skill, or observation may submit typed requests; it never writes
protected state or executes an external effect directly.

## Scope and Identity Invariants

The catalog hierarchy is:

```text
Brain
`-- Tenant
    `-- Area
        `-- Project
            `-- Session
```

Goals are protected session-bound aggregates, not isolation dimensions.

- Persistent operational objects carry immutable authenticated `tenant_id` and
  `area_id`; project-bound objects carry `project_id`.
- Scope, principal, roles, authority, approvals, policy, evaluation policy, and
  kill-switch state come only from authenticated runtime context.
- Prompts, observations, model responses, memory content, tool output, and
  request payloads may not define or change trusted context.
- Raw memory, cognitive working state, authority, or unapproved learning never
  crosses Tenant or Area boundaries.
- Unknown identity, scope, lineage, state, policy, operation, model version,
  data class, or evaluation state is denied by default.

## Neural and Cognitive Requirements

- Trainable, stateful neural mechanisms must contribute causally to multiple
  cognitive functions. An LLM, retrieval system, workflow, or agent collection
  is not sufficient evidence.
- Perception distinguishes signal, observation, inference, belief, and
  prediction and preserves provenance, time, scope, and uncertainty.
- Attention is capacity-bounded and uses relevance, novelty, prediction error,
  uncertainty, risk, and value.
- The Neural Cognitive Workspace integrates specialized processors without
  becoming an unrestricted shared-memory surface.
- Working, episodic, semantic, and procedural memory retain distinct truth and
  lifecycle semantics.
- World, self, and value models remain versioned, uncertain, and correctable by
  actual feedback.
- Executive control, planning, and action selection are explicit mechanisms,
  not an unmodeled central controller.
- Metacognition can propose stop, ask, seek information, fallback, defer, or
  escalate but cannot override gates.

Every claimed component requires a preregistered baseline, held-out test,
meaningful effect threshold, ablation, resource budget, and failure criterion.

## Protected State and External Effects

Goal, Action, Memory, and Learning/Model Promotion Gates are the only writers of
their protected state.

Keep runtime responsibilities technically separate:

- Planner from Executor.
- Executor from independent effect and goal Verifier.
- Requester from Approver for elevated-risk action.
- Policy author from sole policy activator.
- Learning candidate producer from risky-candidate Promoter.
- Brain self-monitoring from independent Safety Supervisor.
- Brain runtime from kill switch and credential revocation.
- Automatic reconciliation from human incident resolution.

No external effect may occur without a committed Action Intent, authenticated
principal, immutable scope, authority snapshot, policy decision, required
approval, budget reservation, resource claims, valid runtime fence, enabled
kill switch, sandbox policy, and atomic auditability.

Security Floor prohibitions cannot be overridden by configurable policy or
human approval. Approval never creates missing authority. Tool or HTTP success
is not goal success. Only the Goal Transition Gate may write `Achieved`, after
independent verification, complete evidence, and quiescence.

Ambiguous effects become `indeterminate`; never retry blindly or release their
budget and resource claims before authoritative reconciliation.

## Memory, Dreaming, and Continual Learning

- The Memory Transition Gate remains the sole writer of protected memory.
- Provenance, freshness, retention, legal hold, deletion propagation,
  quarantine, rollback, and Area isolation remain mandatory.
- Procedural memory informs cognition but does not authorize execution.
- Dreaming is Area-local offline candidate production. It cannot call tools,
  cause effects, activate candidates, or mutate an active model.
- A stored experience, summary, candidate, or Dreaming artifact is not proof of
  learning.
- The active Brain may never mutate its productive model in place.

Learning produces immutable candidates with full data, source, code, model,
training, and evaluation provenance. Promotion requires held-out improvement,
protected retention, forward and backward transfer, calibration, distribution
shift, poisoning and safety tests, independent approval where required, canary
or shadow activation, stop thresholds, atomic activation, and tested rollback.

Authority, Security Floor, policy, approval rules, evaluation definitions,
kill switches, and promotion rules are never self-modifiable.

## Recognition and Claims

The repository may use the label `Neural Brain Candidate` only after every
non-compensatory recognition gate and independent G8 validation passes. A later
strong result cannot compensate for an unknown or failed mechanism, privacy,
authority, safety, or control gate.

Do not infer consciousness, sentience, human equivalence, biological fidelity,
or production autonomy from architecture or benchmark performance.

## Delivery Stages

Implement strictly in this order:

1. NB-0 Foundation Rebaseline.
2. NB-1 Safe Serial Neural Cognition.
3. NB-2 Perception, Attention, and World Model.
4. NB-3 Differentiated Memory and Retrieval.
5. NB-4 Learning, Consolidation, and Plasticity.
6. NB-5 Closed Perception-Cognition-Action Loop.
7. NB-6 Transfer, Causality, and Metacognition.
8. NB-7 Multi-Goal Executive Control.
9. NB-8 Distributed Operation and Scale.

NB-2 and NB-3 may partially overlap after NB-1 only with independent
dependencies and non-overlapping file ownership. Later-stage features may not
be enabled early or used to compensate for a missing earlier safety or evidence
gate.

## Task Execution

Before implementing a main task:

1. Read its Notion record, subtasks, dependencies, acceptance criteria,
   accepted ADRs, and active issues.
2. Verify repository, branch, worktree, PR, and authoritative local artifacts.
3. Create or update the matching `Issues & Open Questions` record with owner,
   exact local start time, status, next step, and documentation impact.
4. Work on a `codex/` branch from the intended accepted base; preserve unrelated
   user changes and other worktrees.
5. Define each subtask's ID, objective, dependencies, affected components and
   invariants, expected files, tests, acceptance, and documentation impact.
6. Parallelize only independent work with non-overlapping file ownership.
7. Integrate centrally and verify the complete repository state.
8. Record code, test, ADR, migration, documentation, PR, and verification
   evidence in Notion. Mark done only when every criterion is proven.

Use Conventional Commits. Do not push directly to `main`. Never use destructive
Git operations without explicit approval.

## Engineering and Verification

- Dependencies are locked and clean-checkout setup is reproducible.
- PostgreSQL is the authoritative transactional ledger for protected state and
  evidence. Test data uses isolated databases and guarded reset commands.
- Protected tables are not writable through general application roles.
- Every transition has positive, negative, actor/authority, scope, audit,
  failure, concurrency, and recovery tests as applicable.
- Persistent or external effects add crash-boundary, retry, expiry,
  stale-checkpoint, stale-fence, kill-switch, and audit-failure tests.
- Every cognitive claim adds baseline, ablation, transfer, robustness,
  calibration, and end-to-end behavioral evidence.
- Every learning claim adds forgetting, forward/backward transfer, promotion,
  rollback, poisoning, deletion, and resource-budget evidence.
- Do not release while any documented release stop is present.
- Run formatter, linter, strict typing, tests, contract validation, migration
  checks, and relevant environment validation before handoff.

## Documentation and Traceability

Maintain as applicable:

- `README.md` for purpose, maturity, stages, non-goals, and quick start.
- `docs/architecture/` for normative architecture, research basis, evaluation,
  and contracts.
- `docs/adr/` for accepted and superseded decisions.
- `docs/runbooks/` for operations, recovery, shutdown, and incidents.
- `docs/traceability/` for requirement-to-code-to-test-to-evidence mapping.
- `migrations/` for ordered PostgreSQL changes.
- `tests/` for automated safety and capability evidence.
- `tools/` for guarded development, evaluation, and verification commands.

Every completed task must be traceable to its Notion record, repository diff,
relevant ADRs, tests, and verification evidence without making Notion
executable truth.
