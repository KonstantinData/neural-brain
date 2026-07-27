# Repository Governance

This directory contains the versioned desired repository-governance state for
Neural Brain. The normative contract is
[`repository-policy.json`](repository-policy.json).

The authoritative repository-facing inventory of implemented and target AI
components, models, datasets, adapters, integrations, data flows, tools, and
deployment boundaries is [`ai-component-inventory.md`](ai-component-inventory.md).
It is deliberately fail-closed: an inventory entry does not enable a capability,
approve a deployment, or establish Neural Brain recognition.

[`model-inference-inventory-v1.md`](model-inference-inventory-v1.md) defines
the required immutable evidence record for a model or inference boundary. It is
fail-closed and does not activate a model, inference provider, Ollama fallback,
deployment, release, Model Promotion Gate, or authority.

[`intended-purpose-assessment-v1.md`](intended-purpose-assessment-v1.md)
defines the stable, product- and domain-neutral intended-purpose assessment
input for future deployments. It is not a legal, regulatory, compliance, or
release determination.

[`gdpr-role-assessment-v1.md`](gdpr-role-assessment-v1.md) defines a
relationship-specific, fail-closed input template for a future qualified GDPR
role assessment. It does not determine a role or authorize processing,
deployment, or release.

[`data-object-catalogue-intake-v1.md`](data-object-catalogue-intake-v1.md)
defines a category-only, fail-closed data-object catalogue evidence intake for
future deployment review. It does not create a processing register, determine
lawfulness, write protected state, or enable processing, deployment, or release.

[`gdpr-applicability-screening-v1.md`](gdpr-applicability-screening-v1.md)
defines a fail-closed input template for qualified GDPR applicability,
special-category, automated-decision, and DPIA screening. It does not determine
lawfulness, a GDPR obligation, DPIA necessity, or authorize processing,
deployment, or release.

[`article-6-legal-basis-evidence-intake-v1.md`](article-6-legal-basis-evidence-intake-v1.md)
defines a fail-closed, qualified-review evidence intake for Article 6
legal-basis candidates and necessity/proportionality facts. It does not select
or validate a legal basis, determine lawfulness, grant authority, authorize
processing, deployment, or release, or enable runtime behavior.

[`article-9-special-category-evidence-intake-v1.md`](article-9-special-category-evidence-intake-v1.md)
defines fail-closed documentation preparation for potential Article 9
conditions, safeguards, and Article 10 controls. It does not validate an intake,
perform qualified review, or
determine applicability, lawfulness, a condition, authority, processing,
deployment, release, or runtime behavior.

[`legitimate-interest-assessment-evidence-intake-v1.md`](legitimate-interest-assessment-evidence-intake-v1.md)
defines fail-closed documentation preparation for a possible Article 6(1)(f)
assessment. It does not validate an intake, perform qualified review, conclude a legitimate interest, balancing,
lawfulness, authority, processing, deployment, release, or runtime behavior.

[`consent-evidence-intake-v1.md`](consent-evidence-intake-v1.md) defines a
fail-closed documentation preparation for possible consent evidence. It does
not validate an intake, perform qualified review, determine consent validity,
lawfulness, authority, processing, deployment,
release, or runtime behavior.

[`compliance-raci-assessment-v1.md`](compliance-raci-assessment-v1.md) defines
a fail-closed input template for qualified deployment-specific responsibility,
approval-authority, independence, and escalation review. It does not assign a
real role, grant authority, approve a release, or enable runtime operation.

[`gpai-provider-obligation-applicability-v1.md`](gpai-provider-obligation-applicability-v1.md)
defines a fail-closed evidence input for qualified review of concrete GPAI
distribution, modification, branding, or fine-tuning facts. It does not assign
provider status, determine an obligation, make a legal conclusion, or authorize
deployment, release, authority, model activation, or runtime operation.

The contract requires task branches under `codex/`, Conventional Commit
headers, pull-request review, blocking quality checks, CODEOWNERS review, and
additional independence evidence for memory separation-of-duties-sensitive
changes.
Unknown or unverifiable governance state fails closed.

Global Codex skills invoked in this repository must first load the local
[`repository-agent-context.md`](repository-agent-context.md). That context
anchor binds reusable global procedures to Neural Brain's repository-specific
architecture, source profile, role coverage, review rules, and governance
gates.

Engineering source governance is defined in
[`engineering-source-governance.md`](engineering-source-governance.md). It sets
the source-governance boundary for development, review, maintenance, operations,
and governance agents. Its machine-readable repository source profile is
[`engineering-source-profile.json`](engineering-source-profile.json). This
governance is an engineering work aid only; it does not create product runtime
retrieval, web search, crawling, RAG, product knowledge stores, or automatic ADR
changes.
Modernization-only source insights that do not prove a current repository defect
or risk remain in the controlled
[`future-considerations-register.md`](future-considerations-register.md).
Individual external source records belong in
[`engineering-source-registry.md`](engineering-source-registry.md). Their
machine-readable records are maintained in
[`engineering-source-records.json`](engineering-source-records.json) and must
validate against
[`engineering-source-registry.schema.json`](engineering-source-registry.schema.json).
Source profile validations, conflicts, approvals, rejections, and supersession
decisions belong in
[`source-governance-audit-records.md`](source-governance-audit-records.md).
Potential architecture implications from external sources belong in
[`architecture-evolution-register.md`](architecture-evolution-register.md) until
the authorized ADR process accepts a change.

`@KonstantinData` and `@KonstantinCondata` are the declared code owners. Each
account must retain accepted repository write access. A pending invitation or
read-only access does not establish CODEOWNER eligibility. For any change, the
approval must come from an eligible owner who is distinct from the author and
latest pusher.

## External enforcement boundary

Repository files define the desired state; GitHub enforces it externally. The
current `main` branch protection was configured and verified against this
contract. The sanitized proof, evidence digest, and mandatory re-verification
conditions are recorded in
[`github-settings-evidence.md`](github-settings-evidence.md). Any unknown or
drifted live setting is a fail-closed merge condition.

Changes to this directory are themselves separation-of-duties-sensitive and
require the review defined by the policy. The policy protects Brain-owned memory
boundaries; it does not assign goals, planning, tool execution, or autonomous
behavior to Neural Brain.
