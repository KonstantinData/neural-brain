# FND-ENT-02: Goal Gate ADR-018 Revalidation

## Implementation Evidence

- Task ID: `FND-ENT-02`
- Task URL: https://app.notion.com/3a91c1ac5ec08128853efdedc6ce8b9b
- Proposed decision record: https://app.notion.com/p/3a91c1ac5ec08181b9f5ff70fa48eac7
- Objective: Classify the historical Goal Gate ADRs against the current
  complete-system architecture and provide an exact, fail-closed replacement
  proposal without claiming its acceptance or enabling runtime.
- Dependencies: `FND-ENT-01`; ADR-004, ADR-007, ADR-011; ADR-018; ADR-019;
  Architecture Directive v4.0; Neural Brain Recognition Standard.
- Branch: `codex/fnd-ent-02-goal-gate-adr-revalidation`
- Commit: working tree; no commit yet
- Pull request: not created

## Acceptance Evidence

- [x] ADR-004, ADR-007, and ADR-011 are each classified as explicitly
  superseded historical evidence; none is accepted as-is.
- [x] The versioned proposal fixes the Goal aggregate as session-bound and
  separately records immutable authenticated scope, identity/lineage, evidence,
  and sole-writer rules.
- [x] The proposal requires independent Gate resolution of scope, principal,
  authority, policy, approval, evidence, and state facts; untrusted input
  cannot alter them and unknown facts deny.
- [x] NB-1 permits only internal proposals and explicitly excludes protected
  Goal lifecycle runtime, migration, `Achieved`, action, effects, approval,
  budget, resource, fence, kill-switch, and verification capability.
- [x] Required future state, transition, separation, audit, recovery,
  concurrency, and positive/negative test evidence is enumerated.
- [x] An exact authorized-acceptance blocker, owner, and unblock condition are
  recorded instead of treating a proposal as an accepted ADR.

## Changed Artifacts

- `docs/architecture/goal-gate-adr-018-revalidation-proposal-v1.md`: versioned
  proposed replacement and stage boundary.
- `tests/architecture/test_goal_gate_adr_018_revalidation_proposal.py`:
  deterministic documentation validation.
- `docs/architecture/README.md` and `docs/traceability/README.md`: discovery
  links and non-authorization boundary.
- Migrations: none. No Goal runtime, protected table, database function, or
  privilege change is added.

## Verification

- `python tools/validate_adrs.py`: passed.
- `uv run pytest -q tests/architecture/test_goal_gate_adr_018_revalidation_proposal.py tests/architecture/test_accepted_adrs.py`: passed, 45 tests.
- `uv run mypy tests/architecture/test_goal_gate_adr_018_revalidation_proposal.py`: passed.
- `ruff check .`: passed.
- `ruff format --check .`: passed, 136 files already formatted.
- `uv run pytest -q`: passed, 579 tests; 56 PostgreSQL live tests skipped only
  because `MIGRATION_ADMIN_DSN` is not configured in this local environment.

## Security and Documentation Impact

The proposal strengthens traceability and default-deny architecture only. It
does not create protected state, authority, policy activation, external effect,
release decision, or product runtime. The remaining blocker is an authorized
acceptance of this proposal or an authorized alternative decision.
