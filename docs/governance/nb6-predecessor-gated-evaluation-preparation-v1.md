# NB-6 Predecessor-Gated Evaluation Preparation

- Status: Preparation only; all predecessor exit evidence is currently incomplete.
- Governing decision: ADR-018
- Machine-readable contract: docs/architecture/contracts/nb6-predecessor-gated-evaluation-v1.json

## Purpose and boundary

This package makes the future NB-6 acceptance boundary reviewable before NB-5
qualification. It creates no runtime capability, candidate, hidden dataset,
evaluation result, stage release, recognition, authority, or external effect.
It is deliberately not an executable evaluation specification: a future
immutable specification can be registered only after the contract's entry
dependencies are independently met.

## Future experiment design

The future specification must separately measure held-out transfer,
intervention-aware causal reasoning, calibrated competence/uncertainty, and
corrigible response selection. It must bind all task splits and declare
baselines, ablations, budgets, thresholds, contamination controls, and failure
criteria before a candidate freeze.

The response surface is propositional, not executive: continue,
seek_information, ask, explore, defer, fallback, escalate, and stop are typed
recommendations. Explore remains simulation-only unless a separate existing
Action Gate admits it. None of these recommendations can create authority,
approve an action, write protected state, or override the Safety Supervisor or
Protected Control Plane.

## Independent hidden evidence

The implementation owner never receives hidden seeds, tasks, labels, latent
structures, detailed scoring, evaluator code, or signing keys. The independent
evaluator owns sealed hidden execution and an all-attempt ledger; an
independent reviewer judges custody and admissibility; a separately authorized
recognition authority can decide only after every required gate is admissible.
The registry custodian independently controls accepted protocol, signer status,
revocation, and attestation references, but cannot score hidden tasks or make a
recognition decision.

Runtime scope, principal, role, authority, policy, approval, budget, fence,
sandbox, kill-switch, and protected state originate only from authenticated
runtime context. Evaluator records can attest evidence metadata only; they
cannot repair or widen that runtime context. Before submissions, the evaluator
commits the candidate freeze, allowed submissions, attempt budget, and feedback
granularity. The implementation owner receives no per-attempt score or tunable
feedback, and the hidden set is retired or replaced after the fixed budget.

G8 requires reproduction from the frozen release artifact in two declared
runtime environments, including baselines, ablations, negative controls and
failure disclosures. A signature proves only its cryptographic binding, not
independence or success.

## External blockers

1. NB-1 through NB-5 do not have complete, independently adjudicated exit
   evidence. NB-6 registration and execution are blocked.
2. No future candidate exists with immutable complete provenance. Hidden
   commitment and evaluation are blocked.
3. No independently appointed evaluator, reviewer, registry custodian, and
   recognition authority are evidenced. Hidden evidence is inadmissible.
4. No independently reproduced G8 package exists. The labels Neural Brain
   Candidate, production autonomous, conscious, sentient, human-equivalent,
   and biologically faithful are prohibited.

## Required future handoff

The implementation owner must provide a reproducible candidate freeze receipt,
the immutable evaluation specification, baseline and ablation declarations,
and a complete disclosure of failures. The evaluator returns signed evidence
envelopes and the all-attempt ledger. The independent reviewer returns an
admissibility decision. Separate authorized stage-release and recognition
decisions remain external to this package.
