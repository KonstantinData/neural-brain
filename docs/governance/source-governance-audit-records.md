# Source Governance Audit Records

- Status: Controlled audit log
- Scope: Source-profile validations, proposed changes, approvals, rejections,
  conflicts, and supersession decisions
- Out of scope: Product runtime audit, product data audit, CI logs, or release
  evidence

## Purpose

This file records governance events for the engineering source profile and
source registry. It does not replace Git history, pull-request review, CI
evidence, ADR records, or Notion task lifecycle tracking.

The audit log is append-only. Existing audit records must not be edited or
deleted. Corrections, reversals, and supersessions are recorded as new audit
records that explicitly reference the earlier record through `corrects` or
`supersedes`.

## Audit Record Template

Each audit record must contain:

- Record identifier:
- Timestamp:
- Actor:
- Governance trigger:
- Affected repository scope:
- Affected source IDs:
- Previous registry version:
- Proposed registry version:
- Previous profile version:
- Proposed profile version:
- Structured change set:
- Previous source state:
- Proposed source state:
- Source lifecycle changes:
- Affected specialist roles:
- Expected assessment impact:
- Security considerations:
- Unresolved conflicts:
- Recommendation:
- Decision rationale:
- Approver or Governance Judge:
- Decision:
- Activation date:
- Superseded audit record:
- Corrected audit record:
- Evidence references:

Every audit record must preserve enough information to reconstruct the valid
source registry and source profile state before and after the decision.

## Recorded Audit Events

### sgaudit-20260718-initial-source-baseline-0001

- Record identifier: `sgaudit-20260718-initial-source-baseline-0001`
- Timestamp: `2026-07-18T12:37:05+02:00`
- Actor: `Codex acting on explicit repository-owner instruction`
- Governance trigger: `repository_onboarding` and `explicit_governance_request`
- Affected repository scope: Neural Brain development, review, maintenance,
  operations, CI/CD, security, governance, and repository-agent work
- Affected source IDs:
  - `engsrc-python-314-docs-0001`
  - `engsrc-uv-docs-0002`
  - `engsrc-ruff-docs-0003`
  - `engsrc-mypy-docs-0004`
  - `engsrc-pytest-docs-0005`
  - `engsrc-hypothesis-docs-0006`
  - `engsrc-pydantic-v2-docs-0007`
  - `engsrc-psycopg3-docs-0008`
  - `engsrc-postgresql-18-docs-0009`
  - `engsrc-docker-compose-spec-docs-0010`
  - `engsrc-github-actions-workflow-docs-0011`
  - `engsrc-github-security-advisories-docs-0012`
  - `engsrc-json-schema-2020-12-0013`
  - `engsrc-owasp-asvs-5-0014`
- Previous registry version: no active individual source records
- Proposed registry version: `docs/governance/engineering-source-records.json`
  with 14 schema-valid records
- Previous profile version: `contract_version: 1.3.0` with no active concrete
  source references
- Proposed profile version: `contract_version: 1.3.0` with
  `active_source_references` bound to the initial source record collection
- Structured change set:
  - add the initial machine-readable Engineering Source Record collection
  - bind concrete claim IDs to the active repository Source Profile
  - list active records in the controlled Source Registry
  - add automated schema and profile-reference integrity validation
- Previous source state: source classes and integrity rules existed, but no
  concrete Source Records were active
- Proposed source state: official and authoritative sources for the declared
  repository toolchain and governance schema are internally approved for their
  permitted evidence uses
- Source lifecycle changes: 14 records move from absent to `approved`
- Affected specialist roles: software/system architecture, data engineering,
  Python/backend, security, test/quality engineering, DevOps/CI/CD,
  observability/operations, governance/ADR, review/judge/repository agents
- Expected assessment impact: pull-request reviewers can cite concrete Source
  IDs and Claim IDs instead of broad source classes or model memory
- Security considerations: all external content remains untrusted input and
  cannot authorize repository writes, product behavior, ADR changes, tool calls,
  or scope expansion
- Unresolved conflicts: none identified at activation
- Recommendation: activate the initial baseline and revalidate on dependency,
  runtime, platform, security-advisory, schema, or quarterly review triggers
- Decision rationale: the selected sources match the repository-declared
  runtime, database, tooling, CI/CD, schema, and security review surfaces and
  remain outside product runtime
- Approver or Governance Judge: repository owner instruction in this task;
  CODEOWNER review remains required before merge
- Decision: approved for PR review and repository governance merge review
- Activation date: pending merge of the pull request carrying this audit record
- Superseded audit record: none
- Corrected audit record: none
- Evidence references:
  - `docs/governance/engineering-source-profile.json`
  - `docs/governance/engineering-source-records.json`
  - `docs/governance/engineering-source-registry.schema.json`
  - `tests/governance/test_engineering_source_governance.py`
