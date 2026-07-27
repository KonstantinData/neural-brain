# Action Gate ADR-018 Revalidation Proposal v1

- Status: Proposed prerequisite; not accepted and not runtime authorization
- Task: FND-ENT-03
- Governing target: ADR-018 and Architecture Directive v4.0
- Related prerequisite: FND-ENT-02 Goal Gate ADR-018 Revalidation Proposal
- Applies to: NB-4/NB-5 boundary and future NB-5 only

## Decision required

ADR-006 through ADR-009 and ADR-011 are historical inputs, not implementation
authority. An authorized architecture decision must accept, replace, or reject
this proposal before any Action runtime, migration, executor, dispatch,
budget, resource claim, fence, sandbox binding, or external effect is added.

The proposed boundary is deliberately split:

- NB-4 owns learning, consolidation, immutable candidates, independent
  promotion, canary, and rollback. It creates no action authority and has no
  tool, budget, resource, fence, sandbox, or external-effect capability.
- NB-5 may introduce only a single-goal bounded loop in simulation and
  controlled tool sandboxes, and only after the complete Action and Goal Gate
  decisions and every non-compensable control prerequisite are accepted and
  evidenced.
- NB-8 alone may add fenced distributed ownership, durable queues, failover,
  and scale. It may not weaken the serial NB-5 action-control requirements.

## Proposed Action Gate boundary

The Action Transition Gate is the sole writer of protected Action Intent state.
The Cognitive Plane, including a planner, action selector, model, and Memory
Core, can submit typed proposals only. They cannot commit an intent, dispatch
an executor, create authority, or mutate action state.

Before an effect, the Gate must atomically bind a committed immutable Action
Intent to authenticated immutable scope and principal, authority snapshot,
exact policy decision, required independent approval claims, budget reservation,
resource claims, valid fence, enabled kill switch, exact sandbox/executor
binding, and audit evidence. Missing, stale, revoked, conflicting, unknown, or
scope-mismatched evidence denies before commitment or effect. Approval cannot
create authority, and policy cannot override the Security Floor.

Executor or tool success is never effect or goal success. Post-action
observation and effect verification must be independent. Only the revalidated
Goal Transition Gate may write `Achieved`, after complete evidence and
quiescence. Ambiguous effects are `indeterminate`: they are neither blindly
retried nor allowed to release budget or resource claims until authoritative
reconciliation establishes an evidence-backed terminal disposition.

## Legacy task disposition

| Legacy task | Disposition | Bounded successor / blocker |
| --- | --- | --- |
| S1-07 | Blocked; not reactivated | NB-5 Action Intent state-machine package after accepted Action and Goal Gate decisions. |
| S1-08 | Blocked; not reactivated | NB-5 atomic Action Gate admission/commit package after accepted precommit evidence and PostgreSQL authorization design. |
| S1-09 | Split; not reactivated | NB-5 serial executor, verification, and reconciliation; NB-8 owns distributed ownership/queue/failover concerns. |

## Explicit blocker

**Owner:** Protected Control Plane architecture owner.

**Unblock condition:** An authorized ADR accepts or replaces the proposed
complete-system Goal and Action Gate design, including state models, actor
separation, authenticated identity/scope, authority/policy/approval,
budget/resource/fence lifecycle, sandbox/kill-switch control, atomic audit,
independent verification, indeterminate reconciliation, recovery, concurrency,
and NB-5 evaluation acceptance criteria.

**Next step:** Do not begin an action-runtime implementation. Once accepted,
create separately owned NB-5 packages for Gate contract, database authorization,
bounded executor, verifier/reconciler, and end-to-end evaluation. Each requires
positive, negative, scope, authority, audit, crash-boundary, stale-fence,
kill-switch, retry, and recovery evidence as applicable.

## Non-claims

This proposal and its contract do not implement or activate NB-4 or NB-5; do
not claim an Action Gate, external effect, learning-to-action integration,
closed loop, safety, recognition, release, legal classification, or production
autonomy.
