# S1-14.4 Runtime Enforcement Decision Package v1

- Status: Draft decision package; runtime authorization blocked
- Task: `S1-14.4`
- Dependent task: `S1-11.2`
- Decision state: all required deployment-specific decisions remain pending
- Data boundary: this document contains categories and evidence references only; it must not contain personal data, special-category values, criminal-offence data, identifiers, credentials, secrets, prompts, memory payloads, consent text, contracts, or legal advice
- Governing repository context: ADR-001, ADR-005, ADR-018, ADR-019, the Architecture Directive v4.0, and the existing Article 6, Article 9/10, and consent evidence-intake contracts

## Authority and claim boundary

This package prepares deployment-specific decisions for qualified owner,
privacy, and legal review. It is not legal advice, a determination of GDPR
applicability or lawfulness, an Article 6 legal-basis selection, an Article 9
condition determination, an Article 10 authorization, a consent validation, a
compliance certification, or a processing, deployment, runtime, release, or
production approval.

No entry in this package creates authority. A completed review record is still
only an input to the independently governed Protected Control Plane and release
gates. Until every applicable required decision is externally decided for one
exact deployment scope, the runtime must not return `ALLOW` for protected
processing or storage.

## Executive summary

The repository already defines fail-closed evidence-intake preparation for
Article 6 and Article 9/10. Those artifacts intentionally provide no typed
deployment instance, qualified review, runtime decision, or mutation authority.
This package reduces the remaining external blocker to fifteen explicit
decisions (`PRIV-01` through `PRIV-15`).

The proposed technical model binds every decision to one immutable artifact,
authenticated Tenant/Area/Project scope, processing activity, purpose version,
data-class disposition, jurisdiction, policy version, evidence set, and review
period. Article 6, Article 9, and Article 10 remain separate gates. Withdrawal,
expiry, loss of basis, purpose change, restriction, retention end, conflicting
evidence, and unknown facts never fall back to permissive processing.

This draft supports technical preparation only. Operational runtime support for
personal data, Article 9 special-category data, or Article 10 data remains
disabled until the applicable rows are changed to `DECIDED` by the designated
external authorities in a separately accepted, scope-bound decision record.

## Official primary references

- [Regulation (EU) 2016/679, official text](https://eur-lex.europa.eu/eli/reg/2016/679/oj), especially Articles 5, 6, 7, 9, 10, 17, 18, 19, 24, 25, 30, 32, and 35
- [EDPB Guidelines 05/2020 on consent under Regulation 2016/679](https://www.edpb.europa.eu/documents/guideline/guidelines-052020-on-consent-under-regulation-2016679_en)
- [EDPB Guidelines 4/2019 on Article 25 Data Protection by Design and by Default](https://www.edpb.europa.eu/documents/guideline/guidelines-42019-on-article-25-data-protection-by-design-and-by-default_en)
- [EDPB Guidelines 2/2019 on Article 6(1)(b) in online services](https://www.edpb.europa.eu/our-work-tools/our-documents/guidelines/guidelines-22019-processing-personal-data-under-article-61b_en)
- [EDPB legal-basis topic and official guidance index](https://www.edpb.europa.eu/topics/key-gdpr-concepts/legal-basis_en)
- [EDPB-endorsed WP29 guidelines, including DPIA guidance](https://www.edpb.europa.eu/endorsed-wp29-guidelines_en)

These sources are qualified-review inputs only. Member State and sector-specific
law cannot be selected until the deployment jurisdiction and processing facts
are supplied and reviewed.

## Proposed concrete use case and deployment scope

No concrete deployment is established by the repository. The accountable owner
must replace every placeholder below with immutable evidence before review:

| Field | Required value | Current disposition |
| --- | --- | --- |
| Deployment identifier and environment | `<PENDING_OWNER: deployment ID and non-production/production environment>` | Unknown; runtime blocked |
| Immutable artifact | `<PENDING_OWNER: version or digest>` | Unknown; runtime blocked |
| Controller and any joint controller | `<PENDING_OWNER: role evidence reference>` | Unknown; runtime blocked |
| Processor and subprocessors | `<PENDING_OWNER: role and instruction evidence references>` | Unknown; runtime blocked |
| Authenticated scope | `<PENDING_OWNER: Tenant, Area, and Project evidence references>` | Unknown; runtime blocked |
| Processing activity | `<PENDING_OWNER: immutable activity ID and version>` | Unknown; runtime blocked |
| Intended purpose | `<PENDING_OWNER: immutable purpose contract ID and version>` | Unknown; runtime blocked |
| Data subjects and data sources | `<PENDING_OWNER: categories and provenance references only>` | Unknown; runtime blocked |
| Jurisdiction | `<PENDING_LEGAL_REVIEW: applicable Union, Member State, and sector-specific law evidence>` | Unknown; runtime blocked |
| Recipients, locations, and transfers | `<PENDING_OWNER: category and transfer evidence references>` | Unknown; runtime blocked |
| Proposed operating period | `<PENDING_OWNER: valid-from, valid-until, and review dates>` | Unknown; runtime blocked |

Evidence instances must contain references and classifications, not the personal
data or protected values being assessed.

## Candidate data-class model

The following classes are proposed for machine validation. Their inclusion in
the taxonomy is not authorization to process them.

| Candidate class | Technical treatment before external decision |
| --- | --- |
| `NON_PERSONAL_DATA` | May leave this privacy gate only after provenance-backed classification shows that the data is outside the personal-data scope; an unsupported assertion is insufficient. |
| `PERSONAL_DATA` | Deny unless the exact purpose, Article 6 basis, retention rule, safeguards, owner, and review evidence are active and scope-matched. |
| `PSEUDONYMISED_PERSONAL_DATA` | Treat as personal data; pseudonymisation is a safeguard and does not by itself remove the data from GDPR scope. |
| `ANONYMISED_DATA` | Treat as personal data until qualified, current evidence and effectiveness testing support the anonymisation disposition for the exact artifact and context. |
| `ARTICLE_9_SPECIAL_CATEGORY_DATA` | Deny unless an Article 6 basis and a separate applicable Article 9(2) condition, safeguards, and qualified review are all active. |
| `ARTICLE_10_DATA` | Deny unless an Article 6 basis and a separate official-authority or Union/Member-State-law authorization disposition with appropriate safeguards are active. |
| `CHILD_OR_MINOR_DATA` | Deny pending scope-specific age, service, consent/authority, vulnerability, transparency, and safeguard review. |
| `UNKNOWN_OR_CONFLICTING` | Always deny and require additional evidence; never infer non-personal or not-applicable. |

### Operationally supported data classes

None. Operational support remains blocked until the applicable decisions in this
package are externally accepted for the exact scope and implemented through the
Protected Control Plane.

### Unsupported data classes and combinations

- unknown, contradictory, stale, unqualified, or scope-mismatched classifications;
- Article 9 data without both an Article 6 disposition and a separate Article 9 disposition;
- Article 10 data without an Article 6 disposition and the required official-authority or law-authorization evidence;
- data whose jurisdiction, subject category, source, recipient, location, or transfer status is unresolved;
- personal data embedded in prompts, model responses, memory payloads, logs, caches, indexes, embeddings, backups, or derivatives without an approved purpose-bound processing and retention disposition;
- a purportedly anonymised dataset without qualified effectiveness evidence for the actual context; and
- any data class outside the accepted decision scope.

## Candidate purpose model

Purposes must be predetermined, specific, explicit, versioned, and bound to the
exact processing activity. Generic labels such as `service_improvement`,
`research`, `security`, or `analytics` are not sufficient without a concrete
description, necessity evidence, data boundary, operation list, recipients,
duration, and expected result.

### Operationally supported purposes

None. Each proposed purpose must be entered under `PRIV-03`, paired with the
applicable Article 6/9/10 decisions, and externally accepted before use.

### Unsupported purposes

- unspecified, bundled, open-ended, inferred, hidden, or payload-defined purposes;
- new or materially changed purposes without a prior compatibility or new-authorization disposition;
- purposes outside the authenticated Tenant/Area/Project and artifact scope;
- purposes that depend on an expired, withdrawn, revoked, superseded, or conflicting decision;
- purposes using more data, longer retention, wider access, or more recipients than the accepted purpose requires; and
- any purpose whose legal or factual prerequisites remain pending.

## Proposed technical enforcement rules

The following rules are proposed architecture inputs, not approved legal or
runtime rules:

1. Determine authenticated scope and immutable artifact identity exclusively
   from trusted runtime context.
2. Validate the data class, processing activity, purpose version, data-subject
   category, source, recipient, location, transfer, and retention metadata.
3. Load one immutable policy and decision-evidence version valid for the exact
   scope, artifact, activity, purpose, data class, and jurisdiction.
4. Require an active Article 6 disposition for personal-data processing.
5. For Article 9 data, require a separate active Article 9(2) disposition and
   every scope-specific safeguard; Article 6 alone never compensates for it.
6. For Article 10 data, require a separate active disposition proving official
   authority control or applicable Union/Member State law authorization and
   appropriate safeguards; Article 9 logic must not be reused as a substitute.
7. Require active owner approval, qualified review, retention, deletion,
   rights-handling, security, and audit evidence. No favorable later gate
   compensates for an earlier missing gate.
8. Immediately before the protected mutation, re-evaluate current policy,
   expiry, revocation, restriction, purpose, scope, kill-switch, and evidence
   state. Cached approval cannot override newer authoritative state.
9. Atomically commit the protected mutation and immutable decision event. An
   audit failure, race, timeout, stale fence, or database error rolls back the
   protected mutation.
10. Bind every decision event to actor, authenticated scope, data class,
    activity, purpose, Article 6/9/10 dispositions, safeguards, retention rule,
    policy version, evidence digests, decision time, reason codes, component,
    code/model version, and mutation correlation.
11. Treat withdrawal, loss of basis, purpose change, restriction, retention
    end, evidence expiry, incident, complaint, restore, or material deployment
    change as mandatory reassessment triggers.
12. Reconcile restores before enabling processing. A backup must not reactivate
    a withdrawn, revoked, expired, superseded, deleted, restricted, or obsolete
    decision or data copy.

### Proposed runtime outcomes

Only `ALLOW` may authorize a protected operation. It is unreachable while any
applicable decision in this package is pending.

| Evidence or review condition | Proposed result |
| --- | --- |
| Every applicable decision is externally `DECIDED`, active, current, exact-scope, and internally consistent | `ALLOW`, subject to all other Protected Control Plane gates |
| Owner fact or evidence missing | `REQUIRE_ADDITIONAL_EVIDENCE` |
| Qualified privacy or legal review pending | `REQUIRE_HUMAN_REVIEW` |
| Evidence or decision validity ended | `EXPIRED` |
| Consent withdrawn or authority/basis revoked | `REVOKED` |
| Evidence, policy, purpose, or scope conflict | `CONFLICT` |
| Data class, purpose, basis, condition, owner, jurisdiction, or policy unknown | `UNKNOWN` |
| Known ineligible, unsupported, or prohibited combination | `DENY` |

All outcomes other than `ALLOW` block protected processing and storage.

## Decision register

The only permitted states in this draft are `PENDING_OWNER`,
`PENDING_PRIVACY_REVIEW`, and `PENDING_LEGAL_REVIEW`. An external accepted
decision record may later set an item to `DECIDED` or `REJECTED`; this draft
does not do so.

| ID | Status | Decision required | Accountable owner/reviewer | Required evidence | Acceptance criterion | Scope and restrictions | Expiry/revalidation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `PRIV-01` | `PENDING_OWNER` | Identify the concrete controller, any joint controller, processors, deployment, environment, artifact, authenticated scope, processing activity, and data-subject population. | Accountable deployment owner; controller role owner | Immutable role, deployment, artifact, Tenant/Area/Project, activity, RoPA, and data-subject-category references | Every role and scope element is identified, internally consistent, immutable, and linked to one proposed deployment; unresolved or disputed roles remain blocked. | Valid only for the named artifact, environment, Tenant, Area, Project, activity, and role allocation; no cross-scope reuse. | Revalidate before activation and on any role, artifact, supplier, environment, scope, or activity change; owner must set a next-review date. |
| `PRIV-02` | `PENDING_LEGAL_REVIEW` | Determine the applicable jurisdiction and identify relevant Union, Member State, and sector-specific law without inferring applicability from repository location. | Qualified independent legal reviewer | Establishment, offering/monitoring, data-subject location, processing-location, controller-role, transfer, and official legal-source evidence | A qualified, dated review identifies the applicable jurisdictional facts and official sources, records conflicts and limitations, and defines the exact covered scope. | No transfer to other countries, sectors, controllers, or purposes; unknown jurisdiction is `UNKNOWN`, never not-applicable. | Revalidate on legal change, location/transfer change, new population or market, reviewer expiry, or at the reviewer-set date. |
| `PRIV-03` | `PENDING_OWNER` | Define one predetermined, specific, explicit, legitimate operational purpose for each processing activity and identify excluded purposes. | Processing/business owner; privacy reviewer consulted | Immutable purpose contract, activity map, necessity objective, data categories, operations, recipients, duration, and expected-result references | The purpose is specific enough to bound data, operations, access, recipients, retention, and testing; bundled or generic purposes are split or rejected. | Exact activity and purpose version only; prompts, payloads, model output, or runtime labels cannot create or broaden purpose. | Revalidate on any purpose, activity, data, recipient, operation, expected-result, or product change and at the owner-set date. |
| `PRIV-04` | `PENDING_LEGAL_REVIEW` | Determine the Article 6 basis, if any, for each exact purpose and processing operation. | Qualified independent legal reviewer; accountable controller owner | Article 6 candidate, necessity, less-intrusive alternatives, proportionality, applicable legal norm or contract/consent/interest evidence, and rights-impact references | The reviewer records one scope-bound disposition and rationale for each operation; missing necessity, external facts, or prerequisites do not produce a favorable disposition. | The disposition cannot be generalized across purposes, operations, data categories, subjects, jurisdictions, or artifacts and does not satisfy Article 9 or 10. | Revalidate on basis facts, purpose, necessity, contract, consent, law, interest, objection, safeguard, or deployment change and at the reviewer-set date. |
| `PRIV-05` | `PENDING_PRIVACY_REVIEW` | Classify each input, stored object, derivative, log, cache, index, embedding, output, and backup as non-personal, personal, pseudonymised, anonymised, Article 9, Article 10, child/minor, or unknown/conflicting. | Privacy owner; qualified legal reviewer for disputed Article 9/10 scope | Data-flow and lineage map, source and field-category evidence, inference risk, identifiability and linkage analysis, anonymisation test evidence, and contradiction status | Every data-bearing path has exactly one current evidence-backed disposition; pseudonymised data remains personal; unknown or conflicting classification blocks. | Classification is artifact-, context-, purpose-, population-, and version-specific and contains no raw protected values. | Revalidate on schema, model, inference capability, source, linkage, recipient, export, data-flow, anonymisation method, or attack-evidence change. |
| `PRIV-06` | `PENDING_LEGAL_REVIEW` | For every Article 9 processing operation, determine whether one specific Article 9(2) condition applies in addition to Article 6 and which safeguards are legally required. | Qualified independent legal reviewer; privacy owner for safeguard evidence | Exact Article 9 category, Article 6 disposition, Article 9(2) candidate, necessity, official law/collective-agreement/professional-secrecy evidence where applicable, purpose and safeguard references | A dated qualified disposition covers the exact category, purpose, operation, jurisdiction, prerequisites, safeguards, and limitations; Article 6 alone never satisfies acceptance. | No reuse between Article 9 categories, purposes, subjects, jurisdictions, or conditions; explicit consent does not override any Union/Member-State-law prohibition. | Revalidate on category, condition, consent, purpose, law, professional secrecy, safeguard, population, or processing change and at the reviewer-set date. |
| `PRIV-07` | `PENDING_LEGAL_REVIEW` | Identify Member State or sector-specific additional conditions and limitations for genetic, biometric, and health data. | Qualified independent legal reviewer | Applicable official national and sectoral sources, category/purpose facts, territorial scope, safeguards, limitations, and effective dates | The review explicitly records applicable additional conditions or a qualified, evidence-backed not-applicable disposition for the exact jurisdiction and use case. | No assumption that GDPR Article 9 alone is sufficient; no cross-jurisdiction or cross-sector reuse. | Revalidate on law, jurisdiction, sector, category, biometric purpose, health context, genetic processing, or deployment change and at the reviewer-set date. |
| `PRIV-08` | `PENDING_LEGAL_REVIEW` | Determine the Article 10 disposition separately from Article 9, including official-authority control or specific Union/Member State law authorization, safeguards, and comprehensive-register restrictions. | Qualified independent legal reviewer; accountable authority owner where applicable | Article 6 disposition, Article 10 classification, official-authority/control evidence or official legal authorization, safeguards, register design, purpose, and scope references | The reviewer confirms the exact applicable route and safeguards; any comprehensive register is shown to remain under official-authority control; otherwise processing remains blocked. | Article 9 conditions cannot substitute for Article 10; no private comprehensive register or unsupported law reference; exact purpose and jurisdiction only. | Revalidate on authority, law, register, safeguard, Article 6, purpose, category, recipient, or jurisdiction change and at the reviewer-set date. |
| `PRIV-09` | `PENDING_PRIVACY_REVIEW` | Decide the handling of every purpose change before further processing, including whether the change needs new authorization or a documented compatibility assessment. | Privacy owner with qualified legal review | Old/new purpose versions, Article 6(4) factors, collection context, relationship, Article 9/10 nature, consequences, safeguards, transparency, and new-basis/consent/law evidence | A pre-processing, scope-bound disposition records compatibility or the required new authorization and controls; unresolved factors block the new purpose. | No post-hoc purpose expansion, dataset linkage, model training, analytics, or reuse; the original purpose remains unchanged and immutable. | Revalidate for every purpose revision or material change to data, operations, consequences, recipients, safeguards, or context. |
| `PRIV-10` | `PENDING_PRIVACY_REVIEW` | Define consent withdrawal intake, authentication, propagation, processing stop, deletion/restriction, reconciliation, and audit behavior for each consent-bound purpose. | Privacy owner; qualified legal reviewer for retained-purpose and exception evidence | Consent-purpose binding, withdrawal channel and timestamp, ease/no-detriment evidence, affected data-flow map, downstream stop/deletion actions, separate-purpose/basis evidence, and audit references | Withdrawal is effective without undue friction; affected processing stops; no silent basis switch occurs; continued retention exists only under a separately established purpose and basis; unresolved cases block. | Applies only where consent is the recorded basis; does not erase or authorize data for unrelated purposes automatically; no raw consent text in this package. | Trigger immediately on withdrawal; revalidate the mechanism on interface, recipient, workflow, storage, legal, or consent-model change and at regular tests. |
| `PRIV-11` | `PENDING_LEGAL_REVIEW` | Define consequences when a non-consent legal basis, contract, statutory authority, necessity fact, or other prerequisite expires or ceases. | Qualified independent legal reviewer; processing owner | Basis lifecycle, contract/law/authority facts, cessation events, affected operations/data, separate retention purpose and basis, claims/legal-hold evidence, and notifications | Each loss event has a pre-defined stop, restriction, deletion, or separately justified retention disposition; no retrospective replacement basis is inferred. | Exact basis, purpose, operation, dataset, and jurisdiction only; unrelated retained data must be separately partitioned and authorized. | Trigger immediately on cessation, invalidation, expiry, objection outcome, law change, or evidence conflict; periodic basis review required. |
| `PRIV-12` | `PENDING_OWNER` | Define a purpose- and category-specific retention rule with start event, end event, period or criteria, and exception handling. | Records/processing owner; privacy and legal reviewers | Data inventory, purpose necessity, official retention law or rationale, category schedule, legal hold, start/end triggers, deletion/anonymisation method, and owner references | Every stored class has a deterministic active retention rule and justified duration; missing, indefinite, generic, or conflicting retention blocks storage. | Separate rules for primary data, evidence, audit, logs, caches, indexes, embeddings, derivatives, and backups; no broader access or use during retention. | Revalidate on purpose, law, claims risk, data class, storage medium, backup, incident, or system change and at least at the owner-set review date. |
| `PRIV-13` | `PENDING_PRIVACY_REVIEW` | Define effective deletion, anonymisation, restriction, recipient propagation, backup handling, and restore reconciliation. | Privacy owner; system/data owner; legal reviewer for exceptions | Article 17/18/19 disposition, data and recipient lineage, deletion/anonymisation tests, restriction controls, copy/derivative inventory, backup schedule, restore reconciliation, exceptions, and audit evidence | Tests show that deletion or anonymisation reaches all in-scope stores and that restricted data cannot be used beyond the accepted restriction; recipient propagation and restore controls are demonstrable. | Legal exceptions require separate purpose/basis/access controls; restriction is not deletion; an unavailable or failed downstream action remains an explicit incident/blocker. | Revalidate on storage, recipient, backup, restore, derivative, model, deletion method, anonymisation attack, law, or rights-process change; test regularly. |
| `PRIV-14` | `PENDING_PRIVACY_REVIEW` | Determine DPIA necessity and, where required, complete and approve the DPIA before processing. | Accountable controller/privacy owner; DPO advice where designated; qualified legal review as needed | Nature, scope, context, purposes, new technology, scale, Article 9/10 use, profiling/decision effects, risk assessment, safeguards, residual risk, DPO advice, and consultation evidence | A documented screening reaches a qualified disposition; any required DPIA is complete, current, scope-bound, and has no unresolved high risk lacking the required consultation or mitigation. | A DPIA does not create legal basis, Article 9/10 condition, processing authority, or release approval; exact assessed deployment only. | Revalidate on material processing, risk, model, scale, data category, population, technology, safeguard, incident, or law change and at the DPIA review date. |
| `PRIV-15` | `PENDING_OWNER` | Name the accountable decision owners, independent reviewers, approval boundaries, restrictions, validity interval, reassessment triggers, and revocation authority. | Accountable deployment owner; privacy owner; qualified independent legal reviewer | Owner identities/roles, independence evidence, signed/digested review references, decision timestamps, restrictions, `valid_from`, `valid_until`, next review, revocation route, and escalation contacts | Every required role is named and authorized; reviews are independent where required; scope, restrictions, expiry, revalidation, revocation, and escalation are explicit and machine-verifiable. | Approval never creates missing authority or compensates for another pending gate; decision reuse outside exact scope is rejected. | No open-ended validity; expire at the earliest evidence/review expiry and revalidate on every registered trigger, incident, complaint, conflict, or material change. |

## Risks and proposed safeguards

| Risk | Proposed safeguard | Remaining external decision |
| --- | --- | --- |
| Payload or model output attempts to set trusted scope, purpose, basis, or approval | Derive trusted context only from authenticated Protected Control Plane state; immutable scope and purpose references | `PRIV-01`, `PRIV-03`, `PRIV-15` |
| Article 6 evidence is mistaken for Article 9 or Article 10 authorization | Separate typed, non-compensatory gates and reason codes | `PRIV-04`, `PRIV-06`, `PRIV-08` |
| Unknown or inferred sensitive data reaches storage | Classification gate immediately before mutation; `UNKNOWN` blocks | `PRIV-05` |
| Consent withdrawal races with an in-flight write | Current-state recheck under the same protected transaction/fence; withdrawal wins before commit | `PRIV-10` |
| Purpose or legal basis is silently changed after collection | Immutable purpose/basis versions; new review on every change; no retrospective switch | `PRIV-04`, `PRIV-09`, `PRIV-11` |
| Approval or evidence is forged, replayed, or used outside scope | Immutable digests, reviewer identity/independence evidence, exact-scope binding, expiry, replay protection, audit correlation | `PRIV-15` |
| Deletion misses copies, derivatives, recipients, or backups | Complete lineage, recipient propagation, tested deletion/anonymisation, tombstones and restore reconciliation | `PRIV-12`, `PRIV-13` |
| Backup restore revives revoked approval or deleted data | Restore in disabled state, authoritative policy/evidence reconciliation, deny until current-state verification | `PRIV-10`, `PRIV-11`, `PRIV-13`, `PRIV-15` |
| Audit fails while mutation succeeds | Atomic mutation and decision-event commit; rollback on audit failure | Technical implementation gate after external decisions |
| Special-category processing creates unassessed high risk | DPIA screening and required DPIA before activation; unresolved high risk remains blocked | `PRIV-14` |

## Alternatives considered

### Metadata validation without a runtime policy gate

Rejected as insufficient. Complete metadata can describe a request but cannot
select a legal basis, establish an Article 9 condition, authorize Article 10
processing, or protect the commit boundary.

### One general privacy approval for the whole product

Rejected. It would not preserve the required binding between artifact, scope,
activity, purpose, data class, jurisdiction, safeguards, and validity period.

### Treat all personal data as Article 9 data

Not selected. Conservative blocking for unknown data is appropriate, but a
runtime taxonomy must preserve the legally distinct Article 9 and Article 10
gates and must not falsely classify or authorize a concrete case.

### Consent as the default basis

Rejected. Consent is one possible Article 6 basis, requires deployment-specific
validity evidence, and must remain withdrawable. It cannot be a fallback for an
unresolved basis or automatically satisfy Article 9 or Article 10.

### Post-processing audit only

Rejected. A post-hoc record cannot replace a missing pre-commit decision or
undo an unauthorized disclosure, processing action, or protected mutation.

### Technical preparation with no productive activation

Selected for the blocked phase. Typed schemas, validators, state machines,
negative tests, and a disabled/fail-closed evaluator may be prepared, provided
they expose no productive `ALLOW` path before the required external decisions
and independently governed technical gates are complete.

## Required external sign-off record

The accepted decision record, stored outside this draft, must provide:

- accountable owner identity and authority reference;
- privacy reviewer identity, qualification, review date, and rationale;
- legal reviewer identity, qualification, independence, review date, and rationale;
- exact artifact, environment, Tenant, Area, Project, activity, purpose, data
  class, jurisdiction, recipient, location, and transfer scope;
- an explicit disposition for each applicable `PRIV-01` through `PRIV-15` item;
- accepted restrictions and unsupported cases;
- immutable evidence identifiers and digests;
- approval and effective dates;
- the earliest expiry or mandatory revalidation date;
- revocation authority and route;
- reassessment triggers; and
- the independent release-decision reference.

Sign-off on this package alone does not authorize processing or release.

## Blocked-state conclusion

`S1-14.4` remains blocked while any required decision is pending. `S1-11.2`
may use this draft only to prepare metadata capture, completeness validation,
classification validation, policy-request interfaces, and fail-closed storage
integration. It must not infer lawfulness, fill missing legal conditions, or
commit protected data without an exact current `ALLOW` from the separately
authorized S1-14.4 gate and every other applicable Protected Control Plane
gate.
