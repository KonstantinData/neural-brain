# Neural Brain

Neural Brain is a product- and domain-neutral, biologically inspired cognitive
system. Its target is an integrated, neural, plastic architecture that connects
perception, attention, differentiated memory, world/self/value models,
executive control, planning, action selection, real outcome feedback,
continual learning, and metacognition.

The repository is in **Foundation / early Memory Core and NB-1 development**.
It includes the first effect-free NB-1 implementation slice, but does not claim
that NB-1 or any complete Neural Brain stage is released. It also does not claim
a stable production API, production deployment, autonomous operation,
consciousness, sentience, human-level intelligence, or neurophysiological
fidelity.

ADR-018 supersedes the former memory-only product boundary. The governed memory
system remains a protected `Memory Core` subsystem rather than the whole
product.

## Status at a Glance

| Surface | Current state |
| --- | --- |
| Product boundary | Complete cognitive-system target governed by [ADR-018](docs/adr/ADR-018-complete-cognitive-system.md) |
| Product maturity | NB-0 Foundation artifacts and a first effect-free NB-1 implementation slice are present; NB-1 is not released |
| Memory maturity | Early MS-1 subset with scoped Working Memory; MS-1 is not complete |
| Runtime | Python library and protected PostgreSQL memory kernel; no stable service API or deployment |
| Dreaming | Reserved schema and contracts; all supported execution paths are disabled fail closed |
| Inference | Normative local-only boundary; no inference adapter or ready deployment exists |
| Autonomy | Internal goal, plan, and metacognitive proposals only; no action execution, external effects, or autonomous operation |
| Recognition | The system is not a `Neural Brain Candidate`; NB-6 plus independent G8 evidence is required |

## Why This Project Exists

Most systems called a brain are an LLM with retrieval, an agent workflow, or a
memory database. Neural Brain exists to make the stronger claim falsifiable:
the same protected system must integrate neural cognitive mechanisms, act in a
closed environment loop, adapt without uncontrolled forgetting, transfer what
it learns, and show through ablation that its claimed components matter.

The project serves cognitive-architecture, AI-safety, memory, database,
reliability, and evaluation engineers who need one auditable platform rather
than disconnected cognitive demos.

## Ownership and Intended Use

Konstantin Milonas is the repository owner and architecture decision owner. The
repository records product direction, architecture, implementation, safety
constraints, and evaluation evidence as reviewable engineering artifacts.

The platform is product- and domain-neutral. A consuming product may integrate
through an explicit scoped contract, but it does not define Neural Brain's
architecture, policies, defaults, or authority model.

## Target State

The enduring target is one complete, protected Neural Brain: an integrated
system that learns from perception, maintains differentiated memory, forms and
updates world/self/value models, controls goals and attention, selects bounded
actions, observes their real effects, corrects its predictions, transfers
learned structure, and monitors the limits of its own competence.

The target is not an LLM wrapper, retrieval database, workflow graph, or loose
collection of cognitive services. The same governed architecture must provide:

- trainable neural mechanisms with demonstrated causal contribution;
- perception, attention, Working Memory, episodic, semantic, and procedural
  memory operating in one closed cognitive loop;
- executive control, planning, action selection, and verified outcome feedback;
- continual learning with bounded forgetting, transfer, canary promotion, and
  rollback;
- metacognitive uncertainty, stop, ask, explore, fallback, and escalation;
- an independent Protected Control Plane for identity, scope, authority,
  approvals, budgets, fences, verification, shutdown, and audit; and
- reproducible benchmarks, baselines, ablations, robustness tests, and
  independent evidence for every recognition claim.

This target remains stable while the implementation status below changes over
time. The normative definition lives in
[ADR-018](docs/adr/ADR-018-complete-cognitive-system.md),
[Architecture Directive v4.0](docs/architecture/architecture-directive-v4.0.md),
and the [recognition standard](docs/architecture/neural-brain-recognition-standard.md).

## Current Implemented State

The current implementation includes early, reusable prerequisites:

- repository governance, locked Python toolchain, quality and release gates;
- a Brain-to-Session PostgreSQL catalog and strict authenticated
  `RuntimeContext`;
- PostgreSQL-backed Working Memory, observations, checkpoints, audit records,
  source references, and schema constraints for inactive memory candidates;
- a first serial NB-1 cognition slice with a fixed-version recurrent neural
  workspace, bounded trainable feature gating, authenticated session scope,
  Memory-Gate checkpoints, and typed internal goal, plan, and metacognitive
  proposals;
- the immutable `EVAL-01.NB-1.safe-serial-cognition.v3` specification and harness
  with six baselines, three mechanism ablations, dataset digests, and confidence
  intervals, plus a deterministic train-only offline grid search and
  self-verifying non-promoted model/provenance bundle;
- a label-free candidate interface, complete candidate freeze receipt, and
  Ed25519-signed external-evidence intake that keep hidden labels, scoring, and
  evaluator key custody outside this repository and never grant a gate;
- the preregistered `EVAL-01.NB-1.safe-serial-cognition.v4` replacement
  specification plus `nb1-serial-context-generator-v4`, which replace the
  rejected enumerable v3 hidden space before any v4 candidate or hidden
  artifact exists;
- a dedicated PostgreSQL cognitive checkpoint adapter and migration that keep
  CAS, transition evidence, trusted training/model provenance, receipt, and
  audit inside one existing Memory Transition Gate transaction;
- v1 and v2 are retained as rejected evaluation history; v3 is also retained
  unchanged but was rejected before hidden attachment after its public generator
  was proven to expose only six distinct feature/label patterns;
- a Memory Transition Gate boundary and a reserved Dreaming schema whose
  execution is fail-closed disabled;
- normative provenance, default-deny, privacy, retention, deletion, and
  model-output trust contracts; their complete runtime enforcement is not yet
  implemented;
- normative target, recognition, evaluation, delivery, and release-stop
  contracts for the complete system.

The NB-1 slice accepts only recorded or synthetic observations and cannot
execute an action or cause an external effect. Its feature gate is not yet
evidence of general cognitive attention, and its `continue`/`ask` ambiguity
heuristic is not calibrated uncertainty. It does **not** yet include active
multimodal perception, a world or self model, protected Goal or Action runtime,
an Executor, closed-loop feedback, productive continual learning, transfer
evidence, completed EVAL-01 results, or Neural Brain Candidate evaluation.

Dreaming is currently unavailable at both service and database boundaries. The
runtime role has no execute privilege, and direct privileged calls fail closed.
No supported runtime path may create a Dreaming run, candidate, audit event, or
active-pointer update until a persistent Area lease, immutable input snapshot,
and independent validation are implemented and verified.

## Target Architecture

The target is normative in [Architecture Directive v4.0](docs/architecture/architecture-directive-v4.0.md).
It is not a claim that the displayed components already exist.

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

## Product and Memory Stage Namespaces

`NB-0` through `NB-8` describe cumulative maturity of the complete Neural Brain
product. `MS-0` through `MS-4` describe only the protected Memory Core
subsystem. An MS stage is never an alias for, and never proves, an NB stage.

The current repository contains NB-0 Foundation artifacts, an early subset of
MS-1, and the first effect-free NB-1 implementation slice. It does not claim
complete MS-1 evidence, complete NB-1 exit evidence, or any released NB-1
through NB-8 cognitive stage. See the machine-readable
[product-stage](docs/architecture/contracts/stage-capabilities.json) and
[Memory Core stage](docs/architecture/contracts/memory-stage-capabilities.json)
contracts.

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

The following are non-negotiable target invariants, not claims that every named
runtime component is implemented. The current code implements only an early
Memory Core slice of these boundaries.

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

## Documentation and Evidence Map

- [Architecture index](docs/architecture/README.md) and
  [Architecture Directive v4.0](docs/architecture/architecture-directive-v4.0.md)
- [ADR index](docs/adr/README.md) and
  [ADR-018](docs/adr/ADR-018-complete-cognitive-system.md)
- [Recognition standard](docs/architecture/neural-brain-recognition-standard.md)
  and [evaluation framework](docs/architecture/evaluation-framework.md)
- [Delivery roadmap](docs/architecture/delivery-roadmap.md) and
  [capability traceability](docs/traceability/neural-brain-capability-matrix.md)
- [Machine-readable contracts](docs/architecture/contracts/README.md),
  [threat model](docs/architecture/threat-model.md), and
  [repository governance](docs/governance/README.md)
- [Repository agent context](docs/governance/repository-agent-context.md)
  for applying global Codex skills inside Neural Brain
- [Engineering source governance](docs/governance/engineering-source-governance.md)
  and [Neural Brain source profile](docs/governance/engineering-source-profile.json)
- [Engineering source registry](docs/governance/engineering-source-registry.md),
  [engineering source records](docs/governance/engineering-source-records.json),
  [source record schema](docs/governance/engineering-source-registry.schema.json),
  [source governance audit records](docs/governance/source-governance-audit-records.md),
  and [architecture evolution register](docs/governance/architecture-evolution-register.md)
- [Operational runbooks](docs/runbooks/README.md) and
  [release evidence](docs/runbooks/release-artifacts.md)

## Quick Start

There is no production Neural Brain service to start. The locked development
and quality environment is executable.

Prerequisite: uv 0.11.28.

```powershell
uvx --from uv==0.11.28 uv sync --locked --all-groups
uvx --from uv==0.11.28 uv run --locked --all-groups python tools/train_nb1_workspace.py --check
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

## Verification and Release Evidence

The locked quality command runs Ruff formatting and linting, strict mypy,
type-exception auditing, and the complete pytest suite. Pull-request CI also
checks PostgreSQL 18 forward migrations, dependency and workflow policy,
secret history, and deterministic release evidence.

Live database tests require an isolated PostgreSQL 18 administrative DSN and
must use disposable databases. The guarded migration and database procedures
are documented in the [local-development runbook](docs/runbooks/local-development.md).
Passing repository tests proves only the tested Foundation, Memory Core, and
first NB-1 implementation surfaces. EVAL-01 v3 cannot supply accepted hidden
evidence because its enumerable generator violates its own contamination
boundary. EVAL-01 v4 is now only a preregistered replacement specification and
generator contract. A v4-bound candidate must still be trained and frozen
before an independent provider attaches any hidden artifact;
neither repository tests nor that evaluation alone complete NB-1, satisfy
Neural Brain recognition, or authorize production use.

## Accepted Foundation Toolchain and Inference Boundary

- CPython 3.14.6 and uv 0.11.28 with an exact lockfile
- Ruff, strict mypy, pytest, Hypothesis, and JSON Schema validation
- Pydantic v2 for untrusted runtime boundaries
- synchronous Psycopg 3 and PostgreSQL as the transactional ledger
- Ollama is the only architecturally approved future local inference adapter
  under ADR-014; no inference adapter or inference deployment is implemented
  or ready.

Ollama is an approved future adapter boundary, not a current runtime dependency
and not proof of neural integration. Any future cognitive substrate requires
its own accepted ADR, contracts, baselines, ablations, and evaluation evidence.

## License and Reuse

This repository currently contains no license file. Do not assume permission to
copy, redistribute, or reuse its contents beyond rights explicitly granted by
the repository owner.
