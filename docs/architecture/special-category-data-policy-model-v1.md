# Special-Category Data Policy Model v1

## Model status

- Status: **Proposed machine-readable model design; non-authorizing**
- Related task: `S1-14.4`
- Current runtime activation: **false**
- Accepted policy instances: **none established by this document**
- Target `ALLOW`: **reserved vocabulary; unavailable in the current runtime**

This document defines the proposed semantic fields and invariants for a future
schema. It is not itself an instance schema, accepted ADR, policy instance,
qualified review, activation record, legal conclusion, migration, or runtime
validator.

## Design principles

1. Policy content is immutable and content-addressed.
2. Trusted identity and scope never come from the policy payload or processing
   request.
3. Classification is multi-axis and versioned; a generic sensitivity label is
   insufficient.
4. Legal- and privacy-relevant facts are references to separately qualified-review-bound
   evidence, never runtime legal inference.
5. General basis and additional special condition are independent fields and
   non-compensatory gates.
6. Policy definitions, evidence, approvals, lifecycle events, decisions, and
   mutations have distinct ownership.
7. Unknown values, undeclared fields, placeholders, stale facts, conflicts, and
   unsupported combinations fail closed.
8. Current activation remains false until an accepted ADR, implementation,
   review, migration, and separate release decision exist.

## Authorization labels

The labels below identify who must authoritatively establish a field in a
future deployment. They do not appoint a person or grant authority.

| Label | Meaning |
| --- | --- |
| `TRUSTED_RUNTIME` | Derived from authenticated Runtime or protected database state |
| `ACCOUNTABLE_OWNER` | Decided by the accountable deployment or processing owner |
| `QUALIFIED_PRIVACY_REVIEW` | Requires qualified privacy review |
| `QUALIFIED_LEGAL_REVIEW` | Requires qualified deployment-specific legal review |
| `SECURITY_CONTROL_OWNER` | Requires verified technical-control ownership and evidence |
| `INDEPENDENT_ACTIVATION_APPROVAL` | Requires an approver independent from author and material changer |
| `SYSTEM_COMPUTED` | Canonically computed by trusted code or PostgreSQL |

Every deployment-specific authorizing field below initially has a pending
status. This proposal marks none `DECIDED`.

## Proposed data-classification model

A single enum cannot represent overlapping properties such as pseudonymized
personal data, Article 9 categories, Article 10 data, and data concerning
children. The future classification record uses independent axes.

### Personal-data status

```text
NON_PERSONAL
PERSONAL
PSEUDONYMIZED_PERSONAL
ANONYMIZED_VERIFIED
UNKNOWN
```

### Special-category status

```text
NOT_APPLICABLE
ARTICLE_9
UNKNOWN
```

### Article 9 category set

The set is defined only by an accepted, qualified-review contract. The runtime
schema stores contract-bound category identifiers or the explicit terminal value
`UNKNOWN`; it does not invent category labels.

### Article 10 status

```text
ARTICLE_10
NOT_APPLICABLE
UNKNOWN
```

### Child-data status

```text
NO
YES
UNKNOWN
```

### Classification record

```text
classification_id                         SYSTEM_COMPUTED
classification_schema_version             SYSTEM_COMPUTED
classification_version                    SYSTEM_COMPUTED
subject_kind                              ACCOUNTABLE_OWNER
subject_digest                            SYSTEM_COMPUTED
tenant_id                                 TRUSTED_RUNTIME
area_id                                   TRUSTED_RUNTIME
project_id                                TRUSTED_RUNTIME
personal_data_status                      QUALIFIED_PRIVACY_REVIEW
special_category_status                   QUALIFIED_PRIVACY_REVIEW + QUALIFIED_LEGAL_REVIEW
article_9_category_ids                    QUALIFIED_PRIVACY_REVIEW + QUALIFIED_LEGAL_REVIEW
article_10_status                         QUALIFIED_PRIVACY_REVIEW + QUALIFIED_LEGAL_REVIEW
child_data_status                         QUALIFIED_PRIVACY_REVIEW + QUALIFIED_LEGAL_REVIEW
source_and_provenance_refs                QUALIFIED_PRIVACY_REVIEW
automated_classifier_version_or_not_used  SYSTEM_COMPUTED
qualified_reviewer_binding                QUALIFIED_PRIVACY_REVIEW
reviewed_at                               SYSTEM_COMPUTED
valid_until                               QUALIFIED_PRIVACY_REVIEW
contradiction_status                      QUALIFIED_PRIVACY_REVIEW
evidence_manifest_digest                  SYSTEM_COMPUTED
classification_digest                     SYSTEM_COMPUTED
```

### Classification invariants

- Any axis value `UNKNOWN` blocks target `ALLOW`.
- `NON_PERSONAL` conflicts with `ARTICLE_9`, Article 10 `YES`, or child data
  `YES`.
- `ANONYMIZED` requires scope-matched anonymization evidence; a request label is
  insufficient.
- `PSEUDONYMIZED_PERSONAL` remains personal for gate evaluation.
- Article 9 categories and Article 10 status cannot both be silently collapsed
  into a generic `restricted` label.
- Model output can propose a review signal but cannot establish the trusted
  classification.
- A subject-content, purpose, activity, scope, source, or classifier change
  invalidates reuse and requires reassessment.

## Proposed immutable policy definition

```text
policy_schema_version                     SYSTEM_COMPUTED
policy_id                                 ACCOUNTABLE_OWNER
policy_version                            SYSTEM_COMPUTED
predecessor_policy_digest                 SYSTEM_COMPUTED
policy_author_id                          TRUSTED_RUNTIME
created_at                                SYSTEM_COMPUTED
deployment_id                             ACCOUNTABLE_OWNER
environment                               ACCOUNTABLE_OWNER
supported_system_ids                      ACCOUNTABLE_OWNER
controller_role_evidence_ref              QUALIFIED_LEGAL_REVIEW
processor_role_evidence_refs              QUALIFIED_LEGAL_REVIEW
tenant_scope                              TRUSTED_RUNTIME + ACCOUNTABLE_OWNER
area_scope                                TRUSTED_RUNTIME + ACCOUNTABLE_OWNER
project_scope                             TRUSTED_RUNTIME + ACCOUNTABLE_OWNER
session_scope_rule                        ACCOUNTABLE_OWNER
jurisdiction_ids                          ACCOUNTABLE_OWNER + QUALIFIED_LEGAL_REVIEW
processing_activity_id_and_digest         ACCOUNTABLE_OWNER + QUALIFIED_PRIVACY_REVIEW
purpose_id_version_and_digest             ACCOUNTABLE_OWNER + QUALIFIED_PRIVACY_REVIEW
supported_operation_ids                   ACCOUNTABLE_OWNER + QUALIFIED_PRIVACY_REVIEW
excluded_operation_ids                    ACCOUNTABLE_OWNER + QUALIFIED_PRIVACY_REVIEW
supported_classification_predicates       QUALIFIED_PRIVACY_REVIEW + QUALIFIED_LEGAL_REVIEW
general_basis_evidence_binding            QUALIFIED_LEGAL_REVIEW
additional_condition_evidence_binding     QUALIFIED_LEGAL_REVIEW + QUALIFIED_PRIVACY_REVIEW
article_10_disposition_binding            QUALIFIED_LEGAL_REVIEW + QUALIFIED_PRIVACY_REVIEW
consent_and_withdrawal_binding             QUALIFIED_LEGAL_REVIEW + QUALIFIED_PRIVACY_REVIEW
safeguard_manifest_binding                QUALIFIED_PRIVACY_REVIEW + SECURITY_CONTROL_OWNER
minimization_rule_binding                 QUALIFIED_PRIVACY_REVIEW
access_rule_binding                       QUALIFIED_PRIVACY_REVIEW + SECURITY_CONTROL_OWNER
rights_process_binding                    QUALIFIED_PRIVACY_REVIEW + ACCOUNTABLE_OWNER
retention_rule_binding                    ACCOUNTABLE_OWNER + QUALIFIED_PRIVACY_REVIEW + QUALIFIED_LEGAL_REVIEW
deletion_and_derivative_rule_binding      ACCOUNTABLE_OWNER + QUALIFIED_PRIVACY_REVIEW
legal_hold_rule_binding                   QUALIFIED_LEGAL_REVIEW + ACCOUNTABLE_OWNER
recipient_processor_location_bindings     ACCOUNTABLE_OWNER + QUALIFIED_PRIVACY_REVIEW + QUALIFIED_LEGAL_REVIEW
transfer_rule_binding                     QUALIFIED_PRIVACY_REVIEW + QUALIFIED_LEGAL_REVIEW
incident_and_reassessment_bindings        ACCOUNTABLE_OWNER + QUALIFIED_PRIVACY_REVIEW + SECURITY_CONTROL_OWNER
effective_from                            ACCOUNTABLE_OWNER + QUALIFIED_PRIVACY_REVIEW + QUALIFIED_LEGAL_REVIEW
valid_until                               ACCOUNTABLE_OWNER + QUALIFIED_PRIVACY_REVIEW + QUALIFIED_LEGAL_REVIEW
revalidation_at                           QUALIFIED_PRIVACY_REVIEW + QUALIFIED_LEGAL_REVIEW
unsupported_cases                         ACCOUNTABLE_OWNER + QUALIFIED_PRIVACY_REVIEW + QUALIFIED_LEGAL_REVIEW
evidence_manifest_digest                  SYSTEM_COMPUTED
approval_manifest_digest                  SYSTEM_COMPUTED
canonical_policy_digest                   SYSTEM_COMPUTED
```

Trusted Runtime scope is compared with approved policy scope. The policy
document cannot create or broaden Tenant, Area, Project, or Session scope.

## Required evidence binding

Every evidence reference contains:

```text
evidence_id
evidence_schema_version
evidence_version_or_content_digest
evidence_type
source_reference
source_provenance
source_date
retrieved_or_verified_at
scope_binding
purpose_and_activity_binding
jurisdiction_binding
reviewer_treatment
contradiction_status
valid_from
valid_until
reassessment_triggers
retention_and_deletion_class
```

Evidence content is immutable. Corrections, withdrawals, expiry, and
supersession create append-only events and new versions. Evidence references
must not contain unnecessary raw personal data, special-category values,
criminal-offence data, credentials, prompts, memory payloads, consent text,
contracts, or legal advice.

For a conditionally required field, exactly one of these branches is present:

```text
scope_matched_approved_evidence
qualified_scope_matched_not_applicable_disposition
```

Both, neither, placeholders, `TBD`, `pending`, or unknown-as-not-applicable are
invalid and block target `ALLOW`.

## Approval model

An approval record contains:

```text
approval_id                               SYSTEM_COMPUTED
approval_type                             SYSTEM_COMPUTED
policy_digest                             SYSTEM_COMPUTED
evidence_manifest_digest                  SYSTEM_COMPUTED
actor_id                                  TRUSTED_RUNTIME
authority_snapshot_digest                 TRUSTED_RUNTIME
qualified_role_binding                    TRUSTED_RUNTIME
scope_binding                             TRUSTED_RUNTIME
decision_status                           authorizing reviewer
rationale_and_constraint_refs             authorizing reviewer
approved_at                               SYSTEM_COMPUTED
valid_until                               authorizing reviewer
revalidation_trigger_ids                  authorizing reviewer
independence_evidence_ref                 INDEPENDENT_ACTIVATION_APPROVAL
```

Allowed decision statuses are:

```text
DECIDED
PENDING_OWNER
PENDING_PRIVACY_REVIEW
PENDING_LEGAL_REVIEW
REJECTED
OUT_OF_SCOPE
```

Only `DECIDED` satisfies a required authorizing decision. `OUT_OF_SCOPE` is
valid only when a qualified, evidence-backed disposition establishes that the
exact field is not applicable. It is not a favorable default.

Policy author and independent activation approver are distinct authenticated
identities. Reviewer qualifications, authority, scope, conflicts, and expiry
are protected facts; a string role supplied in an approval payload is not
sufficient.

## Policy digest and canonicalization

The future schema uses strict validation, rejects unknown fields and duplicate
set members, and defines one canonical byte representation. The policy digest
is:

```text
SHA-256(canonical policy bytes)
```

The canonical policy includes every field that can affect evaluation,
including all evidence and approval manifest digests, scope rules, purposes,
activities, classifications, conditions, safeguards, retention, validity,
exclusions, and predecessor binding.

Changing any evaluation-relevant field creates a new policy version and digest.
No alias, display label, mutable external URL, or database row identifier may
substitute for the content digest.

## Policy lifecycle model

Each immutable policy definition has append-only lifecycle events and one
gate-owned current head.

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

The lifecycle head contains only derived current state, version, last event,
and generation. It is not caller writable. Every transition atomically appends
an event containing actor, authority snapshot, prior and next state, policy
digest, evidence digest, reason codes, timestamp, expiry, approvals, and
idempotency binding.

Only `ACTIVE` is eligible for future target `ALLOW`. `APPROVED` is not active.
`SUSPENDED` blocks until independent reconciliation of unchanged digests.
`REVOKED`, `EXPIRED`, `REJECTED`, and `SUPERSEDED` are terminal.

Any material change while suspended creates a new version rather than
reactivating the old version.

## Proposed processing-decision binding

```text
decision_schema_version
decision_id
transition_request_id
actor_id
tenant_id
area_id
project_id
session_id
database_identity_generation
operation
subject_kind_and_digest
processing_activity_digest
purpose_digest
classification_digest
policy_digest
policy_activation_event_id
evidence_manifest_digest
approval_manifest_digest
authority_snapshot_digest
parameter_digest
code_version
model_version_or_model_not_used
decision_time
valid_until
outcome
reason_codes
obligations
required_review_roles
downstream_action
mutation_and_audit_correlation
```

The target outcome enum is:

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

Only future target `ALLOW` can admit a protected mutation. It is valid only for
exact equality of all bound facts and only before the earliest bound expiry.
The current runtime cannot issue this target `ALLOW` because activation is
explicitly false.

## Non-compensatory validation rules

Target `ALLOW` is impossible if any of the following is missing, unknown,
expired, revoked, contradictory, unsupported, unqualified, or scope-mismatched:

- authenticated actor or scope;
- Tenant-bound database identity;
- released Security Floor operation;
- authority or required approval;
- exact activity or purpose;
- classification;
- jurisdiction or deployment environment;
- general processing-basis evidence;
- required additional condition or Article 10 disposition;
- safeguards or minimization;
- retention, deletion, legal hold, rights, recipient, processor, location, or
  transfer disposition;
- active immutable policy version;
- exact evidence and approval digests;
- current review and reassessment state;
- auditability or atomic commit capability.

No evidence score, risk score, later favorable statement, model confidence,
human approval, or configurable policy parameter can compensate for a failed
Security Floor, identity, authority, scope, required-condition, or audit gate.

## Storage model and writer ownership

A future migration may introduce logically separate protected relations such
as:

```text
privacy_control.policy_definitions
privacy_control.policy_evidence_bindings
privacy_control.policy_approval_events
privacy_control.policy_lifecycle_events
privacy_control.policy_lifecycle_heads
privacy_control.classification_records
privacy_control.processing_decisions
```

Names are proposals, not migration authority.

Policy definitions, evidence bindings, approvals, lifecycle events,
classification records, and decisions are append-only. Lifecycle heads are
writable only through the Policy Lifecycle Gate. Memory tables remain writable
only through the Memory Transition Gate. All protected relations require RLS,
`FORCE ROW LEVEL SECURITY`, immutable scope lineage, restricted privileges, and
Tenant-bound Runtime identity.

JSON may store bounded extensible evidence, but identity, scope, lifecycle,
version, digest, idempotency, validity, decision, and audit-correlation fields
use typed columns and constraints.

## Atomic mutation binding

For a future admitted operation, the active lifecycle head is locked and all
decision inputs are revalidated inside the same PostgreSQL transaction that
writes:

```text
privacy processing decision
protected Memory Gate mutation
mutation audit event
idempotency receipt
```

They commit together or not at all. The client cannot pass an authoritative
policy version or outcome into the transaction. A non-`ALLOW` decision records
no protected data mutation. Audit or database failure rolls back the admitted
path.

Revocation and activation transitions serialize on the same lifecycle head as
the mutation. Cache contents are advisory and invalidated by lifecycle
generation, policy digest, evidence digest, approval digest, or pool-generation
change.

## Retention, revocation, and restore model

Revocation, expiry, purpose change, classification change, evidence conflict,
or reassessment trigger creates an append-only lifecycle event and blocks new
processing. Affected lineage is submitted to separately authorized restriction,
deletion, correction, or reconciliation paths.

Policy and audit immutability does not require indefinite retention of raw
personal data. Authorized deletion or anonymization propagates to payloads,
embeddings, indexes, caches, checkpoints, candidates, summaries, reports, and
backups while retaining only non-reconstructive operation evidence.

Restored policy state is not automatically active. A restored deployment keeps
this capability inactive or `SUSPENDED` until independent recovery verification
establishes exact backup and WAL integrity, migration compatibility, Tenant
identity, Gate privileges, RLS and FORCE, lifecycle and evidence digests,
revocation state, audit continuity, and reconciliation readiness, followed by
an authorized cutover decision.

## Open authorizing decisions

Every item remains pending until separately resolved:

| Decision | Required status/authority |
| --- | --- |
| Concrete deployment, systems, Tenants or Companies, and environment | `PENDING_OWNER` |
| Processing activities and purposes | `PENDING_OWNER`, `PENDING_PRIVACY_REVIEW` |
| Jurisdictions and controller/processor roles | `PENDING_LEGAL_REVIEW` |
| Classification and Article 9/10 applicability | `PENDING_PRIVACY_REVIEW`, `PENDING_LEGAL_REVIEW` |
| General basis and required additional condition | `PENDING_LEGAL_REVIEW` |
| Safeguards, minimization, access, and rights | `PENDING_PRIVACY_REVIEW` plus security evidence |
| Retention, deletion, legal hold, and backup treatment | `PENDING_OWNER`, `PENDING_PRIVACY_REVIEW`, `PENDING_LEGAL_REVIEW` |
| Recipients, processors, location, and transfers | `PENDING_OWNER`, `PENDING_PRIVACY_REVIEW`, `PENDING_LEGAL_REVIEW` |
| Incident, revocation, reconciliation, and operational ownership | `PENDING_OWNER` |
| Exact policy activation | Lifecycle remains non-`ACTIVE`; independent activation-approval evidence is absent pending an accepted ADR and green regression evidence |

## Claim limits

This model does not decide lawfulness, applicability, a general basis, an
additional condition, Article 10 controls, classification, safeguards,
retention, roles, approvals, processing scope, or deployment readiness. It does
not create a schema accepted by runtime, protected tables, a migration, an
active policy, or a processing authorization. Current runtime activation is
**false**, and target `ALLOW` remains unavailable.
