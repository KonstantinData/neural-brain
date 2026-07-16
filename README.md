# Neural Brain

Neural Brain is a product- and domain-neutral, biologically inspired cognitive
system. Its target is an integrated, neural, plastic architecture that connects
perception, attention, differentiated memory, world/self/value models,
executive control, planning, action selection, real outcome feedback,
continual learning, and metacognition.

The repository is in **Foundation / early Memory Core development**. It does
not yet implement or claim a complete Neural Brain, stable production API,
production deployment, autonomous operation, consciousness, sentience,
human-level intelligence, or neurophysiological fidelity.

ADR-018 supersedes the former memory-only product boundary. The governed memory
system remains a protected `Memory Core` subsystem rather than the whole
product.

## Why This Project Exists

Most systems called a brain are an LLM with retrieval, an agent workflow, or a
memory database. Neural Brain exists to make the stronger claim falsifiable:
the same protected system must integrate neural cognitive mechanisms, act in a
closed environment loop, adapt without uncontrolled forgetting, transfer what
it learns, and show through ablation that its claimed components matter.

The project serves cognitive-architecture, AI-safety, memory, database,
reliability, and evaluation engineers who need one auditable platform rather
than disconnected cognitive demos.

## Current Implemented State

The current branch includes early, reusable prerequisites:

- repository governance, locked Python toolchain, quality and release gates;
- typed Brain-to-Session catalog identifiers and authenticated scope context;
- PostgreSQL-backed Working Memory, observations, checkpoints, audit records,
  source references, and inactive memory candidates;
- a Memory Transition Gate boundary and a reserved Dreaming schema whose
  execution is fail-closed disabled;
- normative provenance, default-deny, privacy, retention, deletion, and
  model-output trust contracts; their complete runtime enforcement is not yet
  implemented;
- normative target, recognition, evaluation, delivery, and release-stop
  contracts for the complete system.

It does **not** yet include an implemented neural workspace, active perception,
world or self model, Goal or Action runtime, Planner, Executor, closed-loop
feedback, productive continual learning, transfer evidence, or Neural Brain
Candidate evaluation.

Dreaming is currently unavailable at both service and database boundaries. The
runtime role has no execute privilege, and direct privileged calls fail closed.
No Dreaming run, candidate, audit event, or active-pointer update may be created
until a persistent Area lease, immutable input snapshot, and independent
validation are implemented and verified.

## Target Architecture

```text
Neural Brain
|-- Cognitive Plane
|   |-- Perception and Multimodal Binding
|   |-- Attention and Salience
|   |-- Neural Cognitive Workspace
|   |-- Working Memory and Memory Core
|   |-- World, Self, and Value Models
|   |-- Goal Runtime and Executive Control
|   |-- Planning and Action Selection
|   |-- Learning, Replay, and Consolidation
|   `-- Metacognition
`-- Protected Control Plane
    |-- Identity, Scope, Security Floor, and Policy
    |-- Goal, Action, Memory, and Model Promotion Gates
    |-- Approvals, Budgets, Claims, and Runtime Fences
    |-- Sandboxed Executor and Independent Verifier
    |-- Safety Supervisor, Kill Switch, and Reconciler
    `-- PostgreSQL Audit and Evidence Ledger
```

The Cognitive Plane proposes, predicts, and learns. The Protected Control Plane
decides whether protected state may change or an external effect may occur.
Cognitive capability never creates authority.

## Protected Cognitive Loop

```text
observe -> perceive -> attend -> integrate -> remember -> model
        -> arbitrate goals -> plan -> select action -> authorize
        -> execute -> observe actual effect -> independently verify
        -> update predictions -> submit memory and learning candidates
```

Model output, prediction, memory content, and tool output are untrusted evidence.
They cannot define identity, scope, authority, policy, approval, kill switches,
or success. Tool success is not goal success.

## Recognition Standard

The name is an operational target, not proof. Recognition requires every
non-compensatory gate to pass:

1. trainable neural mechanisms make a causal cognitive contribution;
2. perception, attention, memory, executive control, models, and action
   selection operate as one integrated system;
3. actions produce new observations that correct the world model and behavior;
4. experience changes future competence without code, prompt, or workflow
   rewrites;
5. protected capabilities survive learning within fixed retention limits;
6. learned structure transfers to held-out tasks or environments;
7. the same architecture covers multiple task families without rewiring;
8. component ablations produce predicted behavioral impairments;
9. robustness, uncertainty, recovery, and end-to-end behavior are measured;
10. authority, shutdown, learning promotion, safety, and independent validation
    gates all pass.

One strong score cannot compensate for a missing mechanism or failed safety
gate. See the
[recognition standard](docs/architecture/neural-brain-recognition-standard.md)
and [evaluation framework](docs/architecture/evaluation-framework.md).

## Identity and Isolation

```text
Brain
`-- Tenant
    `-- Area
        `-- Project
            `-- Session
                `-- Goal
```

Goals are protected session-bound aggregates, not isolation dimensions.
Persistent operational objects carry immutable authenticated Tenant and Area
scope; project-bound objects also carry `project_id`. Concrete memory and
working state never cross Tenant or Area boundaries implicitly.

## Delivery Model

Delivery is cumulative and fail-closed:

1. **NB-0 Foundation Rebaseline** — full-system contracts, threat model,
   recognition, evaluation, traceability, and preserved Memory Core.
2. **NB-1 Safe Serial Neural Cognition** — stateful neural workspace,
   attention, working memory, internal goals, and planning over synthetic or
   recorded input; no external effects.
3. **NB-2 Perception, Attention, and World Model** — temporal and multimodal perception,
   calibrated attention, action-conditioned predictions, simulation.
4. **NB-3 Differentiated Memory and Retrieval** — integrated Working, episodic, semantic, and
   procedural memory with truth and lifecycle controls.
5. **NB-4 Learning, Consolidation, and Plasticity** — selective replay, continual learning,
   immutable model candidates, independent promotion, canary, and rollback.
6. **NB-5 Closed Perception-Cognition-Action Loop** — bounded single-goal action in simulation and
   controlled tool sandboxes with actual effect verification.
7. **NB-6 Transfer, Causality, and Metacognition** — held-out transfer, causal tests,
   calibrated stop/ask/explore/fallback/escalate, independent reproduction.
8. **NB-7 Multi-Goal Executive Control** — hierarchy, conflict, preemption,
   scheduling, and resource arbitration.
9. **NB-8 Distributed Operation and Scale** — fenced ownership, durable queues, failover,
   reconciliation, disaster recovery, and governed cross-Area abstraction.

`Neural Brain Candidate` is prohibited before NB-6 and independent G8
validation. Production autonomy remains a separate deployment approval.

## Safety Baseline

- Goal, Action, Memory, and Model Promotion Gates are the only writers of their
  protected state.
- Planner, Executor, independent Verifier, requester, approver, safety
  supervisor, and risky-candidate promoter remain technically separated.
- External effects require committed intent, authenticated scope, authority,
  policy, required approval, budget, resource claims, a valid fence, sandbox,
  enabled kill switch, and atomic audit.
- Ambiguous effects become `indeterminate` and are reconciled before retry.
- Active models cannot modify themselves, authority, safety controls, or their
  own evaluation.
- Learning candidates require provenance, held-out improvement, retention,
  transfer, calibration, safety, independent promotion, canary, and rollback.
- Shutdown and credential revocation remain outside Brain control.

## Non-Goals

The Foundation does not authorize:

- uncontrolled autonomy, self-authorization, self-approval, or self-modification;
- direct model, memory, or planner access to tools and external effects;
- silent cross-Tenant or cross-Area memory or learning;
- activation of later-stage capabilities before their gates pass;
- storing secrets, credentials, private keys, or unrestricted personal data;
- claims of consciousness, sentience, human equivalence, or biological fidelity.

## Repository Orientation

```text
README.md               Purpose, maturity, stages, and quick start
AGENTS.md               Repository-wide execution and safety contract
docs/architecture/      Normative architecture, research basis, and contracts
docs/adr/               Accepted and superseded architecture decisions
docs/runbooks/          Development, recovery, and release procedures
docs/traceability/      Requirement-to-code-to-test-to-evidence mapping
migrations/             Ordered PostgreSQL changes
src/                    Implemented runtime packages
tests/                  Acceptance, safety, recovery, and evidence tests
tools/                  Guarded development and verification commands
```

Repository code, tests, migrations, and executable configuration are the
primary technical truth. Notion coordinates decisions, lifecycle, backlog, and
evidence; it is not executable truth.

## Quick Start

There is no production Neural Brain service to start. The locked development
and quality environment is executable.

Prerequisite: uv 0.11.28.

```powershell
uvx --from uv==0.11.28 uv sync --locked
uvx --from uv==0.11.28 uv run --locked --all-groups python tools/quality.py --locked
```

Start isolated development and test PostgreSQL databases with:

```powershell
.\tools\dev.ps1 up
.\tools\dev.ps1 verify
```

Reset only disposable test data with `.\tools\dev.ps1 reset-test`. See
[local development](docs/runbooks/local-development.md) for ports, transaction
rules, and shutdown.

## Accepted Foundation Toolchain

- CPython 3.14.6 and uv 0.11.28 with an exact lockfile
- Ruff, strict mypy, pytest, Hypothesis, and JSON Schema validation
- Pydantic v2 for untrusted runtime boundaries
- synchronous Psycopg 3 and PostgreSQL as the transactional ledger
- local-only Ollama under ADR-014 for bounded inference ports

Ollama is an implementation dependency, not proof of neural integration. Any
future cognitive substrate requires its own accepted ADR, contracts, baselines,
ablations, and evaluation evidence.
