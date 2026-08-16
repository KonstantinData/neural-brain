# NB-8 Distributed Operation ADR-018 Revalidation Proposal v1

- Status: Proposed prerequisite; not accepted and not runtime authorization
- Task: NB-8
- Governing target: ADR-018, ADR-019, and Architecture Directive v4.0
- Applies to: NB-8 only, after complete NB-7 exit evidence

## Decision required

NB-8 is a future delivery-stage capability, not a continuation of historical
S1/S4 material. Before any distributed runtime, the architecture decision owner
must accept or replace a current contract for fenced ownership, durable queues,
leases, failover, reconciliation, disaster recovery, and governed cross-Area
abstraction. This proposal does not amend, reactivate, or replace historical
S1/S4 material.

The two versioned preparation artifacts are:

- `contracts/nb8-distributed-operation-preparation-v1.json`: future state,
  actor, scope, ownership, recovery, and cross-Area boundary.
- `contracts/nb8-distributed-operation-test-plan-v1.json`: preregistered,
  non-executing partition, split-brain, duplicate-effect, restore,
  semantic-equivalence, and isolation evidence.

## Hard boundary and dependencies

NB-7 complete exit evidence is a hard predecessor. Accepted current Goal and
Action Gate decisions, including NB-5 serial Action Gate, independent
verification, indeterminate-effect, and reconciliation evidence, are also
required. NB-8 may add distribution only; it may not weaken the serial
Action Gate, sandbox, kill-switch, independent-verifier, immutable scope, or
atomic-audit requirements.

A future distributed component transports or verifies a gate-authorized
request. It does not own protected Goal, Action, Memory, or Model Promotion
state. Cognitive Plane output, worker-local cache, queue payload, model output,
prompt, memory, observation, and tool output remain untrusted for identity,
scope, authority, approval, policy, and protected-state decisions.

## Proposed target boundary

Every future worker identity, generation, lease, fence, queue record, attempt,
idempotency key, reconciliation record, backup manifest, restore witness, and
cross-Area abstraction receipt binds the full authenticated
`Brain -> Tenant -> Area -> Project -> Session` lineage. A distributed process
can only preserve or narrow that lineage. It cannot infer, widen, replace, or
repair it. Tenant-bound Runtime database identities and dedicated pools remain
exclusive through worker reuse, failover, and restore.

Leases are bounded coordination evidence, never authority. A stale, expired,
partitioned, or uncertain owner stops before another protected mutation or
effect boundary. Ownership transfer uses an auditable compare-and-swap
transition with a monotonic fence. Duplicate delivery is not evidence that an
effect did not occur. An ambiguous non-idempotent effect remains
`indeterminate`; it receives no blind retry or claim release before an
authorized, evidence-backed reconciliation disposition through the owning Gate.

Restore begins contained, effect-disabled, and not-ready. It can become ready
only after fresh generations fence pre-restore writers and an independent
witness verifies exact scope, protected state, audit continuity, queue, lease,
attempt, approval, claim, and reconciliation consistency.

Cross-Area operation defaults to deny. It is possible only after a separately
accepted explicit cross-Area ADR and contract establishes dual-scope
authorization, minimum necessary versioned and redacted or aggregated
abstraction, provenance, retention/deletion treatment, audit receipt, and
independent review. It never permits raw memory sharing, implicit scope
expansion, authority or approval reuse, or worker/pool identity reuse.

## Required future evidence

The preregistered test plan requires fault-injected evidence for partition and
lease expiry, split brain and stale fences, duplicate delivery/effect,
reconciliation-leader races, restore and generation fencing, semantic
equivalence against a frozen serial reference, and Tenant/Area/cross-Area
isolation. Semantic equivalence compares authenticated scope, Gate receipts,
authority/policy/fence versions, protected terminal state,
independent-verification disposition, retained claims, and audit causal and
hash-chain relations against a frozen serial reference. Every result must bind
immutable contract, implementation, environment, fault-schedule,
serial-reference, ledger/audit, and independent witness artifacts. Missing,
mutable, unverifiable, or scope-mismatched evidence fails closed.

## Explicit blocker

**Owner:** Neural Brain architecture decision owner.

**Unblock condition:** NB-7 exit evidence is complete; an authorized current
ADR or contract accepts the distributed boundary; independent security, safety,
database, and operations review is complete; an isolated fault-injection and
restore environment exists; and the preregistered semantic-equivalence and
isolation evidence is ready to execute.

**Next step:** Do not implement runtime behavior. After acceptance, split
non-overlapping packages for schema/authorization, worker fencing, queue
semantics, reconciliation, disaster recovery, cross-Area abstraction, and
independent verification.

## Non-claims

This proposal and its test plan do not implement or activate a worker, queue,
lease, failover, restore, cross-Area exchange, protected-state writer, external
effect, NB-8 release, cognitive maturity, Neural Brain Candidate label, or
production autonomy. Distribution alone never proves cognitive quality.
