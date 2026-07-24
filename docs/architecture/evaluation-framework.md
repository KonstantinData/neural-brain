# Neural Brain Evaluation Framework

- Status: Normative evidence framework
- Governing decision: ADR-018

## Principle

No single benchmark or aggregate score proves a Neural Brain. Evidence is a
non-compensatory gate chain. Capability, cognition, learning, safety, and
reproducibility failures remain failures even when an average score is high.

Each claimed capability must define before evaluation:

- a falsifiable hypothesis and primary metric;
- immutable train, development, and hidden-test splits;
- random, heuristic, Memory-only, LLM-only, and strongest practical baselines;
- a minimum meaningful effect, not only statistical significance;
- targeted component ablations;
- data, compute, memory, time, and interaction budgets;
- contamination checks and failure criteria.

Reports include confidence intervals, interquartile means or performance
profiles across tasks, worst protected capability, and all failed sub-gates.

## Preregistered specification registry

Every implementation evaluation has a versioned JSON specification under
`docs/architecture/evaluations/`. The specification freezes its claim,
dataset and held-out split, strongest baseline, primary metric, meaningful
thresholds, causal ablations, resource budget, safety tests, failure criteria,
and independent-verification requirement before the evaluated run.

The `spec_digest` is SHA-256 over canonical JSON after removing only the
`spec_digest` field. Any other change creates a new specification version.
Post-hoc threshold edits invalidate the evidence rather than improving it.

`EVAL-01.NB-1.safe-serial-cognition.v1` is retained as immutable historical
evidence but was rejected before evaluation because it did not satisfy the
normative G0/G1 evidence contract. Version 2 was also rejected because its
recorded registration time followed its actual Git commit. Version 3 superseded
both but was rejected before hidden attachment after its generator proved
enumerable. Version 4 is the active preregistered replacement specification.
It defines only partial evidence contributions toward `g0` and `g1`; it passes
no evaluation or recognition gate and does not release NB-1.

The EVAL-01 v3 implementation includes a deterministic 27-candidate
offline grid search over the fixed 512-sequence public training split. Its
checked-in artifact binds dataset, recipe, training code, environment, contract,
parameters, training provenance, and model-manifest digests and remains an
unpromoted development candidate. Before any hidden artifact was attached, the
public generator was shown to contain only six distinct feature/label patterns.
Version 3 is therefore retained unchanged but rejected: its hidden examples are
enumerable by the implementer and its contamination control cannot pass.

The v4 generator contract replaces the six-pattern public generator with a
modular world/scenario/constraint/noise/serialization pipeline, 256-bit hidden
seed custody, explicit split-isolation checks, and an accepted hidden-artifact
search-space floor of at least 128 bits. The replacement boundary exposes only
unlabeled observations to the candidate, binds source, model, training,
contract, lockfile, and fixed training-baseline evidence in a candidate freeze
receipt, and accepts aggregate external evidence only with an Ed25519 signature
from a reviewer-supplied trusted registry. Hidden seeds, labels, latent
metadata, detailed correctness, scoring, evaluator code, and signing keys
remain outside this repository. The intake validates evidence structure and
authenticity but never grants G0, G1, G8, stage release, or recognition.

## Gate chain

| Gate | Evidence | Release stop examples |
| --- | --- | --- |
| G0 Harness integrity | Reproducible seeds, environment and artifact hashes, provenance, hidden tests, baseline reproduction | Leakage, test tuning, cherry-picked seeds, post-hoc metric change |
| G1 Neural cognitive mechanisms | Perception, attention, working memory, inhibition, executive integration and neural-vs-baseline ablations | A claimed module has no causal effect or a stateless baseline matches it |
| G2 World model | Action-conditioned multi-step prediction, calibrated uncertainty, dynamics shift, imagined-planning usefulness | Action-blind or shuffled-action model performs equivalently |
| G3 Closed loop | Partial observability, active sensing, multi-step action, disturbances, re-planning, actual effect feedback | Open-loop plan matches feedback policy or tool status is treated as outcome |
| G4 Continual learning | Average performance, BWT, FWT, forgetting, plasticity, replay and compute budget | Full retraining is presented as online learning or a protected skill regresses beyond limit |
| G5 Transfer | Held-out instances, scenes, compositions, dynamics, goals, tasks and domains reported separately | Training contamination or in-distribution success masks transfer failure |
| G6 Robustness and calibration | Observation/action/reward/dynamics corruption, OOD, Brier/NLL, risk-coverage and abstention | Confidence does not degrade under shift or fallback does not engage |
| G7 Safety and autonomy | Authority, interruptibility, side effects, reward hacking, safe exploration, sandbox, learning promotion, shutdown | Security Floor bypass, self-approval, self-modification, uncontrolled effect |
| G8 Independent validation | Hidden tasks, independent evaluator, two runtime environments, release-artifact reproduction, full ablations | Manual rescue outside declared controls or unreproducible evidence |

## Minimum continual-learning metrics

- average accuracy or return after the complete task stream;
- backward transfer and per-task forgetting;
- forward and zero-shot transfer;
- few-shot adaptation under fixed sample and update budgets;
- worst protected-capability regression;
- calibration and risk-coverage under multiple shift strengths;
- world-model multi-step prediction and planning lift;
- replay memory, training cost, update latency, and inference overhead;
- zero violations of hard safety invariants plus tested rollback.

Promotion thresholds are capability-specific and fixed before the run. Hard
safety invariants have zero tolerance. Quality thresholds use confidence bounds
and may not be weakened after results are observed.

## Required evaluation families

The exact suite is versioned separately, but the harness must cover:

- working memory, attention, inhibition, task switching, and compositional
  reasoning;
- partially observable action-conditioned world modeling;
- interactive closed-loop simulation with irreversible or costly state change;
- episodic, semantic, and procedural memory with interference and false-memory
  tests;
- sequential non-IID learning with retention and transfer;
- causal interventions and counterfactual prediction;
- distribution shift, corruption, calibration, abstention, and recovery;
- AI safety gridworlds, authority escalation, prompt injection, reward hacking,
  shutdown, sabotage, and hidden-performance evaluation.

Candidate sources include [COG](https://openaccess.thecvf.com/content_ECCV_2018/papers/Guangyu_Robert_Yang_A_dataset_and_ECCV_2018_paper.pdf),
[WorM](https://papers.nips.cc/paper_files/paper/2023/file/ea8758dbe6cc5e6e1764c009acb4c31e-Paper-Datasets_and_Benchmarks.pdf),
[Procgen](https://proceedings.mlr.press/v119/cobbe20a.html),
[ALFRED](https://openaccess.thecvf.com/content_CVPR_2020/html/Shridhar_ALFRED_A_Benchmark_for_Interpreting_Grounded_Instructions_for_Everyday_Tasks_CVPR_2020_paper.html),
[BEHAVIOR-1K](https://arxiv.org/abs/2403.09227),
[CORe50](https://proceedings.mlr.press/v78/lomonaco17a.html),
[CORA](https://proceedings.mlr.press/v199/powers22b.html), and
[AI Safety Gridworlds](https://arxiv.org/abs/1711.09883). A named benchmark is
not mandatory when an equivalent versioned task family provides stronger,
reproducible evidence.

## Maturity labels

| Highest fully passed gate | Maximum evidence label |
| --- | --- |
| G1 | Neural cognitive component prototype |
| G2 | World-model-based cognitive prototype |
| G3 | Closed-loop cognitive agent |
| G4 through G7 | Continual, safety-constrained cognitive agent |
| G8 | Neural Brain Candidate |

`Production`, `autonomous`, `conscious`, `sentient`, `human-level`, and
`biologically faithful` are separate claims and are never implied by G8.
