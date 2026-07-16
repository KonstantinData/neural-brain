# Contributing to Neural Brain

Neural Brain is a product- and domain-neutral, safety-constrained integrated
cognitive system. Its current implementation is an early Memory Core
foundation; target cognitive capabilities are not implemented merely because
they are documented.

Read `AGENTS.md`, Architecture Directive v4.0, relevant ADRs, the active Notion
task, dependencies, and open issues before changing the repository.

## Delivery contract

1. Create a `codex/` task branch from the accepted base.
2. Preserve unrelated changes and classify every worktree and open PR that
   affects the task.
3. Use Conventional Commits.
4. Deliver only through a reviewed pull request; never push directly to `main`.
5. Link objective code, test, evaluation, migration, and documentation evidence.
6. Resolve review conversations, obtain independent approval covering the
   latest push, and pass every required check before merge.
7. Never bypass a required check, release stop, authority gate, or review.

The machine-readable repository policy is
[`docs/governance/repository-policy.json`](docs/governance/repository-policy.json).
Live GitHub protection is an external enforcement dependency documented in
[`docs/governance/github-settings-evidence.md`](docs/governance/github-settings-evidence.md).

## Review independence

Architecture, ADR, governance, migration, security, policy, cognitive-cycle,
goal, action, memory, model-promotion, evaluation, tooling, and workflow changes
are sensitive. They require an approving CODEOWNER distinct from the author and
latest pusher.

The independent reviewer must not accept evidence they implemented as the sole
basis for approval. Requester, approver, executor, verifier, policy author,
policy activator, learning-candidate producer, risky-candidate promoter, and
safety supervisor boundaries must remain intact.

## Quality and evidence

Run formatter, linter, strict typing, type-exception audit, dependency-lock
verification, contract validation, migration checks, and the full test suite.

Add positive, negative, scope, actor/authority, provenance, audit, privacy,
failure, concurrency, crash, and recovery evidence in proportion to the change.
Cognitive claims also require a preregistered baseline, held-out test,
meaningful effect threshold, ablation, transfer, robustness, calibration, and
end-to-end behavior. Learning claims additionally require retention, forgetting,
promotion, canary, rollback, poisoning, and resource-budget evidence.

A passing command proves only that check. It does not by itself prove a
cognitive capability, protected transition, safe external effect, learning
promotion, or release is acceptable.
