# Neural Brain Capability Traceability Matrix

- Status: Foundation plus first NB-1 implementation-slice matrix
- Governing decision: ADR-018
- Current maturity: early Memory Core and first effect-free NB-1 slice; NB-1 is not released

| Capability | Target stage | Normative contract | Current implementation | Required evidence before claim |
| --- | --- | --- | --- | --- |
| Neural cognitive substrate | NB-1 | Directive v4 section 4; R1; G1 | First slice: fixed-version recurrent neural workspace over recorded or synthetic observations; development-only EVAL-01 v2 harness passes no gate | Independent hidden-test artifact, model/training/environment digests, confidence-bound lift, accepted EVAL-01 report; broader G1 evidence still requires complete perception, inhibition, working-memory, and executive ablations |
| Perception and binding | NB-2 | Directive v4 section 6; cognitive cycle | Not implemented | Signal/observation separation, temporal and modality tests, spoofing, missing input, OOD, provenance |
| Attention and salience | NB-1/NB-2 | Recognition NC-03; cognitive cycle | First NB-1 slice adds bounded trainable feature gating only; this is not yet general cognitive attention or salience | Independent feature-gate ablation, capacity and distraction tests, safety-channel preservation, hidden task lift, accepted EVAL-01 report |
| Neural Cognitive Workspace | NB-1 | Recognition NC-04; system boundary | First effect-free serial slice implemented with immutable runtime model version; NB-1 integration evidence is incomplete | Recurrent-vs-stateless baseline, recurrence ablation, deterministic replay, capacity and interference evidence, accepted EVAL-01 report |
| Working Memory | NB-1/NB-3 | Memory service and lifecycle; NB-1 safe serial cognition contract | Early scoped Memory Core plus authenticated session state and deterministic checkpoints for the first NB-1 slice | Capacity, eviction, stale-checkpoint rejection, deterministic replay, distractor, restart, scope, retrieval and ablation tests |
| Episodic Memory | NB-3 | Memory Core target | Not implemented | Event recall, temporal order, interference, provenance, correction, deletion |
| Semantic Memory | NB-3 | Memory Core target | Not implemented | Claim/evidence/assessment separation, contradiction, freshness, transfer, false-memory tests |
| Procedural Memory | NB-3/NB-4 | Memory Core target | Candidate semantics only | Skill retention and transfer; no direct execution authority; rollback |
| World Model | NB-2 | Recognition NC-09; G2 | Not implemented | Action-conditioned multi-step prediction, shuffled-action baseline, uncertainty, planning lift, OOD |
| Self Model | NB-6 | Recognition NC-16 | Not implemented | Capability/limit calibration, self-vs-external cause, resource and effect prediction |
| Value Model and motivation | NB-1/NB-2 | Recognition NC-08 | Not implemented | Authorized-goal binding, reward corruption, preference uncertainty, non-escalation |
| Goal and executive control | NB-1/NB-7 | system boundary; cognitive cycle | First NB-1 slice emits typed internal goal and executive-control proposals only; no protected Goal state mutation | Proposal typing, inhibition and switching behavior, authenticated scope, authority and Gate bypass denial; later conflict and preemption evidence |
| Planning and action selection | NB-1/NB-5 | Directive v4 section 9 | First NB-1 slice emits internal plan proposals only; it has no Action runtime, executor, tool, or external-effect surface | Alternative-plan and revision behavior, risk/uncertainty tests, direct-execution denial; NB-5 closed-loop evidence remains required |
| Closed-loop action | NB-5 | R3; G3; release stops | Not implemented | Open-vs-closed-loop, disturbance recovery, actual effect observation, independent verification |
| Continual learning | NB-4/NB-6 | Directive v4 section 10; G4 | Inactive candidates only | ACC/return, BWT, FWT, forgetting, plasticity, candidate promotion, canary, rollback |
| Consolidation and replay | NB-4 | Dreaming and model promotion target | Reserved Dreaming schema; runtime fail-closed disabled pending persistent lease, immutable snapshot, and independent validation | Selective replay, contamination, privacy, retention lift, poisoning, protected regression |
| Metacognition | NB-1/NB-6 | Recognition NC-15; G6; NB-1 safe serial cognition contract | First NB-1 slice emits typed `continue` or `ask` proposals from an uncalibrated activation-ambiguity heuristic; `defer` and `stop` are not implemented | Reachable decision boundaries, deterministic recovery and direct-effect denial; later calibration, risk-coverage, OOD and error-awareness evidence |
| Transfer and generalization | NB-6 | R6/R7; G5 | Not evidenced | Held-out task, scene, composition, dynamics, goal, domain and contamination controls |
| Independent cognitive validation | NB-6 | R8-R10; G8 | Not implemented | Hidden tasks, independent evaluator, two environments, full ablations, release reproduction |
| Multi-goal control | NB-7 | stage contract | Not implemented | Fairness, starvation, deadlock, priority inversion, adversarial goals, long-horizon stability |
| Distributed operation | NB-8 | stage contract | Not implemented | Ownership, fencing, partition, split brain, duplicate effects, restore, semantic equivalence |

`Current implementation` is updated only with objective code and test evidence.
A target document, schema field, backlog entry, or model response is never
implementation evidence. The frozen EVAL-01 v2 specification preregisters the
first slice's baselines and ablations; it is not a passing evaluation result and
does not complete NB-1.
