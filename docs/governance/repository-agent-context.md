# Repository Agent Context

## Status and Scope

- **Status:** Repository-local agent context anchor
- **Repository:** `KonstantinData/neural-brain`
- **Work area:** `Neural Brain`
- **Applies to:** Global Codex skills, development agents, review agents,
  specialist agents, judge agents, repository maintainers, architecture
  reviewers, security reviewers, quality engineers, DevOps reviewers, and
  operations reviewers acting inside this repository.
- **Does not apply to:** Product runtime behavior, product user features,
  product data processing, product memory, runtime retrieval, web search,
  source crawling, RAG, or automatic product modernization.

## Purpose

Global Codex skills are reusable procedures. When a global skill is invoked
inside Neural Brain, it must first load this repository-local context and then
apply the global procedure to Neural Brain's local governance, architecture,
source profile, role coverage, review rules, and current repository evidence.

This file is the stable bridge between global skills and repository-specific
governance. It does not define product knowledge and does not authorize a
runtime integration with external sources.

## Mandatory Load Order

Before forming findings, recommendations, source-governance decisions, or PR
review conclusions, global skills invoked in this repository must load:

1. `AGENTS.md`
2. `docs/governance/repository-agent-context.md`
3. `docs/governance/README.md`
4. `docs/governance/engineering-source-profile.json`
5. `docs/governance/engineering-source-records.json`
6. Relevant ADRs, architecture contracts, runbooks, tests, CI evidence, PR
   metadata, PR diff, review comments, and changed files for the task scope

If any mandatory local governance artifact is missing, contradictory, or
unreadable, the agent must fail closed for the affected conclusion and report
the missing evidence instead of inventing repository rules.

## Local Governance Artifacts

- Repository execution and safety contract: `AGENTS.md`
- Repository governance index: `docs/governance/README.md`
- Repository governance policy: `docs/governance/repository-policy.json`
- Engineering source governance: `docs/governance/engineering-source-governance.md`
- Neural Brain source profile: `docs/governance/engineering-source-profile.json`
- Engineering source registry: `docs/governance/engineering-source-registry.md`
- Machine-readable source records:
  `docs/governance/engineering-source-records.json`
- Source record schema:
  `docs/governance/engineering-source-registry.schema.json`
- Source governance audit log:
  `docs/governance/source-governance-audit-records.md`
- Architecture evolution register:
  `docs/governance/architecture-evolution-register.md`
- Future considerations register:
  `docs/governance/future-considerations-register.md`
- GitHub settings evidence:
  `docs/governance/github-settings-evidence.md`

## Global Skills Bound To This Context

- `$engineering-source-governance` governs how development and review agents
  use external engineering sources. It must use this repository's source
  profile and source records when assessing Neural Brain work.
- `$pull-request-specialist-review` governs scope-based PR assessment with
  specialist reviewers, consensus discussion, and judge escalation. It must use
  this repository's architecture, source profile, governance policy, current PR
  evidence, and review gates before selecting specialists or issuing findings.

Additional global skills may be used only within the same boundary: the global
skill defines the reusable method; this repository defines the applicable
scope, evidence, architecture constraints, source profile, role coverage, and
approval requirements.

## Local Precedence

Repository code, tests, migrations, and executable configuration remain the
primary evidence for current implementation state. This `AGENTS.md`, local
governance documents, accepted ADRs, contracts, and test evidence define the
Neural Brain-specific rules that global skills must obey.

If a global skill instruction conflicts with repository-local governance, the
repository-local rule wins for Neural Brain unless an authorized repository
governance or ADR decision explicitly changes it.

## PR Review Application

For Neural Brain pull-request reviews, specialist selection must be derived
from:

- PR scope, changed files, tests, documentation, CI evidence, and review
  comments;
- Neural Brain architecture boundaries and delivery-stage constraints;
- source-profile role coverage and approved evidence use;
- repository governance gates, CODEOWNERS requirements, and release-stop
  conditions.

Specialist findings must distinguish repository evidence from external
engineering evidence and from derived assessment. External-source-backed
findings must reference concrete source-record claim IDs where applicable.

## Boundary Statement

This context anchor supports agents that build, review, maintain, and govern
Neural Brain. It is not a product feature, not a runtime data source, not a
retrieval configuration, and not an implementation mandate. New technical
knowledge may inform assessment or future options, but it does not
automatically change product behavior, dependencies, ADRs, backlog, or release
scope.
