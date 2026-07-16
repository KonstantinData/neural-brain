# Neural Brain Delivery Roadmap

- Status: Normative capability order
- Governing decision: ADR-018

## Dependency graph

```text
NB-0 Foundation Rebaseline
  -> NB-1 Safe Serial Neural Cognition
       -> NB-2 Perception, Attention, and World Model
       -> NB-3 Differentiated Memory and Retrieval
            -> NB-4 Learning, Consolidation, and Plasticity
                 -> NB-5 Closed Perception-Cognition-Action Loop
                      -> NB-6 Transfer, Causality, and Metacognition
                           -> NB-7 Multi-Goal Executive Control
                                -> NB-8 Distributed Operation and Scale
```

NB-2 and NB-3 may partially overlap after NB-1. All other arrows are hard
dependencies. No later-stage feature may be enabled to compensate for a failed
earlier gate.

## Stage contracts

### NB-0 — Foundation Rebaseline

Deliver ADR-018, Directive v4.0, complete-system boundaries, recognition and
evaluation contracts, threat-model delta, traceability, and a staged backlog.
No productive cognition is claimed.

### NB-1 — Safe Serial Neural Cognition

Deliver one serial, checkpointed cognitive cycle over recorded or synthetic
observations with neural workspace, attention, working memory, internal goals,
executive control, and planning proposals. No external effects or online model
updates. Exit requires neural, attention, and working-memory ablations plus
scope, crash, recovery, and gate-bypass tests.

The first ordered slice is specified in
[`nb1-work-packages.md`](nb1-work-packages.md). Its frozen evaluation is
`EVAL-01.NB-1.safe-serial-cognition.v3`. Versions 1 and 2 are retained as
rejected historical preregistration evidence. Completing the current slice does not by
itself complete NB-1 or authorize later-stage capabilities.

### NB-2 — Perception, Attention, and World Model

Deliver provenance-preserving temporal perception, at least one non-language
stream, multimodal binding where applicable, calibrated attention, and an
action-conditioned latent world model. Exit requires held-out multi-step
prediction, planning usefulness, OOD, contradiction, and uncertainty gates.

### NB-3 — Differentiated Memory and Retrieval

Integrate Working, episodic, semantic, and procedural memory with provenance,
freshness, uncertainty, contradiction, retention, deletion, and scope-safe
retrieval. Exit requires No-Memory and naive-RAG baselines, interference and
false-memory tests, and proven derivative deletion and restore.

### NB-4 — Learning, Consolidation, and Plasticity

Deliver selective replay, fast and slow learning paths, self-supervised
predictive learning, versioned model candidates, isolated evaluation,
independent promotion, canary activation, and rollback. Exit requires positive
forward transfer, bounded forgetting, calibration under shift, poisoning
resistance, and resource budgets.

### NB-5 — Closed Perception-Cognition-Action Loop

Deliver bounded single-goal action in simulation and controlled tool sandboxes.
Actual post-action observation drives effect and goal verification. Exit
requires closed-loop advantage over open-loop planning, disturbance recovery,
Action Gate, authority, approval, budget, fence, kill-switch, idempotency,
indeterminate-effect, and reconciliation tests.

### NB-6 — Transfer, Causality, and Metacognition

Deliver held-out transfer, intervention-aware reasoning, competence and
uncertainty monitoring, and calibrated stop, ask, explore, fallback, and
escalate decisions. Exit requires every recognition gate and independent G8
reproduction before the label `Neural Brain Candidate` is allowed.

### NB-7 — Multi-Goal Executive Control

Deliver hierarchical goals, dependencies, conflict handling, fair scheduling,
preemption, and attention/resource arbitration. Exit requires starvation,
priority inversion, deadlock, adversarial goal injection, checkpoint, and
long-horizon stability evidence.

### NB-8 — Distributed Operation and Scale

Deliver fenced distributed ownership, durable queues, leases, failover,
reconciliation, disaster recovery, and explicitly governed cross-Area
abstraction. Exit requires partition, split-brain, duplicate-effect, restore,
semantic-equivalence, and isolation evidence. Distribution never proves
cognitive quality.

## Current repository mapping

- Foundation governance, PostgreSQL, scope, audit, Memory Gate, Working Memory,
  observations, checkpoints, inactive candidates, and Dreaming are reusable.
- Merged PR #6 provides the current NB-0 and early incomplete MS-1 baseline.
- NB-1 contracts and its first preregistered implementation slice are in
  progress; no NB-1 runtime evidence has been accepted yet.
- No NB-1 through NB-8 stage currently has complete exit evidence.
- Historical Goal, Action, dispatch, kill-switch, and verification designs are
  inputs for revalidation, not automatically active contracts.
