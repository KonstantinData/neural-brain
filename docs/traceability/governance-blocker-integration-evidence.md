# Governance Blocker Integration Evidence

## Scope

- Controller issue: https://app.notion.com/p/3a91c1ac5ec081ef91a4cd2fab4c04c7
- Branch: `codex/backlog-controller-wave-1`
- Commit: pending verified local commit
- Delivery boundary: repository-side preparation only; no Runtime component,
  real data access, hidden evaluation, role appointment, key, signature,
  release, or recognition claim.

## Package mapping

| Package | Dependencies | Durable contracts and evidence | Independent review result | External blocker |
| --- | --- | --- | --- | --- |
| EVAL-01 preparation | ADR-018, v4 preregistration, hidden-evaluation contract | Preparation, manifests, organization, candidate-freeze lifecycle, governance, runbooks, tests, and traceability | Approved after v4 custody and canonical-byte-vector remediation | Independent evaluator/reviewer/registry appointment, accepted public v4 freeze receipt, hidden commitment, independent run, signed aggregate, admissibility review |
| S1-02.5 | ADR-005, ADR-006 historical, ADR-018, ADR-019, Action Gate | Non-authorizing proposal, target contract, scope-decision options, preregistered test plan, governance, runbook, tests, and traceability | Approved after complete transition and stale-checkpoint evidence remediation | Accepted successor ADR, Security/Safety review, recovery owner, future NB-5 sandbox evidence |
| S1-14.9 / S1-11.1 | ADR-018, privacy evidence contracts, future deployment facts | Category-only 19-class inventory, eleven readiness matrices, review checklist, Project-scope catalogue remediation, runbook, tests, and traceability | Approved after eleven-matrix traceability correction | Deployment-specific immutable facts and qualified privacy review; accepted runtime/control/release contracts before any real operation |

## Integrated verification

- `python -m json.tool` for every newly added or changed machine-readable
  governance contract: passed.
- `python tools/validate_adrs.py`: passed.
- `uv run ruff format --check .`: 320 files already formatted.
- `uv run ruff check .`: passed.
- `uv run mypy`: passed, 169 source files.
- `uv run pytest -q`: 699 passed, 56 skipped because `MIGRATION_ADMIN_DSN` is
  unavailable for live PostgreSQL tests.
- `git diff --check`: passed before local commit.

## Review mapping

Three independent read-only reviews were completed: EVAL-01 architecture and
governance; S1-02.5 security architecture; and S1-14.9 privacy plus
traceability. All initially identified findings were repaired and re-reviewed.
The reviews are evidence about repository preparation only. They do not appoint
roles, accept an ADR, authorize a runtime, establish data-processing facts, or
prove independent evaluation.

## Requirement-to-test catalog disposition

`requirement-to-test-catalog-v1.json` remains unchanged: N/A for these
preparation-only target contracts because its accepted scope is bounded to
current release-stop and Memory Core transition mappings. Extending it requires
a separate authorized scope decision.
