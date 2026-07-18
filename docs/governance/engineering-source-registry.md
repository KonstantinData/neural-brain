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

No individual source records are active yet.
