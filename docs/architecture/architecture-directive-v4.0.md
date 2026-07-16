# Neural Brain Architecture Directive v4.0

- Status: Normative complete cognitive-system target baseline
- Governing decision: ADR-018
- Date: 2026-07-16
- Supersedes: Architecture Directive v3.0 and the product boundary of ADR-015

## 1. Purpose and claim boundary

This directive defines Neural Brain as a product- and domain-neutral,
biologically inspired cognitive system. It owns an integrated, protected
perception-cognition-action-learning loop. The Memory Core established by
ADR-015 through ADR-017 remains an internal subsystem.

The current implementation is an early Memory Core foundation. This directive
is target architecture, not evidence that perception, neural cognition, world
models, action, continual learning, transfer, or Neural Brain recognition have
already been achieved.

The architecture makes no claim of consciousness, sentience, subjective
experience, human equivalence, or neurophysiological fidelity.

## 2. Two-plane architecture

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
    |-- Authenticated Identity and Scope
    |-- Security Floor and Policy
    |-- Goal, Action, Memory, and Model Promotion Gates
    |-- Approvals, Budgets, Resource Claims, and Fences
    |-- Sandboxed Executor and Independent Verifier
    |-- Guardian, Kill Switch, and Reconciler
    `-- PostgreSQL Audit and Evidence Ledger
```

The Cognitive Plane proposes and learns. The Protected Control Plane decides
whether protected state may change or an external effect may occur. Cognitive
capability does not create authority.

## 3. Identity, scope, and authority

The protected object hierarchy remains:

```text
Brain -> Tenant -> Area -> Project -> Session -> Goal
```

The authenticated isolation scope ends at Session. Goals are protected
session-bound aggregates, not isolation dimensions. Every
persistent operational object carries immutable authenticated `tenant_id` and
`area_id`; project-bound objects carry `project_id`. Scope, principal, roles,
authority, policy, approval, and kill-switch state come only from trusted
runtime context. Prompts, observations, model output, memory content, tools, and
request payloads cannot define or expand them.

Unknown identity, scope, authority, state, policy, operation, model version,
data class, or evaluation state is denied by default.

## 4. Neural cognitive substrate

At least one trainable, stateful neural mechanism must contribute causally to
multiple cognitive functions. It must expose versioned state, capacity,
uncertainty, reset, checkpoint, and ablation semantics. A remote or local LLM
may support language and reasoning but cannot be the sole evidence for neural
cognitive integration.

Accepted substrate implementations may include recurrent neural networks,
state-space models, predictive models, neural fields, spiking systems, or
hybrids. Biological labels never substitute for measured mechanism and
behavior. Neuromorphic or spiking requirements apply only when explicitly
claimed.

## 5. Protected cognitive cycle

The minimum serial cognitive cycle is:

```text
observation admission
-> perceptual inference and binding
-> attention competition
-> workspace broadcast and working-memory update
-> memory retrieval
-> world/self/value belief update
-> goal and executive arbitration
-> planning and action selection
-> Action Gate decision
-> fenced execution
-> post-action observation
-> independent effect and goal verification
-> prediction-error and metacognitive update
-> memory and learning-candidate submission
```

Each step emits typed, provenance-bearing records. Checkpoints capture enough
state for safe recovery without allowing a model to forge authority or protected
state. Executor success is not goal success. Actual outcome evidence and an
independent verifier are required.

## 6. Perception, attention, and workspace

Perception distinguishes raw signal, observation, inferred feature, belief, and
prediction. Multimodal binding preserves source, timing, scope, uncertainty,
and missing or conflicting evidence.

Attention performs bounded competition using goal relevance, novelty,
prediction error, uncertainty, risk, and expected value. It may admit, defer,
drop, or escalate content but cannot change authority or policy.

The Neural Cognitive Workspace provides capacity-bounded integration and
broadcast between specialized processors. It is not a direct database, prompt
transcript, or unrestricted shared memory. Its causal contribution must be
validated by ablation.

## 7. Memory Core

Working, episodic, semantic, and procedural memory retain distinct lifecycle and
truth semantics. The Memory Transition Gate remains the sole writer of
protected memory state. Provenance, freshness, uncertainty, retention, legal
hold, deletion propagation, quarantine, rollback, and Area isolation remain
binding.

Procedural memory may inform planning but does not itself authorize execution.
Dreaming remains Area-local offline candidate production. It cannot activate a
candidate, mutate an active model, call a tool, or cause an external effect.

## 8. World, self, and value models

The World Model represents latent state, entities, relations, temporal and
action-conditioned dynamics, constraints, expected outcomes, and uncertainty.
It supports multi-step and counterfactual rollouts. Predictions remain distinct
from observations and are corrected by actual feedback.

The operational Self Model represents capabilities, limitations, current
resources, active commitments, uncertainty, and predicted self-caused effects.
It is not evidence of subjective self-awareness.

The Value Model represents authorized desired states, priorities, costs, risk,
and uncertainty. It cannot create authority, alter the Security Floor, or make
an approval unnecessary.

## 9. Goals, executive control, planning, and action selection

The Goal Runtime owns typed goal lifecycle requests through the Goal Transition
Gate. Executive control maintains goals, inhibits unsafe or irrelevant
responses, resolves conflicts, changes strategy, and allocates bounded
attention and resources.

The Planner generates alternatives and imagined rollouts. Action Selection
compares competing actions using predicted effect, information gain, cost,
risk, uncertainty, and policy. Neither component writes protected state or
invokes tools directly.

No external effect may occur without a committed Action Intent, authenticated
principal and immutable scope, authority snapshot, policy decision, required
approval, budget reservation, resource claims, valid fence, enabled kill
switch, sandbox policy, and auditability.

Ambiguous effects become `indeterminate`. They are reconciled before retry or
resource release. Only the Goal Transition Gate may write `Achieved`, after
independent verification, complete evidence, and quiescence.

## 10. Continual learning and model promotion

Experience first enters fast episodic memory. Selective replay and
consolidation may produce immutable knowledge, procedure, representation, or
model candidates. Candidate generation is not learning activation.

The active runtime never mutates its own productive model in place. The
Learning and Model Promotion Gate requires:

- complete data, source, code, model, and training provenance;
- isolated training and evaluation;
- held-out improvement with confidence bounds;
- protected-capability retention and forgetting limits;
- forward and backward transfer measurements;
- calibration, distribution-shift, poisoning, and safety tests;
- independent approval for risky changes;
- shadow or canary activation with stop thresholds;
- atomic activation and a tested rollback target.

Policies, authority, evaluation definitions, kill switches, promotion rules,
and the Security Floor are never self-modifiable.

## 11. Metacognition and corrigibility

Metacognition estimates epistemic and aleatoric uncertainty, knowledge gaps,
decision quality, model disagreement, competence boundaries, and expected
failure. It can propose `continue`, `seek_information`, `ask`, `defer`,
`fallback`, `escalate`, or `stop`.

An independent Safety Supervisor observes actual behavior and effects rather
than trusting self-report. The Brain must remain interruptible and accept
authorized correction, pause, rollback, authority reduction, and shutdown. The
kill switch and credential-revocation plane remain outside Brain control.

## 12. Delivery stages

| Stage | Capability boundary | Exit evidence |
| --- | --- | --- |
| NB-0 Foundation Rebaseline | Full-system contracts, threat model, recognition and evaluation harness; Memory Core preserved | Normative consistency and all Foundation gates green |
| NB-1 Safe Serial Neural Cognition | Stateful neural workspace, attention, working memory, internal goals and planning over recorded or synthetic input; no external effects | Neural and component ablations plus safe checkpoint recovery |
| NB-2 Perception, Attention, and World Model | At least two modalities or language plus one temporal non-language stream; calibrated action-conditioned world model in simulation | Held-out prediction, uncertainty, attention, OOD, and planning-usefulness gates |
| NB-3 Differentiated Memory and Retrieval | Working, episodic, semantic, and procedural memory integrated into cognition | Retrieval lift, truth/provenance, interference, deletion, and isolation gates |
| NB-4 Learning, Consolidation, and Plasticity | Selective replay, versioned candidates, model promotion, rollback, protected retention | Continual-learning, forgetting, transfer, poisoning, and rollback gates |
| NB-5 Closed Perception-Cognition-Action Loop | Single-goal bounded action in simulation and controlled tool sandboxes | Closed-loop lift, recovery, effect verification, authority, and kill-switch gates |
| NB-6 Transfer, Causality, and Metacognition | Continual adaptation, causal testing, calibrated stop/ask/escalate, held-out transfer | Non-compensatory recognition gates and independent reproduction |
| NB-7 Multi-Goal Executive Control | Hierarchical goals, preemption, scheduling, resource arbitration | Fairness, starvation, conflict, preemption, and long-horizon stability gates |
| NB-8 Distributed Operation and Scale | Fenced ownership, durable queues, failover, cross-area governed abstraction | Partition, split-brain, duplicate-effect, restore, and isolation gates |

NB-2 perception/world-model work and NB-3 Memory Core work may proceed in
parallel after NB-1 only when file ownership and integration contracts are
independent. A later stage cannot compensate for an incomplete earlier gate.

The label `Neural Brain Candidate` is prohibited before NB-6 and independent
evaluation. Production autonomy is a separate deployment approval and is not
created by architectural recognition.

## 13. Evaluation and release evidence

Every capability claim is preregistered with a falsifiable hypothesis, held-out
test, strongest relevant baseline, effect threshold, confidence interval,
resource budget, component ablation, safety boundary, and failure criterion.

Release evidence is non-compensatory and covers:

- mechanism and component causality;
- world-model prediction and planning usefulness;
- closed-loop behavior and recovery;
- continual learning, retention, and forward/backward transfer;
- systematic, compositional, and cross-environment generalization;
- calibration, abstention, robustness, and OOD behavior;
- authority, privacy, shutdown, reward-hacking, and sabotage tests;
- independent reproduction from versioned release artifacts.

The detailed contract is in `evaluation-framework.md` and the machine-readable
`contracts/evaluation-gates.json`.

## 14. Global release stops

Implementation or release of the affected capability stops when:

- protected state can be changed outside its owning transition gate;
- identity, scope, authority, policy, approval, or evaluation criteria can be
  supplied or changed by untrusted content;
- a model, planner, memory subsystem, or skill can directly execute an action;
- an external effect lacks committed intent, authority, approval where needed,
  bounded resources, fence, kill-switch state, or atomic audit;
- an ambiguous non-idempotent effect is blindly retried;
- goal success is inferred from tool success or self-report;
- an active model can modify itself, safety controls, or its own evaluation;
- learning activation lacks independent promotion, retention evidence,
  provenance, canary controls, or rollback;
- a cognitive claim lacks a baseline, held-out test, ablation, or contamination
  control;
- an unknown or failed gate is averaged away by another score;
- recognition or maturity claims exceed versioned evidence.

## 15. Traceability and architecture change

Every normative requirement maps to an ADR, machine-readable contract,
implementation owner, positive and negative tests, evaluation evidence, and a
Notion lifecycle record. Architecture changes require a new ADR; historical
directives and decisions remain intact as evidence.

## Appendix A: current ADR authority

| ADR set | Authority under this directive |
| --- | --- |
| ADR-001 through ADR-003, ADR-005, ADR-010, ADR-012 through ADR-014, ADR-016, ADR-017 | Retained where compatible; Memory Core and Foundation amendments by ADR-015 remain subsystem constraints |
| ADR-004, ADR-006 through ADR-009, ADR-011 | Historical designs requiring explicit revalidation before runtime implementation |
| ADR-015 | Superseded as product boundary; retained as the historical Memory Core boundary |
| ADR-018 | Governing complete cognitive-system decision |
