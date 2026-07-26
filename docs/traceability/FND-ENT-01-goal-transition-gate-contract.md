# FND-ENT-01: Goal Transition Gate Prerequisite Contract

## Implementation Evidence

- Task ID: `FND-ENT-01`
- Objective: Define the bounded, versioned Goal Transition Gate aggregate
  contract required to make the historical S1-04.1 revalidation task concrete
  without enabling a Goal runtime, action, or later-stage capability.
- Delivery stage: NB-0 prerequisite contract; it bounds NB-1 internal proposals
  but is not an NB-1 protected-runtime implementation.
- Governing sources: `docs/adr/ADR-018-complete-cognitive-system.md`,
  `docs/adr/ADR-019-tenant-bound-runtime-database-identities-and-pools.md`,
  `docs/architecture/architecture-directive-v4.0.md`,
  `docs/architecture/neural-brain-recognition-standard.md`,
  `docs/adr/STATUS.md`, and the S1-03 audit controls.

## Acceptance Evidence

- [x] The contract fixes immutable authenticated Tenant, Area, Project, and
  Session scope, plus origin, creator, request, and parent lineage references.
- [x] Authority snapshot, success criterion, proposal provenance, and audit
  evidence are typed references only; they do not create authority, success, or
  a protected state transition.
- [x] Deadline, budget, and checkpoint references have explicit NB-1 boundary
  semantics. Only checkpoint provenance for an internal proposal is currently
  NB-1-permitted; deadline and budget runtime semantics remain absent pending
  explicit revalidation.
- [x] The Goal Transition Gate is the sole future protected-state writer, while
  Cognitive Plane and Goal Runtime callers can only submit typed requests.
- [x] Action execution, approval claims, resource locking, later verification,
  external effects, database migrations, and Goal runtime implementation are
  explicitly excluded.
- [x] Deterministic contract tests assert the bounded fields, stage map,
  fail-closed behavior, historical-ADR blocker, and no-early-runtime claim.

## Implementation Boundary and Blocker

No Goal runtime or migration is added. `docs/adr/STATUS.md` classifies ADR-004,
ADR-007, and ADR-011 as historical and requires a new complete-system ADR or
explicit ADR-018 revalidation before Goal/Action gate implementation. Directive
v4.0 allows NB-1 internal goal and plan proposals only; its protected Goal
lifecycle, independent verification, quiescence, and any external effect remain
later protected-control work.

The blocker is architecture/governance, not a missing implementation detail.
The owner is the Protected Control Plane architecture owner. It is unblocked
only by an accepted revalidation defining the Gate state model, separation of
duties, authenticated scope, authority/policy inputs, audit, verification,
recovery, concurrency, and stage-specific tests.

## Changed Artifacts and Verification

- Contract: `docs/architecture/contracts/goal-transition-gate-v1.json`
- Traceability: this document and
  `docs/traceability/requirement-to-test-catalog-v1.json`
- Tests: `tests/architecture/test_goal_transition_gate_contract.py` and
  `tests/architecture/test_machine_readable_contracts.py`
- Migrations: none. S1-03 audit controls remain untouched; no protected-state
  writer or database surface is introduced.
