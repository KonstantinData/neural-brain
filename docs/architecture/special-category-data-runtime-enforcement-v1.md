# Special-Category Data Runtime Enforcement v1

## Contract status

- Status: **Proposed target contract; non-authorizing**
- Related task: `S1-14.4`
- Current runtime activation: **false**
- Current supported processing scope: **none established by this document**
- Target `ALLOW` availability: **reserved and unavailable in the current runtime**

This document specifies the behavior a future accepted runtime implementation
must enforce. It is not an accepted ADR, legal determination, privacy approval,
policy activation, migration, or runtime capability.

## Purpose

Define a deterministic, fail-closed Protected Control Plane decision before any
future storage or protected processing of personal data that may require a
general processing basis, an additional special-category condition, an Article
10 disposition, enhanced safeguards, or another deployment-specific qualified
decision.

The runtime validates exact approved evidence bindings. It does not interpret
law, infer a favorable condition, or convert documentation preparation into
authority.

## Scope boundary

The target gate operates on one exact combination of:

- authenticated actor and Tenant, Area, Project, and Session scope;
- Tenant-bound Runtime database identity and pool generation;
- target environment, deployment, and jurisdiction;
- processing activity, operation, and immutable purpose;
- subject artifact, input, or data-object digest;
- immutable classification record;
- active policy version and evidence manifest; and
- authority, approval, code, and evaluation versions.

Reuse across another Tenant, Area, Project, Session, purpose, activity,
operation, artifact, jurisdiction, classification, recipient, transfer, policy
digest, or approval set is prohibited.

## Trust and input contract

### Trusted inputs

Trusted inputs are resolved from authenticated Runtime context or protected
ledger state:

```text
actor_id
tenant_id
area_id
project_id
session_id
authority_snapshot_digest
database_identity_and_pool_generation
active_policy_binding
approval_and_evidence_bindings
classification_record
decision_time
code_and_schema_versions
```

### Untrusted inputs

Request payloads may propose only opaque content and candidate metadata. They
cannot define or expand:

```text
identity
scope
authority
policy
approval
purpose authority
classification authority
legal basis
additional condition
retention
legal hold
lifecycle state
decision outcome
```

Payload content, prompts, observations, model output, memory content, tool
output, labels, and writable database settings are not trusted control state.

## Responsible components

### Trust-boundary adapter

Authenticates the caller, validates signed identity material, resolves the
Principal, and selects the Tenant-bound pool. It does not evaluate privacy
lawfulness or policy.

### Classification Gate

Validates or records a versioned classification for one exact subject digest.
Automated classifier output is evidence input only. Unknown, contradictory,
stale, unqualified, or scope-mismatched classification remains blocking.

### Policy Lifecycle Gate

Owns state transitions for immutable policy versions. It verifies authenticated
role authority, independence, exact-digest approvals, regression evidence,
expiry, revocation, and supersession. It cannot create missing qualified review.

### Privacy Processing Decision Gate

Loads the active policy and all bindings from protected state, applies the
fixed evaluation order, and emits an immutable decision. It cannot write Memory
Core protected state.

### Memory Transition Gate

Remains the only writer of protected Memory Core state. It invokes or consumes
the transaction-local privacy decision and writes only for target `ALLOW`.

### PostgreSQL protected ledger

Provides the authoritative Tenant anchor, transaction isolation, lifecycle
serialization, append-only decision and audit evidence, idempotency, and atomic
commit boundary.

## Reserved target outcome vocabulary

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

| Outcome | Target semantics | Protected mutation |
| --- | --- | --- |
| `ALLOW` | Every non-compensatory gate passed for the exact binding | Permitted only inside the same authoritative transaction |
| `DENY` | Security Floor, authority, scope, jurisdiction, operation, or explicit policy prohibition | Blocked |
| `REQUIRE_HUMAN_REVIEW` | Required accountable or qualified decision is pending | Blocked |
| `REQUIRE_ADDITIONAL_EVIDENCE` | Required evidence or safeguard proof is absent or incomplete | Blocked |
| `EXPIRED` | Policy, approval, review, classification, authority, or evidence is outside validity | Blocked |
| `REVOKED` | Required policy, approval, basis, condition, consent, or evidence binding is revoked | Blocked |
| `CONFLICT` | Multiple active policies or contradictory scope, classification, evidence, or version facts | Blocked |
| `UNKNOWN` | Unrecognized, corrupted, unavailable, or non-determinable required state | Blocked |

`ALLOW` is reserved target vocabulary only. Because current runtime activation
is false, no present caller or component can obtain an authoritative `ALLOW`
under this document.

## Deterministic evaluation order

The future gate evaluates in this order:

1. Validate request schema and reject undeclared or unknown control fields.
2. Resolve database Tenant from `session_user`; verify expected active pool
   generation and credential revision.
3. Resolve actor, Tenant, Area, Project, and Session from trusted Runtime
   context and verify immutable hierarchy lineage.
4. Apply the code-owned Security Floor.
5. Verify operation-specific authority and existing approvals.
6. Resolve the exact processing activity and immutable purpose.
7. Resolve the subject digest and current classification record.
8. Resolve exactly one active policy version server-side.
9. Verify policy scope, environment, jurisdiction, activity, purpose,
   operation, and classification match.
10. Verify general processing-basis evidence.
11. Where required, verify the additional special condition or Article 10
    disposition and every required qualified review.
12. Verify safeguards, minimization, access, rights, retention, deletion,
    recipients, processors, location, transfer, and derivative handling.
13. Verify all policy, evidence, approval, authority, review, classification,
    and reassessment validity windows and revocation states.
14. Verify audit and atomic commit capability.
15. Produce one decision with all observed stable reason codes.

The gate may stop early for a hard Security Floor or authenticated-scope
failure. Otherwise, it records all independently observed blockers. It never
averages, scores, or compensates failed gates.

When multiple non-hard blockers exist, the primary outcome precedence is:

```text
CONFLICT
UNKNOWN
REVOKED
EXPIRED
REQUIRE_ADDITIONAL_EVIDENCE
REQUIRE_HUMAN_REVIEW
DENY
ALLOW
```

All detected blockers remain present as reason codes regardless of the primary
outcome.

## Non-compensatory decision requirements

The following conditions are independently mandatory:

- complete authenticated identity and scope;
- matching Tenant-bound database identity;
- released operation under the Security Floor;
- sufficient current authority;
- exact processing activity and purpose;
- known, non-conflicting classification;
- supported deployment environment and jurisdiction;
- approved general basis;
- approved additional condition where the classification requires it;
- approved Article 10 disposition where applicable;
- current safeguards and minimization controls;
- current retention, deletion, legal-hold, rights, and derivative rules;
- current recipient, processor, location, and transfer disposition;
- one active immutable policy version;
- complete owner, qualified reviewer, and independent activation evidence;
- no suspension, revocation, expiry, incident stop, restore stop, or unresolved
  reassessment trigger;
- writable owning Gate, available audit ledger, and atomic commit capability.

Missing purpose cannot be compensated by consent evidence. Approval cannot
create missing authority. A general basis cannot replace an additional special
condition. Safeguards cannot make an unsupported jurisdiction or unknown data
class allowable. A favorable reviewer statement cannot override a Security
Floor prohibition.

## Decision record

Every future decision record is immutable and contains at least:

```text
decision_id
decision_schema_version
transition_request_id
actor_id
tenant_id
area_id
project_id
session_id
operation
subject_kind
subject_id_or_digest
processing_activity_id_and_digest
purpose_id_and_digest
classification_id_and_digest
general_basis_evidence_digest
additional_condition_evidence_digest_or_explicit_not_applicable_binding
safeguard_and_retention_manifest_digest
policy_id_version_and_digest
policy_activation_event_id
approval_manifest_digest
authority_snapshot_digest
input_parameter_digest
decision_time
valid_until
outcome
reason_codes
obligations
required_review_roles
executing_component
code_version
model_version_or_explicit_model_not_used
downstream_action
mutation_and_audit_correlation
```

The decision is valid only for exact equality of every bound fact and only
until the earliest bound expiry. It cannot be replayed to authorize another
scope or operation.

## Atomic future mutation sequence

The final authoritative evaluation occurs inside the owning database mutation
transaction, not in a remote policy check performed earlier.

```text
BEGIN
  resolve immutable Tenant identity
  validate trusted scope, Security Floor, and authority
  resolve and lock the active policy lifecycle head
  resolve and revalidate immutable evidence and approval bindings
  resolve the exact classification and metadata binding
  create the transaction-local privacy decision
  IF outcome = target ALLOW THEN
      execute Memory Transition Gate writes
      append decision and mutation audit evidence
      persist exact-input idempotency receipt
  ELSE
      append decision evidence only
      perform no protected data mutation
  END IF
COMMIT
```

Activation, suspension, revocation, supersession, and protected mutation use a
shared serialized lifecycle head. The ordering of concurrent revocation and
mutation is therefore determined by the database commit order rather than an
application cache.

The adapter returns success only after commit. If decision evidence, audit,
receipt, policy locking, or protected mutation fails, the transaction rolls
back. No partial write, audit-free write, cached `ALLOW`, or permissive retry is
allowed.

An exact idempotent replay returns the already committed receipt without
performing a new mutation. A changed input under the same request identifier is
rejected. A previously denied request identifier never becomes allowed after a
policy change; a new request identifier and fresh decision are required.

## Direct-bypass protections

Future implementation must prove:

- Runtime identities use `NOINHERIT` and `NOBYPASSRLS`.
- Productive Runtime pools are Tenant-specific and an established connection
  cannot switch Tenant.
- Protected policy, classification, approval, decision, and target data tables
  use RLS and `FORCE ROW LEVEL SECURITY`.
- `PUBLIC`, readers, general application roles, models, planners, and consumers
  have no direct table mutation privileges.
- Only the owning Gate has the minimum required function execution privilege.
- Gate functions use a non-login owner, fixed trusted search path, qualified
  object references, strict argument validation, and no dynamic SQL from
  untrusted values.
- The caller cannot submit authoritative policy IDs, activation state,
  approvals, classification outcomes, retention decisions, or `ALLOW`.
- Policy and decision caches are non-authoritative and cannot survive a
  revocation or generation mismatch.
- Audit evidence is append-only and integrity protected.
- Direct SQL, forged writable settings, stale connections, role changes,
  restored stale policies, and alternate service paths cannot bypass the gate.

## Policy lifecycle behavior

Runtime evaluation recognizes only `ACTIVE` as eligible for target `ALLOW`.

```text
DRAFT -> PENDING_REVIEW -> APPROVED -> ACTIVE
PENDING_REVIEW -> REJECTED
ACTIVE -> SUSPENDED
SUSPENDED -> ACTIVE  # unchanged digests plus independent reconciliation only
APPROVED|ACTIVE|SUSPENDED -> REVOKED|EXPIRED|SUPERSEDED
```

`DRAFT`, `PENDING_REVIEW`, `APPROVED`, and `SUSPENDED` block processing.
`REVOKED`, `EXPIRED`, `REJECTED`, and `SUPERSEDED` are terminal and cannot be
reactivated. Policy content, evidence content, scope, purpose, classification,
conditions, safeguards, retention, or reviewer set changes always create a new
immutable version.

## Revocation and reassessment

The following trigger immediate blocking and a recorded reassessment event:

- withdrawal or loss of a relied-on basis, condition, consent, or approval;
- purpose or processing-activity change;
- classification or data-subject population change;
- artifact, model, supplier, recipient, processor, location, or transfer change;
- safeguard, minimization, retention, deletion, legal-hold, or rights change;
- policy, evidence, review, or authority expiry;
- evidence contradiction, incident, complaint, material misuse, or integrity
  failure; and
- code, schema, database, Gate, restore, or deployment change that can alter the
  decision boundary.

The gate stops new processing. Separately authorized lifecycle operations may
restrict access, suspend jobs, quarantine data, initiate deletion, propagate a
correction, or reconcile an indeterminate state. The privacy decision itself
does not directly delete or mutate derivatives.

Affected lineage includes payloads, observations, working state, checkpoints,
summaries, embeddings, indexes, caches, candidates, reports, exports, and
backups. Legal hold and retention are evaluated through their authorized paths;
unknown state blocks destructive action as well as continued processing.

## Backup and restore

Backups do not create alternate policy authority. A restore is isolated and
non-serving until independent recovery acceptance verifies:

- backup manifest, source, digest, and WAL continuity;
- exact migration and release compatibility;
- Tenant Runtime identities, pool generations, and credential revisions;
- hierarchy lineage, RLS, FORCE, and Gate-only writer privileges;
- policy definitions, lifecycle heads, approvals, evidence, classification,
  decisions, receipts, and audit-chain continuity;
- revocation, expiry, retention, legal-hold, and deletion state at the selected
  recovery point; and
- reconciliation of all state after the recovery point before cutover.

Special-category processing remains inactive or `SUSPENDED` after restore until
those checks and an authorized cutover decision complete. A stale restored
`ACTIVE` value is never sufficient.

## Failure behavior

| Failure | Required behavior |
| --- | --- |
| Policy or evidence service unavailable | Block; `UNKNOWN` where a durable decision can be recorded |
| Database or audit unavailable | Roll back; no protected mutation |
| Timeout or process interruption | Treat outcome as unknown; reconcile before retry |
| Stale cache or pool generation | Evict and block |
| Concurrent revocation | Serialize on lifecycle head; commit order decides validity |
| Corrupt evidence or digest mismatch | `CONFLICT` or `UNKNOWN`; block |
| Partial migration | Capability inactive; block |
| Restore with incomplete reconciliation | `SUSPENDED`; no serving cutover |

No error state may produce target `ALLOW`.

## Claim limits

This target contract does not approve a legal basis, special condition, Article
10 control, data class, purpose, retention period, safeguard, reviewer, policy,
deployment, processing activity, or release. It does not implement a Runtime
Gate or prove bypass resistance. It cannot satisfy S1-14.4 or entitle S1-11.2
to store data. Current runtime activation is **false**, and `ALLOW` remains
reserved target vocabulary only.
