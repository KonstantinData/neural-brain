# Architecture Decision Records

This directory contains accepted, versioned architecture decision records.

Each record captures its status, context, decision, consequences, and links to
the affected contracts. Discussion alone does not authorize an ADR or an
implementation change.

## Accepted records

| ADR | Decision |
| --- | --- |
| [ADR-001](ADR-001-product-neutral-platform-boundary.md) | Product-neutral platform boundary |
| [ADR-002](ADR-002-immutable-scope-on-persistent-objects.md) | Immutable scope on persistent objects |
| [ADR-003](ADR-003-postgresql-authoritative-transactional-ledger.md) | PostgreSQL authoritative transactional ledger |
| [ADR-004](ADR-004-transition-gates-own-protected-state.md) | Transition gates own protected state |
| [ADR-005](ADR-005-hard-security-floor-and-bounded-policy.md) | Hard Security Floor and bounded policy |
| [ADR-006](ADR-006-hierarchical-kill-switch.md) | Hierarchical kill switch |
| [ADR-007](ADR-007-normative-goal-and-action-state-machines.md) | Normative Goal and Action state machines |
| [ADR-008](ADR-008-atomic-action-preparation-and-commit.md) | Atomic action preparation and commit |
| [ADR-009](ADR-009-stage-1-dispatch-journal.md) | Stage 1 dispatch journal |
| [ADR-010](ADR-010-staged-memory-capabilities.md) | Staged memory capabilities |
| [ADR-011](ADR-011-independent-verification-completion-gate.md) | Independent verification completion gate |
| [ADR-012](ADR-012-retention-aware-evidence-immutability.md) | Retention-aware evidence immutability |
| [ADR-013](ADR-013-python-runtime-and-toolchain.md) | Python runtime and toolchain |

The repository currently contains thirteen accepted records. FND-02.7 remains
blocked because its acceptance criterion states twelve; the repository does not
silently discard or renumber an accepted decision to satisfy that mismatch.
