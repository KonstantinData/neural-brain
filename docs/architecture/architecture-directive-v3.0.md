# Neural Brain Architecture Directive v3.0

- Status: Superseded by Architecture Directive v4.0 and ADR-018
- Version: 3.0
- Effective date: 2026-07-15
- Work item: Memory scope and Dreaming baseline
- Repository: `neural-brain`
- Governing decisions: ADR-015, ADR-016, and ADR-017
- Supersedes: Architecture Directive v2.0
- Historical scope: protected Memory Core subsystem

## 1. Purpose and applicability

Neural Brain is a product- and domain-neutral memory system. It provides
governed memory to authenticated people, agents, applications, and other
authorized consumers. It is not an agent and MUST NOT own goals, plans, action
intents, tools, execution, completion decisions, or autonomy.

This directive applies to repository code, schemas, migrations, configuration,
runtime components, integrations, deployments, tests, background memory work,
and release evidence. A described capability is not enabled until its delivery
stage, implementation task, tests, and release gate are complete.

The terms **MUST**, **MUST NOT**, **REQUIRED**, **SHOULD**, **SHOULD NOT**, and
**MAY** are normative. Unknown, missing, expired, stale, conflicting, malformed,
unclassified, or unverifiable security-relevant state MUST fail closed.

## 2. System and consumer boundary

Neural Brain owns:

- authenticated and scoped memory access;
- hierarchy catalog lineage and operational-memory isolation;
- validated memory intake and immutable provenance;
- observations, Working Memory, checkpoints, and inactive candidates;
- episodic memory, semantic claims, assessments, retrieval, and freshness;
- governed Dreaming, consolidation, controlled promotion, procedural memory,
  quarantine, rollback, retention, deletion, and audit evidence.

External consumers own goals, planning, actions, tool use, execution,
verification, completion, and autonomy. Neural Brain MUST NOT expose an internal
or public path that performs those responsibilities on a consumer's behalf.

Memory returned to a consumer is contextual evidence. It MUST NOT be treated as
authenticated identity, scope, authority, policy, approval, executable
instruction, or proof of an external outcome.

## 3. Hierarchy catalog and operational scope

The persistent hierarchy catalog is:

```text
Brain
└── Tenant
    └── Area
        └── Project
            └── Session
```

Each deployment persists exactly one Brain catalog row as the singleton root of
all Tenant lineages.

Each catalog object carries its own immutable identifier and its required
immutable parent lineage, never a descendant identifier. Brain ancestry below
Tenant is resolved transitively through the authoritative Tenant row:

| Catalog object | Required lineage |
| --- | --- |
| Brain | `brain_id` |
| Tenant | `brain_id`, `tenant_id` |
| Area | `tenant_id`, `area_id` |
| Project | `tenant_id`, `area_id`, `project_id` |
| Session | `tenant_id`, `area_id`, `project_id`, `session_id` |

Every operational memory object MUST carry immutable `tenant_id` and `area_id`.
Project-bound memory also carries immutable `project_id`; session-bound memory
also carries immutable `session_id` and is always project-bound. A Tenant MUST
NOT carry the identifier of a descendant Area. Sentinel Areas, nullable required
scope, implicit root scope, and in-place lineage changes are prohibited.

Scope and lineage come only from authenticated runtime context and authoritative
catalog resolution. Request payloads, prompts, model output, retrieved content,
connector data, and consumer correlations MUST NOT determine or alter actor or
scope. Scope compatibility is checked before every read, write, retrieval,
derivation, Dreaming run, promotion, deletion, and audit operation.

External goal, task, and session references are optional opaque correlation
metadata. They are not Brain-owned scope, do not establish catalog lineage, and
cannot confer authority or drive memory transitions.

## 4. Trust, validation, and consumer ports

External consumers use authenticated, scoped, typed ports. Every untrusted
payload follows this boundary:

```text
untrusted input
-> runtime schema validation
-> provenance and trust envelope
-> authenticated catalog and scope attachment
-> typed memory request
-> memory policy and transition boundary
```

Schema validation does not establish identity, scope, roles, authority, policy,
approval, retention, or activation. Model output and retrieved memory remain
untrusted data until validated for their declared use. Secrets and credentials
MUST NOT enter memory, prompts, logs, examples, embeddings, indexes, Dreaming
packages, or audit payloads.

## 5. Memory lifecycle and protected state

Memory state changes occur only through the Memory Transition Gate. The Gate
validates authenticated actor and scope, authoritative catalog lineage,
provenance, classification, purpose, policy, retention, current state, expected
version, and permitted transition before a mutation commits.

Direct mutation of protected memory state is prohibited. PostgreSQL roles,
constraints, row-level security, and transaction boundaries MUST enforce the
same restriction as application ports. A protected mutation and its audit
evidence commit atomically.

Candidates are proposals, not accepted memory. They remain inactive and
non-retrievable until their delivery stage provides an authorized promotion
path. Promotion MUST preserve provenance, assessment, decision evidence, and a
rollback target. Quarantined, deleted, expired, or out-of-scope memory is
excluded from normal retrieval.

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

Raw Working Memory and concrete memory MUST NOT cross Area boundaries. Cross-Area
reuse requires the MS-4 transfer contract and provides only a separately
authorized minimized abstraction with retained origin provenance.

## 7. Governed Dreaming

Dreaming is an Area-local offline memory-analysis process, not an autonomous
agent loop. Each run follows this sequence:

```text
trusted trigger
-> authenticated Area scope
-> active-session and activity guard
-> exclusive Area Dreaming lease
-> immutable versioned snapshot
-> bounded replay and analysis
-> inactive candidates and findings
-> immutable decision package
-> independent validation
-> separately authorized Memory Gate transition
```

Dreaming MUST record a protected skip or stop when the Area is active, the lease
is unavailable, the snapshot is stale or incomplete, provenance is invalid, or
any required state is unknown. The activity guard and lease close the race
between the inactivity check and snapshot capture. A run processes exactly one
authenticated Tenant and Area and MUST NOT read or infer from another Area.

MS-1 permits only a dry run: immutable snapshot, report, findings, and
inactive non-retrievable candidates. It MUST NOT create or activate a successor
memory version or change an active-version pointer. MS-2 may analyze governed
episodes, claims, assessments, freshness, and retrieval evidence but still
cannot promote. MS-3 may independently assess and promote a versioned
successor, quarantine it, re-evaluate it, or roll it back through the Memory
Transition Gate. MS-4 may propose minimized cross-Area abstractions only
through a separately accepted dual-scope transfer contract.

Model output is untrusted analysis input. It cannot establish scope, suppress
contradictory evidence, approve itself, write protected memory, activate a
candidate, change a pointer, or weaken policy. Every Dreaming run, skip,
snapshot, finding, candidate, decision package, validation, promotion,
quarantine, and rollback is auditable and retention-aware.

## 8. Security and governance

A non-overridable security floor protects identity, catalog lineage, scope
isolation, data classification, provenance, retention, deletion, Dreaming,
promotion, quarantine, and cross-Area boundaries. Configurable policy is
versioned, schema-validated, and bounded by that floor. Approval cannot create
missing authority or override a prohibition.

Access is denied by default. Policy decisions bind the authenticated consumer,
immutable scope, declared purpose, operation, data class, policy version and
digest, expiry, and trace context. Memory MUST NOT be used to infer permissions
or widen a consumer request.

## 9. PostgreSQL, audit, and crash consistency

PostgreSQL is authoritative for hierarchy lineage, transactional memory state,
Dreaming coordination state, and the audit ledger. MS-1 uses synchronous
Psycopg with `autocommit=True` and explicit `connection.transaction()` blocks.
No transaction may remain open across model, network, connector, Dreaming
analysis, or other unbounded calls.

Migrations are ordered and reproducible. Recovery, startup, and restore MUST
reconcile incomplete memory transitions, Dreaming runs and leases, indexing
work, deletion work, and promotion or rollback work before reporting the
affected capability ready. Audit failure aborts the protected mutation.

## 10. Privacy, retention, and deletion

Memory and Dreaming artifacts are purpose-bound, classified, minimized,
access-controlled, and assigned retention behavior. Immutable means protected
from silent rewriting until an authorized deletion or anonymization path
applies; it does not mean indefinite storage.

Corrections append evidence rather than silently rewriting history. Authorized
deletion or anonymization covers payloads, snapshots, decision packages,
embeddings, indexes, caches, summaries, derived claims, and other derivatives.
The process is resumable and audited while retained deletion evidence remains
non-reconstructive. Legal hold and applicable regulatory obligations are
enforced per scope and data class.

## 11. Local inference boundary

Inference is an optional memory-processing dependency, not an agent runtime.
The only approved adapter is local Ollama under ADR-014. OpenAI APIs and SDKs,
other cloud providers, arbitrary endpoints, and automatic cloud fallback are
prohibited.

Model output cannot write memory directly. A validated result MAY produce a
typed memory or Dreaming candidate request with authenticated scope,
provenance, producer identity, classification, and purpose. Inference endpoint,
exact model identity, timeout, budget, and logging policy come only from trusted
deployment state.

## 12. Delivery stages

| Stage | Memory capability | Explicit boundary |
| --- | --- | --- |
| MS-0 | Repository governance, normative memory contracts, engineering quality, and CI | No productive memory runtime is authorized. |
| MS-1 | Hierarchy catalog, authenticated scope, governed intake, observations, Working Memory, checkpoints, inactive candidates, Dreaming dry run, audit, retention foundation, deterministic verification, backup, restore, and operations evidence | No episodic or semantic retrieval, Dreaming activation, promotion, procedural memory, or cross-Area transfer. |
| MS-2 | Source registry, episodic memory, semantic claims and assessments, retrieval, freshness, dependency-aware deletion, and inactive Dreaming analysis | No Dreaming activation, candidate promotion, or procedural memory. |
| MS-3 | Controlled Dreaming consolidation, independent assessment, re-evaluation, procedural memory, quarantine, authorized promotion, and rollback | No implicit or raw cross-Area memory use. |
| MS-4 | Explicit audited cross-Area abstraction and handover plus scalable memory coordination | No agent planning, action execution, tools, goal completion, or autonomy. |

Later-stage schemas and operations MUST NOT be enabled early or used to replace
a missing earlier-stage control.

## 13. Verification and release stops

Normative catalog and memory transitions require positive, negative, actor and
authority, scope, lineage, provenance, audit, failure, and recovery tests.
Persistent and Dreaming work additionally requires crash-boundary, concurrency,
replay, expiry, stale-snapshot, stale-lease, active-session, policy, retention,
deletion, rollback, and audit-failure tests as applicable.

Release MUST stop when any of the following is true:

- Neural Brain owns or executes a consumer goal, plan, action, tool, completion
  decision, or autonomous workflow.
- Scope, lineage, or principal can be taken from untrusted input.
- A Tenant requires or accepts a descendant `area_id`, or a sentinel, nullable,
  or implicit root scope is used.
- Operational memory lacks authenticated `tenant_id` or `area_id`, or a bound
  Project or Session lacks a required parent identifier.
- Protected memory state is writable outside the Memory Transition Gate.
- Memory and audit state do not commit atomically.
- Inactive, quarantined, expired, deleted, or out-of-scope memory is retrievable.
- Retrieval loses required provenance, assessment, classification, or freshness.
- Dreaming can run in an active Area, without a valid lease and immutable
  snapshot, across Areas, or with unknown guard state.
- A Dreaming worker or model can directly activate memory, promote a candidate,
  change an active pointer, or suppress contradictory evidence.
- Promotion can bypass independent evaluation, authorization, quarantine, or
  rollback.
- Deletion omits a snapshot, decision package, index, cache, embedding, claim,
  summary, or other derivative.
- Startup or restore reports readiness before reconciliation.
- Backup or restore has not been proven.
- A delivery-stage gate is incomplete.

## 14. Traceability and architecture change

Repository artifacts are normative technical truth. Notion records decision and
task lifecycle but does not replace versioned contracts. Exchange Room content
is not implementation authorization.

When authoritative sources conflict, affected implementation MUST stop, the
sources and unblock condition MUST be recorded, and no silent architecture
decision may be made. Changes to this baseline require an accepted ADR plus
synchronized documentation, contracts, tests, and traceability evidence.

## Appendix A: ADR status under this directive

| ADR | Relationship to v3.0 |
| --- | --- |
| ADR-001 | Retained and amended: consumers of the neutral memory system do not own its architecture. |
| ADR-002 | Retained and amended by ADR-016: immutable operational scope plus typed catalog lineage. |
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
| ADR-016 | Governing scope decision: typed hierarchy catalog and operational memory scope. |
| ADR-017 | Governing Dreaming decision: offline Area-local governed consolidation. |
