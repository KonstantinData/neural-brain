# ADR-018: Neural Brain is a complete cognitive system

- Status: Accepted
- Date: 2026-07-16
- Decision record: https://app.notion.com/p/39f1c1ac5ec0814cbefff9a5a41887b8
- Supersedes: ADR-015

## Context

ADR-015 defined Neural Brain as a governed memory system and permanently placed
goals, planning, action selection, execution, feedback, and autonomous behavior
outside the product boundary. That decision produced a useful Memory Core
baseline, but it made the repository incapable of satisfying the operational
recognition standard for a Neural Brain.

The accepted product goal is now an integrated, neural, plastic cognitive
system. The name is justified only when one protected system integrates
perception, attention, working and long-term memory, executive control, world,
self, and value models, planning, action selection, feedback, continual
learning, metacognition, and measurable transfer.

## Decision

Neural Brain owns the complete protected cognitive loop:

```text
perceive -> attend -> integrate -> remember -> model -> decide -> act
        -> observe effects -> verify -> learn -> consolidate
```

The existing governed memory system becomes the `Memory Core` subsystem. Its
scope, provenance, privacy, retention, deletion, transition-gate, PostgreSQL,
and audit invariants remain binding.

The Brain may own internal goals, plans, action intents, cognitive state,
learning candidates, model versions, and outcome verification. It may cause an
external effect only through a separate protected control plane with
authenticated authority, bounded policy, required approval, budget and
resource claims, an Action Transition Gate, a fenced executor, an independent
verifier, kill switches, and atomic audit evidence.

Trainable neural mechanisms must make a causal contribution to cognition. An
LLM, embedding model, vector database, workflow graph, or collection of agents
does not by itself satisfy this requirement. Spiking neurons are optional
unless the project makes a neurophysiological-fidelity or neuromorphic claim.

Continual learning may not mutate an active model directly. Learning produces
immutable candidates that pass retention, transfer, calibration, safety,
provenance, independent-promotion, canary, and rollback gates before
activation.

The repository distinguishes target architecture from implemented maturity.
No capability may be represented as implemented, enabled, safe, or released
until its non-compensatory evidence gate passes.

## Consequences

- Architecture Directive v4.0 becomes the normative full-system baseline.
- ADR-015 and Architecture Directive v2.0 remain historical evidence but lose
  implementation authority.
- Goal, Action, independent verification, dispatch, and reconciliation
  decisions superseded by ADR-015 must be revalidated under this ADR before
  dependent runtime implementation.
- Memory Core work remains reusable and may advance independently where it does
  not reassert a memory-only product boundary.
- The delivery model expands from memory stages to cognitive-system stages.
- Release evidence must include cognitive behavior, ablation, closed-loop,
  continual-learning, retention, transfer, calibration, and safety evaluation.
- The architecture does not claim consciousness, sentience, subjective
  experience, human equivalence, or biological fidelity.

## Rejected alternatives

### Keep Neural Brain as a memory-only product

Rejected because the permanent exclusion of integrated cognition and feedback
contradicts the accepted product goal and recognition standard.

### Rename the memory repository and create an unrelated orchestration system

Rejected as the primary direction because it would fragment the integrated
cognitive state. The Memory Core remains a separately protected subsystem, but
it is part of Neural Brain.

### Restore the pre-ADR-015 agent architecture unchanged

Rejected because the new target requires research-backed neural substance,
world and self models, continual learning, metacognition, and falsifiable
evaluation in addition to agent execution. Historical contracts are inputs for
revalidation, not automatic implementation authority.
