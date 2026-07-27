# Protected Control Plane Kill-Switch ADR-018 Revalidation Proposal v1

- Status: Proposed; not accepted and not runtime authorization
- Date: 2026-07-27
- Notion decision record: https://app.notion.com/p/39d1c1ac5ec081878fd1f86e777ac0e9
- Parent task: `S1-02.5`
- Depends on: ADR-005, ADR-006, ADR-018, ADR-019; Architecture Directive v4.0;
  Security Floor governance; Action Transition Gate contract
- Delivery boundary: target Protected Control Plane contract for NB-5 and later;
  NB-1 remains effect-free

## Purpose and authority

This is a versioned decision proposal, not an accepted ADR. It identifies the
bounded successor decision required to replace the historical kill-switch
design. It does not change ADR authority, enable a kill switch, create
credentials, revoke a credential, persist state, operate a gate, authorize an
external effect, or support a runtime, release, recognition, or
production-autonomy claim.

ADR-018 requires a Protected Control Plane whose kill switch and
credential-revocation plane remain outside Brain control. ADR-019 requires
authenticated immutable Tenant-bound runtime identity. This proposal neither
weakens those requirements nor permits untrusted content to define scope,
state, policy, authority, approval, or recovery.

## Historical ADR-006 disposition

ADR-006 is historical evidence. It is not accepted as-is, is not reactivated,
and cannot authorize a runtime implementation. Its hierarchical-stop intent may
be reconsidered only through a future accepted ADR-018-conformant successor.
No historical state name, role, persistence choice, API, or enforcement
behavior is adopted by implication.

## Proposed successor boundary

The accepted successor must define a Protected Control Plane-owned, fail-closed
kill-switch and credential-revocation contract with the following non-optional
properties:

1. A versioned state machine containing `enabled`, `drain`, `disabled`, and
   `recovery`, with default denial for unknown, stale, conflicting, revoked, or
   scope-mismatched state and transitions.
2. Immutable authenticated Brain/Tenant/Area/Project/Session scope, principal,
   role, authority, policy, approval, operation, revision, fence, expiry, and
   audit bindings. Prompts, observations, model output, memory, tool output,
   request payloads, and cache entries cannot establish or broaden them.
3. Separate kill operator, independent Safety Supervisor, credential-revocation
   authority, incident commander, recovery approver, Action/Goal Gate owners,
   executor, and independent verifier roles. The Brain cannot disable, alter,
   or re-enable this control.
4. Atomic compare-and-swap transitions with monotonic revisions, idempotency
   semantics, durable audit evidence, stale-fence denial, and no partial state
   when audit persistence fails.
5. Explicit admission, committed-intent, dispatch, in-flight, sandbox,
   verifier, reconciliation, credential, budget, resource-claim, and fence
   behavior for drain, disable, revocation, crash, restart, partition, timeout,
   and indeterminate effects. Ambiguous effects must be contained and
   reconciled; they must never be retried blindly.
6. A recovery path that remains disabled by default until separately authenticated
   recovery evidence, independent review where required, audit completeness,
   reconciliation, and anti-rollback checks pass.

## NB-1 and implementation exclusion

NB-1 is limited to internal cognition over recorded or synthetic input and has
no external effects. This proposal therefore excludes at NB-1 and until the
successor ADR is accepted:

- a Kill Switch runtime, database table, migration, state writer, credential
  issuer or revoker, API, worker, executor, dispatcher, sandbox controller, or
  network control;
- Action Intent commitment, tool invocation, effect cancellation, budget or
  resource release, fencing, reconciliation, incident resolution, or recovery
  execution; and
- any claim that a future state machine, test definition, proposal, or document
  supplies authority, safety, availability, release readiness, or recognition.

## Required acceptance, evidence, and decision owners

Before any implementation package, the architecture decision owner must accept
an ADR-018-conformant successor or record a different accepted disposition.
The Protected Control Plane architecture owner must supply the complete contract
and implementation decomposition. An independent security/safety reviewer must
approve the threat, role-separation, failure, and test evidence. A qualified
recovery owner must approve recovery and incident-operational requirements.

The accepted decision must fix the full state/transition table, role and
authority matrix, scope and persistence model, credential-revocation authority,
CAS/fencing/idempotency/atomicity rules, cross-gate interfaces, failure and
recovery semantics, retention/audit requirements, and preregistered positive,
negative, actor, scope, audit-failure, race, crash, stale-fence, revocation,
restart, partition, rollback, and recovery tests. Missing evidence denies the
affected transition or implementation package.

## Validation

`tests/architecture/test_protected_control_kill_switch_adr_018_revalidation_proposal.py`
is a deterministic documentation test. It proves only that the historical
disposition, non-authorizing boundary, required acceptance, and early-runtime
exclusions remain explicit. It is not a kill-switch runtime, authorization,
security certification, or recognition evidence.
