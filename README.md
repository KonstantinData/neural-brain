# Neural Brain

Neural Brain is a product- and domain-neutral **memory system**. It provides
durable, scoped, provenance-preserving memory that external agents and other
authorized consumers can use through explicit integration contracts.

Neural Brain is not an agent. It does not pursue goals, plan work, execute tools,
or operate autonomously. Those responsibilities remain with consuming systems.
The Brain accepts bounded memory requests, enforces identity and scope, stores
and retrieves evidence-backed records, and governs retention, deletion,
consolidation, and learning.

The project has completed its Foundation milestone and is in early Stage 1.
The current implementation provides a protected PostgreSQL vertical slice for
the hierarchy catalog, observations, Working Memory, checkpoints, atomic audit,
and guarded Dreaming dry runs. It does not yet provide a stable production API,
complete Stage 1 operations, or a production-ready deployment.

## Who This Is For

This repository is for engineers building memory services and integrations,
security and privacy specialists, database and reliability engineers,
architecture reviewers, and teams whose agents need an auditable memory layer.

Its value is durable context with explicit boundaries: a consumer can attach
observations, retrieve relevant memory, and submit learning candidates without
gaining authority to bypass scope, provenance, policy, retention, or review.

## Product Neutrality

Neural Brain does not encode the domain model, policies, defaults, customer
data, or business rules of any consuming product. Liquisto and other projects
may consume Neural Brain later through explicit, scoped contracts, but they do
not define this platform's architecture.

## Brain and Consumer Boundary

The Brain owns memory capabilities:

- authenticated, scope-bound memory ingestion;
- observations and working context;
- provenance-preserving episodic and semantic memory;
- policy-controlled retrieval with freshness and data-class controls;
- inactive learning candidates and controlled promotion;
- retention, legal hold, deletion propagation, quarantine, and rollback;
- auditable memory transitions and local, bounded inference where an accepted
  contract requires it.

External consumers own behavior outside memory:

- goals, prioritization, and planning;
- tool selection and execution;
- approvals for external effects;
- effect verification and operational reconciliation;
- autonomous runtime loops and domain-specific decisions.

An agent response, model output, tool result, or request payload is untrusted
input. It can propose memory content but cannot define identity, scope,
authority, policy, retention, or activation status.

## Scope and Isolation

Memory is isolated by authenticated ownership and context. The current logical
hierarchy is:

```text
Brain
└── Tenant
    └── Area
        └── Project
            └── Session
```

Brain, Tenant, Area, Project, and Session are typed hierarchy catalog objects.
Brain is a persisted singleton. Tenant has `brain_id` and `tenant_id`, but no
`area_id`. Area has `tenant_id` and `area_id`; its Brain is resolved transitively
through Tenant. Project adds `project_id`, and Session is project-bound and adds
`session_id`. Operational memory always carries authenticated `tenant_id` and
`area_id`; project- and session-bound memory also carries every applicable
parent identifier. No sentinel Area, nullable required identifier, or implicit
root scope is authorized. Scope and actor identity come only from authenticated
runtime context and are immutable after persistence.

External identifiers such as `consumer_session_ref`, `consumer_goal_ref`, and
`consumer_task_ref` may be stored only as non-authoritative correlation
metadata. They are not Brain-owned scope, cannot confer authority, and cannot
control memory transitions.

Area separation does not imply uncontrolled cross-area access. A concrete
memory remains in its origin area. Potentially reusable knowledge must pass
through a controlled generalization flow that preserves origin provenance,
removes or blocks restricted details, evaluates policy and privacy constraints,
and records an auditable promotion decision. Unknown or ambiguous scope and
promotion conditions are denied by default.

## Delivery Model

Delivery is staged. Each stage depends on the isolation, provenance, privacy,
and verification guarantees of the previous one:

1. **Foundation (`MS-0`)** — repository governance, normative memory
   architecture, contracts, engineering quality, and CI baselines.
2. **Stage 1 (`MS-1`)** — a secure scoped memory kernel with the hierarchy
   catalog, authenticated consumers and producers, source references and
   provenance, ingestion normalization and salience, working/context memory,
   observations, checkpoints, the Memory Gate, inactive candidates, Dreaming
   dry runs, audit and RLS, retention and deletion foundations, and
   backup/restore.
3. **Stage 2 (`MS-2`)** — durable episodic and semantic memory, claims and
   assessments, ranked retrieval, and freshness handling.
4. **Stage 3 (`MS-3`)** — controlled Dreaming consolidation, independent
   assessment, re-evaluation, procedural memory, quarantine, promotion, and
   rollback.
5. **Stage 4 (`MS-4`)** — governed cross-area abstraction and handover plus
   scalable distributed memory and index reconciliation.

Later-stage features must not be enabled early or used to compensate for a
missing earlier-stage control. Local model inference is an internal bounded
memory-processing dependency, not an autonomous agent capability. It cannot
perform external actions or bypass deterministic gates.

## Dreaming

Dreaming is Neural Brain's governed offline memory-analysis process. It works on
one inactive Area and one immutable snapshot at a time, under an exclusive
lease. It can replay evidence, detect duplication or contradiction, assess
freshness, and propose inactive candidates. It is not an agent and cannot
execute tools or external actions.

Stage 1 supports only a dry run: reports, findings, and inactive candidates. A
Dreaming worker or model cannot change protected memory or an active-version
pointer. Controlled activation begins in Stage 3 and requires independent
validation, a separate Memory Gate transition, preserved provenance, and a
rollback target. Raw cross-Area Dreaming is prohibited.

## Non-Goals

Neural Brain is not:

- an agent, orchestration framework, planner, executor, or tool runtime;
- a system that owns or decides a consumer's goals;
- a product-specific knowledge base or store for consumer business rules;
- a shortcut around authenticated identity, scope, provenance, policy, or audit;
- a mechanism for unrestricted cross-area access or silent data sharing;
- a general store for secrets, credentials, live personal data, or unbounded
  content;
- an uncontrolled self-learning system;
- a cloud inference gateway or a system with automatic cloud fallback.

## Repository Orientation

```text
README.md               Purpose, maturity, stages, and consumer boundary
AGENTS.md               Repository-wide implementation and governance contract
docs/architecture/      Normative memory architecture and contracts
docs/adr/               Accepted architecture decisions
docs/runbooks/          Operational, incident, recovery, and restore procedures
docs/traceability/      Requirement-to-code-to-test evidence conventions
migrations/             Ordered and reproducible PostgreSQL migrations
tests/                  Automated acceptance, isolation, and safety evidence
tools/                  Guarded development and verification commands
pyproject.toml          Runtime, dependencies, and quality-tool configuration
uv.lock                 Exact cross-platform dependency resolution
.python-version         Exact GIL-enabled CPython runtime request
```

Repository code, tests, migrations, and executable configuration are the
primary technical source of truth. `AGENTS.md`, versioned architecture
documents, and ADRs define the durable engineering contract around them. Notion
coordinates accepted decisions, tasks, issues, and implementation evidence; it
does not replace versioned repository truth. Exchange Room discussions are
proposals, not implementation authorization.

## Quick Start

There is no production memory service to start yet. The Foundation quality
environment and the first Stage 1 PostgreSQL memory-kernel slice are executable
and locked.

Prerequisite: uv 0.11.28.

```powershell
uvx --from uv==0.11.28 uv sync --locked
uvx --from uv==0.11.28 uv run --locked --all-groups python tools/quality.py --locked
```

The first command installs the environment declared by `.python-version`,
`pyproject.toml`, and `uv.lock`. The second runs format checking, linting,
strict static typing, the controlled type-exception audit, and tests.

Before changing the repository, read `AGENTS.md`, the accepted ADRs relevant to
the memory capability, and the active tracked work item. Run the locked quality
gate before and after implementation.

PostgreSQL is the authoritative transactional memory ledger. Start the isolated
local development and test databases with:

```powershell
.\tools\dev.ps1 up
```

Verify both connections and the explicit-transaction contract with
`.\tools\dev.ps1 verify`. Reset only disposable test data with
`.\tools\dev.ps1 reset-test`. See the
[local development runbook](docs/runbooks/local-development.md) for ports,
credential handling, reset safety, and shutdown commands.

## Accepted Foundation Toolchain

- CPython 3.14.6, standard GIL-enabled build
- uv 0.11.28 with an exact lockfile
- Ruff for formatting and linting
- mypy strict mode plus a zero-default type-exception allowlist
- pytest and Hypothesis for deterministic, property-based, and state-machine tests
- Pydantic v2 for runtime validation at untrusted boundaries
- synchronous Psycopg 3 with autocommit connections and explicit transactions

Inference is local-only through Ollama under ADR-014. There is no OpenAI use or
automatic cloud fallback. Inference remains bounded by deterministic memory
contracts and cannot activate candidates or mutate protected memory directly.

## Safety Baseline

Protected memory state is writable only through its owning transition gate.
Memory producers and retrieval consumers cannot promote their own sensitive or
risky candidates. Scope, provenance, audit, and the protected memory mutation
must commit atomically where the contract requires atomicity. Retention and
deletion apply to derived records, indexes, and caches as well as source
records. Unknown identity, scope, source, data class, policy, freshness, or
promotion state fails closed.

These constraints are architectural requirements, not optional hardening.
