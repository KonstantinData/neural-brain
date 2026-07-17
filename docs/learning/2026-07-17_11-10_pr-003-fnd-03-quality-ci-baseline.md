---
title: "PR #3 - FND-03 Quality and CI Release Gates"
created_at: 2026-07-17T11:10:00+02:00
area: Neural Brain
repository: D:\Git-GitHub\Repositories\condata\neural-brain
task: "Learn PR #3: ci: establish FND-03 quality and release gates"
task_type: per-pr-learning-artifact
domain: CI, release governance, supply-chain safety
difficulty: advanced
estimated_learning_time: 90 minutes
concepts:
  - pinned GitHub Actions
  - CODEOWNERS
  - migration validation
  - release evidence
  - SBOM
  - secret scanning
  - dependency and workflow policy
prerequisites:
  - GitHub Actions basics
  - CI permissions model
  - database migration concepts
  - supply-chain security basics
related_files:
  - .github/CODEOWNERS
  - .github/workflows/quality.yml
  - .github/workflows/migrations.yml
  - .github/workflows/security.yml
  - .github/workflows/release.yml
  - docs/governance/repository-policy.json
  - tools/security_policy.py
  - tools/validate_migrations.py
  - tools/build_release_evidence.py
related_components:
  - FND-03 CI baseline
  - repository governance
  - migration validation
  - release evidence tooling
related_repositories:
  - neural-brain
related_topics:
  - PR #3
  - CI hardening
  - release artifacts
  - independent review
learning_status: new
tags:
  - Projektbasiert
  - Fortgeschritten
notion_tracker_url: https://app.notion.com/p/3a01c1ac5ec0819ab073d10115ca0c95
---

# PR #3 - FND-03 Quality and CI Release Gates

## 1. Task Summary

PR #3 established the engineering quality and CI baseline. It added CODEOWNERS, PR template, workflow policy, pinned CI workflows, migration validation, security scanning, dependency checks, release evidence tooling, and governance tests.

The learning goal is to understand how CI becomes part of a protected system's safety argument.

Source PR: https://github.com/KonstantinData/neural-brain/pull/3

## 2. Context

After FND-01 and FND-02, the repository had local quality and architecture contracts. FND-03 moved that discipline into repeatable CI and release evidence. This matters because a local check is not enough for a reviewable repository.

## 3. Approach

The PR introduced separate workflows for quality, migrations, security, and release evidence. It also added repository policy checks for workflow pinning, permissions, and dependency/license constraints.

Migration validation used guarded disposable databases, and release tooling produced deterministic evidence and SBOM outputs.

## 4. Key Decisions

One decision was to require pinned GitHub Action references and least-privilege workflow permissions. The rejected alternative was convenient but mutable action references.

Another decision was to require independent CODEOWNER review for sensitive changes. This supports separation of duties.

Migration validation became a release gate even before production migrations existed, because future database authority depends on trustworthy migration discipline.

## 5. Concepts and Methods

CI is not only automation; it is a policy enforcement surface. In this repo it checks formatting, linting, typing, tests, secrets, dependencies, licenses, workflow safety, migrations, and release evidence.

An SBOM records software components. It helps review dependency provenance and release contents.

CODEOWNERS formalizes review responsibility.

## 6. Knowledge Prerequisites and Gaps

You should understand GitHub Actions, permissions, pinned actions, secret scanning, and migration validation. A useful gap is learning how supply-chain policy can be tested without becoming manual checklist work.

## 7. Learning Path

```text
CI safety baseline
|-- Quality workflow
|-- Migration workflow
|-- Security workflow
|-- Release evidence workflow
`-- Repository policy tests
```

## 8. Practical Examples

Read `tools/security_policy.py` with `tests/foundation/test_security_policy.py`. This pair shows how workflow and dependency rules are enforced by code.

Read `tools/validate_migrations.py` to understand fresh versus upgrade schema validation.

## 9. Exercises

### Beginner

- Objective: Identify each CI workflow and its responsibility.
- Expected result: A table with four rows.
- Hints: Look in `.github/workflows`.
- Validation criteria: You can say which workflow catches which class of risk.

### Intermediate

- Objective: Explain why action pinning matters.
- Expected result: A short risk explanation.
- Hints: Compare immutable commits with moving tags.
- Validation criteria: You mention supply-chain drift.

### Advanced

- Objective: Design a new release evidence check.
- Expected result: Tool output, test, and workflow placement.
- Hints: Follow `build_release_evidence.py`.
- Validation criteria: Evidence is deterministic and reviewable.

## 10. Reflection Questions

1. Why does CI need security policy tests?
2. What is the difference between local quality and CI quality?
3. Why require CODEOWNER review?
4. How do migration checks protect future runtime state?
5. What evidence should a release produce?

## 11. Common Mistakes and Risks

The biggest mistake is treating CI as a convenience layer. Here it is part of the control plane for repository delivery.

Another risk is trusting GitHub Actions defaults. Permissions and action refs must be explicit.

## 12. Key Takeaways

1. CI can enforce architecture and security policy.
2. Workflow pinning reduces supply-chain drift.
3. Release evidence should be deterministic.
4. Migration validation belongs before production data exists.
5. Independent review is a technical control, not only a social process.

## 13. Area and Repository Context

This PR is still Foundation. It does not introduce Stage 1 runtime behavior, but it creates the review and release structure needed before runtime can be trusted.

Related Notion tracker entry: https://app.notion.com/p/3a01c1ac5ec0819ab073d10115ca0c95

## 14. Related Themes

### Supply-Chain Security

- Relationship: Pinned dependencies and workflows reduce mutable upstream risk.
- Type: Security engineering.
- Learning value: Makes dependency trust explicit.

### Release Governance

- Relationship: Release artifacts and SBOM support review.
- Type: DevOps.
- Learning value: Turns release into evidence.

### Separation of Duties

- Relationship: CODEOWNERS and review gates prevent sole-author delivery.
- Type: Governance.
- Learning value: Protects sensitive changes.

## 15. Further Learning Resources

- `.github/workflows/`
- `docs/runbooks/release-artifacts.md`
- `docs/runbooks/security-scanning.md`
- `tools/security_policy.py`

