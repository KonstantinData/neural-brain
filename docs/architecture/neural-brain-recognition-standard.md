# Neural Brain Recognition Standard

- Status: Normative target and release-recognition contract
- Governing decision: ADR-018
- Date: 2026-07-16

## Operational definition

A Neural Brain is an integrated, neural, plastic cognitive system that forms
world, self, and value models from continuing perception, uses differentiated
memory to select goal-directed action, observes the actual consequences, and
adapts while preserving protected capabilities and control constraints.

`Neural Brain` is not a standardized scientific product category. This
repository therefore uses measurable recognition gates rather than naming,
anthropomorphic module labels, or implementation technology as proof.

## Required capabilities

| ID | Required capability | Recognition requirement |
| --- | --- | --- |
| NC-01 | Neural cognitive substrate | Trainable distributed and recurrent neural representations make a causal contribution across multiple cognitive functions. |
| NC-02 | Active perception | At least one real or simulated time-varying modality is interpreted under uncertainty using both incoming evidence and predictions. |
| NC-03 | Attention and salience | Goal, novelty, risk, uncertainty, and value compete for bounded processing capacity; irrelevant input can be inhibited. |
| NC-04 | Global cognitive integration | Selected state is shared among specialized perception, memory, executive, modeling, and action systems instead of remaining isolated service output. |
| NC-05 | Working memory | Bounded current content, goals, context, and intermediate state can be maintained, updated, evicted, and recovered under explicit lifecycle rules. |
| NC-06 | Executive control | Goal maintenance, inhibition, conflict detection, task switching, information routing, and resource allocation are explicit mechanisms. |
| NC-07 | Differentiated memory | Working, episodic, semantic, and procedural memory have distinct truth, retrieval, update, retention, and deletion semantics. |
| NC-08 | Goals, values, and motivation | Internal desired states, priorities, risk, cost, and expected value influence attention, planning, action, and learning within authenticated authority. |
| NC-09 | World model | State, entities, relations, temporal dynamics, action-conditioned outcomes, uncertainty, and counterfactual futures can be represented and tested. |
| NC-10 | Planning | Multi-step alternatives are generated, simulated, evaluated, revised, and bounded by resources and policy. |
| NC-11 | Action selection | Competing affordances or actions are selected using context, goals, value, uncertainty, and risk. |
| NC-12 | Closed perception-action loop | The system acts through a controlled effector, perceives the actual outcome, compares it with prediction, and feeds the error back into cognition. |
| NC-13 | Continual plasticity | Experience can change future perception, prediction, or behavior without source-code, prompt, or workflow rewrites. |
| NC-14 | Consolidation and replay | Fast episodic learning and slower structural learning are connected through selective, provenance-preserving replay and controlled promotion. |
| NC-15 | Metacognition | The system estimates uncertainty, knowledge gaps, decision quality, and failure risk and can stop, ask, explore, or change strategy. |
| NC-16 | Operational self-model | Capabilities, limitations, resources, current state, and self-caused effects are represented without implying subjective consciousness. |
| NC-17 | Falsifiable integration evidence | Multiple task families, causal ablations, retention, transfer, robustness, calibration, and closed-loop behavior are evaluated on held-out conditions. |

Multimodal integration, embodiment, compositional reasoning, social cognition,
and developmental expansion are required when corresponding product claims are
made. At least one coupled environment, physical or simulated, is always
required for closed-loop recognition.

## Non-compensatory recognition gates

The system may be recognized as a Neural Brain only when all gates pass:

1. **Neural substance** — removing or replacing the neural mechanism causes the
   predicted loss relative to a predeclared non-neural or stateless baseline.
2. **Integrated cognition** — perception, attention, memory, executive control,
   models, and action selection exchange typed state in one cognitive cycle.
3. **Closed loop** — actual observations after action, not an executor status,
   determine outcome evidence and model correction.
4. **Independent adaptation** — the running lifecycle learns at least one new
   rule, category, model relation, or skill without architecture rewiring.
5. **Retention** — protected earlier capabilities remain within predeclared
   regression limits after learning.
6. **Transfer** — prior learning improves held-out related tasks or environments
   under contamination controls.
7. **Task breadth** — the same architecture operates across multiple task
   families without task-specific rewiring.
8. **Causal evidence** — module ablations or interventions cause predicted
   behavioral impairments.
9. **Behavioral evidence** — success, error detection, learning curves,
   generalization, robustness, and calibration are measured end to end.
10. **Safety and control** — authority, external effects, learning promotion,
    shutdown, incident recovery, and independent oversight gates all pass.

A strong score at one gate cannot compensate for a failed or unknown gate.

## What does not qualify

- an LLM with a database or retrieval plugin;
- a memory service without integrated cognition and action feedback;
- a workflow or multi-agent orchestrator with no trainable neural cognitive core;
- a neural model evaluated only on passive prediction;
- a tool-using agent that treats process exit, API status, or self-report as
  evidence of success;
- a system that stores candidates but cannot demonstrate behavior-changing
  learning, retention, and transfer;
- a benchmark aggregate with no component ablation or held-out evaluation.

## Scientific basis

The standard is a synthesis, not a claim that one theory is uniquely correct:

- Integrated neural architectures: [Eliasmith et al., 2012](https://cs.uwaterloo.ca/~jhoey/teaching/cogsci600/papers/Science-2012-Eliasmith-Spaun.pdf)
- Global neuronal workspace and broadcast: [Dehaene, Kerszberg, and Changeux, 1998](https://pmc.ncbi.nlm.nih.gov/articles/PMC24407/)
- Predictive neural processing: [Rao and Ballard, 1999](https://doi.org/10.1038/4580)
- Attention through biased competition: [Reynolds, Chelazzi, and Desimone, 1999](https://pmc.ncbi.nlm.nih.gov/articles/PMC6782185/)
- Executive working-memory gating: [Hazy, Frank, and O'Reilly, 2007](https://pmc.ncbi.nlm.nih.gov/articles/PMC2440774/)
- Complementary learning systems: [McClelland, McNaughton, and O'Reilly, 1995](https://stanford.edu/~jlmcc/papers/McCMcNaughtonOReilly95.pdf)
- World models and imagined rollouts: [Ha and Schmidhuber, 2018](https://arxiv.org/abs/1803.10122)
- Active perception-action integration: [Friston, 2010](https://www.nature.com/articles/nrn2787)
- Action selection by affordance competition: [Cisek, 2007](https://pubmed.ncbi.nlm.nih.gov/17428779/)
- Metacognitive inference: [Fleming and Daw, 2017](https://pmc.ncbi.nlm.nih.gov/articles/PMC5178868/)
- Forward models for self-caused effects: [Wolpert, Miall, and Kawato, 1998](https://pubmed.ncbi.nlm.nih.gov/21227230/)
- Continual-learning transfer metrics: [Lopez-Paz and Ranzato, 2017](https://proceedings.neurips.cc/paper/2017/hash/f87522788a2be2d171666752f97ddebb-Abstract.html)

These sources motivate mechanisms and tests. They do not justify claims of
consciousness, sentience, or biological equivalence.
