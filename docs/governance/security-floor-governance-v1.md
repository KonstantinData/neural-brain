# Security Floor Governance v1

- Status: Normative foundation-governance contract
- Contract: [`../architecture/contracts/security-floor-governance-v1.json`](../architecture/contracts/security-floor-governance-v1.json)
- Governing decisions: ADR-005 and ADR-018
- Dependencies: FND-04.3, FND-04.7, and S1-02.1

## Purpose

This contract translates the accepted prohibited-use classifications from FND-04.3 into six non-overridable Security Floor governance rules. It also defines the bounded evidence role of qualified independent human review for a sensitive or high-risk *candidate* case. It preserves the product- and domain-neutral Neural Brain boundary: the Memory Core is a protected subsystem, not the whole product.

The contract is a traceability input, not a legal or regulatory conclusion. It does not classify a real deployment, determine lawfulness, grant authority, activate policy, enable a capability, authorize a release, or implement a human-review service.

## Translation and enforcement boundary

Each `PF-01` through `PF-06` immutable prohibition in `prohibited-unsupported-use-v1.json` maps one-to-one to `SFG-01` through `SFG-06`. A match is prohibited and denied before review evidence is considered. Policy, approval, assessment, exception, or human review cannot weaken these rules.

`S1-02.1` remains the only implemented runtime floor evidence: it admits only `memory_ingest` and `memory_read` with a complete authenticated `RuntimeContext`. This document does not claim that every future Goal, Action, Learning, or Model Promotion rule is implemented. Future runtime work must add each rule through the owning Protected Control Plane component and its transition-gate evidence.

## Sensitive and high-risk candidate boundary

FND-04.7 labels are review-only candidates, not legal classifications. For a sensitive, high-impact, high-risk, prohibited, or not-assessed candidate—or when evidence is unknown, missing, stale, contradictory, or scope-mismatched—qualified independent human-review evidence is mandatory before a separately governed future reassessment or release evaluation can proceed. Its absence is `unsupported_and_deployment_specific_release_blocked`.

Human review may identify gaps and escalate the case. It cannot create missing authority, expand scope, decide a gate, override a Security Floor rule, turn `prohibited` or `unsupported` into an allow outcome, or authorize an external effect, protected-state transition, deployment, productive use, or release.

## Deterministic fail-closed order

1. Deny a mapped immutable prohibition.
2. Deny incomplete, unknown, stale, contradictory, scope-mismatched, or unaccepted classification evidence as unsupported.
3. Require bounded qualified independent human-review evidence for a sensitive or high-risk candidate before any separately governed future evaluation.
4. Retain denial: this contract contains no allow, authorization, activation, or release outcome.
