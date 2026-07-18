# Engineering Source Registry

- Status: Controlled registry
- Scope: Individual external engineering source records used by the Neural Brain
  repository engineering source profile
- Out of scope: Repository evidence, product runtime sources, product knowledge,
  product data, runtime retrieval, crawling, web search, or RAG

## Purpose

This registry contains the individual source records used by
[`engineering-source-profile.json`](engineering-source-profile.json). It is the
place where external engineering evidence becomes auditable enough for
development, review, maintenance, operations, and governance use.

Repository-local code, tests, ADRs, contracts, commits, pull requests, CI
results, release artifacts, and generated runtime artifacts do not belong in
this registry.

Every registry record must validate against the versioned JSON Schema
[`engineering-source-registry.schema.json`](engineering-source-registry.schema.json)
before activation or source-profile reference.

The active machine-readable record collection is
[`engineering-source-records.json`](engineering-source-records.json). Each item
in that collection is an individual Source Record and must validate against the
record schema before it may be referenced by the active profile.

## Source Record Template

Each source record must contain:

- Source identifier:
- Lifecycle state:
- Title:
- Issuing organization:
- Canonical document reference:
- Source class:
- External publication status:
- Internal registry status:
- Permitted evidence use:
- Document or specification version:
- Publication status:
- Publication date:
- Retrieval date:
- Content hash or immutable snapshot reference:
- Applicable technology and version range:
- Repository-scope mapping:
- Relevant sections or claims:
- Source authority assessment:
- Freshness status:
- Conflict status:
- Validator:
- Approval status:
- Superseded sources:
- Superseding sources:
- Next review trigger or review date:
- Claims:

Each claim must contain:

- Claim ID:
- Section or fragment reference:
- Summarized external statement:
- Applicable technology and version:
- Permitted evidence use:
- Known limitations:

## Status Dimensions

Each source record separates three independent status dimensions:

- `external_publication_status`: `draft`, `final`, `superseded`, or `withdrawn`
- `internal_registry_status`: `proposed`, `approved`, `rejected`, or
  `deprecated`
- `permitted_evidence_use`: `normative`, `supporting`, `watch_only`, or
  `prohibited`

External publication status never creates internal approval. Draft and
watch-only records may inform monitoring and future considerations only. They do
not establish mandatory review findings or implementation work.

## Profile Reference Integrity

The active repository source profile may reference only existing source IDs from
this registry. A normative profile reference requires:

- `internal_registry_status: approved`
- `permitted_evidence_use: normative`
- a current, non-withdrawn source record
- at least one concrete claim ID relevant to the assessment

The profile must not use unknown, `rejected`, `withdrawn`, deprecated-for-current
use, `watch_only`, or `prohibited` records as normative evidence.

## Current Source Records

The initial active source baseline was approved through audit record
`sgaudit-20260718-initial-source-baseline-0001`.

| Source ID | Evidence use | Scope |
| --- | --- | --- |
| `engsrc-python-314-docs-0001` | normative | CPython 3.14 runtime and language behavior |
| `engsrc-uv-docs-0002` | normative | uv dependency and environment workflow |
| `engsrc-ruff-docs-0003` | normative | Ruff formatting and linting |
| `engsrc-mypy-docs-0004` | normative | strict mypy typing |
| `engsrc-pytest-docs-0005` | normative | pytest test execution |
| `engsrc-hypothesis-docs-0006` | normative | property-based testing |
| `engsrc-pydantic-v2-docs-0007` | normative | Pydantic v2 validation boundaries |
| `engsrc-psycopg3-docs-0008` | normative | Psycopg 3 PostgreSQL client behavior |
| `engsrc-postgresql-18-docs-0009` | normative | PostgreSQL 18 ledger, roles, and migrations |
| `engsrc-docker-compose-spec-docs-0010` | normative | Docker Compose file review |
| `engsrc-github-actions-workflow-docs-0011` | normative | GitHub Actions workflows and CI/CD checks |
| `engsrc-github-security-advisories-docs-0012` | supporting | dependency advisory monitoring |
| `engsrc-json-schema-2020-12-0013` | normative | JSON Schema Draft 2020-12 validation |
| `engsrc-owasp-asvs-5-0014` | supporting | application-security verification vocabulary |
