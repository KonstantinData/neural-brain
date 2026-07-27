# Goal Gate ADR-018 Revalidation Proposal v1

- Status: Proposed; not accepted and not runtime authorization
- Date: 2026-07-26
- Notion decision record: https://app.notion.com/p/3a91c1ac5ec08181b9f5ff70fa48eac7
- Parent task: `FND-ENT-02`
- Depends on: `FND-ENT-01`; ADR-004, ADR-007, ADR-011; ADR-018; ADR-019;
  Architecture Directive v4.0; Neural Brain Recognition Standard
- Delivery boundary: NB-1 internal proposal boundary only

## Purpose and authority

This is a versioned decision proposal, not an accepted ADR. It records the
only bounded replacement that may be presented for authorized architecture
acceptance. It neither changes the authority of an ADR nor authorizes a Goal
runtime, protected-state mutation, migration, external effect, capability,
release, recognition, or production-autonomy claim.

The proposed replacement is governed by ADR-018's complete protected
cognitive-system boundary and ADR-019's database-anchored Tenant identity. The
Memory Core remains a protected subsystem under ADR-015 through ADR-017; it
does not define the Goal product boundary.

## Historical ADR disposition

| Historical ADR | Disposition | Reason | Reusable input, pending acceptance |
| --- | --- | --- | --- |
| ADR-004 | Explicitly superseded historical evidence | ADR-015 superseded its three-gate agent-runtime decision. ADR-018 restored the complete product boundary but did not reactivate the historical record. | The sole-writer principle, narrowed to a Goal aggregate and authenticated control-plane inputs. |
| ADR-007 | Explicitly superseded historical evidence | ADR-015 removed the historical Goal and Action state machines. ADR-018 requires explicit revalidation before protected runtime implementation. | Default-deny state/transition contract, quiescence and recovery requirements, but no historical state set is adopted as-is. |
| ADR-011 | Explicitly superseded historical evidence | ADR-015 made consumer completion external. ADR-018 restores a Brain-owned Goal boundary only through a new accepted decision. | `Achieved` only after independent verification, complete evidence, and quiescence. |

None of ADR-004, ADR-007, or ADR-011 is accepted as-is. This proposal does not
supersede, amend, or reactivate them. An authorized decision may later replace
the bounded subset described below; Action Gate, effect, dispatch, and
reconciliation decisions remain separate revalidation work.

## Proposed replacement boundary

### Aggregate and scope

- A Goal is a protected, session-bound aggregate, not an isolation dimension.
- Its immutable authenticated scope is `tenant_id`, `area_id`, `project_id`,
  and `session_id`; Goal identity, origin, creator, request, and parent lineage
  are immutable after admission.
- A parent Goal is lineage only. It cannot supply authority, approval, policy,
  scope, execution permission, or a cross-session reference.
- The Gate independently resolves scope and principal facts from authenticated
  Protected Control Plane context. Prompts, observations, model output, memory
  content, tool output, and request payloads are untrusted and cannot set or
  expand trusted context.
- Unknown, missing, stale, conflicting, unverifiable, or scope-mismatched
  identity, lineage, authority, policy, approval, state, success criterion,
  provenance, checkpoint, or audit evidence denies before a protected
  transition.

### Ownership and transition rule

- Only a future Goal Transition Gate may write protected Goal state and its
  atomic audit evidence.
- Cognitive Plane and Goal Runtime components may submit typed requests; they
  cannot write protected state or invoke tools directly.
- Authority snapshot, policy decision, approval reference, success criterion,
  proposal provenance, checkpoint, and audit references are evidence bindings.
  None independently creates authority, approval, success, or a transition.
- A future accepted Goal Gate may write `Achieved` only after an independent
  verifier decision, complete evidence, and quiescence. Tool, executor, HTTP,
  or self-reported success is not goal success.
- State names, transitions, actor matrix, deadlines, blocked/resume semantics,
  recovery, concurrency, and audit schema are intentionally unresolved here.
  They must be fixed by the accepted decision and its implementation package;
  omission from that accepted contract must deny the transition.

## NB-1 and later-stage boundary

At NB-1, only internal Goal and plan proposals over recorded or synthetic input
are permitted. Checkpoint provenance may describe the authenticated immutable
cognitive checkpoint that produced such a proposal; it is not a protected Goal
checkpoint or transition authorization.

This proposal explicitly excludes at NB-1:

- protected Goal lifecycle state, a Goal Transition Gate runtime, protected
  Goal table, database migration, or database writer;
- `Achieved`, independent Goal/effect verification runtime, quiescence runtime,
  reconciliation, retry, recovery, or concurrency implementation;
- Action Intent commitment, tool invocation, dispatch, external effect, or
  sandbox execution;
- approval-claim issuance, validation, or consumption; budget reservation;
  resource claims or locks; fences; kill-switch operation; and
- any implementation, maturity, release, recognition, or production-autonomy
  claim.

NB-5 action and verification capability, NB-7 hierarchical Goal behavior, and
NB-8 distributed ownership remain governed by their own ordered delivery
evidence. A later-stage result cannot compensate for missing earlier Goal Gate
architecture, evidence, or safety controls.

## Required acceptance and implementation evidence

Before any Goal runtime or migration, an authorized architecture owner must
accept an ADR-018-aligned replacement decision (or document a different
accepted disposition). The accepted record must fix and test:

1. versioned Goal state model, permitted transitions, default-deny unknown
   state/transition behavior, deadlines, blocking, termination, and recovery;
2. authenticated identity, immutable Tenant/Area/Project/Session scope,
   principal, authority, policy, approval, success-criterion, provenance, and
   audit inputs; and rejection of all untrusted context sources;
3. sole-writer database and API enforcement, atomic transition plus audit,
   stale-version/concurrency behavior, and no partial state on audit failure;
4. requester/approver/verifier/executor separation, independent verification,
   complete evidence, quiescence, and `Achieved` preconditions; and
5. positive, negative, scope, authority, audit-failure, crash-boundary,
   recovery, stale-checkpoint, concurrency, and stage-exclusion tests.

The Protected Control Plane architecture owner owns this acceptance. The
concrete blocker is an authorized choice to accept this bounded proposal or an
alternative replacement decision. Until that choice is recorded as accepted,
S1-04.1 remains blocked for protected runtime implementation.

## Validation

`tests/architecture/test_goal_gate_adr_018_revalidation_proposal.py` is a
deterministic documentation test. It proves only that the proposed disposition,
NB-1 boundary, required acceptance, and no-early-runtime exclusions remain
explicit. It is not runtime, authorization, or recognition evidence.
