---
title: "PR #1 - FND-01 Repository Governance Baseline"
created_at: 2026-07-17T11:00:00+02:00
area: Neural Brain
repository: D:\Git-GitHub\Repositories\condata\neural-brain
task: "Learn PR #1: chore(foundation): establish FND-01 repository baseline"
task_type: per-pr-learning-artifact
domain: Repository foundation, governance, reproducible development
difficulty: intermediate
estimated_learning_time: 75 minutes
concepts:
  - repository governance
  - locked Python toolchain
  - strict quality baseline
  - local PostgreSQL development environment
  - fail-closed destructive-operation guards
prerequisites:
  - basic Git and pull request workflow
  - Python package management with uv
  - pytest and mypy basics
  - PostgreSQL development basics
related_files:
  - AGENTS.md
  - README.md
  - pyproject.toml
  - uv.lock
  - compose.yaml
  - docs/adr/ADR-013-python-runtime-and-toolchain.md
  - docs/runbooks/local-development.md
  - tools/dev.ps1
  - tools/quality.py
  - tests/foundation/test_reset_fail_closed.py
related_components:
  - FND-01 repository baseline
  - local development environment
  - quality toolchain
related_repositories:
  - neural-brain
related_topics:
  - PR #1
  - ADR-013
  - CPython 3.14
  - uv
  - PostgreSQL 18
learning_status: new
tags:
  - Projektbasiert
  - Fortgeschritten
notion_tracker_url: https://app.notion.com/p/3a01c1ac5ec08177bb15cfb5ac959d2b
---

# PR #1 - FND-01 Repository Governance Baseline

## 1. Task Summary

PR #1 established the repository foundation before Neural Brain implemented any cognitive capability. It added governance instructions, a truthful README, ADR-013 for runtime and tooling, a locked Python environment, local PostgreSQL dev/test infrastructure, and fail-closed reset tests.

The learning goal is to understand why a high-risk AI architecture repo starts with reproducibility, safety rails, and traceability rather than feature code.

Source PR: https://github.com/KonstantinData/neural-brain/pull/1

## 2. Context

At this point Neural Brain needed a reliable engineering base. Without pinned tooling, typed boundaries, local database isolation, and destructive-operation guards, later claims about protected memory or cognitive safety would rest on weak process.

The PR was deliberately scoped to FND-01. FND-02 architecture contracts and FND-03 CI were not mixed into it.

## 3. Approach

The approach was to make the repository executable and governable:

- define repository rules in `AGENTS.md`;
- document maturity and non-goals in `README.md`;
- accept ADR-013 for CPython, uv, strict typing, Pydantic, Psycopg, and explicit transactions;
- add a local PostgreSQL setup through `compose.yaml` and `tools/dev.ps1`;
- centralize quality checks in `tools/quality.py`;
- test reset guards against unsafe database names, labels, and Docker volume failures.

## 4. Key Decisions

The key decision was to treat the repository as a governed product artifact. The alternative was to start implementing memory or cognition first and backfill governance later. That would have hidden foundational risk.

Another decision was to make local destructive operations fail closed. Reset tooling had to prove it was targeting disposable test data before removing anything.

## 5. Concepts and Methods

Repository governance means the repo defines how agents and humans must work: language, branch hygiene, source precedence, verification, and safety boundaries.

Locked tooling means the same Python, dependencies, and quality checks can be reproduced by future work.

Fail-closed reset design means an ambiguous or partially failed reset stops before deletion rather than guessing.

## 6. Knowledge Prerequisites and Gaps

You should know how `pyproject.toml`, `uv.lock`, pytest, Ruff, and mypy work together. You should also understand why local databases need isolated names, labels, and disposable volume handling.

A useful gap to study is how to design operational scripts so that every destructive branch has a preceding proof step.

## 7. Learning Path

```text
Repository foundation
|-- Governance rules
|-- Locked runtime and dependencies
|-- Quality command
|-- Local database setup
`-- Fail-closed reset safety
```

## 8. Practical Examples

Read `tools/dev.ps1` together with `tests/foundation/test_reset_fail_closed.py`. The important pattern is not the PowerShell syntax; it is the sequence of validation before reset.

Read ADR-013 to see how a tooling decision becomes durable technical authority instead of an informal preference.

## 9. Exercises

### Beginner

- Objective: List every FND-01 file that makes the repo reproducible.
- Expected result: A short map from file to responsibility.
- Hints: Start with `pyproject.toml`, `uv.lock`, `tools/quality.py`, and `compose.yaml`.
- Validation criteria: You can explain why each file matters before any feature work.

### Intermediate

- Objective: Explain the fail-closed reset tests.
- Expected result: A paragraph for each negative reset case.
- Hints: Focus on what condition stops deletion.
- Validation criteria: You do not describe Docker success as sufficient safety.

### Advanced

- Objective: Draft a new dangerous dev command and its preconditions.
- Expected result: A guarded command contract with positive and negative tests.
- Hints: Use the reset pattern as the template.
- Validation criteria: Ambiguous target identity stops before mutation.

## 10. Reflection Questions

1. Why is governance useful before feature implementation?
2. What would make a local reset command unsafe?
3. Why should tooling choices be captured in an ADR?
4. Which checks belong in one locked quality command?
5. What does this PR intentionally not implement?

## 11. Common Mistakes and Risks

The main mistake is treating setup work as low value. In this repo, setup is part of the safety argument.

Another risk is making reset scripts convenient but under-validated. Convenience without proof can destroy real state.

## 12. Key Takeaways

1. Safe projects start with reproducible foundations.
2. Tooling decisions need durable rationale.
3. Destructive operations must prove target identity first.
4. FND-01 is about readiness, not product capability.
5. Good scope control makes later PRs easier to review.

## 13. Area and Repository Context

This belongs to Neural Brain's foundation stage. It does not add Memory Core, Dreaming, or cognition. It creates the baseline needed to trust later architecture and implementation work.

Related Notion tracker entry: https://app.notion.com/p/3a01c1ac5ec08177bb15cfb5ac959d2b

## 14. Related Themes

### Engineering Governance

- Relationship: Defines how future work is allowed to proceed.
- Type: Process and repository architecture.
- Learning value: Shows why rules are implementation prerequisites.

### Reproducibility

- Relationship: Pinned runtime and lockfile support repeatable validation.
- Type: Tooling.
- Learning value: Prevents environment drift from becoming hidden risk.

### Operational Safety

- Relationship: Reset guards protect local database state.
- Type: Reliability and safety.
- Learning value: Teaches fail-closed command design.

## 15. Further Learning Resources

- `docs/adr/ADR-013-python-runtime-and-toolchain.md`
- `docs/runbooks/local-development.md`
- `tools/dev.ps1`
- `tests/foundation/test_reset_fail_closed.py`

