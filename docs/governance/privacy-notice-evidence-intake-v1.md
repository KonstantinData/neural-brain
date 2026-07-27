# Privacy-Notice Evidence Intake v1

- Status: Normative Foundation-governance template
- Contract: [`../architecture/contracts/privacy-notice-evidence-intake-v1.json`](../architecture/contracts/privacy-notice-evidence-intake-v1.json)
- Governing decisions: ADR-001, ADR-005, ADR-018, and ADR-019
- External reference: [Regulation (EU) 2016/679](https://eur-lex.europa.eu/eli/reg/2016/679/oj)

## Purpose and boundary

This versioned template collects evidence references that a qualified reviewer
may need to assess a possible privacy notice for direct or indirect collection
in one proposed processing activity. It is product- and domain-neutral. It
records immutable evidence references for artifact, authenticated scope,
purpose, activity, jurisdiction, collection path, possible notice elements,
reviewer, evidence currency, and known gaps; it makes no legal conclusion.

The repository establishes no controller, representative, DPO, processing
activity, collection path, data-subject population, recipient, transfer,
jurisdiction, or privacy-notice fact. The intake contains no personal data,
identifiers, notice text, contact values, credentials, prompts, memory payloads,
contract text, or legal advice. The Memory Core is a protected subsystem, not
the product boundary.

## Required evidence

One immutable intake is required for each exact artifact, authenticated Tenant,
Area, and Project scope, purpose, activity, jurisdiction, collection path, and
notice-version combination. It requires qualified reviewer and independence
evidence; direct/indirect collection-path evidence; controller, representative,
and DPO contact evidence; possible purpose, basis, category, data-subject,
indirect source, recipient, transfer, retention, rights, complaint, and contact
route evidence; possible Article 22 automated-decision/profiling disposition;
notice delivery, timing, language, accessibility, version, integrity, and
currency evidence; explicit non-applicability, unknown, conflict, gap, and
expiry dispositions; release blockers; and a next review date.

Authenticated scope, purpose, activity, jurisdiction, and collection-path
evidence are review inputs only. No label, prompt, payload, observation, model
output, memory content, or tool output can establish trusted context or replace
immutable evidence. Missing or disputed facts are not silently interpreted in
favor of collection or processing.

## Fail-closed boundary

Missing, unknown, stale, contradictory, unqualified, non-immutable, or
scope-mismatched evidence rejects or leaves the intake incomplete and blocks the
deployment-specific release decision. This also applies to unresolved collection
path, contact, source, recipient, transfer, retention, rights, Article 22,
delivery, accessibility, version, integrity, and currency evidence. A favorable
later statement never compensates for an unresolved earlier fact.

The template has no allow outcome. It cannot provide legal advice, assess notice
sufficiency, determine lawfulness or a legal basis, grant authority, approve
collection, processing, disclosure, transfer, or release, change policy,
activate a runtime path, deliver a notice, respond to a data subject, or enable
any external effect. All such outcomes require separately governed qualified
review and the applicable Protected Control Plane, transition-gate, evaluation,
recognition, and release evidence.
