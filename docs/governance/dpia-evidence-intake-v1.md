# DPIA Evidence Intake v1

## Status and purpose

- Status: normative foundation governance template.
- Contract: `docs/architecture/contracts/dpia-evidence-intake-v1.json`.
- Task: `S1-14.12`.
- Scope: versioned, product- and domain-neutral evidence intake for a proposed
  DPIA review. It records immutable, scope-bound evidence references; it is not
  an approved DPIA or a processing, runtime, release, or legal decision.

The template is intentionally not populated with a concrete deployment. Neural
Brain has no accepted scoped customer or domain integration and no concrete
processing, jurisdiction, assessment, risk, mitigation, approval, review, or
prior-consultation facts. Those unknowns are release blockers, not implied
favorable outcomes.

## Required evidence boundary

One intake binds exactly one immutable artifact version or digest, authenticated
Tenant/Area/Project scope, intended-purpose version, processing activity,
proposed deployment, and jurisdiction evidence combination. It requires an
accountable owner and a qualified independent reviewer. Assessment, risk,
mitigation, residual-risk, approval, review, and Article 36
prior-consultation-trigger material must be durable evidence references with
provenance, currency, scope, and contradiction treatment.

The template is category- and reference-only. It rejects raw personal data,
special-category or criminal-offence values, identifiers, credentials, secrets,
prompts, memory payloads, consent text, contracts, legal advice, and
unverified assertions.

## Fail-closed operation

Missing, unknown, stale, contradictory, unqualified, non-immutable, or
scope-mismatched evidence blocks the deployment-specific release decision.
Unresolved high residual-risk evidence or an unresolved prior-consultation
trigger disposition also blocks it. Evidence cannot be reused after a Tenant,
Area, Project, artifact, purpose, activity, deployment, or jurisdiction change.

The intake cannot determine DPIA necessity, high or residual risk, mitigation
adequacy, approval validity, prior-consultation necessity, lawfulness, or any
legal obligation. It cannot establish trusted scope, grant authority, override
the Security Floor, activate processing, enable runtime capability, or approve
release. Only separately governed qualified review and the applicable Protected
Control Plane, transition-gate, evaluation, recognition, and release evidence
can decide a concrete deployment.

## Review and reassessment

Review proceeds in the deterministic order defined in the JSON contract:
validate immutable identity and scope; validate linked screening and register
evidence; record assessment and risk evidence; record mitigation, residual-risk,
approval, and review evidence; record prior-consultation-trigger disposition;
then retain blockers and reassessment evidence. Any gap stays explicit and
cannot be compensated by a later favorable entry.

Reassessment is mandatory after a scoped artifact, deployment, purpose,
activity, jurisdiction, data-category, recipient, transfer, safeguard,
assessment, risk, mitigation, residual-risk, reviewer, approval, or
prior-consultation-trigger change, and on expiry, incident, complaint, conflict,
or material misuse signal.
