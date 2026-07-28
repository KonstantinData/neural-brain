# S1-14.4 Privacy Ledger Migration Plan v1

- Status: Proposal only; pending accountable-owner and qualified review
- Applies to: S1-14.4 preparation and the later S1-11.2 protected-storage integration
- Runtime enabled: no
- `ALLOW` authorized: no
- Executable migration delivered by this plan: none

## Purpose and boundary

This plan defines a reviewable migration sequence for a future privacy-policy
ledger and atomic protected-storage enforcement path. It does not create a
database object, legal basis, special-category condition, approval, active
policy, runtime decision, storage permission, or release outcome.

The current repository already has immutable scope catalogs, Tenant-bound
database identities, authority snapshots, gate-only writes, transition
receipts, append-only audit evidence, a hash chain, and audit redaction. The
future design must extend those controls. It must not reinterpret the existing
`memory_core.observations.classification` field as a privacy classification or
the existing free-text `purpose` field as a versioned approved purpose.

The evidence-intake contracts for Article 6, Article 9, Article 10, consent,
RoPA, data-object catalogue, and personal-data flows remain qualified-review
inputs. They never become runtime authority merely because their document
shape is complete.

## Proposed ownership model

The future `brain_privacy` schema would hold immutable, scope-bound rule-set,
classification, policy, evidence-reference, approval, lifecycle, and decision
records. The future `privacy_gate` schema would hold the only SECURITY DEFINER
functions allowed to transition privacy policy state or evaluate protected
storage. Runtime roles would receive no direct table-write privilege.

All persistent rows would retain immutable Tenant and Area identity. Policy
and protected-storage records in the first operational slice would also retain
Project and Session identity where applicable. Scope supplied by a payload,
prompt, model result, tool result, memory value, or consumer correlation would
remain untrusted.

## Proposed migration sequence

### `0016_privacy_policy_ledger.sql`

Preparation migration, subject to accepted schema and database review:

- create `brain_privacy` and `privacy_gate` with ownership by
  `neural_brain_owner` and no PUBLIC privileges;
- create immutable version tables for rule sets, protected-data
  classifications, processing policies, evidence references, and review
  approvals;
- create append-only policy lifecycle events and immutable processing decision
  records;
- create a gate-owned active-policy pointer whose historical truth remains the
  lifecycle event ledger;
- apply composite scope foreign keys, bounded identifiers, digest checks,
  validity-window checks, forced RLS, immutable-scope triggers, and append-only
  triggers;
- create no default rule set, data class, purpose, legal basis, special
  condition, approval, active pointer, or `ALLOW` decision;
- leave every runtime evaluation disabled and fail closed.

The migration must be valid on both a fresh database and an upgraded database.
It must not copy governance values from an existing request or payload.

### `0017_privacy_policy_transition_gate.sql`

Preparation migration, still non-authorizing:

- add gate functions for registering immutable versions, attaching evidence
  references, recording independent reviews, and appending lifecycle events;
- validate exact policy, rule-set, classification, purpose, activity,
  jurisdiction, retention, protection, evidence, approval, and scope bindings;
- reject unknown fields, versions, states, transitions, actors, scopes,
  digests, validity facts, and requirement codes;
- enforce the state machine in
  `contracts/special-category-policy-state-machine-v1.json`;
- return only a blocking preparation result while the accepted runtime
  contract has `runtime_enabled=false` or `allow_authorized=false`;
- extend the audit-redaction trigger with explicitly approved privacy event
  types before any such event can be appended;
- preserve the existing per-Tenant/Area audit hash chain and atomicity.

No function in this migration may authorize a protected mutation.

### `0018_memory_governance_bindings.sql`

Preparation migration for S1-11.2 integration:

- create an immutable normalized governance-binding table containing only
  typed metadata, references, versions, and digests;
- create scope-bound association tables for observations, working-context
  versions, checkpoints, memory candidates, and any selected cognitive
  transition evidence;
- bind each governed record to its data-object type, technical security
  classification, protected-data classification, purpose, processing
  activity, data-subject reference mode, source evidence, retention policy,
  protection profile, exact processing policy, approval set, evidence set, and
  decision;
- require the referenced decision outcome to be exactly `ALLOW` through an
  exact composite reference in the later enabled design;
- add deferred commit-time enforcement so a new protected record cannot commit
  without its binding once cutover is authorized;
- do not backfill existing rows with guessed classifications, purposes, legal
  bases, retention rules, or approvals.

Existing unbound records would be legacy reconciliation inputs. They would not
be treated as approved, and protected reads or further processing would remain
blocked until an authorized reconciliation, deletion, or anonymization result
exists.

### `0019_privacy_enforcement_cutover.sql`

Post-authorization migration only. It must not be authored or applied until:

- the accountable owner has approved the exact deployment scope;
- qualified privacy and required legal review are current and digest-bound;
- the independent security and architecture reviews have no open Critical or
  High finding;
- the runtime contract, rule set, classifications, purposes, activities,
  retention policies, protection profiles, rollback, and incident behavior
  are accepted;
- legacy protected records have an authorized reconciliation disposition;
- application and database cutover compatibility has been demonstrated.

The proposed cutover would:

1. lock affected protected tables for the bounded cutover transaction;
2. verify migration-plan digest, audit continuity, active policy uniqueness,
   approval validity, policy validity, and legacy reconciliation completion;
3. revoke EXECUTE from the old protected write signature before enabling the
   replacement path;
4. enable one database transaction that resolves authenticated scope, validates
   metadata, evaluates the current policy, appends the decision, commits the
   protected mutation and governance binding, writes the transition receipt,
   and appends redacted audit evidence;
5. roll back the complete transaction on validation, policy, audit, receipt,
   storage, timeout, or connection failure;
6. leave old or incompatible clients failing closed;
7. require startup and restore reconciliation before readiness.

Only this post-authorization cutover may make an accepted `ALLOW` consumable,
and only inside the same protected transaction. A decision is single-use and
cannot be replayed for another record, purpose, activity, scope, policy
version, or evidence set.

## Versioning and bitemporal requirements

- Immutable policy, rule-set, classification, approval, and evidence records
  use explicit positive integer versions and canonical SHA-256 digests.
- Valid time is represented by `valid_from` and `valid_until`.
- Transaction time is database-generated `recorded_at` using
  `transaction_timestamp()`.
- Lifecycle events additionally carry `effective_at`.
- Approval or activation cannot be backdated to authorize an earlier
  operation.
- A recorded suspension, revocation, or expiry blocks future decisions and
  starts reconciliation for affected prior decisions from its effective time.
- Corrections create a new immutable version; they never rewrite history.
- Terminal versions never reactivate. A new active policy requires a new
  version and an audited pointer transition.

## Backward compatibility and rollout

The existing technical classifications and purpose strings remain historical
fields with their original meaning. No automatic conversion is safe.

A compatible rollout would first deploy readers and adapters that understand
the new contract while the evaluator remains disabled. It would then reconcile
legacy records under explicit owner and qualified-review authority. The final
cutover would revoke the old write path and enable the new gate atomically.
Clients that have not adopted the new metadata contract would receive a
bounded denial rather than a permissive fallback.

Rollback cannot silently restore an older active policy or old write path. It
must restore code and schema only to a state that still denies protected
processing, reconcile policy pointers and audit continuity, and require a new
authorized activation if processing is to resume.

## Required migration and database evidence

Before any executable migration is accepted, tests must prove:

- fresh and upgraded PostgreSQL 18 migration paths;
- exact scope lineage and forced RLS;
- runtime-role direct writes are denied;
- policy and evidence versions are immutable;
- every legal-basis, special-condition, Article 10, consent, safeguard,
  retention, approval, and auditability requirement resolves exactly as the
  accepted rule set requires;
- unknown and inconsistent values never produce `ALLOW`;
- expired, suspended, revoked, rejected, superseded, or conflicting policies
  never produce `ALLOW`;
- mutation, governance binding, decision, receipt, and audit are atomic;
- audit failure, policy failure, stale active pointer, concurrent revocation,
  crash, timeout, and restore fail closed;
- legacy unbound records cannot be returned or further processed as approved;
- the old write path is unavailable after cutover;
- the authoritative ledger and audit chain reconcile before readiness.

## Decision still required

This plan deliberately leaves jurisdiction rules, supported purposes,
processing activities, protected-data taxonomy, Article 6 basis codes, Article
9 conditions, Article 10 controls, consent conditions, retention periods,
protection measures, required reviewer roles, and revalidation intervals to
the accountable owner and qualified review. Missing decisions are blockers,
not implementation defaults.
