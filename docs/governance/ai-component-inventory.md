# Neural Brain AI Component Inventory

- Status: Authoritative repository inventory for the versioned implementation and
  normative target; it is not a deployment inventory or a maturity claim.
- Inventory version: `1.0.0`
- Governing sources: ADR-018, Architecture Directive v4.0, the Neural Brain
  Recognition Standard, and the contracts cited in each record.
- Accountable owner: Neural Brain repository maintainers. The relevant protected
  gate owns state transitions; an inventory record never transfers that authority.
- Review trigger: any accepted ADR, contract, migration, runtime component,
  deployment approval, model/dataset change, or recognition-evidence change.

## Status semantics and fail-closed use

`implemented` means that the cited repository artifact and its cited automated
evidence exist. `partial` means that only the explicitly named bounded slice is
implemented. `target` means normative architecture only: it is **not** enabled,
deployable, or recognition evidence. `not deployed` means that no approved
deployment evidence exists. An unknown component, version, provenance,
evaluation state, owner, or risk control is denied for capability, deployment,
or recognition claims.

The rows are an allow-list for inventory claims, not an authorization surface.
The Cognitive Plane may submit typed proposals only. The Protected Control Plane
and its named transition gates remain the sole authority for protected state and
external effects. The Memory Core is a protected subsystem, not the product
boundary.

## Cognitive Plane inventory

| ID | Component and lifecycle | Current status | Owner and version/authority | Provenance and evaluation evidence | Principal risk and fail-closed control | Repository evidence |
| --- | --- | --- | --- | --- | --- | --- |
| CP-01 | Observation admission, perception, and multimodal binding | target (NB-2) | Cognitive Plane; ADR-018 / Directive v4.0 | Future records require source, time, scope, uncertainty, and held-out/OOD evidence | Untrusted content can forge observation or scope; unknown provenance is denied | `cognitive-cycle.json`, `system-boundary.json` |
| CP-02 | Attention and bounded neural workspace | partial (NB-1, recorded or synthetic input only) | Cognitive Plane; `neural-brain.nb1.safe-serial-cognition` v1.0.0 | Immutable model/training/evaluation digests; NB-1 unit and evaluation ablations | Online mutation, unbounded capacity, or untrusted model selection; immutable trusted model resolution and bounded contract | `src/neural_brain/cognition/workspace.py`, `tests/unit/test_cognition_service.py`, `tests/evaluation/test_nb1_safe_serial_cognition.py` |
| CP-03 | Working memory | partial (Memory Core checkpoint slice) | Memory Transition Gate; memory ledger v2.0.0 | Atomic checkpoint, transition, receipt, and audit provenance | Direct state write or stale checkpoint; gate-only writer and CAS fail closed | `src/neural_brain/memory/service.py`, `src/neural_brain/postgres/cognitive_repository.py`, `migrations/0004_nb1_cognitive_checkpoints.sql` |
| CP-04 | Episodic, semantic, and procedural memory | target (NB-3) | Memory Transition Gate; ADR-015 through ADR-017 retained subsystem authority | Future differentiated truth, deletion, retrieval-lift, and interference evidence required | Cross-Area leakage or inactive-candidate retrieval; immutable scope and lifecycle denial | `memory-lifecycle.json`, `memory-stage-capabilities.json` |
| CP-05 | World, self, and value models | target (NB-2) | Cognitive Plane; ADR-018 | Future calibrated action-conditioned, held-out prediction and planning-usefulness evidence required | Prediction represented as fact or value creates authority; typed provenance and Control Plane gates | `cognitive-cycle.json`, `evaluation-gates.json` |
| CP-06 | Goal runtime and executive control | partial (internal NB-1 proposals only) | Goal Transition Gate for protected lifecycle; Directive v4.0 | Proposal provenance is checkpoint-bound; no achieved-goal or runtime evidence exists | Proposal may be mistaken for authority; no direct protected write and no external effect surface | `nb1-safe-serial-cognition.json`, `src/neural_brain/cognition/service.py` |
| CP-07 | Planning and action selection | partial (bounded internal proposals only) | Cognitive Plane proposes; Action Transition Gate is target owner of protected action state | NB-1 plan proposal tests only; future simulated rollout and policy evidence required | Planner/tool bypass; Action Gate commitment is required before any dispatch | `nb1-safe-serial-cognition.json`, `cognitive-cycle.json` |
| CP-08 | Learning, replay, consolidation, and model candidates | partial (offline non-promoted NB-1 bundle) | Learning and Model Promotion Gate owns activation; Directive v4.0 | Parameter, training, model, and evaluation digests; candidate/hidden-evidence tests | Active-model self-mutation or unverified promotion; immutable candidate, independent promotion, rollback | `src/neural_brain/cognition/training.py`, `tools/train_nb1_workspace.py`, `tests/unit/test_nb1_training.py` |
| CP-09 | Metacognition | partial (`continue` and `ask` proposals only) | Cognitive Plane; independent Safety Supervisor remains target | NB-1 proposal evidence only; future calibration, stop/ask/escalate evidence required | Self-report overrides safety; no authority and independent supervisor required | `nb1-safe-serial-cognition.json`, `src/neural_brain/cognition/models.py` |

## Memory Core and Protected Control Plane inventory

| ID | Component and lifecycle | Current status | Owner and version/authority | Provenance and evaluation evidence | Principal risk and fail-closed control | Repository evidence |
| --- | --- | --- | --- | --- | --- | --- |
| MC-01 | Protected memory lifecycle and Memory Transition Gate | implemented (Memory Core foundation) | Memory Transition Gate; `neural-brain.memory-ledger-invariants` v2.0.0 | Immutable scope, provenance, state-version, receipt, and audit records; database and unit tests | General role, model, or consumer writes protected memory; database gate and atomic rollback | `src/neural_brain/memory/service.py`, `src/neural_brain/postgres/memory_repository.py`, `migrations/0002_stage1_memory_kernel.sql` |
| MC-02 | Area-local Dreaming and inactive candidate production | partial (dry run only) | Memory Transition Gate; ADR-017 | Dreaming run and inactive-candidate provenance; dry-run tests | Dreaming activates, writes, calls tools, or crosses Area; gate-only inactive output | `migrations/0003_dreaming_dry_run.sql`, `dreaming.json`, `tests/database/test_stage1_memory_kernel.py` |
| MC-03 | Retrieval, indexes, caches, and projections | target beyond guarded foundation | Memory Transition Gate and source-policy assessor; ledger v2.0.0 | Future freshness, provenance, deletion cascade, retrieval lift, and isolation evidence required | Stale, deleted, cross-scope, or inactive state influences cognition; unknown is excluded | `ledger-invariants.json`, `memory-release-stops.json` |
| PC-01 | Authenticated identity, immutable scope, and Tenant-bound pools | implemented foundation | Protected Control Plane; ADR-019 | OIDC principal, catalog lineage, database identity, and isolation tests | Payload-defined scope or cross-Tenant pool reuse; authenticated context and bound database identity | `src/neural_brain/consumer/oidc.py`, `src/neural_brain/postgres/tenant_pool.py`, `migrations/0007_tenant_bound_database_identities.sql` |
| PC-02 | Security Floor and policy decision path | partial (implemented memory operation floor and policy contracts) | Protected Control Plane; `security-floor-v1` | Policy/floor positive and negative unit evidence | Unknown operation, incomplete context, or override bypass; code-owned deny-by-default floor | `src/neural_brain/security/floor.py`, `src/neural_brain/security/policy.py`, `tests/unit/test_security_floor.py` |
| PC-03 | Goal, Action, and Model Promotion Gates | target; Memory Gate only is implemented | Respective named transition gate; ADR-018 | Future gate-specific transition, actor, authority, audit, concurrency, and recovery evidence required | Protected state changes outside an owner gate; release stop prohibits enablement | `system-boundary.json`, `release-stops.json` |
| PC-04 | Approvals, budgets, resource claims, and runtime fences | target | Protected Control Plane; Directive v4.0 | Future committed-intent, approval, budget, resource, and fence evidence required | External effect lacks mandatory preconditions; no effect surface is enabled | `system-boundary.json`, `cognitive-cycle.json` |
| PC-05 | Sandboxed executor, tool registry, and independent effect/goal verifier | target; no tool or external-effect integration exists | Executor and independent verifier are separate target owners | Future sandbox, effect observation, verifier, recovery, and quiescence evidence required | Tool success treated as goal success or direct tool call; denied by NB-1 contract and release stops | `nb1-safe-serial-cognition.json`, `release-stops.json` |
| PC-06 | Guardian, kill switch, credential revocation, and reconciliation | target except Memory Core recovery controls | Independent Safety Supervisor / kill-switch plane; Directive v4.0 | Future stale-fence, shutdown, incident, and reconciliation evidence required | Brain controls its own shutdown or ambiguous effects retry; independent plane and `indeterminate` reconciliation required | `system-boundary.json`, `release-stops.json` |
| PC-07 | PostgreSQL audit and evidence ledger | implemented for Memory Core foundation | Memory Transition Gate database role; ledger v2.0.0 | Atomic transition/audit receipts and migration tests | Audit failure accepted with state change; transaction rolls back | `migrations/0002_stage1_memory_kernel.sql`, `tests/database/test_postgres_memory_repository.py` |

## Models, datasets, adapters, integrations, data flow, and deployment

| ID | Asset or boundary | Current status | Owner and version/authority | Provenance and evaluation evidence | Principal risk and fail-closed control | Repository evidence |
| --- | --- | --- | --- | --- | --- | --- |
| AS-01 | Active NB-1 cognitive model and parameter bundle | partial, fixed-version development slice | Trusted active-model provider; `nb1.safe-serial-cognition` v1.0.0 | Exact model, parameter, training-code, and evaluation digests; ablation tests | Request-selected or mutable model; trusted configuration only and manifest mismatch denial | `src/neural_brain/cognition/adapters.py`, `src/neural_brain/cognition/ports.py`, `tests/evaluation/test_nb1_safe_serial_cognition.py` |
| AS-02 | Training data and evaluation datasets | partial, recorded/synthetic development data only | Offline training owner; NB-1 contract | Dataset digest, candidate export, hidden-label separation, and frozen-evidence tests | Leakage, contamination, or self-scoring; hidden evaluator and signing material are outside repository | `src/neural_brain/cognition/training.py`, `tests/unit/test_nb1_hidden_evidence.py`, `tests/architecture/test_nb1_preregistration.py` |
| AS-03 | Inference adapter: local Ollama boundary | target and **not deployed**; no adapter implementation or approved model/deployment record exists | Trusted deployment configuration; ADR-014 and `memory-inference-provider` v1.1.0 | Future exact endpoint, model ID/version/digest, budget, egress, and readiness evidence required | Cloud egress, fallback, request-selected endpoint/model, or untrusted output; local-only fail closed | `inference-provider.json`, `tests/architecture/test_inference_provider_contract.py` |
| AS-04 | Product integrations and external data flows | target; no product-specific integration is part of Neural Brain | Explicit scoped integration contract and Protected Control Plane | Future authenticated source, scope, provenance, minimization, and effect-verification evidence required | Product domain rules or untrusted data define authority; integrations are external consumers only | `ADR-001-product-neutral-platform-boundary.md`, `system-boundary.json` |
| AS-05 | Tools and effect adapters | target; tool registry, invocation, and effects are absent | Action Transition Gate, sandboxed executor, independent verifier | Future committed intent, sandbox, fence, post-effect observation, and quiescence evidence required | Direct tool invocation, blind retry, or status-as-success; prohibited until NB-5 gates pass | `nb1-safe-serial-cognition.json`, `cognitive-cycle.json` |
| AS-06 | Persistent data flow: runtime context to Memory Gate ledger | implemented Memory Core foundation | Authenticated context provider and Memory Transition Gate | Immutable scope, source references, transition receipts, audit and database integration tests | Context supplied by payload or non-atomic audit; trusted context and atomic transaction required | `src/neural_brain/memory/ports.py`, `ledger-invariants.json`, `tests/database/test_tenant_isolation_contract.py` |
| AS-07 | Deployment and operational runtime | not deployed; library plus guarded local demonstration only | Repository maintainers and trusted deployment approval | Locked toolchain and local-environment checks; no production readiness evidence | Demo or HTTP/process status mistaken for deployment readiness; no production/autonomy claim | `README.md`, `tools/dev.ps1`, `tests/foundation/test_local_environment_contract.py` |

## Inventory completeness gates

Before a record can move from `target`, `partial`, or `not deployed` to
`implemented`, its update must cite an accepted authority, concrete owner,
version, immutable provenance, applicable evaluation/negative evidence, risk
controls, implementation artifact, and traceability record. Recognition also
requires every non-compensatory gate in `recognition-gates.json`; this inventory
cannot substitute for those gates. Ollama may be recorded only as the future,
local, non-public, untrusted inference boundary described above. It is not a
current adapter, model deployment, cloud fallback, or proof of neural cognition.
