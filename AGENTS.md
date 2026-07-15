# Neural Brain Repository Instructions

## Scope

This repository implements Neural Brain, a product- and domain-neutral platform
for a biologically inspired agent system. Product repositories, including
Liquisto, may consume Neural Brain later through explicit integrations; they do
not define this repository's domain model, policies, defaults, or architecture.

The active work area for this repository is `Neural Brain`. Do not import data,
assumptions, rules, or product behavior from another work area unless an
accepted, scoped integration contract explicitly requires it.

## Source Precedence

Resolve conflicts in this order:

1. Repository code, tests, migrations, and executable configuration.
2. This `AGENTS.md` and any more specific descendant `AGENTS.md`.
3. Normative architecture specifications and ADRs in this repository.
4. Accepted records in the Neural Brain Notion `Architecture Decisions` data source.
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
  coordination, decision status, backlog state, and implementation evidence; it
  does not replace repository artifacts.
- Never store secrets, credentials, tokens, private keys, live personal data,
  or `.env` values in the repository, Notion, logs, audit payloads, or examples.

## Scope and Identity Invariants

The fixed hierarchy is:

```text
Brain
└── Tenant
    └── Area
        └── Project
            └── Session
                └── Goal
```

- Every persistent domain object carries immutable `tenant_id` and `area_id`.
- Project-bound objects also carry immutable `project_id`.
- Scope and actor identity come only from authenticated runtime context.
- Prompts, model responses, tool output, and request payloads may not define or
  change principal, scope, roles, authority, approvals, policy, or kill switches.
- Unknown identity, scope, state, policy, tool, operation, or data class is
  denied by default.

## Runtime Separation of Duties

Keep these runtime responsibilities technically separate:

- Planner from executor.
- Executor from independent verifier.
- Requester from approver for elevated-risk actions.
- Policy author from sole policy activator.
- Automatic reconciliation adapter from human incident resolver.
- Memory candidate producer from sole promoter for sensitive or risky candidates.

Development contributors may work across roles, but runtime ports, identities,
permissions, state transitions, and audit evidence must preserve these
boundaries.

## Protected State and External Effects

- Goal, Action, and Memory Transition Gates are the only writers of their
  protected domain state.
- Planner, models, skills, executors, verifiers, guardians, and adapters submit
  typed requests; they do not mutate protected state directly.
- No external effect may occur without a committed action intent, authenticated
  principal, immutable scope, authority snapshot, policy decision, required
  approval, budget reservation, resource claims, valid runtime fence, enabled
  kill switch, and auditability.
- Security-floor prohibitions cannot be overridden by configurable policy or
  human approval. Approval never creates missing authority.
- Tool success, an HTTP status, or a process exit code is not sufficient evidence
  that a goal is achieved.
- Only the Goal Transition Gate may write `Achieved`, after independent
  verification, complete evidence, and quiescence.
- Ambiguous external effects become `indeterminate`; never retry them blindly or
  release associated budget and resource claims prematurely.
- Protected state changes and their audit records commit atomically.

## Delivery Stages

Implement strictly in this order:

1. Foundation (`FND-01`, `FND-02`, `FND-03`, `MS-0`).
2. Stage 1 safe serial cognitive core and `MS-1`.
3. Stage 2 episodic and semantic memory with retrieval and `MS-2`.
4. Stage 3 controlled consolidation, re-evaluation, procedural learning, and `MS-3`.
5. Stage 4 multi-goal scheduling and distributed execution ownership and `MS-4`.

Later-stage features must not be enabled early or used to compensate for a
missing earlier-stage safety mechanism. Stage 1 includes working memory,
checkpoints, observations, and inactive memory candidates only. A generalized
distributed outbox is Stage 4; Stage 1 uses only the minimal persistent dispatch
journal required by its serial executor.

## Task Execution

Before implementing a main task:

1. Read the Notion task, all subtasks, dependencies, acceptance criteria,
   relevant accepted ADRs, and active issues.
2. Verify repository state and authoritative local artifacts.
3. Create or update the matching Neural Brain `Issues & Open Questions` record,
   including owner, exact local start time, status, next step, and documentation
   impact.
4. Work on a `codex/` task branch created from the current `origin/main` unless
   the user specifies another base.
5. Define for each subtask: ID, objective, dependencies, affected components,
   affected invariants, expected files, required tests, acceptance criteria, and
   documentation impact.
6. Parallelize only independent work with non-overlapping file ownership.
7. Integrate centrally and verify the complete repository state.
8. Record code, test, ADR, migration, documentation, and verification evidence
   in Notion. Mark a record done only when every acceptance criterion is proven.

Use Conventional Commits. Do not push directly to `main`. Preserve unrelated
user changes and never use destructive Git operations without explicit approval.

## Engineering and Verification

- Dependencies must be locked and clean-checkout setup must be reproducible.
- PostgreSQL is the authoritative transactional ledger. Development and test
  data must use isolated databases and disposable test data must be reset only
  through an explicit guarded command.
- Protected tables must not be writable through general application roles.
- Every normative transition requires positive, negative, actor/authority,
  scope, audit, failure, and recovery tests.
- Persistent or external effects additionally require crash-boundary,
  concurrency, retry, expiry, stale-checkpoint, stale-fence, kill-switch, and
  audit-failure tests.
- Do not release a stage while any documented release-stop criterion is present.
- Run formatter, linter, type checker, tests, migration checks, and relevant
  environment validation before handoff. State explicitly when a check could
  not run and why.

## Documentation and Traceability

The repository must keep, as applicable:

- `README.md` for purpose, maturity, non-goals, stages, structure, and quick start.
- `docs/architecture/` for normative architecture and contracts.
- `docs/adr/` for accepted architecture decisions.
- `docs/runbooks/` for operational and recovery procedures.
- `docs/traceability/` for requirement-to-code-to-test evidence conventions.
- `migrations/` for ordered, reproducible database changes.
- `tests/` for automated acceptance and safety evidence.
- `tools/` for guarded development and verification commands.

Every completed task must be traceable to its Notion record, repository changes,
relevant ADRs, tests, and verification evidence without making Notion executable
truth.
