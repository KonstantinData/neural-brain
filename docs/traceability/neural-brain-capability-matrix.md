# Neural Brain Capability Traceability Matrix

- Status: Foundation target matrix
- Governing decision: ADR-018
- Current maturity: early Memory Core; no complete Neural Brain stage released

| Capability | Target stage | Normative contract | Current implementation | Required evidence before claim |
| --- | --- | --- | --- | --- |
| Neural cognitive substrate | NB-1 | Directive v4 section 4; R1; G1 | Not implemented | Learned-vs-fixed, recurrent-vs-stateless, non-neural and LLM-only baselines; causal ablation |
| Perception and binding | NB-2 | Directive v4 section 6; cognitive cycle | Not implemented | Signal/observation separation, temporal and modality tests, spoofing, missing input, OOD, provenance |
| Attention and salience | NB-1/NB-2 | Recognition NC-03; cognitive cycle | Memory-ingress salience only; no cognitive attention | Capacity, distraction, safety-channel, attention ablation, task lift |
| Neural Cognitive Workspace | NB-1 | Recognition NC-04; system boundary | Not implemented | Cross-module integration, capacity, interference, broadcast and workspace ablations |
| Working Memory | NB-1/NB-3 | Memory service and lifecycle | Early scoped implementation | Capacity, eviction, checkpoint, distractor, restart, scope, retrieval and ablation tests |
| Episodic Memory | NB-3 | Memory Core target | Not implemented | Event recall, temporal order, interference, provenance, correction, deletion |
| Semantic Memory | NB-3 | Memory Core target | Not implemented | Claim/evidence/assessment separation, contradiction, freshness, transfer, false-memory tests |
| Procedural Memory | NB-3/NB-4 | Memory Core target | Candidate semantics only | Skill retention and transfer; no direct execution authority; rollback |
| World Model | NB-2 | Recognition NC-09; G2 | Not implemented | Action-conditioned multi-step prediction, shuffled-action baseline, uncertainty, planning lift, OOD |
| Self Model | NB-6 | Recognition NC-16 | Not implemented | Capability/limit calibration, self-vs-external cause, resource and effect prediction |
| Value Model and motivation | NB-1/NB-2 | Recognition NC-08 | Not implemented | Authorized-goal binding, reward corruption, preference uncertainty, non-escalation |
| Goal and executive control | NB-1/NB-7 | system boundary; cognitive cycle | Historical designs only | State-machine, inhibition, conflict, switching, preemption, authority and Gate bypass tests |
| Planning and action selection | NB-1/NB-5 | Directive v4 section 9 | Historical designs only | Multi-step alternatives, model-based lift, plan revision, risk/uncertainty, direct-execution denial |
| Closed-loop action | NB-5 | R3; G3; release stops | Not implemented | Open-vs-closed-loop, disturbance recovery, actual effect observation, independent verification |
| Continual learning | NB-4/NB-6 | Directive v4 section 10; G4 | Inactive candidates only | ACC/return, BWT, FWT, forgetting, plasticity, candidate promotion, canary, rollback |
| Consolidation and replay | NB-4 | Dreaming and model promotion target | Reserved Dreaming schema; runtime fail-closed disabled pending persistent lease, immutable snapshot, and independent validation | Selective replay, contamination, privacy, retention lift, poisoning, protected regression |
| Metacognition | NB-6 | Recognition NC-15; G6 | Not implemented | Calibration, risk-coverage, stop/ask/fallback/escalate quality, OOD, error awareness |
| Transfer and generalization | NB-6 | R6/R7; G5 | Not evidenced | Held-out task, scene, composition, dynamics, goal, domain and contamination controls |
| Independent cognitive validation | NB-6 | R8-R10; G8 | Not implemented | Hidden tasks, independent evaluator, two environments, full ablations, release reproduction |
| Multi-goal control | NB-7 | stage contract | Not implemented | Fairness, starvation, deadlock, priority inversion, adversarial goals, long-horizon stability |
| Distributed operation | NB-8 | stage contract | Not implemented | Ownership, fencing, partition, split brain, duplicate effects, restore, semantic equivalence |

`Current implementation` is updated only with objective code and test evidence.
A target document, schema field, backlog entry, or model response is never
implementation evidence.
