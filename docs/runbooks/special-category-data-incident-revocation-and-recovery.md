# Special-Category Data Incident, Revocation, and Recovery Preparation

## Scope and readiness boundary

This preparation runbook defines the target incident, revocation, containment,
deletion, and recovery behavior for a future S1-14.4 runtime. It supplements
[`special-category-data-runtime-enforcement.md`](special-category-data-runtime-enforcement.md),
[`tenant-database-operations.md`](tenant-database-operations.md), and
[`protected-ledger-backup-recovery.md`](protected-ledger-backup-recovery.md).

It is not a production incident plan, a legal-notification determination, a
processing authorization, or evidence that revocation, deletion, backup, PITR,
restore, monitoring, paging, or recovery is deployed. No real personal data may
be admitted on the strength of this document.

## Trigger conditions

Open a scoped incident or protected revocation workflow when any of the
following is suspected or observed:

- forged, missing, stale, contradictory, or scope-mismatched policy, approval,
  reviewer, authority, evidence, classification, purpose, or retention state;
- special-category or otherwise protected data stored without a committed
  exact-scope `ALLOW`;
- direct database write, unsafe role assumption, RLS/FORCE drift, definer-path
  drift, or privileged bypass;
- revocation, expiry, purpose change, classification change, safeguard loss,
  reviewer-role loss, policy supersession, or unsupported jurisdiction;
- raw personal data in audit, logs, telemetry, receipts, evidence, test output,
  queues, caches, indexes, embeddings, exports, backups, or restore targets;
- stale cache, derivative, queued retry, or long-running job continuing after
  revocation;
- partial commit, missing audit, hash-chain failure, ambiguous outcome, or
  blind retry;
- restored data or authorization state exposed before reconciliation;
- incomplete correction, deletion, retention expiry, legal-hold evaluation, or
  backup destruction.

Unknown scope or impact is treated as the highest affected protection class
for containment. This precaution does not make a legal classification or
notification decision; qualified owners make those decisions separately.

## Roles and evidence separation

| Activity | Required future role | Separation rule |
| --- | --- | --- |
| Detection and evidence preservation | Monitoring or security responder | Cannot reactivate processing |
| Immediate capability reduction | Protected-control-plane incident operator | Cannot approve own recovery |
| Privacy and legal assessment | Assigned qualified reviewer | Does not alter technical evidence |
| Scope and data-flow investigation | Security and privacy engineers | Uses minimized, access-controlled evidence |
| Deletion or anonymization decision | Authorized lifecycle owner | Separate from ordinary Runtime worker |
| Backup/restore operation | Restricted recovery operator | Restore remains isolated and non-serving |
| Recovery verification | Independent verifier | Tool success is not acceptance |
| Service reactivation | Authorized recovery decision owner | Requires closed gates and current evidence |

Credentials, raw personal data, evidence bodies, legal advice, and live subject
identifiers must not enter repository files, Notion, generic incident tickets,
logs, command output, PRs, or chat. Use opaque references to separately
protected evidence.

## Immediate containment target

The exact response depends on the authorized deployment plan. The target
fail-closed order is:

1. preserve immutable, secret-free detection and correlation evidence;
2. mark the affected Tenant/Area/Project/Session, policy version, purpose,
   classification, data-object type, jobs and derivatives as potentially
   affected without broadening access to investigate;
3. stop new admission and protected commits for the affected scope by changing
   a protected monotonic revocation fence or equivalent Gate-owned state;
4. disable routing and evict affected Tenant pool generations when identity,
   credential, role, or database-bound scope may be compromised;
5. fence or terminate running jobs, consumers, exports, indexers, embedding
   workers and queued retries before they can perform another protected commit;
6. quarantine affected caches, indexes, embeddings, summaries, exports and
   restore material from retrieval or processing;
7. retain ambiguous operations as `indeterminate` and reconcile by transition
   ID and exact request digest; do not retry blindly;
8. assign accountable incident, privacy, legal, deletion, backup and recovery
   owners and record the separate decisions still required.

Containment may reduce capability. It must not invent missing authority,
silently change purpose, downgrade classification, delete evidence, or activate
another policy as a convenience fallback.

## Policy, approval, and authority revocation

A revocation record must identify the immutable policy/evidence/grant or
reviewer binding, exact authenticated scope, prior version, expected fence,
reason code, authorized actor, effective time, incident reference, and required
downstream actions without storing the protected payload.

The protected transition must:

- reject a stale expected version or fence;
- move only through an allowed state transition;
- prevent `REVOKED`, `EXPIRED`, `REJECTED`, or `SUPERSEDED` state from returning
  directly to `ACTIVE`;
- invalidate every cached decision bound to an older version or fence;
- append an atomic redacted audit event;
- create resumable follow-up work for jobs, derivatives, retention, deletion,
  backups, and reconciliation;
- remain idempotent for the same transition and input digest.

Revocation blocks future use. It does not by itself select deletion over legal
hold, authorize destruction, prove that downstream processing stopped, or
resolve notification duties.

## Cache, derivative, and running-job containment

Every cache entry, index row, embedding, summary, export, queue message and job
checkpoint must be discoverable by authenticated scope, source reference,
policy version, decision reference, retention state and revocation fence.

Preparation and future exercises must prove:

- a worker checks the current fence before reading protected input and again
  immediately before every protected output commit;
- a cache hit with an old policy version or fence is denied rather than served;
- a queue retry cannot reuse an expired or revoked decision;
- a job interrupted after producing an uncommitted derivative cannot publish
  or activate it after restart;
- quarantined derivatives are unavailable to retrieval, inference, export,
  Dreaming, training and promotion;
- reconciliation records every derivative as deleted, anonymized, retained
  under an authorized hold, or still blocking completion.

The absence of a cache or job error is not proof that revocation propagated.

## Data minimization, correction, retention, and deletion

Investigators access only the minimum fields necessary for their assigned role.
Prefer digests, reason codes, scope references, policy versions, transition IDs
and timestamps over raw content. Any exceptional access to protected content is
separately authorized, time-bounded and audited.

For each affected data object, classify the required lifecycle disposition:

```text
blocked from further use
pending qualified review
correction or supersession required
deletion or anonymization authorized
retained under an authorized legal hold
indeterminate pending reconciliation
```

Deletion or anonymization is complete only after the authoritative record,
working/context copies, immutable-history payload copies, receipts,
checkpoints, caches, indexes, embeddings, summaries, exports, queues, replicas,
eligible backups and restore targets are reconciled. Audit retains only the
minimum permitted non-reconstructive proof. A primary-row deletion alone is
not completion.

## Backup resurrection and restore quarantine

Follow the protected-ledger backup and recovery contract. A restored database
is untrusted for serving even when PostgreSQL starts and integrity checks pass.
Restore only into an isolated non-serving environment with separate recovery
credentials and no Runtime pool or production cutover route.

Before any recovery acceptance, independently compare the restored state with
current protected-control-plane evidence for:

- Tenant-role mappings, credential revisions, grants and pool routing;
- policy active pointers, immutable versions and revocation fences;
- owners, reviewer identities, approval status and evidence expiry;
- classification, purpose, basis, additional condition, safeguards and
  retention state;
- deletion and correction tombstones, legal holds and pending propagation;
- audit sequence, hash-chain continuity and incident evidence;
- cache, index, embedding, export, job and queue invalidation state;
- migration and release-artifact compatibility, RLS, FORCE, grants, ownership,
  triggers and definer search paths.

An older backup value never wins merely because it is internally consistent.
Any stale, missing, contradictory, scope-mismatched or unreconciled fact keeps
the target quarantined and `not_ready`. Do not activate a restored policy,
approval, grant, credential, data record, cache or job automatically.

## Investigation and decision package

Produce a secret-free package that distinguishes repository facts, runtime
evidence, external qualified decisions and remaining uncertainty. At minimum
record:

- incident and immutable correlation identifiers;
- detection source and time;
- affected and potentially affected authenticated scope;
- policy, evidence, decision, code, migration and release versions;
- data-object and derivative categories, not raw values;
- known transitions, revocations, failures, ambiguous outcomes and retries;
- containment actions and independently observed results;
- retention, legal-hold, deletion, backup and restore implications;
- required accountable owner, privacy, legal, security, recovery and release
  decisions with explicit status;
- next safe action and the exact evidence required to close each blocker.

Do not infer that a technical containment result resolves legal, privacy,
contractual, notification, data-subject, retention or release obligations.

## Recovery and reactivation gate

Recovery is a new protected decision, never reversal by deleting or editing the
incident record. Service remains blocked until all applicable criteria are
independently verified:

1. root cause and affected scope are bounded or the remaining uncertainty is
   accepted by the authorized decision owner;
2. compromised credentials, roles, policies, approvals, evidence and caches
   are revoked or replaced with new immutable versions;
3. no P0/P1 finding remains open for the intended scope;
4. required correction, deletion, legal hold and derivative reconciliation is
   complete or explicitly blocks only an isolated non-serving scope;
5. audit continuity and every ambiguous commit are reconciled;
6. restored state, if any, passes quarantine checks and independent witness;
7. negative, race, failure, direct-bypass, revocation and recovery tests pass
   against the exact release artifact and deployment-equivalent roles;
8. accountable owner, qualified reviewers, security verifier and recovery
   decision owner approve the exact bounded reactivation;
9. a new active policy version or recovery fence is committed atomically with
   its redacted audit evidence.

Reactivation never restores an expired, revoked, rejected or superseded
version. It creates a new current version after separate authorization.

## Required exercises and failure tests

Before productive approval, exercise at least:

- forged approval or policy evidence discovered after an apparent commit;
- policy revocation while a protected write is paused;
- reviewer-role revocation and purpose change during a long-running job;
- stale cache and queued retry after fence increment;
- direct database write or unsafe role grant detection;
- raw personal data detected in audit, receipt, telemetry or test output;
- audit failure and ambiguous client disconnect at commit;
- incomplete deletion with a remaining checkpoint, receipt, embedding or
  backup copy;
- restore of an older active policy, grant, deleted payload and credential
  revision;
- failed restore reconciliation and denied cutover;
- independently authorized recovery using a new version and proof that old
  credentials, policies, decisions, caches and jobs remain denied.

Exercise success requires secret-free immutable evidence of detection,
containment, denial, reconciliation, independent verification and safe final
state. A planned scenario, tool exit code, database startup, operator statement,
or model summary is not success evidence.

## Non-claims

This runbook does not establish an incident-response organization, paging
channel, backup target, restore capability, deletion processor, legal-hold
system, notification procedure, production monitoring, qualified review, or
runtime readiness. Those remain deployment-specific release stops.
