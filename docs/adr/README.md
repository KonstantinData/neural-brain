# Architecture Decision Records

This directory contains versioned architecture decision records for Neural
Brain. ADR file names are intentionally kept stable because repository docs,
Notion records, pull requests, release evidence, and learning artifacts link to
them. Structure is provided by this index, [`STATUS.md`](STATUS.md), and
[`adr-authority.json`](adr-authority.json), not by moving historical files.

Superseded records remain in place as historical evidence, but they are not
current implementation authority unless the current authority map explicitly
retains them for a subsystem.

## Current Authority

For the compact current-state view, read [`STATUS.md`](STATUS.md) first.

| Authority layer | Current decision | Scope |
| --- | --- | --- |
| Complete product boundary | [ADR-018](ADR-018-complete-cognitive-system.md) | Neural Brain is a complete protected cognitive system with a Cognitive Plane and independent Protected Control Plane. |
| Memory Core subsystem | [ADR-015](ADR-015-memory-system-not-agent-runtime.md), [ADR-016](ADR-016-hierarchy-catalog-and-operational-memory-scope.md), [ADR-017](ADR-017-governed-area-local-dreaming.md) | Memory lifecycle, hierarchy scope, provenance, retention, Dreaming, and Memory Transition Gate constraints retained inside the complete system. |
| Foundation ledger and security | [ADR-002](ADR-002-immutable-scope-on-persistent-objects.md), [ADR-003](ADR-003-postgresql-authoritative-transactional-ledger.md), [ADR-005](ADR-005-hard-security-floor-and-bounded-policy.md), [ADR-012](ADR-012-retention-aware-evidence-immutability.md) | Scope, PostgreSQL protected-state ledger, Security Floor, and evidence-retention constraints. |
| Runtime and inference baseline | [ADR-013](ADR-013-python-runtime-and-toolchain.md), [ADR-014](ADR-014-local-ollama-only-inference.md) | CPython toolchain and local Ollama-only bounded inference dependency. |

ADR-018 governs the complete cognitive-system boundary. ADR-015 is no longer
the product boundary; it remains subsystem authority for the governed Memory
Core together with ADR-016 and ADR-017. Earlier agent-runtime decisions are
historical inputs that require explicit revalidation before implementation.

## Authority States

| State | Meaning | Implementation rule |
| --- | --- | --- |
| Current | Governs Neural Brain as a whole or a current foundation concern. | May authorize implementation when aligned with current architecture, contracts, tests, and release gates. |
| Retained subsystem | Superseded for the whole product but retained for Memory Core or another named subsystem. | May authorize only that subsystem scope. It cannot narrow ADR-018. |
| Historical | Preserved as decision history after supersession. | May inform design but cannot authorize implementation without a new accepted ADR or explicit revalidation decision. |

## Thematic Map

| Theme | ADRs | Current reading order |
| --- | --- | --- |
| Product boundary | [ADR-001](ADR-001-product-neutral-platform-boundary.md), [ADR-015](ADR-015-memory-system-not-agent-runtime.md), [ADR-018](ADR-018-complete-cognitive-system.md) | Read ADR-018 first, then ADR-015 only for Memory Core history and retained constraints. |
| Scope and isolation | [ADR-002](ADR-002-immutable-scope-on-persistent-objects.md), [ADR-016](ADR-016-hierarchy-catalog-and-operational-memory-scope.md) | ADR-016 resolves hierarchy catalog scope; ADR-002 remains operational-object scope authority as amended. |
| Protected state and control gates | [ADR-004](ADR-004-transition-gates-own-protected-state.md), [ADR-005](ADR-005-hard-security-floor-and-bounded-policy.md), [ADR-006](ADR-006-hierarchical-kill-switch.md), [ADR-007](ADR-007-normative-goal-and-action-state-machines.md), [ADR-008](ADR-008-atomic-action-preparation-and-commit.md), [ADR-009](ADR-009-stage-1-dispatch-journal.md), [ADR-011](ADR-011-independent-verification-completion-gate.md), [ADR-018](ADR-018-complete-cognitive-system.md) | ADR-018 is current. ADR-004, ADR-006 through ADR-009, and ADR-011 are historical until revalidated. |
| Memory lifecycle and Dreaming | [ADR-010](ADR-010-staged-memory-capabilities.md), [ADR-012](ADR-012-retention-aware-evidence-immutability.md), [ADR-015](ADR-015-memory-system-not-agent-runtime.md), [ADR-016](ADR-016-hierarchy-catalog-and-operational-memory-scope.md), [ADR-017](ADR-017-governed-area-local-dreaming.md) | Treat ADR-010 as Memory Core stage order only; NB stages come from ADR-018 and the delivery roadmap. |
| Runtime, toolchain, and inference | [ADR-013](ADR-013-python-runtime-and-toolchain.md), [ADR-014](ADR-014-local-ollama-only-inference.md) | Current foundation/runtime authority, with later-stage capability enablement still gated. |

## Supersession Matrix

| ADR | Current authority | Supersession relationship |
| --- | --- | --- |
| ADR-001 | Current, amended | Product-neutral boundary retained and widened by ADR-018. |
| ADR-002 | Current, amended | Operational object scope retained; hierarchy catalog rule resolved by ADR-016. |
| ADR-003 | Current, amended | PostgreSQL ledger authority retained under ADR-018. |
| ADR-004 | Historical | Superseded by ADR-015; Goal and Action gates need ADR-018 revalidation. |
| ADR-005 | Current, amended | Security Floor retained and widened for the complete cognitive system. |
| ADR-006 | Historical | Superseded by ADR-015; kill-switch design needs ADR-018 revalidation. |
| ADR-007 | Historical | Superseded by ADR-015; goal/action state machines need ADR-018 revalidation. |
| ADR-008 | Historical | Superseded by ADR-015; action commit model needs ADR-018 revalidation. |
| ADR-009 | Historical | Superseded by ADR-015; dispatch and reconciliation need ADR-018 revalidation. |
| ADR-010 | Retained subsystem | Superseded as product delivery model by ADR-018; retained as Memory Core stage order. |
| ADR-011 | Historical | Superseded by ADR-015; completion gate needs ADR-018 revalidation. |
| ADR-012 | Current, amended | Retention-aware evidence immutability retained for memory and Dreaming artifacts. |
| ADR-013 | Current, amended | Python toolchain retained; later-stage runtime choices remain gated. |
| ADR-014 | Current, amended | Local Ollama-only inference retained as bounded untrusted dependency. |
| ADR-015 | Retained subsystem | Superseded as product boundary by ADR-018; retained for Memory Core. |
| ADR-016 | Current subsystem/foundation | Hierarchy and isolation scope authority retained under ADR-018. |
| ADR-017 | Current subsystem | Area-local Dreaming authority retained under ADR-018. |
| ADR-018 | Current | Governs the complete protected cognitive-system target. |

## Decision Records

| ADR | Status | Authority | Theme | Decision |
| --- | --- | --- | --- | --- |
| [ADR-001](ADR-001-product-neutral-platform-boundary.md) | Accepted, amended by ADR-018 | Current | Product boundary | Product-neutral complete cognitive-system boundary |
| [ADR-002](ADR-002-immutable-scope-on-persistent-objects.md) | Accepted, amended by ADR-015 and ADR-016 | Current | Scope and isolation | Immutable operational memory scope and typed catalog lineage |
| [ADR-003](ADR-003-postgresql-authoritative-transactional-ledger.md) | Accepted, amended by ADR-018 | Current | Ledger and evidence | PostgreSQL authoritative protected-state ledger |
| [ADR-004](ADR-004-transition-gates-own-protected-state.md) | Superseded by ADR-015 | Historical | Protected control | Historical Goal, Action, and Memory gate decision |
| [ADR-005](ADR-005-hard-security-floor-and-bounded-policy.md) | Accepted, amended by ADR-018 | Current | Protected control | Complete-system Security Floor and bounded policy |
| [ADR-006](ADR-006-hierarchical-kill-switch.md) | Superseded by ADR-015 | Historical | Protected control | Historical agent execution kill switch |
| [ADR-007](ADR-007-normative-goal-and-action-state-machines.md) | Superseded by ADR-015 | Historical | Protected control | Historical Goal and Action state machines |
| [ADR-008](ADR-008-atomic-action-preparation-and-commit.md) | Superseded by ADR-015 | Historical | Protected control | Historical action preparation and commit |
| [ADR-009](ADR-009-stage-1-dispatch-journal.md) | Superseded by ADR-015 | Historical | Protected control | Historical agent dispatch journal |
| [ADR-010](ADR-010-staged-memory-capabilities.md) | Superseded as product stages by ADR-018; retained for Memory Core | Retained subsystem | Memory lifecycle | Memory-specific staged capabilities including Dreaming |
| [ADR-011](ADR-011-independent-verification-completion-gate.md) | Superseded by ADR-015 | Historical | Protected control | Historical consumer-goal completion gate |
| [ADR-012](ADR-012-retention-aware-evidence-immutability.md) | Accepted, amended by ADR-015 and ADR-017 | Current | Ledger and evidence | Retention-aware memory and Dreaming-artifact immutability |
| [ADR-013](ADR-013-python-runtime-and-toolchain.md) | Accepted, amended by ADR-018 | Current | Runtime and inference | Current Python baseline with later-stage runtime choices gated |
| [ADR-014](ADR-014-local-ollama-only-inference.md) | Accepted, amended by ADR-018 | Current | Runtime and inference | Local Ollama inference as an untrusted bounded dependency |
| [ADR-015](ADR-015-memory-system-not-agent-runtime.md) | Superseded as product boundary by ADR-018; retained for Memory Core | Retained subsystem | Product boundary | Governed memory-system boundary retained for Memory Core |
| [ADR-016](ADR-016-hierarchy-catalog-and-operational-memory-scope.md) | Accepted, amended by ADR-018 | Current | Scope and isolation | Brain-to-Goal hierarchy; isolation ends at Session |
| [ADR-017](ADR-017-governed-area-local-dreaming.md) | Accepted, amended by ADR-018 | Current | Memory lifecycle | Governed Area-local offline Memory Core Dreaming |
| [ADR-018](ADR-018-complete-cognitive-system.md) | Accepted | Current | Product boundary | Neural Brain is a complete protected cognitive system |

The repository preserves the continuous decision sequence from ADR-001 through
ADR-018.

## Maintenance

New ADRs must use [`TEMPLATE.md`](TEMPLATE.md), update [`STATUS.md`](STATUS.md)
and [`adr-authority.json`](adr-authority.json), and pass:

```powershell
python tools/validate_adrs.py
```

The validator is also exercised by the architecture tests. Unknown, missing, or
conflicting ADR authority fails closed.
