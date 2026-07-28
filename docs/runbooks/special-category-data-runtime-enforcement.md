# Special-Category Data Runtime Enforcement Preparation

## Scope and readiness boundary

This preparation runbook defines how to inspect and verify a future S1-14.4
runtime enforcement slice and its S1-11.2 storage integration. It is governed
by the repository-wide threat model and
[`special-category-data-runtime-threat-and-privacy-assessment-v1.md`](../architecture/special-category-data-runtime-threat-and-privacy-assessment-v1.md).

This document is not an executable production procedure. It does not provide a
lawful-basis decision, Article 9 or Article 10 determination, owner approval,
qualified review, policy activation, deployment authorization, or permission
to process real personal data. Until the normative runtime contract is accepted
and every gate below passes, operators may perform preparation checks only.
There is no permissive compatibility mode or fallback policy.

## Required separation of duties

| Responsibility | Required future owner | Prohibited shortcut |
| --- | --- | --- |
| Processing-purpose and scope proposal | Accountable business or deployment owner | Runtime, payload, model, or developer self-authorization |
| Privacy and legal decision evidence | Qualified assigned reviewer for the exact deployment | Repository text or general legal source treated as an operational approval |
| Policy authorship | Authorized policy author | Author activating or approving the same version alone |
| Policy activation | Independent protected-control-plane actor | Caller-supplied active flag or approver-role string |
| Runtime decision | Protected policy decision point | Precomputed or caller-supplied `ALLOW` |
| Protected storage | Sole mutation Gate | General repository, ORM, worker, or direct table DML |
| Audit and verification | Gate plus independent verifier | Post-hoc summary as a substitute for a missing decision event |
| Incident revocation and recovery | Authorized incident and recovery owners | Automatic, model-controlled, or restore-triggered reactivation |

The policy author, approver, protected-data requester, migration actor, restore
operator, and independent verifier must not collapse into an unreviewed single
actor for elevated-risk processing.

## Preparation preflight

Before implementing or reviewing an enforcement slice, record and verify:

1. the exact task, accepted contract version, artifact digest, base revision,
   environment, jurisdiction, Tenant, Area, Project and Session applicability;
2. the accountable owner and the qualified privacy or legal review references
   for every decision required by the accepted contract;
3. the supported classification, purpose, general-basis, additional-condition,
   safeguard, approval, retention, and evidence identifiers;
4. the explicitly unsupported and unknown cases, each with a blocking outcome;
5. the protected policy store, active-version state machine, revocation fence,
   reviewer-role source, decision record, mutation Gate, audit schema, and
   reconciliation owner;
6. every primary and derivative storage location, including receipts,
   checkpoints, caches, indexes, embeddings, queues, exports, backups, WAL, and
   restore targets;
7. the negative, concurrency, failure-injection, deletion, and restore tests
   required for the exact change.

Missing, stale, scope-mismatched, contradictory, placeholder, unqualified, or
unverifiable evidence stops preparation from advancing to runtime activation.

## Target enforcement sequence

The following sequence is a design and verification target. Do not execute it
against productive data before separate authorization.

```text
1. resolve authenticated Principal and immutable scope outside the payload
2. parse and strictly validate minimized metadata and payload shape
3. begin the protected PostgreSQL transaction
4. load the current immutable policy, authority, approval, evidence, and fence
5. validate classification, purpose, basis, special condition, safeguards,
   retention, environment, scope, reviewer authority, version, and time
6. compute one deterministic decision inside the protected boundary
7. if and only if the result is ALLOW, prepare a minimized audit intent
8. revalidate or lock the current versions and revocation fence
9. atomically commit decision, protected mutation, receipt, and redacted audit
10. return the committed result; ambiguous outcomes enter reconciliation
```

Every result other than `ALLOW` blocks storage. Human review or additional
evidence outcomes route only a secret-free reference to the separately
authorized review workflow; they do not persist the proposed protected payload
as a convenience queue.

## Payload and metadata validation checks

Verify that the untrusted request cannot contain or override authenticated
scope, Principal, roles, authority, policy activation, reviewer status,
decision outcome, revocation fence, retention exception, legal hold, release
status, or audit result.

The input boundary must reject:

- unknown fields and unsupported enum values;
- duplicate or ambiguous JSON keys before typed conversion;
- empty, whitespace-only, non-canonical, or Unicode-confusable identifiers;
- unknown, missing, contradictory, or mixed classifications;
- absent or unapproved purposes;
- missing general basis or required additional special condition;
- stale, expired, revoked, rejected, superseded, future-dated, or
  scope-mismatched evidence;
- raw personal data, credentials, secrets, prompts, or evidence bodies in
  policy, approval, decision, audit, telemetry, or incident metadata.

Use protected identifiers and immutable digests for policy facts. A free-form
purpose label, display name, narrative rationale, or payload classification is
not an authorization key.

## Protected policy and evidence checks

The evaluator must load records from protected storage rather than trusting
fully populated objects supplied by a service caller. For the exact attempted
mutation, verify:

- one current policy version and no competing active version;
- permitted lifecycle transition and current revocation fence;
- immutable digest and artifact-version match;
- authenticated actor, complete scope, environment, resource and purpose;
- current authority that is necessary but not treated as policy sufficiency;
- accountable owner and current qualified reviewer authority;
- distinct author and approver where independent approval is required;
- current evidence validity, review date, expiry and revalidation trigger;
- retention policy, legal-hold state, safeguards and deletion responsibility;
- no conflict, placeholder, unknown fact, or unsupported jurisdiction.

An audit hash or canonical digest establishes neither legal sufficiency nor
reviewer authority. It is only one integrity control around separately
authenticated evidence.

## Database bypass and privilege review

Preparation review must prove that every new protected policy, approval,
decision, data, receipt, audit, deletion, and reconciliation table is covered
by the intended role and scope model. Preserve the Tenant-bound controls in
[`tenant-database-operations.md`](tenant-database-operations.md).

At minimum verify:

- Runtime logins remain `NOSUPERUSER`, `NOBYPASSRLS`, `NOCREATEDB`,
  `NOCREATEROLE`, `NOINHERIT`, and own no database objects;
- Gate and reader roles have no direct protected-table DML;
- the Runtime cannot assume owner, provisioner, migration, backup, restore, or
  policy-activation roles;
- protected tables use appropriate RLS and `FORCE ROW LEVEL SECURITY`, or are
  completely unavailable to Runtime roles behind a scoped definer function;
- every `SECURITY DEFINER` function has a fixed trusted search path, fixed SQL
  structure, explicit privilege revocation, and exact execution grants;
- owner, grant, membership, function, policy, trigger, and schema-creation
  drift is tested from real restricted logins;
- direct SQL cannot insert an `ALLOW`, activate a policy, alter a revocation
  fence, mutate protected data, or suppress its audit event.

The database owner and migration administrator remain privileged operational
actors, not Runtime identities. Their changes require separate governance,
review, immutable migration evidence, and incident handling.

## TOCTOU and atomicity review

An application-level preflight followed by an independent storage call is not
sufficient. Introduce controlled concurrency barriers in tests and change one
protected fact after the initial read but before the attempted commit:

- policy supersession or revocation;
- evidence expiry or replacement;
- approval withdrawal or reviewer-role revocation;
- Principal, Tenant, Area, Project or Session suspension;
- retention, safeguard or legal-hold change;
- revocation-fence increment.

The paused transaction must not commit under the old state. The implementation
must use row locking, a monotonic revision/fence, serializable validation, or an
equivalent PostgreSQL mechanism whose failure is proven to roll back the whole
operation. Rechecking only a process-local cache is insufficient.

## Audit preparation checks

The future audit event must bind the actor, immutable scope, decision ID,
policy ID/version/digest, classification identifier, purpose identifier,
general-basis and special-condition references, evidence references, decision
time, expiry, result, reason codes, executing component, code version,
transition ID, protected subject reference, and downstream disposition.

Do not copy the protected payload, personal identifiers, consent text, legal
advice, credentials, prompts, or full evidence bodies into audit. Extend the
existing approved redaction contract deliberately; an unknown event type or
prohibited field must fail the transaction. Hash-chain generation occurs only
after redaction, and audit insert failure rolls back decision, data and receipt.

## Failure-injection and acceptance checks

For every commit boundary, inject policy-store unavailability, audit failure,
timeout, deadlock, serialization failure, backend termination, connection loss,
stale cache, malformed evidence and ambiguous client outcome. Verify one of two
states only:

1. no decision, protected mutation, receipt, or audit record exists; or
2. one complete, mutually bound, hash-verifiable commit exists.

Never retry an ambiguous outcome blindly. Reconcile by immutable transition ID
and exact request digest. Identical retry input may return the committed result;
the same ID with different input is denied.

Acceptance evidence must also cover the full policy state machine, every
non-`ALLOW` outcome, cross-scope and cross-purpose reuse, direct-table denial,
concurrent revocation, cache/job invalidation, deletion propagation, and
quarantined restore. Planned tests, static document-shape tests, local owner SQL,
or a successful happy path do not establish runtime enforcement.

## Handoff gate

Preparation is ready for authoritative review only when every decision point
has an owner, required evidence, acceptance criterion, supported scope,
restriction, expiry/revalidation date, and explicit status. Runtime activation
remains blocked while any required point is not decided, any P0/P1 finding is
open, any negative or failure test is missing, or backup/restore, incident,
retention, deletion, monitoring, and independent-review evidence is incomplete.
