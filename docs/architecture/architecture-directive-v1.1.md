# Neural Brain Architecture Directive v1.1

- Status: Superseded by Architecture Directives v2.0 and v3.0 and ADR-015,
  ADR-016, and ADR-017
- Version: 1.1
- Effective date: 2026-07-15
- Work item: FND-02.1 / NB-10
- Repository: `neural-brain`
- Related decisions: ADR-001 through ADR-013

> **Historical record.** This directive is no longer implementation authority.
> ADR-015 corrected the system boundary: Neural Brain is a memory system, not
> an agent runtime. The current normative directive is
> `architecture-directive-v3.0.md`. Version 2.0 remains the intermediate
> memory-system rebaseline in repository history.

## 1. Purpose and applicability

This directive defines the non-negotiable architecture and delivery boundaries
for Neural Brain. It applies to repository code, schemas, migrations,
configuration, runtime components, tools, integrations, deployments, tests, and
release evidence.

Neural Brain is a product- and domain-neutral platform for a biologically
inspired agent system. Product repositories may consume the platform only
through explicit, scoped integration contracts. They do not define this
platform's domain model, policy defaults, security floor, or architecture.

This directive does not claim that the described runtime exists. The repository
is in the Foundation phase. A capability described here is not enabled until its
own stage, implementation task, tests, and release gate are complete.

## 2. Normative language

The terms **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**,
**SHOULD**, **SHOULD NOT**, and **MAY** are normative.

Unknown, missing, expired, stale, conflicting, malformed, unclassified, or
unverifiable security-relevant input or state MUST fail closed. A configurable
policy, model response, tool result, operator request, or approval MUST NOT turn
an unknown condition into authorization.

## 3. Source control and architecture change

Conflicts are resolved in this order:

1. repository code, tests, migrations, and executable configuration;
2. the nearest applicable repository `AGENTS.md`;
3. normative repository architecture specifications and ADRs;
4. accepted Neural Brain Notion Architecture Decisions;
5. Neural Brain Feature Backlog tasks and acceptance criteria;
6. active Issues & Open Questions; and
7. unaccepted Exchange Room discussion.

Exchange Room content is never implementation authorization. When authoritative
sources conflict, work on the affected contract MUST stop, the conflicting
sources MUST be recorded, and an Issue & Open Questions record MUST identify the
unblock condition. The conflict MUST NOT be resolved silently.

Normative technical truth MUST be versioned in this repository. Notion records
lifecycle, coordination, decision status, and implementation evidence; it does
not replace repository contracts. A change to an accepted architecture decision
requires an explicit accepted ADR and synchronized repository evidence.

## 4. Platform boundary and non-goals

Neural Brain exists to add useful autonomy incrementally while keeping
perception, attention, memory, goals, planning, tool execution, verification,
learning, reflection, and operations governable and testable.

Neural Brain is not:

- a product-specific agent or a store for consumer-specific business rules;
- a mechanism for bypassing authenticated identity, scope, authority, policy,
  approvals, budgets, resource controls, audit, or emergency controls;
- a planner, model, prompt, or skill that directly invokes tools;
- a system that treats an adapter result, HTTP status, or process exit code as
  proof of goal achievement;
- an early implementation of distributed execution, unrestricted cross-area
  processing, or uncontrolled learning;
- a general-purpose store for secrets, credentials, live personal data, or
  unbounded memory; or
- a prototype that weakens a mandatory safety mechanism to demonstrate a later
  capability.

## 5. Scope and authenticated runtime context

The fixed scope hierarchy is:

```text
Brain
└── Tenant
    └── Area
        └── Project
            └── Session
                └── Goal
```

Every persistent domain object MUST carry immutable `tenant_id` and `area_id`.
A project-bound object MUST also carry immutable `project_id`. Canonical
identifier encodings and machine-readable scope envelopes are owned by
FND-02.2; this directive does not invent them.

Principal and scope MUST originate only from authenticated runtime context.
Request payloads, prompts, model responses, tool output, integration messages,
and persisted untrusted payloads MUST NOT define or change principal, scope,
roles, authority, approvals, policy, or kill-switch state. Cross-area access is
denied unless a later accepted, explicit, audited handover contract authorizes
the exact transfer. Raw working memory MUST NOT cross an area boundary.

## 6. Runtime component and responsibility boundaries

The target component model consists of:

1. **Perception**, which normalizes user, tool, timer, system, integration, and
   recovery signals.
2. **Attention**, which admits, defers, drops, or escalates normalized signals.
3. **Working Memory**, which holds bounded, goal-specific context and immutable
   checkpoints.
4. **Goal Runtime**, which owns goal origin, authority, budgets, deadlines, and
   resume context through protected contracts.
5. **Planner**, which proposes bounded steps but does not execute tools or write
   protected state.
6. **Policy Engine and Security Floor**, which evaluate scope, authority, risk,
   approvals, privacy, compliance release, and emergency controls.
7. **Goal, Action, and Memory Transition Gates**, which are the only writers of
   their respective protected domain state.
8. **Executor**, which dispatches only committed action intents through
   registered tool adapters.
9. **Independent Verifier**, which evaluates goal success from declared
   criteria and evidence.
10. **Guardian and Reconciler**, which handle deadlines, cancellation, crashes,
    orphaned claims, ambiguous effects, and startup reconciliation.
11. **PostgreSQL**, which is the authoritative transactional state and audit
    ledger.

The following runtime responsibilities MUST remain technically separate:

- planner and executor;
- executor and independent verifier;
- requester and approver for elevated-risk actions;
- policy author and sole policy activator;
- automatic reconciliation adapter and human incident resolver; and
- memory-candidate producer and sole promoter for sensitive or risky
  candidates.

A development contributor MAY implement more than one responsibility, but
runtime ports, identities, permissions, state transitions, and audit evidence
MUST preserve the separation.

## 7. Trust boundaries and runtime validation

Every untrusted runtime payload MUST pass this boundary:

```text
Untrusted input
-> runtime schema validation
-> Trust Envelope
-> typed domain object
-> transition gate or typed component port
```

Stage 1 uses Pydantic v2 for runtime schema validation. Validation proves only
that a payload conforms to a declared schema. It does not authenticate a
principal, derive scope, grant authority, approve an action, select policy, or
change a kill switch.

Trust Envelopes MUST retain provenance and integrity-relevant metadata needed by
later policy, transition, evidence, and audit checks. Their exact identifiers,
correlation, causation, evidence, and artifact schemas are owned by FND-02.2.

## 8. Security floor, policy, approval, and kill switches

The Security Floor is implemented in code and is non-overridable. Configurable
policy MUST operate inside it. Human approval MUST NOT override a Security Floor
prohibition, create missing authority, repair a scope mismatch, bypass audit, or
re-enable a kill switch.

Policy parameters and decisions MUST be versioned, schema-validated, bound to
the evaluated inputs and policy digest, and constrained by explicit validity and
expiry. A stale or mismatched decision is invalid. Unknown identity, scope,
state, policy, tool, operation, risk class, data class, intended purpose, or
compliance state is denied by default.

Kill switches exist at global, tool, and goal levels with `enabled`, `drain`,
and `disabled` semantics. They MUST be checked before action preparation,
commit, and dispatch. `drain` blocks new prepare and commit work while permitting
settlement and reconciliation. Agent, planner, model, tool, skill, and adapter
paths MUST NOT re-enable a switch. The exact persisted representation of a
global control versus tenant- and area-scoped domain objects requires a separate
resolved contract and is not invented by this directive.

## 9. Protected state and transition contracts

Goal, Action, and Memory Transition Gates are the only writers of their
protected state. Planner, models, skills, executors, verifiers, guardians,
reconcilers, and adapters MAY submit typed requests; they MUST NOT mutate
protected tables or state directly. Database privileges MUST make bypass through
general application roles impossible.

Every normative transition MUST declare its authorized actors, source and
target conditions, guards, authority requirements, evidence, side effects,
audit event, timeout behavior, and recovery behavior. Unknown states and
undeclared transitions are denied.

Goal and Action enums, exact edges, and machine-readable transition structures
are owned by FND-02.3. The Goal-State/Intent-Purpose guard matrix and reusable
quiescence predicate are owned by FND-02.4. This directive establishes their
mandatory semantics but does not pre-empt those definitions.

Blocking, cancellation, termination, and recovery MUST preserve enough explicit
state to support `blocked_from_state`, `termination_disposition`, and resolution
of `indeterminate` actions without inference from logs or model output.

## 10. Goal completion, verification, and quiescence

Only the Goal Transition Gate MAY write `Achieved`. It MUST do so only after a
separate verifier decision, complete evidence for machine-readable success
criteria, and quiescence. Executor success, planner self-assessment, adapter
success, HTTP status, and process exit code are insufficient evidence.

When independence is required, the verifier runtime identity and permissions
MUST differ from the executor's. A blocked verification flow resumes in
verification context and MUST NOT silently become an execution intent.

`Suspended` and every terminal goal state require quiescence. At minimum, a goal
is not quiescent while it has unresolved action or verification intents,
execution attempts, approval claims, budget reservations, resource claims,
locks, reconciliation work, cancellation work, or possible external effects.
The exact reusable predicate is defined by FND-02.4.

## 11. Action authorization and four-resource transaction

No external effect may occur without all of the following:

- a committed action intent;
- an authenticated principal and immutable scope;
- a current authority snapshot;
- a current policy decision inside the Security Floor;
- any required non-replayed approval;
- a budget reservation;
- required resource claims;
- a valid runtime fencing token;
- permissive kill-switch state; and
- atomic auditability.

Action preparation uses a two-phase contract. It MUST first validate authority,
approval, budget, and resource availability together. Commit MUST revalidate the
complete contract and atomically create all required claims, or create none.
Partial claims and unaccounted reservations are prohibited.

Approval is an independent claim over a specific request and context. It MUST be
bound against replay, scope mismatch, payload substitution, expiry, and reuse.
The approval mechanism MUST NOT be treated as authority.

## 12. Dispatch and external-effect contract

Stage 1 uses a single serial executor. Before an adapter is invoked, the system
MUST persist the committed action intent, minimal local dispatch-journal record,
execution grant, and monotonic execution attempt. Every registered operation
MUST declare its reconciliation and compensation capabilities.

Stage 1 does not implement a generalized distributed outbox, multi-consumer
ownership, or replicated dispatch coordination. Those are Stage 4 capabilities.

An external effect that cannot be proven absent or complete becomes
`indeterminate`. A non-idempotent or otherwise ambiguous operation MUST NOT be
retried automatically. Associated budget, claims, and locks MUST NOT be released
while the effect may still exist. Non-reconcilable ambiguity requires the
authorized human incident-resolution path.

## 13. PostgreSQL, transactions, and audit

PostgreSQL is the authoritative transactional ledger for protected state,
claims, attempts, audit, and recovery evidence. Protected state mutation and its
audit record MUST commit in one transaction. An audit failure MUST fail the
protected transition.

Stage 1 uses synchronous Psycopg 3 connections with `autocommit=True` and
explicit `connection.transaction()` blocks. Transaction boundaries MUST be
visible in code. A database transaction MUST NOT remain open across model, tool,
network, operator, or other unbounded external calls.

Database roles, row-level isolation, migration ordering, backup, restore, and
reconciliation are release-critical controls. General application roles MUST
not have direct write access to protected tables.

## 14. Crash consistency, cancellation, reconciliation, and readiness

Every persistent transition and external-effect boundary MUST define recovery
for a crash before and after its commit point. Recovery MUST use durable state
and declared contracts, not model inference or best-effort log interpretation.

Cancellation is a stateful, auditable workflow. It MUST NOT report completion or
release claims until quiescence and external-effect disposition are established.
An unresolved effect remains `indeterminate`.

Startup and restore MUST run reconciliation before the service reports
`ready=true`. Reconciliation MUST identify incomplete transitions, orphaned or
expired claims, stale fences, unfinished attempts, pending settlements, and
ambiguous effects. Restore evidence is incomplete until this reconciliation has
been demonstrated.

## 15. Memory architecture and stage separation

Working context, observations, episodes, semantic knowledge, and learned
procedures have different truth, provenance, retention, and safety semantics.
Memory candidates are operational work items; they are not a fifth memory type.
Only the Memory Transition Gate may write protected memory state.

Stage 1 provides only bounded Working Memory, immutable checkpoints,
Observations, and inactive Memory Candidates. Stage 1 MUST NOT provide a
long-term-memory promotion path, and configuration MUST NOT enable one.

Stage 2 adds a Source Registry, immutable episodic memory, semantic claims and
assessments, scope-safe retrieval, freshness handling, curated imports, and
dependency-aware deletion. It does not enable autonomous consolidation or
procedural learning.

Stage 3 alone enables controlled candidate evaluation, semantic consolidation,
re-evaluation, procedural evaluation and promotion, quarantine, and authorized
rollback. Sensitive or risky candidates require separation between producer and
sole promoter.

The machine-readable Stage Capability Matrix is owned by FND-02.5. Stage 1 MUST
reject every unimplemented Stage 2 through Stage 4 memory or runtime operation by
contract, not merely by absence of a user-interface option.

## 16. Privacy and data governance

Every data object and processing path MUST have a declared data classification,
purpose, scope, provenance, retention rule, and deletion responsibility before
use. Personal data MUST be minimized and purpose-bound. Secrets and credentials
MUST NOT be stored in prompts, model context, memory, logs, audit payloads,
Notion, examples, or ordinary repository documentation.

"Immutable" means immutable until an authorized retention, lawful-deletion, or
anonymization workflow applies. Corrections append evidence rather than silently
rewriting history. A lawful deletion or anonymization workflow MUST cover primary
payloads, embeddings, indexes, caches, derived artifacts, and other
reconstructive copies. It MUST be resumable and audited while retaining only
non-reconstructive evidence that the governed operation occurred.

Legal hold, applicable rights, and binding retention duties MUST be evaluated by
the authorized governance workflow. This directive does not make a legal
applicability determination for a deployment.

## 17. Intended-purpose contract

The platform's neutral purpose does not authorize any productive use case.
Before productive activation, each use case MUST have a stable, versioned purpose
contract scoped to its tenant and area and, when project-bound, its project. The
contract semantics MUST cover intended users, operating context, expected
benefit, permitted capabilities and external effects, affected people and data,
limitations, human oversight, and explicit non-goals.

A use case outside that purpose is unauthorized. A change to purpose, scope,
data, model, supplier, tool capability, deployment context, or branding MUST
invalidate or trigger reassessment of dependent regulatory and release evidence.
The exact machine-readable purpose schema is owned by the later regulatory
governance work; this directive does not invent it.

## 18. Prohibited and unsupported use

A use prohibited by the Security Floor, applicable binding law, an accepted
architecture contract, or the current purpose contract MUST be denied
unconditionally. Neither policy configuration nor human approval can authorize
such a use.

An unsupported, sensitive, high-impact, or unclassified use MUST remain disabled
until the applicable classification, authority, safeguards, independent review,
and scoped compliance-release evidence are complete. Classification and approval
are necessary controls where applicable; they are never a mechanism for
overriding a prohibition.

The versioned prohibited- and unsupported-use catalog, classification rules, and
review authorities belong to follow-on regulatory governance tasks. Absence of
that implemented catalog denies productive activation; it is not permission.

## 19. Regulatory applicability and role contract

Regulatory applicability and operator roles depend on the concrete deployment,
intended purpose, data flows, affected people, branding, suppliers, integrations,
and allocation of control. Neural Brain MUST NOT infer a legal role from its
neutral repository identity or assign one by default.

Every productive use case MUST have current, versioned evidence of applicable
regulatory findings, role determinations, accountable ownership, obligations,
review date, and reassessment triggers, or an explicit evidence-backed
non-applicability determination. Actual role assignments, legal conclusions,
review authorities, and evidence schemas are owned by the follow-on regulatory
governance tasks and require qualified review. This directive does not invent or
approve them.

## 20. Per-scope compliance-release contract

This directive does not authorize productive activation. Until the later
compliance-release mechanism is implemented and verified, productive tenants,
areas, personal-data processing, and real mutating tools MUST remain disabled.

Once that mechanism exists, productive activation MUST require current
compliance-release evidence bound to the exact `tenant_id` and `area_id` and,
when project-bound, `project_id` and intended use. Its semantics MUST bind the
current purpose, regulatory applicability and role findings, prohibited-use and
risk classification, required controls, supporting evidence versions,
accountable decision, validity, reassessment triggers, and revocation state.

Missing, incomplete, expired, revoked, stale, or scope-mismatched release
evidence denies activation. A compliance release does not create authority,
replace an operational approval, waive the Security Floor, or authorize a later
delivery-stage capability. Exact record schemas, decision authorities,
signature or verification mechanisms, and lifecycle state machines are owned by
follow-on regulatory governance tasks and are not decided here.

## 21. Delivery stages and capability boundaries

Stages MUST be implemented and accepted in this order:

| Stage | Required scope | Explicit boundary |
| --- | --- | --- |
| Foundation / MS-0 | FND-01 repository and governance foundation; FND-02 normative architecture and contracts; FND-03 engineering quality and CI baseline | No productive agent runtime or external mutating effect is authorized. |
| Stage 1 / MS-1 | Authenticated identity and scope; Security Floor, policy, kill switches; PostgreSQL and audit; Goal Gate; perception, attention, Working Memory and checkpoints; authority and approvals; budget and claims; Action Gate and minimal dispatch journal; serial executor, cancellation, guardian and reconciliation; planner, verifier and serial cognitive loop; privacy foundation; deterministic verification; operations and release evidence | No Stage 2 or Stage 3 memory capability, generalized outbox, multi-goal scheduler, distributed ownership, or cross-area handover. |
| Stage 2 / MS-2 | Source Registry, episodic memory, semantic claims and assessments, retrieval, freshness, retention and dependency-aware deletion | No autonomous consolidation, candidate promotion, procedural learning, or distributed execution. |
| Stage 3 / MS-3 | Controlled semantic consolidation and re-evaluation; procedural learning with evaluation, quarantine, authorized promotion and rollback | No multi-goal scheduling or distributed ownership before Stage 4. |
| Stage 4 / MS-4 | Multi-goal scheduling, fairness, preemption, explicit cross-area handover, distributed executor ownership, hierarchical locks, deadlock handling, distributed reconciliation and disaster recovery | Raw Working Memory never crosses area boundaries; all earlier security and compliance controls remain mandatory. |

A later stage MUST NOT replace or weaken a missing safety function from an
earlier stage. No Stage 2 through Stage 4 feature may be enabled early through
configuration. FND-02.5 owns the exact machine-readable capability matrix.

## 22. Verification obligations

Every normative transition requires all of the following automated evidence:

- a positive test;
- a negative test;
- an actor and authority test;
- a scope test;
- an audit test; and
- failure and recovery tests.

Persistent transitions and external effects additionally require tests for:

- crash before the transition;
- crash after the transition;
- a concurrent request;
- a repeated request;
- an expired decision, claim, or approval;
- a stale checkpoint;
- a stale fencing token;
- kill-switch activation; and
- audit failure.

Verification evidence MUST identify the exact repository revision and commands
executed. A required check that was not executed is not passing evidence.

## 23. Release-stop criteria

Implementation or release MUST stop when any of the following is true:

1. A forbidden transition is possible.
2. Protected state can be mutated outside its transition gate.
3. Scope or principal can be taken from untrusted input.
4. `Achieved` is reachable without independent evidence.
5. An external action can execute without complete authorization.
6. Approval replay is possible.
7. Budget can be charged twice or become negative.
8. Locks can be released while an external effect may remain unresolved.
9. A non-idempotent ambiguous action can be retried automatically.
10. Audit and the protected domain transition are not atomic.
11. Startup or restore can report `ready=true` before reconciliation.
12. A kill switch can be bypassed.
13. A critical runbook is missing.
14. Backup or restore has not been proven.
15. A stage gate is incomplete.

These criteria are cumulative. A later approval, policy, stage, or operational
workaround MUST NOT waive one.

## 24. Engineering runtime and inference boundary

ADR-013 defines CPython 3.14 with the standard GIL-enabled runtime, uv, Ruff,
strict mypy, pytest, Hypothesis, Pydantic v2, and synchronous Psycopg 3. Its
runtime validation and explicit transaction rules are part of this directive.

ADR-014 selects local Ollama as the only approved inference provider behind the
provider-neutral internal `InferencePort`. OpenAI APIs and SDKs, external model
APIs, provider or model switching, API-key fallback, and automatic cloud
fallback are prohibited. Inference fails closed unless the exact approved local
endpoint, model identifier, version, digest, timeout, budget, minimized-logging
policy, and egress controls are present and verified.

ADR-014 authorizes only that architectural adapter boundary. Foundation does
not implement or enable a runtime adapter, select concrete deployment values,
or prove inference readiness. Those capabilities require their owning Stage 1
implementation tasks and tests.

## 25. Traceability and completion

Every completed requirement MUST have an evidence chain:

```text
Notion task and acceptance criterion
-> normative directive and relevant ADR
-> code, schema, migration, or configuration
-> automated tests and verification commands
-> immutable repository revision and review evidence
```

Documentation-only assertions do not prove runtime enforcement. Conversely,
Notion status does not replace repository evidence. A task MUST NOT be marked
complete while a required acceptance criterion, test, migration check,
documentation update, release stop, or known critical deviation remains open.

## Appendix A: ADR-to-directive mapping

| ADR | Directive coverage |
| --- | --- |
| ADR-001 — Neutral platform and dedicated repository | Sections 1, 4 |
| ADR-002 — Immutable tenant and area scope from foundation | Section 5 |
| ADR-003 — PostgreSQL as authoritative transactional ledger | Sections 13, 14 |
| ADR-004 — Three transition gates are the only protected writers | Sections 6, 9 |
| ADR-005 — Non-overridable security floor plus versioned policy parameters | Section 8 |
| ADR-006 — Three-level kill switch with drain semantics | Sections 8, 23 |
| ADR-007 — Explicit Goal and Action state contracts | Sections 9, 10 |
| ADR-008 — Four-resource action transaction | Section 11 |
| ADR-009 — Persist-before-dispatch with attempts and reconciliation strategy | Sections 12, 14, 21 |
| ADR-010 — Stage-separated memory model | Sections 15, 21 |
| ADR-011 — Independent verification before goal completion | Section 10 |
| ADR-012 — Immutable until lawful deletion | Section 16 |
| ADR-013 — CPython 3.14 GIL runtime and engineering toolchain | Sections 7, 13, 24 |
| ADR-014 — Local Ollama-only inference | Sections 7, 15, 24 |

## Appendix B: Follow-on contract ownership

This directive intentionally leaves exact machine-readable forms to their
owning tasks:

- FND-02.2: identifiers, immutable scope context, correlation, causation,
  evidence, Trust Envelopes, and artifact envelopes;
- FND-02.3: Goal and Action states and default-deny transition tables;
- FND-02.4: Goal-State/Intent-Purpose guards and normative quiescence;
- FND-02.5: Stage Capability Matrix;
- FND-02.6: threat model and trust-boundary diagram, materialized in
  `docs/architecture/threat-model.md`;
- FND-02.7: repository synchronization of accepted ADRs, with ADR-001 through
  ADR-013 as the historical FND-02 baseline and ADR-014 as an additional
  accepted decision; and
- follow-on regulatory governance tasks: intended-purpose schemas, prohibited-
  and unsupported-use catalog, applicability and role records, compliance
  release, accountable review, and reassessment mechanisms.

Until each follow-on contract is accepted, implemented, and verified, its
dependent productive capability remains denied. Deferral is not an implicit
allow rule.

## Appendix C: Non-negotiable invariant index

1. Scope and principal originate only from authenticated runtime context.
2. Unknown security-relevant state is denied.
3. Only the three transition gates write protected state.
4. Planner, model, prompt, and skill never dispatch tools.
5. External effects require the complete committed authorization contract.
6. Approval never creates authority or overrides the Security Floor.
7. Protected mutation and audit commit atomically.
8. `Achieved` requires independent verification, evidence, and quiescence.
9. Suspension and terminal states require quiescence.
10. Ambiguous effects become `indeterminate` and are not blindly retried.
11. Claims remain held while an effect may be unresolved.
12. Stage 1 is serial and uses only its minimal dispatch journal.
13. Stage 1 has no long-term-memory promotion path.
14. Stage 2 has no autonomous consolidation or procedural learning.
15. Stage 3 alone enables controlled promotion and procedural learning.
16. Cross-area processing requires a later explicit audited handover; raw
    Working Memory never crosses an area.
17. Evidence is immutable only until lawful deletion or anonymization.
18. Productive activation requires current, scope-matched compliance-release
    evidence once the later mechanism exists; absence of the mechanism denies
    activation.
19. Later stages cannot replace missing earlier-stage safety controls.
