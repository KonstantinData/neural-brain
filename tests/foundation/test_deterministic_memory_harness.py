"""Evidence for the S1-12.2 deterministic Memory Core test harness."""

from datetime import UTC, datetime, timedelta

import pytest

from neural_brain.memory import (
    AtomicPersistenceError,
    MemoryService,
    RuntimeContext,
    ScopeIsolationError,
)
from tests.support.deterministic_memory_harness import (
    DeterministicIds,
    DeterministicMemoryRepository,
    FrozenClock,
    MemoryCycleFactory,
    MemoryFailpoint,
    ScriptedMemoryRepository,
    reproduce_seed,
)


class FixedContextProvider:
    """Supply a trusted test context without accepting it from request fixtures."""

    def __init__(self, context: RuntimeContext) -> None:
        self.context = context

    def current_context(self) -> RuntimeContext:
        return self.context


def _context(*, tenant_id: str = "tenant-a", area_id: str = "area-a") -> RuntimeContext:
    return RuntimeContext(
        actor_id="test-principal",
        tenant_id=tenant_id,
        area_id=area_id,
        project_id="project-a",
        session_id="session-a",
    )


def _factory(seed: str = "reproducible-seed") -> MemoryCycleFactory:
    return MemoryCycleFactory(
        clock=FrozenClock(datetime(2026, 7, 26, 12, 0, tzinfo=UTC)),
        ids=DeterministicIds(seed),
    )


def test_clock_ids_and_seed_reproduce_identical_memory_inputs() -> None:
    first_factory = _factory()
    second_factory = _factory()

    assert first_factory.build() == second_factory.build()
    assert reproduce_seed("reproducible-seed") == reproduce_seed("reproducible-seed")
    assert reproduce_seed("reproducible-seed") != reproduce_seed("another-seed")
    assert first_factory.clock.advance(timedelta(seconds=1)) == datetime(
        2026, 7, 26, 12, 0, 1, tzinfo=UTC
    )
    with pytest.raises(ValueError, match="cannot move backwards"):
        first_factory.clock.advance(timedelta(seconds=-1))


def test_failpoint_leaves_no_partial_persistent_memory_or_audit_state() -> None:
    repository = DeterministicMemoryRepository()
    inputs = _factory().build()
    repository.inject(MemoryFailpoint.BEFORE_COMMIT)

    with pytest.raises(AtomicPersistenceError, match="before atomic commit"):
        repository.commit_memory_cycle(
            context=_context(),
            transition_request_id=inputs.transition_request_id,
            observation=inputs.observation,
            working_memory=inputs.working_memory,
            checkpoint=inputs.checkpoint,
        )

    assert repository.observations == {}
    assert repository.working_memories == {}
    assert repository.checkpoints == {}
    assert repository.audit_ids == []


def test_persistent_fixture_is_scoped_idempotent_and_rejects_cross_scope_read() -> None:
    repository = DeterministicMemoryRepository()
    inputs = _factory().build()
    result = repository.commit_memory_cycle(
        context=_context(),
        transition_request_id=inputs.transition_request_id,
        observation=inputs.observation,
        working_memory=inputs.working_memory,
        checkpoint=inputs.checkpoint,
    )

    assert (
        repository.commit_memory_cycle(
            context=_context(),
            transition_request_id=inputs.transition_request_id,
            observation=inputs.observation,
            working_memory=inputs.working_memory,
            checkpoint=inputs.checkpoint,
        )
        == result
    )
    assert repository.audit_ids == [inputs.transition_request_id]
    with pytest.raises(Exception, match="record unavailable"):
        repository.read_checkpoint(
            context=_context(tenant_id="tenant-b"), checkpoint_id=inputs.checkpoint.checkpoint_id
        )


def test_scripted_untrusted_adapter_response_cannot_widen_authenticated_scope() -> None:
    foreign_repository = DeterministicMemoryRepository()
    foreign_inputs = _factory("foreign").build()
    foreign_result = foreign_repository.commit_memory_cycle(
        context=_context(tenant_id="tenant-b"),
        transition_request_id=foreign_inputs.transition_request_id,
        observation=foreign_inputs.observation,
        working_memory=foreign_inputs.working_memory,
        checkpoint=foreign_inputs.checkpoint,
    )
    repository = ScriptedMemoryRepository((foreign_result,))
    service = MemoryService(
        context_provider=FixedContextProvider(_context()),
        repository=repository,
    )
    inputs = _factory().build()

    with pytest.raises(ScopeIsolationError, match="crossed authenticated memory scope"):
        service.record_observation_and_checkpoint(
            transition_request_id=inputs.transition_request_id,
            observation=inputs.observation,
            working_memory=inputs.working_memory,
            checkpoint=inputs.checkpoint,
        )
    assert repository.calls == ["commit_memory_cycle"]
