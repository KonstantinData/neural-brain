# NB-248: NB-3 Contract and Readiness Package

- Status: preparation-only, not an implementation or release claim
- Backlog record: NB-248 — Differentiated Memory and Retrieval
- Governing decisions: ADR-015, ADR-018, ADR-019, Architecture Directive v4.0
- Delivery stage: NB-3 target; current repository maturity remains MS-1 Memory Core foundation and incomplete NB-1

## Scope and boundary

`docs/architecture/contracts/nb3-differentiated-memory-readiness-v1.json`
defines the non-activating entry, retrieval, deletion, restore, evaluation, and
release-stop requirements for future NB-3 work. It creates no record type,
database migration, retrieval endpoint, privacy decision, memory authority,
runtime `ALLOW`, or productive activation.

The four required memory kinds have distinct truth and lifecycle semantics:
Working state is bounded session-local cognition; episodic records preserve
event provenance without turning recall into truth; semantic claims preserve
supporting and contradicting evidence; procedural information cannot become
execution authority. All protected state remains Memory Transition Gate-owned.

NB-2 and NB-3 coordinate only through the versioned contract: NB-2 owns
perception, attention, and the world model; NB-3 owns memory-evidence
attachment and retrieval readiness. The boundary carries typed
signal/observation/inference/belief/prediction inputs with provenance, time,
uncertainty, and authenticated scope, and returns only non-authorizing,
freshness- and contradiction-bound memory evidence or abstention. Shared
mutable state and either stage writing the other's protected state are
prohibited.

## Dependency and activation status

NB-1 exit evidence is incomplete. The NB-3 backlog permits overlap with NB-2
only through an accepted versioned interface and non-overlapping ownership.
The current privacy preparation has no accepted, authorized, implemented, and
verified runtime decision. Therefore the contract sets productive NB-3
activation to `denied`.

## Required future evidence

Before an NB-3 implementation or capability claim, a preregistered held-out
evaluation must compare No-Memory, naive-RAG, and the strongest practical
non-memory baseline. It must also pass memory-kind ablations, interference and
false-memory tests, provenance/truth/freshness/uncertainty/contradiction
calibration, scope and privacy isolation, derivative deletion, and restore
non-reappearance. Every test family is non-compensatory.

Deletion requires legal-hold and derivative inventory handling through the
Memory Transition Gate. A restore stays quarantined and `not_ready` until
authoritative ledger, audit, scope, retention, hold, deletion, and derivative
reconciliation are independently proven.

## Verification boundary

`tests/architecture/test_nb3_differentiated_memory_readiness_contract.py`
guards the machine-readable contract against accidental activation, baseline
omission, semantic collapse, scope-bypass, missing deletion/restore controls,
or compensatory pass semantics. It verifies contract shape only; it is not
runtime, privacy, retrieval, deletion, restore, or stage-exit evidence.
