"""Generated model evidence for the implemented working-memory foundation.

Goal, Action, tool, and dispatch runtimes are absent. Their only assertion in
this module is the current fail-closed N/A contract boundary.
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path

import pytest
from hypothesis import HealthCheck, Phase, event, given, settings
from hypothesis import strategies as st
from pydantic import BaseModel

from neural_brain.memory import (
    AtomicPersistenceError,
    CheckpointUnavailableError,
    DreamingRequest,
    DreamingUnavailableError,
    MemoryCycleResult,
    MemoryService,
    RuntimeContext,
    ScopeIsolationError,
    StaleWorkingMemoryVersionError,
)
from tests.support.deterministic_memory_harness import (
    DeterministicIds,
    DeterministicMemoryRepository,
    FrozenClock,
    MemoryCycleFactory,
    MemoryCycleInputs,
    MemoryFailpoint,
)

TRACE_COUNT = 100_000
TRACE_STEPS = 6
GENERATED_STEP_COUNT = TRACE_COUNT * TRACE_STEPS
MAX_SEED = (1 << 63) - 1
WORKING_MEMORY_ID = "working-memory-fixture"

_ROOT = Path(__file__).resolve().parents[2]
_MEMORY_LIFECYCLE = json.loads(
    (_ROOT / "docs/architecture/contracts/memory-lifecycle.json").read_text(encoding="utf-8")
)
_MEMORY_STAGES = json.loads(
    (_ROOT / "docs/architecture/contracts/memory-stage-capabilities.json").read_text(
        encoding="utf-8"
    )
)
_AUTHORITY_CONTRACT = json.loads(
    (_ROOT / "docs/architecture/contracts/memory-authority-grants.json").read_text(encoding="utf-8")
)
_SYSTEM_BOUNDARY = json.loads(
    (_ROOT / "docs/architecture/contracts/system-boundary.json").read_text(encoding="utf-8")
)


class TraceOperation(StrEnum):
    """One generated transition or protected negative path."""

    ADVANCE = "advance"
    EXACT_REPLAY = "exact_replay"
    CONFLICTING_REPLAY = "conflicting_replay"
    STALE_WRITE = "stale_write"
    ROLLBACK_WRITE = "rollback_write"
    RETRY_ROLLED_BACK = "retry_rolled_back"
    CROSS_SCOPE_READ = "cross_scope_read"
    INCOMPLETE_SCOPE = "incomplete_scope"
    AUTHORITY_NA = "authority_na"
    DREAMING_DENIED = "dreaming_denied"
    RECONCILIATION_REQUIRED = "reconciliation_required"
    DISPATCH_NA = "dispatch_na"


class ModelOperationOutcome(StrEnum):
    """Observed outcome classification for one modeled operation or boundary."""

    COMMITTED = "committed"
    REPLAYED = "replayed"
    DENIED = "denied"
    ROLLED_BACK = "rolled_back"
    NOT_APPLICABLE = "not_applicable"


MODEL_OPERATION_OUTCOMES = frozenset(ModelOperationOutcome)
_SCOPE_DIMENSIONS = ("tenant_id", "area_id", "project_id", "session_id")


@dataclass(slots=True)
class MutableContextProvider:
    """Test-only authenticated context seam."""

    context: RuntimeContext

    def current_context(self) -> RuntimeContext:
        return self.context


@dataclass(frozen=True, slots=True)
class RepositorySnapshot:
    """Complete observable state of the deterministic repository harness."""

    observations: tuple[tuple[str, str], ...]
    working_memories: tuple[tuple[str, str], ...]
    checkpoints: tuple[tuple[str, str], ...]
    receipts: tuple[tuple[str, str, str], ...]
    audit_ids: tuple[str, ...]
    failpoint: MemoryFailpoint | None


@dataclass(slots=True)
class MemoryTraceModel:
    """Persistent oracle shared by every operation in one generated trace."""

    committed_version: int = 0
    last_committed: tuple[MemoryCycleInputs, MemoryCycleResult] | None = None
    pending_retry: MemoryCycleInputs | None = None
    outcome_history: list[ModelOperationOutcome] = field(default_factory=list)

    def record_outcome(self, outcome: ModelOperationOutcome) -> None:
        """Record a classification after an observed result, denial, or N/A check."""
        before = tuple(self.outcome_history)
        assert outcome in MODEL_OPERATION_OUTCOMES
        self.outcome_history.append(outcome)
        assert tuple(self.outcome_history[: len(before)]) == before


def _context(seed: int) -> RuntimeContext:
    suffix = f"{seed:x}"
    return RuntimeContext(
        actor_id=f"actor-primary-{suffix}",
        tenant_id=f"tenant-primary-{suffix}",
        area_id=f"area-primary-{suffix}",
        project_id=f"project-primary-{suffix}",
        session_id=f"session-primary-{suffix}",
    )


def _foreign_scope_context(seed: int, dimension: str) -> RuntimeContext:
    assert dimension in _SCOPE_DIMENSIONS
    return _context(seed).model_copy(update={dimension: f"{dimension}-foreign-{seed:x}"})


def _factory(seed: int) -> MemoryCycleFactory:
    return MemoryCycleFactory(clock=FrozenClock(), ids=DeterministicIds(seed=f"s1-12-4-{seed:x}"))


def _record_dump(values: Iterable[tuple[object, BaseModel]]) -> tuple[tuple[str, str], ...]:
    return tuple(sorted((repr(key), value.model_dump_json()) for key, value in values))


def _snapshot(repository: DeterministicMemoryRepository) -> RepositorySnapshot:
    receipts = tuple(
        sorted(
            (repr(key), signature, result.model_dump_json())
            for key, (signature, result) in repository._receipts.items()
        )
    )
    return RepositorySnapshot(
        observations=_record_dump(repository.observations.items()),
        working_memories=_record_dump(repository.working_memories.items()),
        checkpoints=_record_dump(repository.checkpoints.items()),
        receipts=receipts,
        audit_ids=tuple(repository.audit_ids),
        failpoint=repository._failpoint,
    )


def _commit(service: MemoryService, inputs: MemoryCycleInputs) -> MemoryCycleResult:
    return service.record_observation_and_checkpoint(
        transition_request_id=inputs.transition_request_id,
        observation=inputs.observation,
        working_memory=inputs.working_memory,
        checkpoint=inputs.checkpoint,
    )


def _assert_quiescent(
    repository: DeterministicMemoryRepository,
    before: RepositorySnapshot,
    *,
    pending_before: MemoryCycleInputs | None,
    model: MemoryTraceModel,
) -> None:
    assert _snapshot(repository) == before
    assert model.pending_retry == pending_before


def _assert_repository_model(
    repository: DeterministicMemoryRepository,
    model: MemoryTraceModel,
    context: RuntimeContext,
) -> None:
    committed = model.committed_version
    assert len(repository.observations) == committed
    assert len(repository.checkpoints) == committed
    assert len(repository._receipts) == committed
    assert len(repository.audit_ids) == committed
    assert len(set(repository.audit_ids)) == committed
    assert len(repository.working_memories) == (1 if committed else 0)
    assert all(outcome in MODEL_OPERATION_OUTCOMES for outcome in model.outcome_history)

    if not committed:
        return
    working_memory = next(iter(repository.working_memories.values()))
    assert working_memory.working_memory_id == WORKING_MEMORY_ID
    assert working_memory.version == committed
    assert working_memory.scope.model_dump() == {
        "tenant_id": context.tenant_id,
        "area_id": context.area_id,
        "project_id": context.project_id,
        "session_id": context.session_id,
    }
    assert sorted(
        checkpoint.working_memory_version for checkpoint in repository.checkpoints.values()
    ) == list(range(1, committed + 1))
    for observation in repository.observations.values():
        assert observation.scope == working_memory.scope
    for checkpoint in repository.checkpoints.values():
        assert checkpoint.scope == working_memory.scope


def _advance(service: MemoryService, factory: MemoryCycleFactory, model: MemoryTraceModel) -> None:
    inputs = factory.build(expected_version=model.committed_version)
    result = _commit(service, inputs)
    model.committed_version += 1
    assert result.working_memory.version == model.committed_version
    model.last_committed = (inputs, result)
    model.record_outcome(ModelOperationOutcome.COMMITTED)


def _run_operation(
    operation: TraceOperation,
    *,
    seed: int,
    provider: MutableContextProvider,
    repository: DeterministicMemoryRepository,
    service: MemoryService,
    factory: MemoryCycleFactory,
    model: MemoryTraceModel,
) -> None:
    before = _snapshot(repository)
    pending_before = model.pending_retry
    history_before = tuple(model.outcome_history)
    event(f"operation={operation.value}")

    if operation is TraceOperation.ADVANCE:
        _advance(service, factory, model)
    elif operation is TraceOperation.EXACT_REPLAY:
        assert model.last_committed is not None
        inputs, expected = model.last_committed
        assert _commit(service, inputs) == expected
        model.record_outcome(ModelOperationOutcome.REPLAYED)
        _assert_quiescent(repository, before, pending_before=pending_before, model=model)
    elif operation is TraceOperation.CONFLICTING_REPLAY:
        assert model.last_committed is not None
        original, _ = model.last_committed
        conflict = MemoryCycleInputs(
            transition_request_id=original.transition_request_id,
            observation=original.observation.model_copy(update={"content": "conflict"}),
            working_memory=original.working_memory,
            checkpoint=original.checkpoint,
        )
        with pytest.raises(AtomicPersistenceError, match="idempotency key reused"):
            _commit(service, conflict)
        model.record_outcome(ModelOperationOutcome.DENIED)
        _assert_quiescent(repository, before, pending_before=pending_before, model=model)
    elif operation is TraceOperation.STALE_WRITE:
        with pytest.raises(StaleWorkingMemoryVersionError):
            _commit(service, factory.build(expected_version=max(0, model.committed_version - 1)))
        model.record_outcome(ModelOperationOutcome.DENIED)
        _assert_quiescent(repository, before, pending_before=pending_before, model=model)
    elif operation is TraceOperation.ROLLBACK_WRITE:
        if model.pending_retry is not None:
            model.record_outcome(ModelOperationOutcome.NOT_APPLICABLE)
            _assert_quiescent(repository, before, pending_before=pending_before, model=model)
        else:
            retry = factory.build(expected_version=model.committed_version)
            repository.inject(MemoryFailpoint.BEFORE_COMMIT)
            with pytest.raises(AtomicPersistenceError, match="before atomic commit"):
                _commit(service, retry)
            assert repository._failpoint is None
            model.pending_retry = retry
            model.record_outcome(ModelOperationOutcome.ROLLED_BACK)
            assert _snapshot(repository) == before
    elif operation is TraceOperation.RETRY_ROLLED_BACK:
        if model.pending_retry is None:
            model.record_outcome(ModelOperationOutcome.NOT_APPLICABLE)
            _assert_quiescent(repository, before, pending_before=None, model=model)
        else:
            retry = model.pending_retry
            model.pending_retry = None
            if retry.working_memory.expected_version == model.committed_version:
                result = _commit(service, retry)
                model.committed_version += 1
                model.last_committed = (retry, result)
                model.record_outcome(ModelOperationOutcome.COMMITTED)
            else:
                with pytest.raises(StaleWorkingMemoryVersionError):
                    _commit(service, retry)
                model.record_outcome(ModelOperationOutcome.DENIED)
                assert _snapshot(repository) == before
    elif operation is TraceOperation.CROSS_SCOPE_READ:
        assert model.last_committed is not None
        inputs, _ = model.last_committed
        for dimension in _SCOPE_DIMENSIONS:
            event(f"foreign_scope_dimension={dimension}")
            provider.context = _foreign_scope_context(seed, dimension)
            with pytest.raises(CheckpointUnavailableError):
                service.read_checkpoint(inputs.checkpoint)
            model.record_outcome(ModelOperationOutcome.DENIED)
            with pytest.raises(CheckpointUnavailableError):
                service.read_observation(inputs.observation.observation_id)
            model.record_outcome(ModelOperationOutcome.DENIED)
            with pytest.raises(CheckpointUnavailableError):
                service.read_working_memory(WORKING_MEMORY_ID)
            model.record_outcome(ModelOperationOutcome.DENIED)
        provider.context = _context(seed)
        _assert_quiescent(repository, before, pending_before=pending_before, model=model)
    elif operation is TraceOperation.INCOMPLETE_SCOPE:
        for dimension in ("project_id", "session_id"):
            event(f"missing_scope_dimension={dimension}")
            provider.context = _context(seed).model_copy(update={dimension: None})
            with pytest.raises(ScopeIsolationError):
                _commit(service, factory.build(expected_version=model.committed_version))
            model.record_outcome(ModelOperationOutcome.DENIED)
        provider.context = _context(seed)
        _assert_quiescent(repository, before, pending_before=pending_before, model=model)
    elif operation is TraceOperation.AUTHORITY_NA:
        assert _AUTHORITY_CONTRACT["current_operation_boundary"][
            "implemented_security_floor_operations"
        ] == ["intake"]
        assert not hasattr(service, "authority_resolver")
        assert not hasattr(service, "authority_snapshot")
        model.record_outcome(ModelOperationOutcome.NOT_APPLICABLE)
        _assert_quiescent(repository, before, pending_before=pending_before, model=model)
    elif operation is TraceOperation.DREAMING_DENIED:
        with pytest.raises(DreamingUnavailableError):
            service.run_dreaming_dry_run(
                DreamingRequest(
                    dreaming_run_id=f"dream-{seed:x}",
                    requested_reason="generated MS-1 negative path",
                )
            )
        model.record_outcome(ModelOperationOutcome.DENIED)
        _assert_quiescent(repository, before, pending_before=pending_before, model=model)
    elif operation is TraceOperation.RECONCILIATION_REQUIRED:
        assert _MEMORY_LIFECYCLE["reconciliation"]["ready_default"] is False
        assert "Do not retry" in _MEMORY_LIFECYCLE["reconciliation"]["unknown_commit_outcome"]
        assert not hasattr(service, "reconcile_unknown_commit")
        model.record_outcome(ModelOperationOutcome.NOT_APPLICABLE)
        _assert_quiescent(repository, before, pending_before=pending_before, model=model)
    else:
        assert operation is TraceOperation.DISPATCH_NA
        operation_ids = {item["id"] for item in _MEMORY_LIFECYCLE["operations"]}
        assert all("dispatch" not in operation_id for operation_id in operation_ids)
        assert "external effects" in _MEMORY_STAGES["semantics"]["rule"]
        assert _SYSTEM_BOUNDARY["cognitive_plane"]["may_directly_execute_external_effects"] is False
        assert not hasattr(service, "dispatch")
        assert not hasattr(repository, "dispatch")
        model.record_outcome(ModelOperationOutcome.NOT_APPLICABLE)
        _assert_quiescent(repository, before, pending_before=pending_before, model=model)

    assert tuple(model.outcome_history[: len(history_before)]) == history_before


_TAIL_OPERATIONS = st.lists(st.sampled_from(tuple(TraceOperation)), min_size=5, max_size=5).map(
    tuple
)
_TRACE_SEQUENCES = _TAIL_OPERATIONS.map(
    lambda tail: (
        TraceOperation.ADVANCE,
        *tail,
    )
)


@settings(
    max_examples=TRACE_COUNT,
    deadline=None,
    database=None,
    derandomize=True,
    phases=(Phase.generate,),
    suppress_health_check=(HealthCheck.too_slow,),
)
@given(
    seed=st.integers(min_value=0, max_value=MAX_SEED),
    operations=_TRACE_SEQUENCES,
)
def test_generated_sequences_preserve_memory_state_machine_invariants(
    seed: int, operations: tuple[TraceOperation, ...]
) -> None:
    """Run 100,000 six-step traces against one persistent model per example."""
    assert len(operations) == TRACE_STEPS
    primary_context = _context(seed)
    provider = MutableContextProvider(primary_context)
    repository = DeterministicMemoryRepository()
    service = MemoryService(context_provider=provider, repository=repository)
    factory = _factory(seed)
    model = MemoryTraceModel()

    for operation in operations:
        _run_operation(
            operation,
            seed=seed,
            provider=provider,
            repository=repository,
            service=service,
            factory=factory,
            model=model,
        )
        assert provider.context == primary_context
        _assert_repository_model(repository, model, primary_context)

    assert len(model.outcome_history) >= TRACE_STEPS
    assert all(outcome in MODEL_OPERATION_OUTCOMES for outcome in model.outcome_history)


def test_trace_volume_and_negative_runtime_boundary_are_explicit() -> None:
    assert TRACE_COUNT == 100_000
    assert TRACE_STEPS == 6
    assert GENERATED_STEP_COUNT == 600_000
    assert _SYSTEM_BOUNDARY["current_maturity"] == "memory_core_foundation"
    assert not any(
        operation["id"].startswith(("goal.", "action.", "dispatch."))
        for operation in _MEMORY_LIFECYCLE["operations"]
    )
