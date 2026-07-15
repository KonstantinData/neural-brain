# Neural Brain

Neural Brain is a product- and domain-neutral platform for building a
biologically inspired agent system. It is intended to grow from a strictly
controlled serial cognitive core into a system that can perceive, focus
attention, maintain working memory, pursue goals, plan, execute tools, verify
outcomes independently, retain long-term memory, learn under explicit controls,
reflect, and operate with bounded autonomy.

The project is currently in its **Foundation phase**. Its pinned Python runtime
and engineering quality environment are reproducible, but it does not yet
provide a runnable agent runtime, a stable API, or a production-ready
deployment. This README describes the intended platform and the repository
contract without claiming that later-stage capabilities already exist.

## Who This Is For

This repository is for engineers, security and policy specialists, database and
reliability engineers, architecture reviewers, and future integration teams who
need an auditable agent platform with explicit scope, authority, state, and
verification boundaries.

Its value is not unrestricted agent autonomy. Its value is a foundation on which
useful autonomy can be added incrementally while identity, authorization,
external effects, protected state, evidence, and recovery remain governable and
testable.

## Product Neutrality

Neural Brain does not encode the domain model, policies, defaults, customer data,
or business rules of any consuming product. Liquisto and other projects may
integrate with Neural Brain later through explicit, scoped contracts, but they do
not define this platform's architecture.

## Core Scope Contract

All runtime and persistent work follows this fixed hierarchy:

```text
Brain
└── Tenant
    └── Area
        └── Project
            └── Session
                └── Goal
```

Every persistent domain object carries immutable `tenant_id` and `area_id`.
Project-bound objects also carry immutable `project_id`. Scope and actor identity
come only from authenticated runtime context. Prompts, model responses, tool
outputs, and request payloads cannot define or change identity, scope, roles,
authority, approvals, policy, or kill switches. Unknown values are denied by
default.

## Delivery Model

Delivery is intentionally staged, and each stage depends on the safety and
verification guarantees of the previous one:

1. **Foundation (`MS-0`)** — repository governance, normative architecture and
   contracts, engineering quality, and continuous-integration baselines.
2. **Stage 1 (`MS-1`)** — a safe serial cognitive core with identity and scope
   isolation, policy enforcement, PostgreSQL-backed ledgers, protected state
   transitions, working memory, planning, controlled tool execution, independent
   verification, privacy foundations, recovery, and operations evidence.
3. **Stage 2 (`MS-2`)** — episodic and semantic memory, source-aware retrieval,
   freshness handling, and deletion propagation.
4. **Stage 3 (`MS-3`)** — controlled consolidation and re-evaluation, plus
   procedural learning with quarantine and rollback.
5. **Stage 4 (`MS-4`)** — multi-goal scheduling, preemption, explicit cross-area
   handover, and distributed execution ownership and reconciliation.

Later-stage features must not be enabled early or used to compensate for a
missing earlier-stage control. In particular, Stage 1 uses a minimal persistent
dispatch journal for its serial executor; a generalized distributed outbox and
multi-consumer ownership belong to Stage 4.

## Non-Goals

Neural Brain is not:

- a product-specific agent or a place for consumer-specific business logic;
- a shortcut around authenticated identity, policy, approval, budget, or audit;
- a planner that directly executes tools or mutates protected state;
- a system that treats tool success, an HTTP status, or an exit code as proof
  that a goal was achieved;
- an early implementation of distributed execution or uncontrolled learning;
- a general store for secrets, credentials, live personal data, or unbounded
  memory;
- a prototype in which safety mechanisms are mocked out to demonstrate
  autonomy.

## Repository Orientation

The repository is being established in Foundation tasks. Its durable layout is:

```text
README.md               Project purpose, maturity, stages, and orientation
AGENTS.md               Repository-wide implementation and governance contract
docs/architecture/      Normative architecture and machine-readable contracts
docs/adr/               Accepted architecture decisions
docs/runbooks/          Operational, incident, recovery, and restore procedures
docs/traceability/      Requirement-to-code-to-test evidence conventions
migrations/             Ordered and reproducible PostgreSQL migrations
tests/                  Automated acceptance and safety evidence
tools/                  Guarded development and verification commands
pyproject.toml          Runtime, dependencies, and quality-tool configuration
uv.lock                 Exact cross-platform dependency resolution
.python-version         Exact GIL-enabled CPython runtime request
```

Directories and commands are added by their owning Foundation tasks. Their
presence in this orientation is not a claim that their implementation is already
complete.

Repository code, tests, migrations, and executable configuration are the primary
technical source of truth. `AGENTS.md`, versioned architecture documents, and
ADRs define the durable engineering contract around them. Notion coordinates
accepted decisions, tasks, issues, and implementation evidence; it does not
replace versioned repository truth. Exchange Room discussions are proposals,
not implementation authorization.

## Quick Start

There is no application runtime to start yet. The Foundation quality environment
is executable and locked.

Prerequisite: uv 0.11.28. From any existing uv installation, the repository can
bootstrap and use the exact required uv release without changing the global uv
installation:

```powershell
uvx --from uv==0.11.28 uv sync --locked
uvx --from uv==0.11.28 uv run --locked python tools/quality.py
```

The first command installs the exact CPython and dependency environment declared
by `.python-version`, `pyproject.toml`, and `uv.lock`. The second command runs
format checking, linting, strict static typing, the controlled type-exception
audit, and the test suite.

To orient yourself at the current maturity level:

1. Clone the repository and work from a task branch based on the current default
   branch.
2. Read `AGENTS.md` before making changes; it defines scope, source precedence,
   safety invariants, and delivery rules.
3. Read this README for the platform boundary and staged delivery model.
4. Read [ADR-013](docs/adr/ADR-013-python-runtime-and-toolchain.md) for the
   accepted runtime, trust-boundary, typing, and transaction contracts.
5. Run the locked quality gate before and after every implementation change.

PostgreSQL is the planned authoritative transactional ledger. The isolated local
development and test database environment, including the guarded test-data reset,
is introduced by FND-01.6.

## Accepted Foundation Toolchain

- CPython 3.14.6, standard GIL-enabled build
- uv 0.11.28 with an exact lockfile
- Ruff for formatting and linting
- mypy strict mode plus a zero-default type-exception allowlist
- pytest and Hypothesis for deterministic, property-based, and state-machine tests
- Pydantic v2 for runtime validation at untrusted boundaries
- synchronous Psycopg 3 with autocommit connections and explicit transactions

This toolchain does not select an inference provider. Model inference requires a
separate accepted ADR defining local Ollama and prohibiting OpenAI and automatic
cloud fallback.

## Safety Baseline

Planner, executor, and independent verifier are separate runtime
responsibilities. Protected Goal, Action, and Memory state is writable only
through its transition gate. External effects require committed intent,
authenticated identity, immutable scope, authority and policy decisions,
required approval, budget and resource controls, a valid runtime fence, an
enabled kill switch, and atomic auditability. Ambiguous external effects are
recorded as indeterminate and are not retried blindly.

These constraints are architectural requirements, not optional hardening to be
added after feature development.
