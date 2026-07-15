# Contributing to Neural Brain

Neural Brain is a product- and domain-neutral safety-oriented platform. Read
`AGENTS.md`, the architecture directive, relevant ADRs, the active Notion task,
and active issues before changing the repository.

## Delivery contract

1. Create a task branch from current `origin/main`. Its name must match
   `codex/<lowercase-task-name>`.
2. Use Conventional Commit headers such as
   `feat(runtime): add guarded checkpoint resume`.
3. Push the task branch and deliver only through a reviewed pull request.
4. Complete every pull-request template section and link objective evidence.
5. Resolve conversations, obtain approval covering the latest push, and pass
   every required quality check before merge.
6. Never push directly to `main`, bypass required checks, force-push a protected
   branch, or request an unreviewed delivery.

The machine-readable policy is
[`docs/governance/repository-policy.json`](docs/governance/repository-policy.json).
The live GitHub branch protection is an external enforcement dependency. Its
verified state and the required re-verification contract are recorded in
[`docs/governance/github-settings-evidence.md`](docs/governance/github-settings-evidence.md).

## Review independence

Architecture, ADR, governance, migration, security, policy, transition-gate,
executor, verifier, memory, tooling, and workflow changes are sensitive. They
require an approving CODEOWNER who is distinct from the author and latest
pusher, plus explicit evidence that the review preserves the relevant runtime
separation-of-duties boundary. The independent verification reviewer must not
accept evidence they implemented as the sole basis for approval. A policy
author cannot be the sole policy activator. Narrow security exceptions can
require an additional reviewer under their specific runbook.

## Quality and evidence

Run the repository formatter, linter, strict type checker, type-exception
audit, dependency-lock verification, and full test suite. Add positive,
negative, scope, actor/authority, audit, failure, and recovery evidence in
proportion to the affected contract. State explicitly when a check could not
run. A passing tool exit code is evidence of that check only; it is not proof
of goal achievement or release readiness.
