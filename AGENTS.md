# Neural Brain Repository Instructions

## Scope

This repository implements Neural Brain, a product- and domain-neutral memory
system. External agents and other authorized systems may consume Neural Brain
through explicit integrations; Neural Brain itself is not an agent. It does not
own goals, plan work, execute tools, or operate autonomously.

Product repositories, including Liquisto, do not define this repository's
memory model, policies, defaults, or architecture. The active work area is
`Neural Brain`. Do not import data, assumptions, rules, or product behavior from
another work area unless an accepted, scoped integration contract requires it.

## Source Precedence

Resolve conflicts in this order:

1. Repository code, tests, migrations, and executable configuration.
2. This `AGENTS.md` and any more specific descendant `AGENTS.md`.
3. Normative architecture specifications and ADRs in this repository.
4. Accepted Neural Brain Notion `Architecture Decisions` records.
5. Neural Brain Notion `Feature Backlog` tasks and acceptance criteria.
6. Active Neural Brain Notion `Issues & Open Questions` records.
7. Discussed but unaccepted Neural Brain Notion `Exchange Room` content.

Exchange Room content is never implementation authorization. If authoritative
sources conflict, stop the affected implementation, document the exact sources,
create or update an `Issues & Open Questions` record, and do not invent a
resolution.

## Language and Durable Artifacts

- Write code, identifiers, docstrings, commit messages, tests, technical
  documentation, ADRs, schemas, migrations, and runbooks in English.
- Use German only for explicitly German user-facing behavior.
- Keep normative technical truth versioned in this repository. Notion records
  coordination and evidence; it does not replace repository artifacts.
- Never store secrets, credentials, tokens, private keys, live personal data,
  or `.env` values in the repository, Notion, logs, audit payloads, or examples.

## Brain and Consumer Boundary

Neural Brain may ingest observations, maintain bounded working context, store
episodic and semantic memory, retrieve memory, assess freshness, produce
inactive learning candidates, and perform controlled consolidation,
re-evaluation, quarantine, rollback, retention, and deletion.

External consumers retain responsibility for goals, planning, tool execution,
external effects, operational approvals, and autonomous behavior. A model,
agent, skill, tool, or integration submits typed requests; it does not gain
direct write access to protected memory state or authority to promote memory.
Local inference is a bounded internal dependency and may not perform external
actions, establish scope, or bypass deterministic gates.

## Scope, Provenance, and Identity Invariants

- Brain, Tenant, Area, Project, and Session are typed hierarchy catalog objects.
  Brain is a persisted singleton. Tenant carries `brain_id` and `tenant_id` but
  no `area_id`; Area and its descendants carry their required Tenant/Area parent
  lineage. Brain ancestry below Tenant is resolved transitively through Tenant.
- Operational memory always carries authenticated immutable `tenant_id` and
  `area_id`. Project- and session-bound memory also carries every applicable
  ancestor identifier. No sentinel Area, nullable required identifier, or
  implicit root scope is authorized.
- `Area` separates distinct memory contexts.
- Project and session identifiers narrow provenance and retrieval context when
  the record is bound to those levels.
- External task or goal identifiers are optional, non-authoritative correlation
  metadata. They are not Brain-owned scope and cannot confer authority or drive
  memory transitions.
- Persistent memory objects carry immutable authenticated scope appropriate to
  their level and retain origin provenance through derivation.
- Scope and actor identity come only from authenticated runtime context.
- Prompts, model responses, agent requests, tool output, and request payloads
  may not define or change principal, scope, roles, authority, policy,
  retention, legal hold, or activation status.
- Unknown identity, scope, source, state, policy, data class, freshness, or
  promotion status is denied by default.

Concrete memory does not silently cross area boundaries. Reusable knowledge
requires an explicit, auditable generalization and promotion contract that
preserves origin provenance and enforces privacy, sensitivity, and purpose
constraints.

## Runtime Separation of Duties

Keep these runtime responsibilities technically separate:

- Memory producer from protected-state transition gate.
- Retrieval consumer from source and policy assessment.
- Memory candidate producer from sole promoter for sensitive or risky
  candidates.
- Policy author from sole policy activator.
- Requester from approver where elevated-risk memory access or promotion
  requires approval.
- Automated retention or reconciliation logic from human incident resolution.

Development contributors may work across roles, but runtime ports, identities,
permissions, transitions, and audit evidence must preserve these boundaries.

## Protected Memory State

- The Memory Transition Gate is the only writer of protected memory state.
- Producers, consumers, models, and integrations submit validated typed
  requests; they do not mutate protected state directly.
- A memory mutation requires authenticated principal, immutable scope, source
  provenance, policy decision, applicable purpose and data-class controls, and
  atomic auditability.
- Security-floor prohibitions cannot be overridden by configurable policy or
  human approval. Approval never creates missing authority.
- Inactive candidates do not affect retrieval or behavior until their required
  independent assessment and promotion complete.
- Retrieval preserves scope, source, freshness, sensitivity, and policy
  constraints; relevance alone never grants access.
- Retention, legal hold, deletion, quarantine, rollback, and derived-artifact
  cleanup are protected transitions.
- Protected memory changes and their audit records commit atomically.

## Governed Dreaming

- Dreaming is an Area-local offline memory-analysis process, not an autonomous
  agent loop.
- A run requires authenticated Area scope, an inactive Area, an exclusive
  Dreaming lease, and an immutable versioned snapshot.
- Stage 1 Dreaming is dry-run only. It may produce reports, findings, and
  inactive candidates, but cannot activate a successor memory version or change
  an active pointer.
- Dreaming workers and model output never mutate protected memory directly,
  approve their own candidates, or mix raw memory across Areas.
- Stage 3 promotion requires independent validation, a separate Memory Gate
  transition, preserved provenance, and a rollback target.

## Delivery Stages

Implement strictly in this order:

1. Foundation (`FND-01`, `FND-02`, `FND-03`, `MS-0`).
2. Stage 1 secure scoped memory kernel and `MS-1`.
3. Stage 2 durable episodic and semantic memory with retrieval and `MS-2`.
4. Stage 3 controlled consolidation, re-evaluation, and procedural memory and
   `MS-3`.
5. Stage 4 governed cross-area abstraction, handover, and distributed memory
   scale and `MS-4`.

Later-stage features must not be enabled early or used to compensate for a
missing earlier-stage safety mechanism. Stage 1 establishes authenticated
consumers and producers, source provenance, ingestion normalization and
salience, working/context memory, observations, checkpoints, inactive
candidates, the Memory Gate, audit and RLS, retention and deletion foundations,
Dreaming dry runs, and backup/restore. Stage 2 adds durable episodic and
semantic memory, claims, assessments, ranked retrieval, freshness, and inactive
Dreaming analysis. Stage 3 owns controlled Dreaming consolidation,
re-evaluation, procedural memory, quarantine, promotion, and rollback.
Stage 4 owns governed cross-area abstraction and handover plus scalable
distributed memory and index reconciliation.

## Task Execution

Before implementing a main task:

1. Read the Notion task, all subtasks, dependencies, acceptance criteria,
   relevant accepted ADRs, and active issues.
2. Verify repository state and authoritative local artifacts.
3. Create or update the matching Neural Brain `Issues & Open Questions` record,
   including owner, exact local start time, status, next step, and documentation
   impact.
4. Work on a `codex/` task branch created from current `origin/main` unless the
   user specifies another base.
5. Define for each subtask: ID, objective, dependencies, affected components,
   affected invariants, expected files, required tests, acceptance criteria,
   and documentation impact.
6. Parallelize only independent work with non-overlapping file ownership.
7. Integrate centrally and verify the complete repository state.
8. Record code, test, ADR, migration, documentation, and verification evidence
   in Notion. Mark a record done only when every acceptance criterion is proven.

Use Conventional Commits. Do not push directly to `main`. Preserve unrelated
user changes and never use destructive Git operations without explicit
approval.

## Engineering and Verification

- Dependencies must be locked and clean-checkout setup must be reproducible.
- PostgreSQL is the authoritative transactional memory ledger. Development and
  test data use isolated databases; reset disposable data only through an
  explicit guarded command.
- Protected tables must not be writable through general application roles.
- Every normative memory transition requires positive, negative,
  actor/authority, scope, provenance, audit, failure, and recovery tests.
- Persistent transformations additionally require crash-boundary,
  concurrency, retry, expiry, stale-source, retention, deletion-propagation,
  quarantine, and audit-failure tests as applicable.
- Do not release a stage while any documented release-stop criterion is
  present.
- Run formatter, linter, type checker, tests, migration checks, and relevant
  environment validation before handoff. State explicitly when a check could
  not run and why.

## Documentation and Traceability

The repository keeps, as applicable:

- `README.md` for purpose, maturity, non-goals, stages, and consumer boundary.
- `docs/architecture/` for normative memory architecture and contracts.
- `docs/adr/` for accepted architecture decisions.
- `docs/runbooks/` for operational and recovery procedures.
- `docs/traceability/` for requirement-to-code-to-test evidence conventions.
- `migrations/` for ordered, reproducible database changes.
- `tests/` for automated acceptance, isolation, and safety evidence.
- `tools/` for guarded development and verification commands.

Every completed task must be traceable to its Notion record, repository
changes, relevant ADRs, tests, and verification evidence without making Notion
executable truth.
