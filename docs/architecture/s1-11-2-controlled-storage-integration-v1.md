# S1-11.2 Controlled Storage Integration v1

## Status and purpose

- Status: technical preparation; no runtime authorization
- Task: S1-11.2
- Blocking dependency: accepted and implemented S1-14.4 runtime-enforcement
  contract, including an operative Article 6 decision authority or an explicit
  binding to a separately governed Article 6 runtime authority
- Scope: protected Memory Core storage intake

This document defines the integration boundary by which S1-11.2 metadata may
be admitted to protected storage. It separates strict metadata validation from
the legal, privacy, authority, and runtime decisions that metadata cannot make.
It also defines a preparation-only port that can be implemented before the
authoritative decision contracts exist while guaranteeing that preparation can
never produce an `ALLOW` result.

This document does not select a legal basis, determine Article 9 or Article 10
applicability, approve a processing purpose, establish a retention period,
authorize processing, or approve a deployment or release.

## Current repository facts

The current Memory Core intake has useful protected-storage foundations but
does not implement S1-11.2 or S1-14.4 runtime enforcement:

- `ObservationRequest` records `source_kind`, `source_ref`, `classification`,
  free-text `purpose`, content, and occurrence time.
- The existing technical `classification` vocabulary is `public`, `internal`,
  `confidential`, and `restricted`.
- `MemoryService` obtains authenticated runtime context and invokes the fixed
  Security Floor before calling the repository.
- `PostgresMemoryRepository` invokes `memory_gate.commit_memory_cycle` through
  a Tenant-bound connection and a short transaction.
- `memory_gate.commit_memory_cycle` checks scope authority and active Session
  state, then commits the observation, working context, checkpoint, transition
  receipt, and audit event atomically.
- Runtime roles cannot write the protected Memory Core tables directly.

The existing technical classification is a handling and confidentiality
classification. It is not a GDPR personal-data classification and must never
be interpreted as one. In particular, `restricted` does not mean Article 9
special-category data, and a less restrictive technical classification does
not mean that personal-data, Article 9, or Article 10 requirements are absent.

The repository also contains Article 6 and Article 9/10 evidence-intake
contracts. Those contracts prepare immutable evidence references for qualified
review. They explicitly do not provide instance validation, a legal
determination, runtime authority, an `ALLOW` result, or a protected-state gate.

## Current gaps

The current protected intake does not require or persist:

- a distinct personal-data classification;
- a versioned processing-purpose reference;
- an operative Article 6 decision reference;
- an Article 9 condition or Article 10 authorization decision when applicable;
- a data-subject category or pseudonymous subject reference;
- a retention-rule reference and evaluated retention state;
- a protection-requirement reference distinct from technical classification;
- safeguard, approval, policy-version, or qualified-evidence references;
- expiry, revocation, conflict, or reassessment state;
- an immutable binding between metadata, authenticated scope, the policy
  decision, and the protected mutation; or
- a privacy decision event committed atomically with storage.

The current Security Floor and memory-risk vocabulary do not close these gaps.
They protect identity, scope, known operations, provenance, purpose presence,
and transition-gate use, but they do not decide Article 6, Article 9, Article
10, purpose lawfulness, safeguard sufficiency, retention validity, or
deployment-specific authorization.

## Responsibility boundary

### S1-11.2 metadata validation

S1-11.2 may:

- accept typed metadata fields and immutable evidence references;
- reject undeclared, malformed, empty, unknown, contradictory, or unsupported
  values;
- check internal field dependencies defined by an accepted schema;
- calculate a canonical metadata digest;
- require the exact authenticated-scope binding expected by the decision port;
- request an authoritative policy decision; and
- block storage unless the protected gate verifies an exact current `ALLOW`.

S1-11.2 must not:

- infer whether data are personal data, Article 9 special-category data, or
  Article 10 data from the technical classification;
- select or validate an Article 6 legal basis;
- select an Article 9 condition or establish Article 10 authorization;
- invent a missing purpose, retention rule, safeguard, approval, jurisdiction,
  owner, or evidence reference;
- treat a completed evidence intake as runtime authority;
- resolve policy conflicts or stale evidence favorably;
- accept a decision for a different artifact, actor, scope, purpose, activity,
  data class, policy version, or metadata digest; or
- persist protected data after any result other than a gate-verified `ALLOW`.

### S1-14.4 and Article 6 runtime decision

The authoritative decision component owns evaluation of:

- the applicable, accepted Article 6 runtime decision;
- whether an additional Article 9 condition or Article 10 authorization is
  required and satisfied;
- exact purpose and processing-activity admission;
- jurisdiction and deployment constraints;
- safeguards, approvals, evidence currency, and qualified-review state;
- policy version, activation state, effective time, expiry, revocation,
  supersession, and conflicts; and
- the terminal decision and reason codes.

Only this protected decision component may produce `ALLOW`. Article 6 runtime
authority remains an explicit dependency even after an Article 9-specific
contract is approved. S1-11.2 is not implementable to its full acceptance
criterion if S1-14.4 neither owns the Article 6 decision nor binds to a
separately implemented Article 6 runtime authority.

### Protected Mutation Gate

The Protected Mutation Gate owns the final write boundary. It must revalidate
the current decision and policy state immediately before mutation in the same
database transaction. An application-layer preflight is necessary for early
rejection but is never sufficient authorization for storage.

## Required pipeline

Every protected storage operation follows this exact order:

```text
Metadata Validation
-> Classification Validation
-> S1-14.4 / Article 6 Decision
-> Protected Mutation Gate
-> Atomic Storage and Audit
```

The stages have the following meanings:

1. **Metadata Validation** checks strict shape, completeness, immutable
   references, field dependencies, and canonical representation.
2. **Classification Validation** validates the separately defined privacy data
   class and the independent technical protection classification. Unknown,
   contradictory, unsupported, or unverified privacy classification blocks.
3. **S1-14.4 / Article 6 Decision** evaluates current, scope-bound policy and
   review evidence. Only an exact `ALLOW` may proceed.
4. **Protected Mutation Gate** rechecks the decision binding, effective policy
   version, current activation, expiry, revocation, and authenticated runtime
   scope inside the mutation transaction.
5. **Atomic Storage and Audit** commits the protected record, decision event,
   immutable policy and metadata bindings, transition receipt, and audit event
   together, or commits none of them.

Missing stages, skipped validation, unavailable dependencies, timeouts,
unknown outcomes, stale caches, and ambiguous errors all block storage.

## Strict prepared metadata model

The executable preparation type is `PreparedStorageMetadata`; it is a preflight
candidate, not the later persisted `protected-storage-metadata-v1` binding.
The preparation model records references and classifications only. Exact enum
members and conditional requirements remain subordinate to the accepted
runtime contract. A prepared model must be strict, frozen, reject undeclared
fields, and use no permissive defaults.

The minimum field set is:

| Field | Preparation meaning | Runtime requirement |
| --- | --- | --- |
| `schema_version` | Exact metadata schema version | Must be supported and immutable |
| `data_object_type_id`, `data_object_type_version` | Declared data-object type reference | Must resolve to the accepted data-object catalogue |
| `privacy_data_class_id`, `privacy_data_class_version` | Separate personal-data classification reference | Must be trusted or validated under the accepted classification contract |
| `technical_classification` | Existing handling class | Must not determine GDPR classification |
| `processing_activity_id`, `processing_activity_version` | Immutable activity identifier and version | Must match the approved decision scope |
| `purpose_id`, `purpose_version` | Immutable purpose identifier and version | Must resolve to an admitted purpose |
| `article_6_evidence_ref` | Reference to qualified-review evidence | Must resolve through operative Article 6 runtime authority |
| `additional_condition_evidence_ref` | Conditional Article 9 or Article 10 reference | Required only as determined by authoritative policy, never by payload inference |
| `subject_category_id`, `subject_category_version` | Category-level subject reference | Must contain no raw special-category value |
| `subject_reference_kind`, `subject_reference_token` | Pseudonymous or otherwise approved subject reference | Must follow the accepted minimization and scope contract |
| `source_id`, `source_version`, `source_digest` | Immutable provenance reference | Must be current, scope-bound, and integrity checked |
| `retention_rule_id`, `retention_rule_version` | Immutable retention-rule identifier and version | Must be active and compatible with the operation |
| `protection_requirements_id`, `protection_requirements_version`, `protection_requirements_digest` | Required safeguards and handling controls | Must resolve to satisfied safeguards |
| `policy_id`, `policy_version`, `policy_digest` | Policy identifier, version, and digest | Must identify the exact active policy evaluated |
| `approval_refs` | Immutable approval evidence references | Must satisfy required roles and independence |
| `evidence_refs` | Additional immutable evidence identifiers | Must be current, non-conflicting, and scope-bound |
| `evidence_set_digest` | Digest of the canonical evidence-reference set | Must match the set consumed by the authoritative decision |

Presence of a reference proves only that a value was supplied. Metadata
validation must not claim that the referenced evidence exists, is authentic,
is current, is sufficient, or authorizes processing. Those are runtime
decision responsibilities.

The canonical metadata digest must cover every metadata field and schema
version. The authoritative decision binding must additionally cover:

- actor and authenticated Tenant, Area, Project, and Session;
- artifact or record identifier;
- operation and resource;
- processing activity and purpose versions;
- privacy data class and technical classification;
- metadata digest;
- authority snapshot digest;
- policy identifier, version, and digest;
- decision identifier, outcome, reason codes, and validity window; and
- required approval and evidence digests.

Any mismatch invalidates the decision.

## Preparation-only decision port

Before authoritative S1-14.4 and Article 6 runtime components exist, integration
may depend on a narrow decision port so metadata and service boundaries can be
tested. The only permitted preparation implementation is a never-allow port.

Conceptually:

```python
class ProcessingDecisionPort(Protocol):
    def decide(self, request: ProcessingDecisionRequest) -> ProcessingDecision: ...


class PreparationOnlyProcessingDecisionPort:
    def decide(self, request: ProcessingDecisionRequest) -> ProcessingDecision:
        return ProcessingDecision(
            outcome="UNKNOWN",
            reason_codes=("runtime_authority_not_implemented",),
        )
```

The real types must use strict enums rather than free-form strings. The example
shows the required behavior, not a final API. The preparation port must:

- have no configuration that can enable `ALLOW`;
- have no caller-supplied override;
- never translate evidence presence into approval;
- never fall back to the current generic memory-risk `ALLOW`;
- return a terminal blocking result when unavailable or unsupported; and
- be covered by a test proving that no possible valid prepared metadata input
  produces `ALLOW`.

The preparation port must not be wired to a productive storage path unless the
result is unconditionally rejected before repository access.

## Smallest post-authorization implementation slice

After the runtime contract, owner decision, qualified review, exact deployment
scope, Article 6 authority, Article 9/10 rules, and Critical/High review gates
are accepted, the smallest safe vertical slice is one protected observation
intake for one supported policy version and one explicitly supported
processing-purpose family.

The slice consists of:

1. strict privacy metadata and decision-binding models;
2. a pure metadata validator with canonical digest generation;
3. an authoritative decision adapter implementing the accepted contract;
4. service orchestration that never calls the repository without an exact
   current `ALLOW` bound to the request and authenticated context;
5. a repository interface carrying immutable metadata and decision evidence;
6. a database-owned final decision check inside the Memory Transition Gate;
7. atomic persistence of metadata, the decision event, the observation,
   working-memory update, checkpoint, receipt, and audit event; and
8. direct-write denial and complete negative, concurrency, and rollback tests.

The slice must not initially support multiple jurisdictions, policy-version
fallback, cross-purpose evidence reuse, implicit classification, or automatic
translation of legacy records. Unsupported combinations remain denied.

## Database and cutover requirements

The next available migration must preserve the existing owner and runtime-role
separation and add protected, machine-checkable storage for:

- the complete S1-11.2 metadata document and canonical digest;
- the privacy decision identifier, outcome, reason codes, validity, and
  immutable binding;
- the exact Article 6 and, when required, Article 9 or Article 10 evidence
  references;
- policy identifier, version, digest, activation, expiry, revocation, and
  supersession state; and
- the atomic correlation among decision, observation, transition receipt, and
  audit event.

The database gate must:

- derive scope and principal only from trusted runtime context;
- reject missing, unknown, malformed, contradictory, stale, expired, revoked,
  superseded, or scope-mismatched inputs;
- reject every decision outcome other than `ALLOW`;
- lock or otherwise transactionally protect the evaluated policy and decision
  state against concurrent revocation and time-of-check/time-of-use races;
- prevent replay with changed metadata, policy, scope, purpose, activity, or
  decision evidence;
- commit the decision event and protected mutation in one transaction;
- roll back the entire operation if audit, receipt, decision persistence, or
  any protected-state write fails; and
- expose no table-level DML path to application runtime roles.

Existing rows cannot be declared compliant by migration default. Cutover must
choose one explicit disposition per legacy record set:

- migration through separately authorized, evidence-backed reclassification;
- quarantine or read-only retention pending review;
- authorized deletion through the retention/deletion gate; or
- exclusion from the new productive path with a documented release stop.

No nullable column, synthetic evidence reference, inferred purpose, default
legal basis, or assumed retention rule may be used to make legacy rows pass.

Before cutover, operators must verify the exact supported deployment,
jurisdiction, Tenant scope, purposes, privacy classes, policy versions,
qualified approvals, migration result, rollback procedure, and restore
behavior. A restored stale policy or approval must not become active merely
because it was present in a backup.

## Required verification

### Model and validator tests

- Reject every missing required field and every undeclared field.
- Reject unknown privacy classes and unknown technical classifications.
- Prove that technical classification never determines privacy classification.
- Reject empty, malformed, mutable, unresolved, or conflicting references.
- Prove deterministic canonical metadata digests.
- Prove that prepared metadata cannot itself produce authority or `ALLOW`.

### Service tests

- Prove the required pipeline order.
- Prove that the repository is never called for `DENY`,
  `REQUIRE_HUMAN_REVIEW`, `REQUIRE_ADDITIONAL_EVIDENCE`, `EXPIRED`, `REVOKED`,
  `CONFLICT`, or `UNKNOWN`.
- Prove fail-closed behavior for evaluator exceptions, timeouts, unavailable
  policy state, malformed responses, and decision-binding mismatches.
- Prove that caller payloads cannot replace authenticated scope, policy,
  approval, or authority facts.

### Policy-decision tests

- Admit a supported Article 6-only case only with complete current evidence.
- Admit a supported Article 9 case only with the required condition,
  safeguards, purpose, and approvals.
- Keep Article 10 separate and deny it without the accepted authorization and
  safeguard contract.
- Reject expired, revoked, superseded, contradictory, unqualified,
  jurisdiction-mismatched, purpose-mismatched, and scope-mismatched evidence.
- Prove that no favorable field compensates for a missing non-compensatory
  gate.

### PostgreSQL and gate tests

- Commit metadata, decision evidence, observation, working context,
  checkpoint, receipt, and audit atomically for an exact `ALLOW`.
- Commit no rows for every non-`ALLOW` outcome.
- Deny direct table mutation by every runtime role.
- Deny wrong Tenant, Area, Project, Session, actor, purpose, activity, policy,
  metadata digest, or decision binding.
- Prove deterministic exact replay and reject altered replay.
- Prove rollback on audit, receipt, policy, metadata, checkpoint, and storage
  failures.
- Race decision evaluation and revocation; revocation must prevent the commit.
- Restore stale decision or policy data and prove it remains inactive until
  authoritative reconciliation.

### Property and state-machine tests

- No incomplete or unknown metadata reaches storage.
- No outcome other than exact `ALLOW` reaches storage.
- Scope, purpose, activity, data class, and policy version never widen.
- Policy and decision records are immutable.
- Equal canonical input and policy state produce the same decision.
- Expired, revoked, rejected, or superseded policy state never transitions
  directly to active.
- Audit and mutation are always both present or both absent.

## Claim limits

Completion of this preparation means only that an integration contract exists.
It does not mean:

- S1-14.4 is authorized or implemented;
- Article 6 runtime authority exists;
- S1-11.2 storage enforcement is implemented;
- any Article 6 basis, Article 9 condition, or Article 10 authorization is
  applicable or sufficient;
- any processing purpose, retention period, safeguard, approval, evidence
  source, deployment, jurisdiction, or release is approved;
- existing records are classified, lawful, migrated, or safe for processing;
- a test fixture is qualified review evidence; or
- the repository is production ready.

A future implementation may claim S1-11.2 completion only after the accepted
runtime contracts are implemented, the Article 6 dependency is closed, every
protected storage path uses the gate, live PostgreSQL atomicity and bypass
tests pass, independent Security, Privacy, and Architecture review closes all
Critical and High findings, the pull request is merged, and repository and
lifecycle evidence agree.
