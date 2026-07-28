# S1-14.4 Runtime Privacy Enforcement ADR Proposal v1

## Status and authority boundary

- Status: **Proposed, non-authorizing architecture input**
- Task: `S1-14.4`
- Location: architecture preparation, not an accepted ADR in `docs/adr/`
- Current runtime activation: **false**
- Current production authorization: **none**
- Reserved target outcome: `ALLOW` is vocabulary for a future accepted and
  implemented contract only; this proposal cannot produce or authorize it.

This proposal does not amend an accepted ADR, activate a policy, determine
lawfulness, classify real data, appoint a controller or processor, approve a
purpose, or authorize processing, storage, deployment, or release. Acceptance
requires the repository ADR process, an accountable deployment owner, the
required qualified privacy and legal reviews, independent technical review,
and all applicable release gates.

## Context

The repository already contains fail-closed documentation-preparation
contracts for Article 6 evidence, Article 9 special-category and Article 10
evidence, consent, retention-related evidence, and deployment review. Those
artifacts explicitly do not validate a concrete intake or enable runtime
behavior.

The implemented early Memory Core accepts a generic data classification and a
purpose at its request boundary. The existing Security Floor and policy
contracts protect authenticated scope, released operations, immutable policy
digests, activation evidence, and database-gate ownership, but they do not
constitute a deployment-specific legal or privacy authorization system.

A future S1-14.4 implementation therefore needs a distinct runtime contract
that consumes approved, immutable evidence without interpreting law or allowing
an untrusted caller to create trusted purpose, classification, authority,
approval, retention, or policy state.

## Governing repository authority

This proposal is constrained by:

- ADR-003: PostgreSQL is the authoritative transactional ledger and protected
  state plus audit evidence commit atomically.
- ADR-005: the Security Floor is non-overridable; policy is versioned,
  schema-validated, digest-bound, and cannot create missing authority.
- ADR-012: evidence immutability coexists with authorized retention, deletion,
  anonymization, and derivative propagation.
- ADR-018 and Architecture Directive v4.0: the Protected Control Plane decides
  whether protected state may change; cognitive capability creates no
  authority.
- ADR-019: productive Runtime database identities and pools are Tenant-bound;
  `session_user` is the immutable database Tenant anchor.

If a future accepted decision conflicts with this proposal, the accepted
decision wins. Until such acceptance, the current fail-closed runtime remains
unchanged.

## Proposed decision

Introduce a future `Privacy Processing Decision Gate` in the Protected Control
Plane. It evaluates a strictly typed request against one immutable, activated,
scope-matched policy version and its exact evidence and approval bindings.

The decision gate does not write Memory Core protected state. The Memory
Transition Gate remains the sole writer of protected memory state and may
commit a protected mutation only when the privacy decision is `ALLOW` within
the same authoritative PostgreSQL transaction.

The future contract is separate from the current `policy-v1` intake allow-list
and the current `MemoryRiskOutcome` vocabulary. Existing Security Floor,
authority, approval, scope, and Memory Transition Gate decisions remain
independent non-compensatory prerequisites.

## Proposed component ownership

| Component | Proposed responsibility | Prohibited responsibility |
| --- | --- | --- |
| Trust-boundary adapter | Authenticate the actor and establish immutable Runtime scope | Accept identity, scope, authority, policy, or approval from payload content |
| Classification Gate | Produce immutable classification evidence for one exact subject artifact or input digest | Treat a caller label or model output as trusted classification |
| Policy Registry | Store immutable policy definitions and evidence manifests | Mutate an existing policy version in place |
| Policy Lifecycle Gate | Own policy review, activation, suspension, revocation, expiry, and supersession transitions | Permit self-approval or implicit activation |
| Privacy Processing Decision Gate | Evaluate non-compensatory runtime prerequisites and emit a bound decision record | Write Memory Core state or infer legal conclusions |
| Memory Transition Gate | Remain the sole writer of protected Memory Core state | Commit without a transaction-local valid target `ALLOW` decision |
| PostgreSQL ledger | Bind policy, activation, decision, mutation, receipt, and audit evidence transactionally | Accept an alternate mutable authority outside the ledger |
| Retention and reconciliation workers | Submit typed suspend, delete, reconcile, or derivative-propagation requests | Write protected state directly |
| S1-11.2 metadata layer | Capture and validate metadata and request a decision | Invent a legal basis, special condition, approval, or favorable fallback |

## Authoritative roles requiring future appointment

Role names in this proposal are responsibility classes, not appointments.
Their identities, qualifications, authority scopes, independence, and expiry
must be established in authenticated protected state before use.

| Role class | Decision responsibility |
| --- | --- |
| Accountable deployment owner | Deployment, system, Tenant or Company, processing activity, purpose, supported operation, and operational ownership |
| Qualified privacy reviewer | Classification, minimization, safeguards, access, rights, retention, deletion, and privacy-engineering review |
| Qualified legal reviewer | Jurisdiction, role disposition, general legal-basis evidence, additional special condition, Article 10 disposition, and legal constraints |
| Security control owner | Technical safeguard and bypass-resistance evidence |
| Independent activation approver | Exact-digest activation after regression evidence; must be distinct from the policy author and latest material changer |
| Policy Lifecycle Gate | Mechanical enforcement of authorized state transitions; it is not a human authority source |

No role is appointed and no role decision is approved by this proposal.

## Reserved target outcomes

The proposed deterministic outcome set is:

```text
ALLOW
DENY
REQUIRE_HUMAN_REVIEW
REQUIRE_ADDITIONAL_EVIDENCE
EXPIRED
REVOKED
CONFLICT
UNKNOWN
```

Only target `ALLOW` may admit a future protected operation. Every other outcome
blocks the protected operation. `REQUIRE_HUMAN_REVIEW` and
`REQUIRE_ADDITIONAL_EVIDENCE` may create a separately governed review task, but
they do not create processing authority.

In the current repository state, target `ALLOW` is unavailable because this
proposal is not accepted, no runtime contract is activated, and no concrete
deployment-specific authorization package is established.

## Non-compensatory gates

Every gate below must pass independently. A positive result from one gate never
compensates for an unknown, failed, expired, revoked, or conflicting result in
another gate.

1. Authenticated actor and complete Tenant, Area, Project, and Session scope.
2. Tenant-bound database identity and matching active pool generation.
3. Existing Security Floor and operation release.
4. Existing authority and approval prerequisites.
5. Exact processing activity and immutable purpose binding.
6. Valid classification evidence for the exact subject artifact or input.
7. Supported jurisdiction and deployment environment.
8. Approved general processing-basis evidence.
9. Approved additional special condition or Article 10 disposition where
   required.
10. Complete safeguards, minimization, access, rights, retention, deletion,
    transfer, and derivative-handling evidence.
11. Exactly one active, scope-matched, non-expired policy version.
12. Current qualified reviews and independent activation evidence bound to the
    exact policy digest.
13. Auditability and atomic mutation capability.
14. No active suspension, revocation, incident stop, restore stop, evidence
    conflict, or reassessment trigger.

Unknown data class, purpose, basis, additional condition, retention rule,
owner, reviewer, policy version, evidence state, or audit state blocks the
operation.

## Proposed lifecycle

The policy lifecycle is:

```text
DRAFT
PENDING_REVIEW
APPROVED
ACTIVE
SUSPENDED
REVOKED
EXPIRED
REJECTED
SUPERSEDED
```

Proposed transitions:

- `DRAFT -> PENDING_REVIEW`: policy author submits a complete immutable policy
  and evidence manifest.
- `PENDING_REVIEW -> APPROVED`: accountable owner and every required qualified
  reviewer decide all mandatory fields; no conflict or placeholder remains.
- `PENDING_REVIEW -> REJECTED`: an authorized reviewer rejects with stable
  reason codes.
- `APPROVED -> ACTIVE`: the Lifecycle Gate verifies exact-digest regression
  evidence and independent approval within all validity windows.
- `ACTIVE -> SUSPENDED`: an authorized request or automatic fail-closed trigger
  records an incident, unknown, conflict, drift, or reconciliation stop.
- `SUSPENDED -> ACTIVE`: only after independent reconciliation of unchanged
  policy and evidence digests. Any material change requires a new version.
- `APPROVED`, `ACTIVE`, or `SUSPENDED` may transition to `REVOKED`, `EXPIRED`,
  or `SUPERSEDED` through the owning gate.

`REVOKED`, `EXPIRED`, `REJECTED`, and `SUPERSEDED` are terminal. They cannot
return to `ACTIVE`; a new independently approved policy version is required.

## Future authoritative commit boundary

The target sequence is one short database-controlled transaction:

```text
1. derive and verify the Tenant from session_user and the selected Tenant pool
2. verify actor, Area, Project, Session, authority, and Security Floor
3. validate the S1-11.2 metadata candidate
4. resolve classification evidence for the exact subject digest
5. resolve the single active policy server-side
6. lock and revalidate policy lifecycle, activation, revocation, evidence,
   approval, and classification bindings
7. evaluate and create the bound privacy decision
8. only for target ALLOW, execute the owning Memory Gate mutation
9. write decision evidence, mutation audit, and idempotency receipt
10. commit all records together and return only after commit
```

The client cannot select an authoritative policy version, submit an `ALLOW`, or
reuse a decision for another actor, scope, operation, purpose, classification,
artifact, or policy digest. A separate application-service or HTTP check before
the database transaction is advisory preflight only and cannot authorize the
mutation.

For target `ALLOW`, decision, mutation, audit, and receipt commit together or
none persist. For a non-`ALLOW` outcome, decision evidence may commit without a
protected data mutation. Database, policy, audit, lock, or transaction failure
blocks the operation and never falls back to permissive behavior.

## Revocation, expiry, reassessment, and restore

Revocation, expiry, purpose change, classification change, evidence conflict,
or a mandatory reassessment trigger stops new processing immediately at the
gate. The control plane records affected scope and submits separately governed
suspension, restriction, deletion, correction, or reconciliation requests.

Derivative handling covers payloads, working state, checkpoints, embeddings,
indexes, caches, candidates, summaries, reports, and backups as applicable.
Deletion or anonymization follows an authorized retention path and preserves
only non-reconstructive evidence of the operation.

A restored ledger is non-serving for this capability. Restored policy heads do
not become trusted merely because a database starts. Runtime activation remains
false or suspended until independent verification confirms manifest and WAL
integrity, migration compatibility, Tenant bindings, RLS and FORCE, gate-only
writer privileges, policy and evidence digests, audit-chain continuity,
reconciliation readiness, and an authorized cutover decision.

## Consequences if accepted later

- S1-11.2 metadata capture can become implementable without gaining policy or
  legal authority.
- New immutable policy, evidence, approval, lifecycle, and decision records and
  migrations will be required.
- The existing Memory Gate call signature and audit evidence will require a
  compatible migration rather than an in-place reinterpretation of generic
  classification values.
- Positive, negative, state-machine, property-based, concurrency, failure,
  restore, and direct-bypass tests become release-critical.
- Activation remains a separate deployment decision after implementation and
  verification.

## Alternatives not selected by this proposal

### Treat `restricted` as special-category authorization

Rejected. A generic sensitivity label contains no deployment-specific legal,
purpose, condition, safeguard, retention, or review authority.

### Extend current `policy-v1` in place

Rejected. That contract is a bounded early Memory Core intake policy. Silent
semantic expansion would invalidate existing digests and claim boundaries.

### Evaluate policy only in the application service

Rejected. It leaves a time-of-check/time-of-use gap and does not make direct
database bypass technically impossible.

### Allow processing while review is pending

Rejected. Missing qualified review is a non-compensatory blocker.

## Acceptance prerequisites

This proposal may move to an accepted ADR only after:

1. a concrete supported deployment scope and explicit exclusions exist;
2. the accountable owner and qualified reviewer role bindings are established;
3. every authorizing field is decided or explicitly out of scope;
4. Security, Privacy, Architecture, database, restore, and operations reviews
   have no open Critical or High findings;
5. the machine-readable policy, decision, lifecycle, and audit contracts are
   reviewed together;
6. the migration and backward-compatibility strategy is accepted; and
7. the activation and release decision remains explicitly separate from ADR
   acceptance and code merge.

## Claim limits

This proposal provides no legal advice, lawfulness determination, data
classification, authority grant, role appointment, approval, processing right,
deployment decision, production readiness, or release. It does not satisfy the
operational acceptance criteria of S1-14.4 or S1-11.2. Current runtime
activation remains **false**.
