# S1-14.4 Privacy Engineering Requirements v1

- Status: Decision-ready technical requirements; no runtime authorization
- Scope: S1-14.4 privacy enforcement and the S1-11.2 storage integration boundary
- Product boundary: Neural Brain, product- and domain-neutral
- Legal boundary: This document is not legal advice, a lawfulness determination,
  a qualified privacy review, or an approval to process personal data.
- Runtime boundary: This document has no `ALLOW` outcome and does not activate a
  policy, authorize processing, release a capability, or permit a protected
  mutation.

## Purpose

This document translates data minimisation, purpose limitation, storage
limitation, deletion propagation, access control, redaction, auditability,
data-subject binding, provenance, and privacy by design into technical
requirements for Neural Brain.

It is an engineering input to the separately governed S1-14.4 runtime contract.
It does not select an Article 6 basis, determine an Article 9 condition, decide
an Article 10 disposition, establish a controller or processor role, or decide
whether a concrete processing activity is lawful. Those conclusions require
deployment-specific evidence, an accountable owner, and qualified review.

Unknown, missing, stale, contradictory, unqualified, non-immutable, or
scope-mismatched facts remain blockers. No favorable fact may compensate for a
failed privacy invariant.

## Evidence Classification

### Existing executable evidence

The current MS-1 foundation provides bounded controls that future privacy
enforcement may reuse:

- authenticated Tenant, Area, Project, and Session context;
- Tenant-bound database identities, RLS, FORCE RLS, and protected database
  roles;
- immutable persisted scope and Memory Transition Gate-only protected writes;
- an atomic observation, Working Memory, checkpoint, transition-receipt, and
  audit transaction;
- strict request models that reject undeclared fields and caller-supplied
  trusted scope;
- a code-owned Security Floor that denies unknown operations and incomplete
  runtime context;
- redacted audit evidence written before the audit hash-chain append;
- immutable, scope-, operation-, resource-, classification-, purpose-,
  environment-, and validity-bound authority-evidence primitives.

These controls prove only their bounded MS-1 behavior. They do not prove
privacy-specific lawfulness or S1-14.4 enforcement.

### Preparation evidence

The repository contains preparation-only contracts and typed seams for:

- Article 6 evidence intake;
- Article 9 special-category and Article 10 evidence intake;
- RoPA, personal-data-flow, data-object-catalogue, consent, legitimate-interest,
  privacy-notice, data-subject-request, and DPIA evidence intake;
- versioned policy digests, policy-decision bindings, approval evidence, and
  request-evidence validation;
- retention, deletion, anonymisation, derivative handling, and reconciliation
  in the normative Memory Lifecycle contract.

This preparation records required evidence shapes and fail-closed boundaries.
It is not an accepted intake instance, a runtime validator, an integrated
policy decision, or a processing authorization.

### Missing runtime authorization and enforcement

The following are not currently established:

- a qualified, deployment-specific processing decision;
- an accepted S1-14.4 policy instance and activation decision;
- an Article 9 or Article 10 runtime enforcement decision;
- a privacy-policy evaluation inside the atomic Memory Transition Gate;
- purpose-bound and data-class-bound read authorization;
- executable retention, expiry, deletion, anonymisation, derivative cleanup,
  or restore reconciliation;
- complete data-subject-to-record and data-subject-to-derivative linkage;
- an S1-11.2 protected-storage metadata contract and integration;
- production authorization for personal, special-category, or Article 10 data.

The existing observation model accepts the coarse classifications `public`,
`internal`, `confidential`, and `restricted`, a free non-empty purpose string,
and a source reference. It does not represent the privacy facts required by
this document.

The current Memory Cycle also places content into the observation payload,
Working Memory value, Working Memory version, checkpoint snapshot, and
transition receipt. Working Memory versions, checkpoints, and transition
receipts are append-only. A future privacy design must therefore separate
deletable content from non-reconstructive immutable evidence before protected
personal-data processing can be authorized.

## Common Protected Privacy Context

Every future protected store, read, transformation, disclosure, retention,
deletion, anonymisation, export, or recovery operation must be bound to one
immutable `ProtectedPrivacyContext`. The exact schema remains subject to the
accepted S1-14.4 contract, but it must include or reference at least:

- authenticated actor and immutable Tenant, Area, Project, and Session scope as
  applicable;
- immutable artifact, data-object type, processing-activity, and purpose
  identifiers and versions;
- an explicit data classification, including `unknown` and `conflict` states;
- a category-only personal-data and data-subject classification;
- a pseudonymous data-subject reference or a qualified, evidence-backed
  non-applicability disposition;
- immutable references to the qualified general-basis assessment and any
  required additional special-category condition or Article 10 disposition;
- required safeguards and the evidence that proves their active runtime state;
- a versioned retention rule, retention start, expiry, legal-hold disposition,
  and deletion owner;
- source provenance and complete transformation lineage;
- the exact policy identifier, version, digest, activation evidence, expiry,
  and reassessment state;
- required approval and qualified-review references;
- an immutable parameter digest and correlation identifier;
- the decision result, reason codes, obligations, decision time, and validity
  boundary.

The context must be constructed from authenticated control-plane facts and
accepted immutable evidence. A payload, prompt, observation, model response,
memory item, tool output, label, or caller assertion cannot establish or widen
it.

## 1. Data Minimisation

### Technical requirements

- Each data-object type and purpose combination must have a versioned,
  schema-enforced field allowlist and an explicit maximum content budget.
- The protected gate must reject undeclared, unnecessary, unknown, or
  incompatible fields before content reaches a persistent table.
- Raw content must be separated from governance and transition evidence.
  Receipts, checkpoints, audit events, policy decisions, and authority snapshots
  must contain only non-reconstructive metadata, digests, and opaque references.
- The same content must not be copied into multiple durable objects unless each
  copy is required by the approved purpose and is included in retention and
  deletion propagation.
- Pseudonymisation must occur before persistence where the accepted processing
  contract requires it. Pseudonymisation must never be represented as
  anonymisation.
- Logs, traces, metrics, exceptions, fixtures, and test evidence must not contain
  raw personal, special-category, Article 10, credential, prompt, or memory
  payload data.

### Invariants

- No protected mutation occurs with an unknown field or an unapproved content
  copy.
- Immutable evidence is sufficient to prove the transition but insufficient to
  reconstruct deleted content.
- Data minimisation applies to primary records and every derivative, projection,
  cache, index, snapshot, receipt, backup-eligible object, and observability
  surface.

### Acceptance criteria

- Adding any undeclared field produces a fail-closed result and zero protected
  rows.
- A sensitive marker used in an isolated test is absent from audit events,
  receipts, checkpoints, policy records, logs, and exception text.
- The test inventory enumerates every durable copy of one accepted field and
  proves its purpose, retention rule, and deletion edge.
- A content-budget overflow fails before storage and produces only
  non-reconstructive denial evidence.

### Owner and evidence needs

- Accountable processing owner: approved data-object and field inventory.
- Qualified privacy reviewer: minimisation and pseudonymisation disposition for
  the exact purpose and data-subject category.
- Technical owner: storage-copy inventory, schema allowlists, size limits, and
  proof that transition evidence is non-reconstructive.

## 2. Purpose Limitation

### Technical requirements

- `purpose` must be an immutable, versioned registry reference, not an arbitrary
  free-text value.
- Every operation must bind to the exact artifact, scope, data object,
  processing activity, and purpose version accepted by qualified review.
- Read, retrieval, transformation, disclosure, export, retention, and deletion
  must each evaluate purpose compatibility independently.
- A purpose change must create a new evidence package and decision. It must not
  mutate or broaden an earlier decision.
- Purpose labels contained in payloads or memory content are untrusted and must
  not influence the protected decision.

### Invariants

- A decision for one purpose cannot be replayed for another purpose, activity,
  artifact, data class, recipient, or scope.
- Purpose compatibility is non-compensatory: authority, approval, or a valid
  general basis cannot cure a missing or mismatched purpose.
- The effective purpose at decision time is preserved in immutable audit
  evidence.

### Acceptance criteria

- A changed purpose identifier, version, activity, artifact, or recipient
  invalidates the previous decision and blocks the operation.
- A read request without an independently authorized purpose returns no data.
- Property-based tests prove that no transformation of untrusted payload fields
  can change the trusted purpose.
- Repeated evaluation with identical protected inputs and policy version is
  deterministic.

### Owner and evidence needs

- Accountable processing owner: exact supported purposes and excluded secondary
  uses.
- Qualified privacy reviewer: purpose-compatibility and reassessment evidence.
- Technical owner: purpose registry, immutable versioning, and purpose-bound
  read/write tests.

## 3. Storage Limitation

### Technical requirements

- Every protected content object must reference one current, versioned
  retention rule with a calculable retention start and expiry.
- The rule must identify the accountable deletion owner, applicable legal-hold
  state, archive behavior, recovery behavior, and deletion or anonymisation
  action.
- Missing, unknown, expired, contradictory, or scope-mismatched retention
  evidence must block initial storage.
- Expired, suspended, revoked, quarantined, deleted, or anonymised content must
  not be returned as current memory.
- An authorized retention worker must operate through the Memory Transition
  Gate and must be idempotent, resumable, audited, and reconciliation-aware.
- Readiness after startup or restore must remain false until expired content and
  incomplete retention actions are reconciled.

### Invariants

- No protected content exists without an evaluable expiry or an explicitly
  reviewed alternative disposition.
- A legal hold may suspend deletion only for the scope and duration established
  by accepted evidence; it does not authorize new processing or broader access.
- Retention metadata and policy versions are immutable for a committed object;
  changes create successor evidence.

### Acceptance criteria

- Missing retention data, an unknown retention policy, or an already expired
  policy produces no protected mutation.
- At expiry, reads fail closed and an authorized deletion, anonymisation, block,
  or review transition is recorded according to the accepted rule.
- A legal-hold transition cannot be created from payload data and cannot widen
  access.
- Time-boundary, clock-skew, stale-cache, and concurrent-expiry tests preserve
  fail-closed behavior.

### Owner and evidence needs

- Accountable processing owner: retention schedule and deletion responsibility.
- Qualified privacy reviewer: scope-specific retention and legal-hold
  disposition.
- Operations owner: scheduler, retry, reconciliation, alerting, and restore
  evidence.

## 4. Deletion Propagation

### Technical requirements

- Every protected content object must have an authoritative dependency graph
  covering source records, Working Memory values, historical versions,
  checkpoints, candidates, summaries, assessments, embeddings, indexes, caches,
  projections, replicas, exports, and eligible backup handling.
- Deletion and anonymisation must be explicit protected transitions with a
  stable request identifier and states such as `requested`, `validated`,
  `in_progress`, `reconciling`, `completed`, `blocked`, and `indeterminate`.
- Unknown commit outcomes must be reconciled against the PostgreSQL ledger and
  must not be retried blindly.
- Deletion evidence must retain only non-reconstructive facts necessary to
  prove what category of data and derivatives was handled, by whom, under which
  decision, and with which result.
- Restore, PITR, replica recovery, and cache rebuild must not reactivate deleted,
  expired, revoked, or superseded content.
- Immutable transition evidence that currently embeds raw content must be
  redesigned before processing deletable personal data.

### Invariants

- Completion is impossible while any required derivative or projection is
  unknown, unreachable, unreconciled, or still retrievable.
- Deletion of a source invalidates or removes every reconstructive derivative.
- A backup restore creates quarantine and reconciliation work, not automatic
  readiness or reactivation.

### Acceptance criteria

- After a completed deletion test, an isolated marker is not reconstructable
  from any primary, historical, derived, indexed, cached, exported, audit, or
  restored surface covered by the test inventory.
- Injected failure after each cascade step is resumable and never reports
  completion early.
- A concurrent read, transformation, or promotion cannot return or activate a
  record after deletion authorization commits.
- Restore of a snapshot containing previously deleted content keeps the service
  unready and the restored content quarantined until reconciliation completes.

### Owner and evidence needs

- Data owner: complete system-of-record and derivative inventory.
- Technical owners for each store: deletion adapter and reconciliation proof.
- Operations owner: backup/PITR/restore and incident-runbook evidence.
- Qualified privacy reviewer: deletion, anonymisation, legal-hold, and retained
  evidence disposition.

## 5. Access Control

### Technical requirements

- Access must require current authenticated actor, immutable scope, operation,
  resource, data class, purpose, environment, authority snapshot, policy
  decision, and required approval evidence.
- Database identity must remain Tenant-bound; application context may only
  narrow Area, Project, and Session scope.
- Purpose and classification checks must apply to reads as well as writes.
- Direct table DML by application, consumer, model, integration, or general
  reader roles must remain denied.
- Grant revocation, policy expiry, approval expiry, purpose change, data-class
  change, or scope change must invalidate cached decisions immediately.
- Human approval cannot create missing authority, waive a Security Floor rule,
  or supply a missing qualified privacy decision.

### Invariants

- Default access is deny.
- Scope, authority, purpose, classification, and policy inputs come only from
  authenticated control-plane state.
- Every access decision is bound to immutable digests and a short validity
  boundary.

### Acceptance criteria

- Cross-Tenant, cross-Area, cross-Project, cross-Session, cross-purpose,
  cross-classification, and cross-resource attempts return no content.
- Revoked or expired grant, policy, approval, or review evidence blocks the next
  operation, including when a stale cache exists.
- Direct SQL write and read attempts by non-gate roles fail.
- A derived context can only preserve or narrow scope, grants, purposes, and
  resources.

### Owner and evidence needs

- Protected Control Plane owner: authority and policy lifecycle.
- Database owner: role, privilege, RLS, FORCE RLS, and Tenant identity evidence.
- Accountable processing owner and qualified reviewer: purpose, data-class, and
  recipient access rules.

## 6. Redaction

### Technical requirements

- Redaction must use fixed schema projections or positive field allowlists at
  every evidence and observability boundary.
- Name-based sensitive-field detection is defense in depth and must not be the
  sole privacy control.
- Audit, logs, metrics, traces, errors, receipts, and decision records must not
  contain raw payloads, prompts, direct identifiers, special-category values,
  credentials, secrets, consent text, contracts, or legal advice.
- Data-subject references in control evidence must be pseudonymous, scoped, and
  non-authorizing.
- Unknown event types or schema versions must be rejected before hash-chain
  append or protected mutation commit.

### Invariants

- Redaction occurs before persistence and before integrity hashing.
- Redaction failure rolls back the entire protected transition.
- Redacted evidence preserves actor, scope, decision, result, reason codes,
  correlation, and non-reconstructive evidence references.

### Acceptance criteria

- Nested, renamed, encoded, and unexpectedly structured sensitive test markers
  cannot appear in an accepted evidence record.
- An unknown event type, evidence schema, or prohibited field causes an atomic
  rollback.
- Exception and timeout paths contain no raw input or credential material.
- Stored redacted evidence remains sufficient to verify the audit chain and
  correlate the protected operation.

### Owner and evidence needs

- Security and privacy engineering owners: redaction schemas and adversarial
  test corpus.
- Observability owner: log, trace, metric, and exception inventory.
- Audit owner: proof that the retained record is non-reconstructive and
  operationally useful.

## 7. Auditability

### Technical requirements

- The privacy decision, protected mutation, and audit event must commit in one
  database transaction or all roll back.
- Every decision event must record actor, immutable scope, operation, resource,
  data class, purpose, processing activity, qualified evidence references,
  policy identifier/version/digest, authority and parameter digests, decision
  time, validity, result, reason codes, obligations, executing component,
  code/model version where applicable, correlation identifier, and downstream
  action.
- Audit events must be append-only and hash-chain protected, subject to
  ADR-012-compliant non-reconstructive deletion or anonymisation evidence.
- Post-hoc summaries cannot replace a missing decision event.
- Audit continuity must be verified before readiness after migration, restore,
  or reconciliation.

### Invariants

- No protected mutation exists without its matching atomic privacy-decision
  evidence.
- Audit evidence never creates authority or a favorable privacy decision.
- Corrections append successor evidence and preserve lineage; they do not
  silently rewrite history.

### Acceptance criteria

- Injected audit failure leaves no protected mutation, receipt, or partial
  decision record.
- Removal, reordering, replacement, or digest tampering is detected.
- Correlation queries resolve one decision to its exact mutation and all
  downstream retention or deletion work without reading raw content.
- Restore and migration tests verify chain continuity before `ready=true`.

### Owner and evidence needs

- Audit owner: event schema, custody, access, and reconciliation requirements.
- Database owner: transaction and hash-chain evidence.
- Qualified reviewer and accountable owner: required reason codes, review
  references, and retention of non-reconstructive audit evidence.

## 8. Data-Subject Binding

### Technical requirements

- Every personal-data object must carry or reference a pseudonymous,
  Tenant-/Area-bound data-subject identifier and an explicit relationship type,
  including single subject, multiple subjects, category-only, not applicable,
  unknown, and conflict.
- Unknown or conflicting subject binding must block special-category or Article
  10 processing and must not be inferred as not applicable.
- Direct identifiers must remain outside control-plane, policy, audit, and
  transition evidence.
- The subject binding must cover primary records and every derivative needed for
  access, correction, restriction, export, objection, deletion, and
  reconciliation workflows.
- Subject references cannot establish authenticated identity, scope, authority,
  or approval.

### Invariants

- Subject references are unique only within their declared immutable scope and
  cannot be resolved across Tenant or Area boundaries.
- Every derivative preserves a traceable subject-binding edge or an explicit
  qualified non-applicability disposition.
- A correction or subject-binding change creates a successor record and
  invalidates decisions bound to the prior state.

### Acceptance criteria

- An authorized subject-coverage query identifies all in-scope primary and
  derived records without exposing out-of-scope subjects.
- Missing, conflicting, cross-scope, or malformed subject references block the
  operation.
- Multi-subject records remain blocked from deletion completion until every
  affected relationship and retained obligation is reconciled.
- Direct identifiers inserted into control metadata are rejected.

### Owner and evidence needs

- Data owner: subject categories and relationship model.
- Identity/privacy engineering owners: pseudonymisation and resolution design.
- Qualified privacy reviewer: treatment of unknown, multi-subject, and
  non-applicable cases.

## 9. Provenance

### Technical requirements

- Every protected content object must reference immutable source identifier,
  source version or digest, source class, acquisition time, authenticated
  collector, exact scope, purpose, currency, review state, contradiction state,
  and permitted-use boundary.
- Every transformation must append a lineage edge containing input digests,
  transformation identifier and version, executing component, time, output
  digest, purpose, and policy decision reference.
- Payloads, model output, tool output, prompts, and memory content cannot attest
  their own source authority or review state.
- Provenance changes, stale sources, conflicting sources, or missing lineage
  must invalidate the prior decision and block downstream use.
- Deletion and correction must propagate through provenance-linked derivatives
  without retaining a reconstructive content copy.

### Invariants

- No accepted content exists without complete, current, scope-matched
  provenance.
- Provenance is immutable and append-only; corrections create successor
  evidence.
- Source permission never creates processing authority.

### Acceptance criteria

- Digest, source version, scope, purpose, acquisition time, transformation, or
  review-state tampering invalidates the object.
- A missing lineage edge blocks retrieval, transformation, promotion, and
  disclosure.
- A source correction or deletion identifies every affected derivative and
  creates required re-evaluation or deletion work.
- Identical source, transformation, policy, and protected inputs produce the
  same lineage digest.

### Owner and evidence needs

- Source owner: source identity, version, currency, and permitted-use evidence.
- Data engineering owner: lineage graph and digest implementation.
- Qualified reviewer: source suitability and contradiction treatment for the
  exact processing activity.

## 10. Privacy by Design and by Default

### Technical requirements

- S1-14.4 enforcement must be owned by the independent Protected Control Plane
  and invoked inside the authoritative database transaction immediately before
  protected mutation.
- S1-11.2 may collect and validate metadata and request a decision; it cannot
  invent lawfulness, select a missing condition, waive an unknown, or write
  around S1-14.4.
- The only permitted sequence is authenticated scope, strict metadata and
  classification validation, current policy and evidence resolution, privacy
  decision, audit intent, atomic protected mutation and audit, and committed
  result.
- All unsupported environments, jurisdictions, data classes, purposes,
  operations, policy versions, evidence states, or runtime failures must deny or
  route to a separately governed review process without storing content.
- Policy activation must require immutable versioning, qualified scope-specific
  evidence, accountable ownership, independent review where required,
  regression evidence, expiry, reassessment triggers, and rollback.
- No application-service, adapter, migration, maintenance job, restore process,
  model, integration, or database role may bypass the protected privacy gate.

### Invariants

- Only an accepted and current runtime contract may define an `ALLOW` result.
  This requirements document never does so.
- Approval never creates missing authority, evidence, safeguards, purpose,
  retention, subject binding, or auditability.
- Unknown state is never interpreted favorably.
- Privacy enforcement and the protected mutation are atomic and fail closed.

### Acceptance criteria

- Unit, schema, integration, PostgreSQL, migration, end-to-end, property-based,
  state-machine, concurrency, crash-boundary, and restore tests cover every
  non-compensatory gate.
- Unknown data class, missing purpose, missing general-basis evidence, missing
  required additional-condition evidence, missing safeguard, missing retention,
  missing approval, unknown owner, expired evidence, revoked evidence, policy
  conflict, or missing auditability always produces zero protected content
  mutations.
- Failure injection for database, policy evaluation, audit, timeout, process
  crash, stale cache, network partition, concurrent revocation, partial
  migration, restore, and corrupted evidence never produces permissive
  behavior.
- Direct-database and alternate-adapter tests prove that no bypass path can
  create, read, transform, disclose, retain, delete, anonymise, or restore
  protected content outside the gate.

### Owner and evidence needs

- Architecture owner: accepted S1-14.4 runtime contract and protected-writer
  boundary.
- Accountable processing owner: exact deployment, purpose, data categories,
  exclusions, owners, and supported operations.
- Qualified privacy and, where required, legal reviewers: immutable decisions,
  scope, restrictions, expiry, and reassessment date.
- Security owner: threat model, bypass analysis, and negative-test approval.
- Data and operations owners: migrations, retention, deletion, backup, restore,
  reconciliation, and incident evidence.
- Independent reviewer: closure of all Critical and High findings before
  activation.

## Non-Compensatory Runtime Gates

The accepted runtime contract must block protected processing when any of the
following is absent, unknown, stale, contradictory, revoked, expired,
non-immutable, unqualified, or scope-mismatched:

- authenticated identity and scope;
- data classification and personal-data disposition;
- purpose and processing activity;
- qualified general-basis evidence;
- required additional-condition or Article 10 evidence;
- data-subject binding;
- source provenance and transformation lineage;
- required safeguards and their active runtime proof;
- retention, legal-hold, deletion, and recovery disposition;
- authority, policy, activation, and required approval evidence;
- audit availability and atomicity;
- accountable owner and required independent review;
- supported environment, deployment, jurisdiction, recipient, and transfer
  boundary.

## Decision Package Required Before Runtime Activation

The following deployment-specific decisions remain external blockers until
recorded as immutable accepted evidence:

1. supported deployment and jurisdictions;
2. accountable controller/processor and technical owners;
3. supported processing activities and purposes;
4. supported and excluded data and data-subject categories;
5. qualified general-basis decisions;
6. required additional special-category conditions or Article 10 dispositions;
7. required safeguards and runtime verification method;
8. data minimisation and pseudonymisation rules;
9. retention, legal-hold, deletion, anonymisation, backup, and restore rules;
10. subject-rights and incident handling;
11. recipient, processor, location, and transfer boundaries;
12. policy activation authority, review independence, validity, expiry,
    restrictions, reassessment triggers, and rollback.

Until every required item is accepted for the exact artifact, scope, purpose,
activity, data class, subject category, environment, and jurisdiction, S1-14.4
remains blocked and S1-11.2 must not persist protected personal data.

## Smallest Safe Implementation Slice After Authorization

After the runtime contract and required decisions are accepted, the smallest
safe slice is:

1. define a strict, versioned `ProtectedPrivacyContext` instance schema;
2. bind it to the existing authenticated Runtime Context, authority snapshot,
   policy digest, parameter digest, checkpoint, and immutable evidence
   references;
3. remove reconstructive payloads from transition receipts and protected
   evidence snapshots, or provide an accepted ADR-012-compliant content
   separation and deletion design;
4. evaluate the accepted privacy policy inside
   `memory_gate.commit_memory_cycle` immediately before mutation;
5. atomically commit the decision event, protected mutation, and
   non-reconstructive receipt;
6. prove denial and zero-write behavior for every missing or conflicting gate;
7. keep personal, special-category, and Article 10 processing disabled until
   independent review verifies the complete integrated state.

This slice is implementation preparation only until its accepted policy,
qualified evidence, independent review, migration validation, complete test
evidence, and release gate are all present.
