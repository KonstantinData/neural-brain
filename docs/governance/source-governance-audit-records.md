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

No governance audit events have been recorded yet.
