# Architecture Decision Records

This directory contains versioned architecture decision records. Superseded
records remain in place as historical evidence but are not current
implementation authority.

Each record captures its status, context, decision, consequences, and links to
the affected contracts. Discussion alone does not authorize an ADR or an
implementation change.

## Decision records

| ADR | Status | Decision |
| --- | --- | --- |
| [ADR-001](ADR-001-product-neutral-platform-boundary.md) | Accepted, amended by ADR-018 | Product-neutral complete cognitive-system boundary |
| [ADR-002](ADR-002-immutable-scope-on-persistent-objects.md) | Accepted, amended by ADR-015 and ADR-016 | Immutable operational memory scope and typed catalog lineage |
| [ADR-003](ADR-003-postgresql-authoritative-transactional-ledger.md) | Accepted, amended by ADR-018 | PostgreSQL authoritative protected-state ledger |
| [ADR-004](ADR-004-transition-gates-own-protected-state.md) | Superseded by ADR-015 | Historical Goal, Action, and Memory gate decision |
| [ADR-005](ADR-005-hard-security-floor-and-bounded-policy.md) | Accepted, amended by ADR-018 | Complete-system Security Floor and bounded policy |
| [ADR-006](ADR-006-hierarchical-kill-switch.md) | Superseded by ADR-015 | Historical agent execution kill switch |
| [ADR-007](ADR-007-normative-goal-and-action-state-machines.md) | Superseded by ADR-015 | Historical Goal and Action state machines |
| [ADR-008](ADR-008-atomic-action-preparation-and-commit.md) | Superseded by ADR-015 | Historical action preparation and commit |
| [ADR-009](ADR-009-stage-1-dispatch-journal.md) | Superseded by ADR-015 | Historical agent dispatch journal |
| [ADR-010](ADR-010-staged-memory-capabilities.md) | Superseded as product stages by ADR-018; retained for Memory Core | Memory-specific staged capabilities including Dreaming |
| [ADR-011](ADR-011-independent-verification-completion-gate.md) | Superseded by ADR-015 | Historical consumer-goal completion gate |
| [ADR-012](ADR-012-retention-aware-evidence-immutability.md) | Accepted, amended by ADR-015 and ADR-017 | Retention-aware memory and Dreaming-artifact immutability |
| [ADR-013](ADR-013-python-runtime-and-toolchain.md) | Accepted, amended by ADR-018 | Current Python baseline with later-stage runtime choices gated |
| [ADR-014](ADR-014-local-ollama-only-inference.md) | Accepted, amended by ADR-018 | Local Ollama inference as an untrusted bounded dependency |
| [ADR-015](ADR-015-memory-system-not-agent-runtime.md) | Superseded as product boundary by ADR-018; retained for Memory Core | Governed memory-system boundary |
| [ADR-016](ADR-016-hierarchy-catalog-and-operational-memory-scope.md) | Accepted, amended by ADR-018 | Brain-to-Goal hierarchy; isolation ends at Session |
| [ADR-017](ADR-017-governed-area-local-dreaming.md) | Accepted, amended by ADR-018 | Governed Area-local offline Memory Core Dreaming |
| [ADR-018](ADR-018-complete-cognitive-system.md) | Accepted | Neural Brain is a complete protected cognitive system |

The repository preserves the continuous decision sequence from ADR-001 through
ADR-018. ADR-018 governs the complete cognitive-system boundary. ADR-015 remains
the subsystem boundary for the Memory Core, ADR-016 governs hierarchy scope,
and ADR-017 governs Dreaming. Earlier agent-runtime decisions remain historical
inputs requiring explicit revalidation rather than silent reactivation.
