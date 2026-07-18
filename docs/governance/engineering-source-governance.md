# Engineering Source Governance

- Status: Normative repository governance
- Scope: Development, review, maintenance, operations, and governance agents
- Out of scope: Product runtime, user-facing product behavior, product data,
  runtime retrieval, web search, crawling, RAG, or product knowledge stores

## Purpose

Engineering source governance keeps the specialists who build, review, operate,
and maintain Neural Brain aligned with current, authoritative technical
knowledge.

It governs the knowledge basis of development and review work only. It does not
grant Neural Brain product functionality, runtime data access, external
research capability, or a product knowledge base.

The governing principle is:

> External sources keep the engineering organization current. They do not keep
> the product runtime current.

## Mandatory Separation

Three knowledge layers remain separate:

| Layer | Contents | Governed here |
| --- | --- | --- |
| Repository evidence | Code, tests, migrations, configuration, ADRs, contracts, commits, pull requests, release artifacts, and traceability records | No |
| Engineering knowledge base | External technical standards, framework documentation, dependency documentation, security advisories, platform documentation, operations references, and review methodology used by development agents | Yes |
| Product knowledge and product data | Information Neural Brain processes, stores, retrieves, or presents as part of product behavior | No |

Repository evidence remains the durable technical source of truth for what this
repository currently implements or requires. Engineering sources may inform
analysis and future options, but they do not override repository evidence,
accepted ADRs, executable contracts, or tests.

## Governed Agent Roles

This governance applies to every specialist role that contributes to repository
development or validation, including:

- software and system architects
- data engineers
- Python and backend specialists
- security specialists
- test and quality-engineering specialists
- DevOps, CI/CD, observability, and operations specialists
- governance and ADR maintainers
- review, judge, and repository agents

Each role must base repository-specific assertions first on repository evidence
and then use external engineering sources only to validate technical standards,
current library behavior, security posture, operational practice, and review
quality.

## Source Profile Requirement

Every repository must have a source profile that matches its engineering scope.
For Neural Brain, the active profile is
[`engineering-source-profile.json`](engineering-source-profile.json).

A source profile must define:

- repository identity and engineering scope
- governed layer and explicitly excluded product-runtime effects
- allowed source categories for engineering work
- source quality rules such as authority, freshness, version match, and
  conflict handling
- required role-to-source coverage for specialist review
- evidence rules for how agents cite or record source use

## Allowed Engineering Source Classes

Agents may use external engineering sources when they are needed for their
development or review task. Allowed classes include:

- official language, framework, library, database, platform, and tool
  documentation
- standards, specifications, and security baselines from authoritative bodies
- vendor security advisories, changelogs, release notes, and migration guides
- official CI/CD, deployment, observability, and operations documentation
- peer-reviewed or primary research sources when a cognitive, neural, or
  evaluation claim requires scientific grounding
- repository-local evidence from the active checkout, Git history, pull
  requests, CI runs, and versioned artifacts

Secondary sources may support orientation, but they cannot be the only basis for
a normative technical recommendation when a primary source is reasonably
available.

## Quality Rules

Engineering source use must follow these rules:

- Prefer primary and official sources for normative claims.
- Match sources to the repository's pinned versions, configured platform, and
  active delivery stage.
- Treat stale, undated, unofficial, or version-mismatched sources as weak
  evidence unless corroborated by current authoritative evidence.
- Record uncertainty when the source does not prove the exact repository case.
- Do not turn new external knowledge into an ADR, product feature, or runtime
  requirement automatically.
- Route new insights as review findings, implementation options, backlog
  candidates, or ADR proposals according to the repository workflow.
- Keep secrets, credentials, private customer data, and live personal data out
  of source notes, prompts, Notion records, repository docs, and examples.

## Runtime Non-Effects

This governance explicitly does not authorize or require:

- a product web search feature
- a source crawler
- runtime external research
- a product RAG system
- a product knowledge store
- ingestion of engineering sources into product memory
- automatic product changes when an engineering source changes
- automatic ADR changes when an engineering source changes

If an external source reveals a relevant technical improvement, the result is
only an engineering input. It becomes product or architecture work only through
the normal issue, backlog, ADR, implementation, review, and verification path.

## Review Use

For repository review, agents must distinguish:

- what the repository currently proves
- what external engineering sources say about the relevant technology or risk
- whether the repository's implementation matches those sources
- what is unknown, stale, version-mismatched, or unverified
- whether a finding is a defect, a risk, an optional improvement, or an ADR
  candidate

Specialist review must not present external source guidance as implemented
repository behavior unless repository evidence proves it.

## Acceptance

This governance is satisfied when:

- the engineering source basis is outside the product runtime
- no product search, retrieval, crawler, or knowledge-processing feature is
  inferred from it
- sources support development, review, maintenance, operations, and governance
  agents only
- the repository has an engineering source profile matching its scope
- source-profile changes do not automatically mutate product behavior or ADRs
- new technical knowledge is treated first as evaluation input or a future
  option
