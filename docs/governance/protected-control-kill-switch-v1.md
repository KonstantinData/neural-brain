# Protected Control Plane Kill-Switch Governance v1

- Status: Proposed prerequisite; not accepted and not runtime authorization
- Task: S1-02.5
- Governing target: ADR-018, ADR-019, Architecture Directive v4.0
- Historical input: ADR-006 only; it is not reactivated by this proposal

## Decision request

The architecture decision owner must accept, replace, or reject the companion
machine-readable contract before any runtime, database, credential-revocation,
executor, dispatch, recovery, or network-control implementation starts. The
accepted decision must select the protected-state owner, PostgreSQL role and
authorization design, exact control scopes, incident/recovery authority,
credential-revocation integration, and NB-5 evidence thresholds.

This proposal does not amend ADR-006. Repository convention keeps accepted ADRs
in `docs/adr/`; a separate unaccepted ADR-018 revalidation proposal must live
under `docs/architecture/` and remain explicitly non-authoritative until an
authorized decision record is accepted. This governance document is supporting
evidence, not the ADR decision draft.

## Non-negotiable governance boundary

Only authenticated Protected Control Plane runtime context may supply identity,
scope, actor role, authority, policy, approvals, credential status, and
kill-switch state. The Cognitive Plane, Brain self-monitoring, prompts, model
output, memory, observations, tools, and request payloads are untrusted. They
may submit a typed stop/escalation proposal but cannot disable, re-enable,
recover, revoke credentials, or write protected control state.

Unknown, missing, stale, expired, revoked, conflicting, unverifiable, or
scope-mismatched evidence denies or stops. Approval and review never create
missing authority and never override the Security Floor.

## Proposed operating model

The companion contract defines four state values: `enabled`, `drain`,
`disabled`, and `recovery`. `enabled` is conditional admission, never a broad
authorization. `drain` denies new effect work while allowing authenticated
containment, audit completion, settlement, and reconciliation. `disabled`
denies effect work and credential use. `recovery` is evidence-gathering only;
it remains effect-disabled until a separate recovery approver accepts complete
independent evidence.

```text
enabled --authorized stop--> drain --fault/escalation--> disabled
   |                                      ^                |
   +--emergency stop----------------------+                |
                                                          independent
                                                          recovery approval
                                                               |
                                                               v
                                                          recovery --all guards--> enabled
                                                               |
                                                     any uncertainty/failure
                                                               v
                                                           disabled
```

Every transition must be scope-bound, compare-and-swap guarded, idempotent for
the exact request, durably and atomically audited, and bound to a monotonic
revision. An implicit restart or cached enabled value is forbidden.

## Separation of duties

| Role | May do | May not do |
| --- | --- | --- |
| Kill operator | Request `drain` or `disabled` | Approve own recovery or re-enable the Brain |
| Independent Safety Supervisor | Force or request fail-closed stop; observe evidence | Be controlled by the Brain or solely approve recovery |
| Credential revoker | Revoke/rotate scoped credentials and attest evidence | Enable operations or approve own recovery |
| Incident commander | Coordinate containment and reconciliation | Replace independent verification or re-enable unilaterally |
| Recovery approver | Approve `recovery -> enabled` after evidence | Be the triggering operator, sole verifier, credential revoker, or Brain |
| Independent reviewer | Review design and evidence | Waive Security Floor or create authority |

## Required review and acceptance checklist

Before ADR acceptance, the architecture decision owner, Protected Control Plane
owner, independent security/safety reviewer, and operational recovery owner
must confirm all of the following:

1. Exact hierarchical scope semantics and authenticated source of every scope
   field, including overlap/conflict resolution and expiry.
2. Future protected-state schema, PostgreSQL ownership/roles/RLS, append-only
   audit chain, retention, restoration, and break-glass controls.
3. Transition guards, linearization point, CAS/revision strategy, idempotency
   domain, fencing/lease semantics, clock behavior, and atomic audit failure.
4. Credential lifecycle, revocation propagation, executor/sandbox enforcement,
   in-flight containment, and evidence of revocation acknowledgement.
5. Drain/disabled/recovery semantics for effects, claims, audit, reconciliation,
   restart, partition, split brain, and indeterminate outcomes.
6. Separation of duties and named independent reviewer evidence; no Brain or
   policy author can activate or recover the control alone.
7. Complete NB-5 test plan and independently reviewed controlled-sandbox
   evaluation; no release or maturity claim follows merely from this draft.

## Remaining decision blocker

**Cause:** ADR-006 is historical and has no accepted ADR-018/v4 successor.

**Owners:** Neural Brain architecture decision owner; Protected Control Plane
architecture owner. Independent security/safety reviewer and qualified
operational recovery owner must supply separate evidence.

**Concrete unblocker:** accept an ADR-018-conformant successor decision with
the checklist above completed and its test/evaluation evidence requirements
registered. Only then may separately scoped implementation work be made Ready.
