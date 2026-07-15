# Neural Brain Architecture Directive v2.0

- Status: Normative memory-system baseline
- Version: 2.0
- Effective date: 2026-07-15
- Work item: Memory-system rebaseline
- Repository: `neural-brain`
- Governing decision: ADR-015
- Supersedes: Architecture Directive v1.1

## 1. Purpose and applicability

Neural Brain is a product- and domain-neutral memory system. It provides
governed memory to authenticated people, agents, applications, and other
authorized consumers. It is not an agent and MUST NOT own goals, plans, action
intents, tools, execution, completion decisions, or autonomy.

This directive applies to repository code, schemas, migrations, configuration,
runtime components, integrations, deployments, tests, and release evidence.
Capabilities described here are not enabled until their delivery stage,
implementation task, tests, and release gate are complete.

The terms **MUST**, **MUST NOT**, **REQUIRED**, **SHOULD**, **SHOULD NOT**, and
**MAY** are normative. Unknown, missing, expired, stale, conflicting, malformed,
unclassified, or unverifiable security-relevant state MUST fail closed.

## 2. System boundary

Neural Brain owns:

- authenticated and scoped memory access;
- validated memory intake and immutable provenance;
- observations, Working Memory, and checkpoints;
- inactive memory candidates;
- episodic memory, semantic claims, assessments, and retrieval;
- freshness, consolidation, controlled promotion, procedural memory, quarantine,
  rollback, retention, deletion, and audit evidence.

External consumers own their goals, planning, actions, tool use, execution,
verification, completion, and autonomy. Neural Brain MUST NOT expose an internal
or public path that performs those responsibilities on a consumer's behalf.

Memory returned to a consumer is contextual evidence. It MUST NOT be treated as
authenticated identity, scope, authority, policy, approval, executable
instruction, or proof of an external outcome.

## 3. Scope and authenticated context

The current hierarchy is:

```text
Brain
└── Tenant
    └── Area
        └── Project
            └── Session
```

Memory records carry immutable scope derived only from authenticated runtime
context. Request payloads, prompts, model output, retrieved content, connector
data, and consumer-provided identifiers MUST NOT determine or alter actor or
scope.

Every operational memory object MUST carry immutable `tenant_id` and `area_id`.
Project-bound objects also carry immutable `project_id`. Scope compatibility is
checked at every read, write, retrieval, promotion, deletion, and audit
boundary.

The persistent Tenant root conflicts with the literal requirement that every
persistent domain object carry both `tenant_id` and `area_id`: an Area is below
Tenant. ADR-015 does not resolve this conflict. Tenant-root persistence and all
dependent implementation remain blocked until a separate accepted decision
defines the root representation. Synthetic or sentinel Areas and silent
nullability exceptions are prohibited.

## 4. Trust, validation, and consumer ports

External consumers use authenticated, scoped, typed ports. Every untrusted
payload follows this boundary:

```text
untrusted input
-> runtime schema validation
-> provenance and trust envelope
-> typed memory request
-> memory policy and transition boundary
```

Schema validation does not establish identity, scope, roles, authority, policy,
or approval. A model response or retrieved memory remains untrusted data until
validated for its declared use. Secrets and credentials MUST NOT enter memory,
logs, examples, embeddings, indexes, or audit payloads.

## 5. Memory lifecycle and protected state

Memory state changes occur only through the owning typed memory boundary. That
boundary validates authenticated actor and scope, provenance, classification,
purpose, policy, retention, current state, and permitted transition before a
mutation commits.

Direct mutation of protected memory state is prohibited. PostgreSQL roles,
constraints, and transaction boundaries MUST enforce the same restriction as
application ports. A protected mutation and its audit evidence commit
atomically.

Candidates are proposals, not accepted memory. They remain inactive and
non-retrievable until their delivery stage provides an authorized promotion
path. Promotion MUST preserve provenance, assessment, decision evidence, and a
rollback target. Quarantined or expired memory is excluded from normal
retrieval.

## 6. Memory forms and retrieval

- Working Memory is bounded, session-oriented context and is not durable truth.
- Observations preserve source and capture context without claiming truth.
- Episodic Memory preserves scoped events and provenance.
- Semantic Memory stores claims with source references, assessments, freshness,
  and supersession relationships.
- Procedural Memory stores evaluated reusable methods, not executable authority.

Retrieval MUST be scope-checked, purpose-bound, minimized, provenance-preserving,
and freshness-aware. Consumers MUST be able to distinguish observations,
claims, assessments, procedures, and stale or contested material. Retrieval
ranking MUST NOT erase origin, uncertainty, sensitivity, or validity status.

Raw Working Memory MUST NOT cross Area boundaries. Cross-area use requires the
Stage 4 transfer contract and MUST provide only an authorized minimized
representation with retained provenance.

## 7. Security and governance

A non-overridable security floor protects identity, scope isolation, data
classification, provenance, retention, deletion, promotion, quarantine, and
cross-area boundaries. Configurable policy is versioned, schema-validated, and
bounded by that floor. Approval cannot create missing authority or override a
prohibition.

Access is denied by default. Policy decisions bind the authenticated consumer,
immutable scope, declared purpose, operation, data class, policy version and
digest, expiry, and trace context. Memory MUST NOT be used to infer additional
permissions or widen a consumer request.

## 8. PostgreSQL, audit, and crash consistency

PostgreSQL is authoritative for transactional memory state and its audit
ledger. Stage 1 uses synchronous Psycopg with `autocommit=True` and explicit
`connection.transaction()` blocks. No transaction may remain open across model,
network, connector, or other unbounded calls.

Migrations are ordered and reproducible. Recovery, startup, and restore MUST
reconcile incomplete memory transitions, indexing work, deletion work, and
promotion or rollback work before reporting the affected capability ready.
Audit failure aborts the protected mutation.

## 9. Privacy, retention, and deletion

Memory is purpose-bound, classified, minimized, access-controlled, and assigned
retention behavior. Immutable means protected from silent rewriting until an
authorized deletion or anonymization path applies; it does not mean indefinite
storage.

Corrections append evidence rather than silently rewriting history. Authorized
deletion or anonymization covers payloads, embeddings, indexes, caches,
summaries, derived claims, and other derivatives. The process is resumable and
audited while retained deletion evidence remains non-reconstructive. Legal hold
and applicable regulatory obligations are enforced per scope and data class.

## 10. Local inference boundary

Inference is an optional memory-processing dependency, not an agent runtime.
The only approved adapter is local Ollama under ADR-014. OpenAI APIs and SDKs,
other cloud providers, arbitrary endpoints, and automatic cloud fallback are
prohibited.

Model output cannot write memory directly. A validated result MAY produce a
typed memory request with authenticated scope, provenance, producer identity,
classification, and purpose. Inference configuration, endpoint, exact model
identity, budget, and logging policy come only from trusted deployment state.

## 11. Delivery stages

| Stage | Memory capability | Explicit boundary |
| --- | --- | --- |
| Foundation / MS-0 | Repository governance, normative memory contracts, engineering quality, and CI | No productive memory runtime is authorized. |
| Stage 1 / MS-1 | Authenticated scope, governed intake, observations, Working Memory, checkpoints, inactive candidates, audit, retention foundation, deterministic verification, backup, restore, and operations evidence | No episodic or semantic retrieval, promotion, procedural memory, or cross-area transfer. |
| Stage 2 / MS-2 | Source registry, episodic memory, semantic claims and assessments, retrieval, freshness, retention, and dependency-aware deletion | No autonomous consolidation, candidate promotion, or procedural memory. |
| Stage 3 / MS-3 | Controlled consolidation, re-evaluation, procedural memory, evaluation, quarantine, authorized promotion, and rollback | No implicit or raw cross-area memory use. |
| Stage 4 / MS-4 | Explicit audited cross-area knowledge transfer and scalable memory coordination | No agent planning, action execution, tools, goal completion, or autonomy. |

Later-stage schemas and operations MUST NOT be enabled early or used to replace
a missing earlier-stage control.

## 12. Verification and release stops

Normative memory transitions require positive, negative, actor and authority,
scope, audit, failure, and recovery tests. Persistent work additionally
requires crash-boundary, concurrency, retry, expiry, stale-context, policy,
retention, deletion, and audit-failure tests as applicable.

Release MUST stop when any of the following is true:

- Neural Brain owns or executes a consumer goal, plan, action, tool, completion
  decision, or autonomous workflow.
- Scope or principal can be taken from untrusted input.
- Protected memory state is writable outside its owning typed boundary.
- Memory and audit state do not commit atomically.
- Inactive, quarantined, expired, deleted, or out-of-scope memory is retrievable.
- Retrieval loses required provenance, assessment, classification, or freshness.
- Cross-area memory use lacks an explicit audited transfer contract.
- Promotion can bypass evaluation, authorization, quarantine, or rollback.
- Deletion omits an index, cache, embedding, claim, summary, or other derivative.
- Startup or restore reports readiness before reconciliation.
- Backup or restore has not been proven.
- A delivery-stage gate is incomplete.
- The unresolved Tenant-root scope conflict affects the proposed implementation.

## 13. Traceability and architecture change

Repository artifacts are normative technical truth. Notion records decision and
task lifecycle but does not replace versioned contracts. Exchange Room content
is not implementation authorization.

When authoritative sources conflict, affected implementation MUST stop, the
sources and unblock condition MUST be recorded, and no silent architecture
decision may be made. Changes to this baseline require an accepted ADR plus
synchronized documentation, contracts, tests, and traceability evidence.

## Appendix A: ADR status under this directive

| ADR | Relationship to v2.0 |
| --- | --- |
| ADR-001 | Retained and amended: consumers of the neutral memory system do not own its architecture. |
| ADR-002 | Retained and amended: immutable memory scope; Tenant-root representation remains open. |
| ADR-003 | Retained and amended: PostgreSQL is authoritative for transactional memory and audit state. |
| ADR-004 | Superseded: Goal and Action gates are outside the memory-system boundary. |
| ADR-005 | Retained and amended: the security floor governs memory access and lifecycle. |
| ADR-006 | Superseded: agent execution kill switches are outside the memory-system boundary. |
| ADR-007 | Superseded: Goal and Action state machines belong to external consumers. |
| ADR-008 | Superseded: action preparation and commit belong to external consumers. |
| ADR-009 | Superseded: dispatch and effect reconciliation belong to external consumers. |
| ADR-010 | Retained and amended: stages contain memory capabilities only. |
| ADR-011 | Superseded: consumer goal completion is not a Neural Brain responsibility. |
| ADR-012 | Retained and amended: retention-aware immutability applies across memory and derivatives. |
| ADR-013 | Retained and amended: the Python toolchain implements a memory runtime. |
| ADR-014 | Retained and amended: local inference supports memory processing only. |
| ADR-015 | Governing decision: Neural Brain is a memory system, not an agent runtime. |
