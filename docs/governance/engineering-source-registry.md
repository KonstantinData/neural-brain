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

## Source Record Template

Each source record must contain:

- Source identifier:
- Title:
- Issuing organization:
- Canonical document reference:
- Source class:
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

## Lifecycle States

Each source record has exactly one lifecycle state:

- `normative`
- `approved`
- `draft`
- `watch_only`
- `deprecated`
- `withdrawn`
- `rejected`

Draft and watch-only sources may inform monitoring and future considerations.
They do not establish mandatory review findings or implementation work.

## Current Source Records

No individual source records are active yet.
