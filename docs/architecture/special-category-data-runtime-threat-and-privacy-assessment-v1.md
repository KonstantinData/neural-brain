# Special-Category Data Runtime Threat and Privacy Assessment v1

- Status: Preparation-only security and privacy assessment
- Scope: S1-14.4 runtime enforcement and the dependent S1-11.2 storage boundary
- Runtime authorization: Not granted
- Production authorization: Not granted
- Governing baseline: ADR-004, ADR-005, ADR-012, ADR-018, ADR-019, and
  Architecture Directive v4.0

## Purpose and authority boundary

This assessment defines the security and privacy delta for a future runtime
contract covering special-category personal data and other specially protected
data. It supplements, and does not replace, the repository-wide
[`threat-model.md`](threat-model.md), the Article 9/10 preparation contract,
the Tenant-bound database operating contract, or the protected-ledger backup
and recovery contract.

The current repository contains evidence-intake preparation and an early
Memory Core. It does not contain an accepted S1-14.4 runtime authorization.
This document does not determine a lawful basis, select an Article 9 condition,
authorize Article 10 processing, approve a purpose, assign a qualified owner,
activate a policy, enable productive storage, or establish compliance.

S1-11.2 may use this assessment to prepare strict types, schemas, validators,
interfaces, disabled evaluators, and test fixtures. It must not persist or
process specially protected data until the accepted S1-14.4 contract and every
P0/P1 gate below are independently verified.

## Relationship to the master threat model

The master threat model remains authoritative for identity, scope, Gate-only
writes, PostgreSQL, audit, retention, deletion, derivatives, backup, restore,
and readiness. This assessment narrows those controls to the proposed sequence:

```text
authenticated scope
-> metadata and classification validation
-> current protected policy and evidence resolution
-> S1-14.4 decision
-> protected mutation gate
-> atomic decision, storage, receipt, and redacted audit commit
```

The sequence is one protected transaction boundary, not a chain of independent
application checks. Any missing stage, stale binding, ambiguous outcome, or
failure denies the operation. Only a committed `ALLOW` may authorize the exact
mutation to which it is bound.

Existing controls that must be preserved include Tenant-bound database
identity, immutable authenticated Tenant/Area/Project/Session scope, dedicated
Gate roles, no direct runtime table DML, RLS plus `FORCE ROW LEVEL SECURITY`,
fixed `SECURITY DEFINER` search paths, short transactions, idempotency
receipts, redacted append-only audit, and audit-failure rollback. Their current
existence is not evidence that S1-14.4 is implemented.

## Protected assets and added trust boundaries

| ID | Asset or boundary | Required property |
| --- | --- | --- |
| SCD-A01 | Data-classification result | Complete, deterministic, versioned, conflict-visible, and incapable of self-authorizing storage |
| SCD-A02 | General basis, additional special condition, purpose, jurisdiction, safeguards, retention, and review evidence | Authentic, current, scope-bound, independently reviewed where required, and immutable by ordinary runtime actors |
| SCD-A03 | Policy document, active-version pointer, and revocation fence | Version integrity, single active version per exact scope, monotonic invalidation, and no caller-controlled activation |
| SCD-A04 | Runtime decision | Server-produced, exact-input-bound, expiry-bound, non-replayable outside scope, and terminal for one attempted mutation |
| SCD-A05 | Protected personal-data mutation | Gate-only, minimized, purpose-bound, retention-bound, and atomically coupled to decision and audit |
| SCD-A06 | Decision and incident audit | Minimal, secret-free, payload-free, immutable, causally linked, and sufficient for independent reconstruction |
| SCD-A07 | Caches, indexes, embeddings, summaries, jobs, exports, and other derivatives | Same scope and policy version as the source, revocable, discoverable, and deletion-propagating |
| SCD-A08 | Backups, WAL, restore targets, and recovery decisions | Encrypted, access-separated, retention-aware, quarantined before readiness, and incapable of resurrecting stale authorization |

The added trust boundaries are:

1. untrusted payload to typed metadata;
2. typed metadata to trusted classification and policy identifiers;
3. policy author or reviewer evidence to a protected activation record;
4. current activation, approval, and authority state to a runtime decision;
5. decision to the sole protected storage Gate;
6. committed source state to derivatives and long-running jobs;
7. revocation or expiry to cache invalidation, job fencing, and deletion work;
8. backup or restored state to quarantined reconciliation and serving readiness.

## P0 threats and mandatory gates

| ID | Threat | Required gate before any runtime activation |
| --- | --- | --- |
| SCD-P0-01 | The current Memory Gate admits a coarse `classification` and free-form `purpose` after general ingest authority without an S1-14.4 decision. Specially protected content could therefore be stored without the required basis, additional condition, retention, safeguard, or qualified review. | The accepted runtime contract defines the complete decision input and only a server-produced, current, exact-scope `ALLOW` reaches the protected mutation. |
| SCD-P0-02 | A caller forges a policy decision, approval object, approver role, policy digest, or evidence reference. Preparation-only Python models or evidence tables are treated as runtime authority. | The Gate loads immutable policy, authority, approval, reviewer-role, and evidence records from protected storage by exact identifiers and digests. Caller-supplied outcome, role, owner, scope, or activation state is rejected. |
| SCD-P0-03 | Policy evaluation occurs before the database transaction. Revocation, expiry, reviewer-role loss, policy supersession, scope suspension, or retention change races with storage. | Decision, current-version and revocation-fence checks, mutation, receipt, and audit execute in one transaction. Required records are locked or checked by a monotonic revision/fence immediately before commit. |
| SCD-P0-04 | Payload is copied into observations, working versions, checkpoints, idempotency receipts, logs, or audit. Immutable history then prevents complete correction, retention, or deletion. | The data inventory identifies every raw and reconstructive copy. The runtime contract minimizes receipts and audit to digests and references and supplies an authorized, resumable deletion/anonymization path for every protected copy. |
| SCD-P0-05 | Revocation or expiry stops a primary request but stale caches, indexes, embeddings, exports, queues, retries, or long-running jobs continue processing or disclose prior results. | Every derivative and job carries source scope, policy version, decision reference, retention state, and revocation fence. Current fence validation occurs before use and before every protected commit; unknown propagation state blocks availability. |
| SCD-P0-06 | A backup or PITR restore reintroduces an old active policy, approval, grant, raw copy, deleted record, or stale cache and resumes service automatically. | Restore is isolated and `not_ready`. Current policy/grant/reviewer state, revocation fences, deletion tombstones, audit continuity, role graph, and derivatives are reconciled before an independently authorized cutover. |

An open P0 is a release stop. A technical implementation cannot compensate for
missing owner, privacy, legal, jurisdiction, purpose, Article 9, Article 10, or
retention decisions.

## P1 threats and mandatory verification

| ID | Threat | Required verification |
| --- | --- | --- |
| SCD-P1-01 | `restricted` is treated as a sufficient special-category taxonomy, or an unknown/conflicting classification is silently downgraded. | The accepted taxonomy distinguishes the supported classes and represents unknown/conflict explicitly as non-allowing decision input. |
| SCD-P1-02 | Free-form, whitespace, case, Unicode, or payload-defined purpose values bypass an allow-list. | Purpose is a canonical protected identifier bound to exact policy scope; malformed, unknown, broader, or changed purpose denies. |
| SCD-P1-03 | A broad `can_ingest` grant or general application role bypasses the purpose-, class-, and evidence-specific decision. | General authority remains necessary but never sufficient. Runtime roles have no direct DML and no ability to activate policies, write approvals, or assume owner/provisioner roles. |
| SCD-P1-04 | Audit records show a committed mutation but omit the policy version, evidence references, result, reason codes, or code version, or contain raw sensitive payload. | The approved audit event schema retains the minimum decision proof and correlation while the redaction contract rejects raw data, identifiers, credentials, prompts, or evidence bodies. |
| SCD-P1-05 | Two policy versions become active, a superseded/revoked version becomes active again, or an old decision is replayed. | A protected state machine and unique active-version invariant enforce permitted transitions and bind each decision to the current immutable version and fence. |
| SCD-P1-06 | Database owner, migration, restore, or break-glass access becomes an ordinary runtime bypass. | Privileged paths remain separately authenticated, approved, time-bounded, audited, and excluded from Runtime pools; role, ownership, grant, RLS/FORCE, and definer-path drift is tested. |
| SCD-P1-07 | Audit or policy-service failure degrades to a permissive response, or an ambiguous commit is retried blindly. | Every dependency failure denies. Unknown commit outcome becomes `indeterminate` and is reconciled using the immutable transition identity before any retry. |

## Privacy engineering assessment

### Data minimization and raw-copy control

The protected payload must be stored only when the accepted purpose requires
it and only in the minimum authorized fields. Classification, decision, audit,
idempotency, telemetry, and incident records should retain identifiers,
digests, reason codes, and durable evidence references rather than duplicate
personal-data values.

Before activation, the data-flow inventory must enumerate observations,
working and context memory, checkpoints, transition receipts, evidence logs,
caches, indexes, embeddings, summaries, exports, queues, test fixtures,
backups, WAL, and restore targets. A missing inventory row blocks processing.

### Purpose, basis, safeguards, and retention

Purpose, general basis, additional special condition when required,
jurisdiction, safeguards, approval, retention policy, and evidence version are
independent non-compensatory gates. One positive field cannot substitute for a
missing field. A data-class change, purpose change, evidence expiry, reviewer
revocation, policy supersession, or safeguard loss invalidates the old decision
and requires a new evaluation before further processing.

### Revocation, correction, and deletion

Revocation stops new protected commits and invalidates cached decisions. It
also creates scoped follow-up work for blocking access, terminating or fencing
jobs, invalidating derivatives, and evaluating correction, deletion,
anonymization, legal hold, incident preservation, and backup expiry. Revocation
does not itself authorize destructive deletion, and legal hold does not permit
continued incompatible processing.

Deletion completion requires reconciliation evidence for every primary and
reconstructive copy. Immutable audit may retain only the minimum permitted
proof that an operation occurred; it must not retain the deleted payload.

## Required negative and failure evidence

The future implementation must provide executable evidence for at least:

- payload attempts to supply Tenant, Area, Project, Session, owner, role,
  policy version, approval, evidence status, retention override, or `ALLOW`;
- missing, unknown, contradictory, malformed, whitespace, Unicode-confusable,
  or unsupported classification and purpose values;
- missing general basis or required additional special condition;
- cross-Tenant, cross-Area, cross-Project, cross-Session, cross-purpose,
  cross-environment, and cross-policy evidence reuse;
- forged, unpersisted, digest-mismatched, stale, expired, future-dated,
  self-approved, revoked, rejected, or superseded evidence;
- concurrent policy supersession, approval revocation, role loss, scope
  suspension, retention change, or evidence expiry while a write is paused;
- direct table `SELECT`, `INSERT`, `UPDATE`, and `DELETE`, unsafe role
  assumption, ownership, schema creation, RLS/FORCE drift, and unsafe
  `SECURITY DEFINER` search paths;
- audit insert failure, policy lookup failure, timeout, deadlock,
  serialization failure, process termination, connection loss, and ambiguous
  commit outcome at every protected commit boundary;
- stale caches, indexes, embeddings, queued retries, and long-running jobs
  after revocation or policy-version change;
- incomplete deletion where a receipt, checkpoint, version, cache, derivative,
  WAL segment, backup, or restore target still permits reconstruction;
- restore of an older active policy, approval, grant, role mapping, raw copy,
  deletion state, or revocation fence while readiness remains false.

For every injected failure, the expected result is either no protected state,
decision, receipt, or audit row, or one complete mutually bound commit. A
returned `ALLOW` without a known committed result is prohibited.

## Residual blockers and non-claims

This assessment does not close the accepted-contract, qualified-review,
deployment, privacy, legal, backup, restore, deletion, monitoring, or release
stops. It supplies preparation requirements only. Runtime activation remains
blocked until all P0 and P1 gates have current repository, PostgreSQL,
independent-review, and deployment-specific evidence.
