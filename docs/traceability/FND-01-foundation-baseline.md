# FND-01 Foundation Baseline Evidence

- Task ID: `FND-01`
- Source PR: <https://github.com/KonstantinData/neural-brain/pull/1>
- Source PR title: `chore(foundation): establish FND-01 repository baseline`
- Base commit: `7218755`
- Merge commit: `3482d1fe20cb0b12badfdb67c58ed84e4ecac264`
- Merged at: `2026-07-15T07:03:43Z`
- Evidence status: historical Foundation evidence with remediation follow-up
- Remediation issue: `Remediate PR01 Foundation review findings`

## Scope

PR #1 established the first repository-local Foundation baseline:

- repository governance and product-neutral scope orientation;
- CPython 3.14, uv, Ruff, mypy, pytest, and type-exception audit policy;
- isolated local PostgreSQL development and test services;
- fail-closed disposable test-data reset checks;
- ADR-013 and initial traceability/runbook scaffolding.

FND-01 did not implement Memory Core behavior, NB-1 cognition, CI workflows,
release evidence, production deployment, or an external-effect surface.

## Historical Verification Recorded in PR #1

The PR body records these local verification results:

| Command or check | Recorded result |
| --- | --- |
| `uv lock --check` | passed |
| `uv sync --locked` | passed |
| Ruff format and lint | passed |
| `mypy --strict` | passed |
| controlled type-exception audit | passed with 0 findings |
| pytest | passed, 13 tests |
| unsafe reset negative tests | blocked before `volume rm` |
| PowerShell parser validation for `tools/dev.ps1` | passed |
| PostgreSQL 18.4 dev/test smoke | passed |
| explicit transaction commit and rollback probes | passed |
| reset isolation marker test | development marker preserved, test marker removed |
| local credential ACL | owner-only, inheritance disabled |
| `git diff --check` | passed |

These results were recorded in GitHub PR text. They were not originally stored
as a versioned traceability artifact in the repository.

## Specialist Review Findings

The PR01 specialist review on `2026-07-18` found that FND-01 was useful as a
Foundation start, but not sufficient as a fully reliable baseline without
remediation:

- `typing.cast` aliases could bypass the type-exception audit.
- Early hierarchy wording could be read as making Goal a scope dimension.
- Local Docker project and volume names were not checkout-isolated.
- `reset-test` could stop and remove the test container before proving volume
  ownership.
- PostgreSQL smoke verification used `SELECT 1` rather than real write
  commit/rollback probes.
- Local PostgreSQL app/test roles were created through the image bootstrap user
  path and could be superuser-like.
- CI baseline claims were not backed by a PR01 workflow.
- Verification evidence lived in PR text rather than a versioned repository
  evidence file.

## Remediation Mapping

| Finding | Remediation expectation |
| --- | --- |
| Type-exception alias bypass | Track cast aliases through assignment and add regression tests. |
| Goal as scope ambiguity | Keep catalog hierarchy at Brain to Session; document Goal as a session-bound protected aggregate. |
| Shared local Docker volumes | Derive Compose project and volume names from the local repository path. |
| Reset preflight gap | Prove test-volume ownership before any `compose stop`, `compose rm`, or `volume rm`. |
| Weak transaction smoke | Use temporary writes to prove commit persistence and rollback absence. |
| Superuser app/test roles | Bootstrap separate non-superuser scope roles for local dev/test access. |
| CI gap | Keep pinned locked quality workflow as the executable CI gate. |
| Missing versioned evidence | Keep this file as the FND-01 evidence record and update it when remediation lands. |

## Current Claim Boundary

Passing FND-01 and its remediation proves only the repository Foundation
controls named above. It does not release NB-1, validate neural cognition,
promote a model, authorize external effects, prove production readiness, or
permit the `Neural Brain Candidate` label.
