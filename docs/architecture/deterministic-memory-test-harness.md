# Deterministic Memory Core Test Harness

- Status: test infrastructure
- Delivery evidence: S1-12.2
- Governing sources: ADR-018, Architecture Directive v4.0, S1-12.1

## Boundary

`tests/support/deterministic_memory_harness.py` is effect-free test-only
infrastructure for reproducing protected Memory Core boundary behavior. It is
not imported by `src/`, does not connect to PostgreSQL or any external service,
does not create authority, and does not add a runtime, Action, Dreaming,
learning, or model-promotion capability.

## Components

- `FrozenClock` supplies an explicit, monotonic test instant.
- `DeterministicIds` and `reproduce_seed` derive stable fixture identifiers and
  scenario content from a declared seed.
- `MemoryCycleFactory` creates scope-free request payloads; authenticated scope
  remains exclusively in the runtime context provided by each test.
- `DeterministicMemoryRepository` simulates one scoped atomic persistence
  boundary with replay receipts and an explicit `before_commit` failpoint.
- `ScriptedMemoryRepository` returns only declared adapter outcomes, allowing
  callers to reproduce untrusted adapter responses without a live dependency.

## Evidence and limits

`tests/foundation/test_deterministic_memory_harness.py` proves deterministic
seed reproduction, monotonic time, atomic rollback at the crash boundary,
scope-isolated reads, idempotent replay, and rejection of a foreign-scope
scripted adapter result. The harness supplements, but never substitutes for,
PostgreSQL migration, RLS, transition-gate, live crash/recovery, or independent
evaluation evidence. It therefore makes no lifecycle-completion, external
effect, or product-stage claim.
