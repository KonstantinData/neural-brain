# NB-1 Planner and Verification ADR-018 Revalidation Proposal v1

- Status: Proposed prerequisite; not accepted and not runtime authorization
- Task: FND-ENT-04
- Governing target: ADR-018, ADR-019, and Architecture Directive v4.0
- Delivery boundary: NB-1 internal, effect-free proposal boundary only

## Purpose and authority

This versioned proposal revalidates the historical S1-10 planning, success,
verification, and serial-loop text against the current complete protected
cognitive-system architecture. It is not an accepted ADR and does not amend,
reactivate, or replace historical S1/S4 material. It creates no implementation
authority for `S1-10.1`, `S1-10.3`, or `S1-10.6`.

The Memory Core remains a protected subsystem under its retained authority. It
does not narrow ADR-018's product boundary or provide planner, Goal Gate,
Action Gate, verifier, or external-effect authority.

## Proposed NB-1 boundary

At NB-1, a Cognitive Plane planner may emit an immutable typed internal plan
proposal from recorded or synthetic observations and a trusted bounded cognitive
checkpoint. A proposal may describe candidate steps, estimated costs, predicted
effects, requested evidence, abort conditions, uncertainty, and a no-op, ask,
defer, or stop recommendation. It is not a Goal, Action Intent, authority,
approval, policy decision, budget reservation, resource claim, fence, sandbox
binding, or execution request.

The proposal's provenance must bind immutable model identity, code and
parameter digests, observation provenance, authenticated checkpoint reference,
and evaluation-policy reference. Scope, principal, roles, authority, policy,
approval, kill-switch state, and evaluation status come only from authenticated
Protected Control Plane context; untrusted observations, prompts, memory,
model output, tool output, and request payloads cannot create or change them.
Unknown, missing, stale, conflicting, unverifiable, or scope-mismatched facts
deny the future protected operation by default.

## Success and verification boundary

Planner output, model confidence, executor output, HTTP status, or tool success
is only a claim. It is never an effect result or goal success. A future accepted
Goal Gate decision must define a goal-bound success specification containing a
verification method, threshold, evidence requirements, failure behavior,
applicable legal-effect classification, and required meaningful human
confirmation. An independent verifier must resolve that specification using
separately attributable evidence. Only the revalidated Goal Transition Gate may
write `Achieved`, and only after independent verification, complete evidence,
and quiescence.

This proposal does not define a protected Goal state model, verification runtime,
human approval channel, legal classification, or any determination about a real
deployment. Missing accepted semantics deny a protected transition.

## Serial-loop boundary

The existing NB-1 development slice may remain an effect-free serial cognitive
cycle over recorded or synthetic observations. It may durably checkpoint only
its authenticated cognitive working state through the existing protected Memory
Core boundary where separately authorized. It cannot create a protected Goal
checkpoint, bind a plan to an Action Intent, dispatch a tool, or invoke an
executor. An unsuccessful cognitive step must produce a bounded internal
failure, no-op, ask, defer, or stop proposal and auditable checkpoint outcome;
it cannot bypass a gate or retry an ambiguous effect.

Any future loop that reaches protected Goal state, Action Intent, execution,
effect observation, or reconciliation is NB-5 or later and requires separately
accepted Goal and Action Gate decisions. NB-2+ perception, world-model, and
learning capabilities are not enabled by this document.

## Required authorized disposition

The Protected Control Plane architecture owner must accept, replace, or reject
this proposal before implementation of the three successor tasks. An accepted
replacement must fix, at minimum:

1. versioned planner proposal, plan hierarchy, checkpoint, provenance, expiry,
   invalidation, and default-deny semantics;
2. the boundary between Cognitive Plane internal proposals and every protected
   Goal, Action, Memory, Learning, and Model Promotion writer;
3. independent verifier identity, evidence package, success criteria,
   human-confirmation applicability, complete-evidence and quiescence rules;
4. authenticated identity and immutable Tenant/Area/Project/Session scope,
   authority, policy, approval, evaluation, audit, recovery, and concurrency
   evidence required before protected transitions; and
5. positive, negative, actor/separation, scope, authority, audit-failure,
   stale-checkpoint, crash-boundary, recovery, determinism, resource-budget,
   evaluation, and stage-exclusion tests for each resulting implementation.

## Successor packages and non-claims

After acceptance, create separate packages with non-overlapping ownership:

| Successor | Permitted scope after acceptance | Still excluded until its own gate |
| --- | --- | --- |
| S1-10.1 | Typed Cognitive Plane planner proposal and versioned hierarchy | protected state, tools, execution, authority, approval |
| S1-10.3 | Goal-bound success-specification and independent-verifier contract | legal conclusion, human-confirmation runtime, `Achieved` transition |
| S1-10.6 | Effect-free NB-1 serial cognitive/checkpoint integration | Goal/Action runtime, effect verification, reconciliation, external effect |

No migration is authorized by this proposal. No protected state, authority,
approval, policy activation, executor, tool, external effect, model mutation,
stage release, recognition, legal conclusion, or production-autonomy claim is
implemented or enabled.

## Validation

`tests/architecture/test_nb1_planner_verification_adr_018_revalidation_proposal.py`
is a deterministic documentation test. It validates only that this proposal
remains explicit, fail-closed, and non-authorizing; it is not runtime,
authorization, evaluation, recognition, or release evidence.
