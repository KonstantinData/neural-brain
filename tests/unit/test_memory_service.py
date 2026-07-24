"""Unit evidence for the synchronous trusted-context MS-1 Memory Core kernel."""

from dataclasses import dataclass
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from neural_brain.memory import (
    AtomicPersistenceError,
    CheckpointRecord,
    CheckpointRequest,
    CheckpointUnavailableError,
    DreamingRequest,
    DreamingResult,
    DreamingUnavailableError,
    InvalidMemoryCycleError,
    MemoryCycleResult,
    MemoryScope,
    MemoryService,
    ObservationRecord,
    ObservationRequest,
    OpaqueId,
    RuntimeContext,
    StaleWorkingMemoryVersionError,
    WorkingMemoryEntryRequest,
    WorkingMemoryRecord,
    WorkingMemoryRequest,
)
from neural_brain.postgres import PostgresMemoryRepository

type ScopeKey = tuple[str, str, str | None, str | None]


@dataclass
class MutableContextProvider:
    """Test-only provider that emulates authenticated runtime context changes."""

    context: RuntimeContext

    def current_context(self) -> RuntimeContext:
        """Return the context selected by the test harness."""
        return self.context


class InMemoryMemoryRepository:
    """Deterministic test fake for the atomic repository protocol."""

    def __init__(self) -> None:
        self.observations: dict[tuple[ScopeKey, str], ObservationRecord] = {}
        self.working_memories: dict[tuple[ScopeKey, str], WorkingMemoryRecord] = {}
        self.checkpoints: dict[tuple[ScopeKey, str], CheckpointRecord] = {}
        self.active_pointers: dict[tuple[str, str], str] = {}
        self.audit_count = 0
        self.fail_next_cycle = False
        self.dreaming_calls = 0

    def commit_memory_cycle(
        self,
        *,
        context: RuntimeContext,
        transition_request_id: OpaqueId,
        observation: ObservationRequest,
        working_memory: WorkingMemoryRequest,
        checkpoint: CheckpointRequest,
    ) -> MemoryCycleResult:
        """Stage all records and expose them only after the simulated commit."""
        key = self._scope_key(context)
        working_memory_key = (key, working_memory.working_memory_id)
        previous = self.working_memories.get(working_memory_key)
        current_version = 0 if previous is None else previous.version
        if current_version != working_memory.expected_version:
            raise StaleWorkingMemoryVersionError("stale working-memory version")

        scope = self._scope(context)
        next_version = current_version + 1
        staged_observation = ObservationRecord(
            observation_id=observation.observation_id,
            source_kind=observation.source_kind,
            source_ref=observation.source_ref,
            classification=observation.classification,
            purpose=observation.purpose,
            content=observation.content,
            occurred_at=observation.occurred_at,
            scope=scope,
        )
        staged_memory = WorkingMemoryRecord(
            working_memory_id=working_memory.working_memory_id,
            version=next_version,
            entries=working_memory.entries,
            scope=scope,
        )
        staged_checkpoint = CheckpointRecord(
            checkpoint_id=checkpoint.checkpoint_id,
            working_memory_id=working_memory.working_memory_id,
            working_memory_version=next_version,
            entries=working_memory.entries,
            scope=scope,
        )
        if self.fail_next_cycle:
            self.fail_next_cycle = False
            raise AtomicPersistenceError("simulated transaction rollback")

        self.observations[(key, observation.observation_id)] = staged_observation
        self.working_memories[working_memory_key] = staged_memory
        self.checkpoints[(key, checkpoint.checkpoint_id)] = staged_checkpoint
        self.audit_count += 1
        return MemoryCycleResult(
            observation=staged_observation,
            working_memory=staged_memory,
            checkpoint=staged_checkpoint,
            audit_committed=True,
        )

    def read_checkpoint(
        self, *, context: RuntimeContext, checkpoint_id: OpaqueId
    ) -> CheckpointRecord:
        """Return absent for both missing and cross-scope checkpoints."""
        try:
            return self.checkpoints[(self._scope_key(context), checkpoint_id)]
        except KeyError as error:
            raise CheckpointUnavailableError("checkpoint unavailable") from error

    def read_observation(
        self, *, context: RuntimeContext, observation_id: OpaqueId
    ) -> ObservationRecord:
        """Return absent for both missing and cross-scope observations."""
        try:
            return self.observations[(self._scope_key(context), observation_id)]
        except KeyError as error:
            raise CheckpointUnavailableError("observation unavailable") from error

    def read_working_memory(
        self, *, context: RuntimeContext, working_memory_id: OpaqueId
    ) -> WorkingMemoryRecord:
        """Return absent for both missing and cross-scope working-memory values."""
        try:
            return self.working_memories[(self._scope_key(context), working_memory_id)]
        except KeyError as error:
            raise CheckpointUnavailableError("working memory unavailable") from error

    def execute_dreaming_dry_run(
        self, *, context: RuntimeContext, request: DreamingRequest
    ) -> DreamingResult:
        """Detect any accidental call past the service-level availability guard."""
        self.dreaming_calls += 1
        raise AssertionError("Dreaming repository must not be called")

    @staticmethod
    def _scope(context: RuntimeContext) -> MemoryScope:
        return MemoryScope(
            tenant_id=context.tenant_id,
            area_id=context.area_id,
            project_id=context.project_id,
            session_id=context.session_id,
        )

    @staticmethod
    def _scope_key(context: RuntimeContext) -> ScopeKey:
        return (
            context.tenant_id,
            context.area_id,
            context.project_id,
            context.session_id,
        )


@pytest.fixture
def context_provider() -> MutableContextProvider:
    """Provide one authenticated Area context."""
    return MutableContextProvider(
        RuntimeContext(
            actor_id="actor-1",
            tenant_id="tenant-condata",
            area_id="area-neural-brain",
            project_id="project-stage-1",
            session_id="session-1",
        )
    )


@pytest.fixture
def repository() -> InMemoryMemoryRepository:
    """Provide an empty deterministic repository fake."""
    return InMemoryMemoryRepository()


@pytest.fixture
def service(
    context_provider: MutableContextProvider, repository: InMemoryMemoryRepository
) -> MemoryService:
    """Build a service around test-only ports."""
    return MemoryService(context_provider=context_provider, repository=repository)


def observation() -> ObservationRequest:
    """Build a valid untrusted observation."""
    return ObservationRequest(
        observation_id="observation-1",
        source_kind="consumer_event",
        source_ref="consumer-message-1",
        classification="internal",
        purpose="working_context",
        content="Evidence",
        occurred_at=datetime(2026, 7, 15, 12, 0, tzinfo=UTC),
    )


def working_memory(expected_version: int = 0) -> WorkingMemoryRequest:
    """Build a bounded working-memory update containing the observation."""
    return WorkingMemoryRequest(
        working_memory_id="working-memory-1",
        expected_version=expected_version,
        entries=(
            WorkingMemoryEntryRequest(
                entry_id="entry-1",
                source_observation_id="observation-1",
                content="Evidence",
            ),
        ),
    )


@pytest.mark.parametrize(
    ("model", "payload"),
    [
        (
            ObservationRequest,
            {
                "observation_id": "observation-1",
                "source_kind": "consumer_event",
                "source_ref": "source-1",
                "classification": "internal",
                "purpose": "working_context",
                "content": "content",
                "occurred_at": datetime(2026, 7, 15, 12, 0, tzinfo=UTC),
                "tenant_id": "attacker-tenant",
            },
        ),
        (
            WorkingMemoryRequest,
            {
                "working_memory_id": "working-memory-1",
                "expected_version": 0,
                "entries": (),
                "actor_id": "attacker",
            },
        ),
        (
            CheckpointRequest,
            {"checkpoint_id": "checkpoint-1", "area_id": "attacker-area"},
        ),
        (
            DreamingRequest,
            {
                "dreaming_run_id": "dream-1",
                "requested_reason": "scheduled dry run",
                "scope": {"tenant_id": "attacker", "area_id": "attacker"},
            },
        ),
    ],
)
def test_untrusted_requests_reject_actor_and_scope_fields(
    model: type[ObservationRequest]
    | type[WorkingMemoryRequest]
    | type[CheckpointRequest]
    | type[DreamingRequest],
    payload: dict[str, object],
) -> None:
    """Untrusted payloads cannot define actor or operational scope."""
    with pytest.raises(ValidationError):
        model.model_validate(payload)


def test_requests_are_strict() -> None:
    """Schema boundaries reject coercion of untrusted scalar values."""
    with pytest.raises(ValidationError):
        ObservationRequest.model_validate(
            {
                "observation_id": "observation-1",
                "source_kind": "consumer_event",
                "source_ref": "source-1",
                "classification": "internal",
                "purpose": "working_context",
                "content": 7,
                "occurred_at": datetime(2026, 7, 15, 12, 0, tzinfo=UTC),
            }
        )
    with pytest.raises(ValidationError):
        WorkingMemoryRequest.model_validate(
            {"working_memory_id": "memory-1", "expected_version": "0", "entries": ()}
        )


def test_checkpoint_round_trip_is_deterministic_and_audited(
    service: MemoryService, repository: InMemoryMemoryRepository
) -> None:
    """A committed checkpoint reads back exactly and includes atomic audit evidence."""
    result = service.record_observation_and_checkpoint(
        transition_request_id="transition-1",
        observation=observation(),
        working_memory=working_memory(),
        checkpoint=CheckpointRequest(checkpoint_id="checkpoint-1"),
    )

    request = CheckpointRequest(checkpoint_id="checkpoint-1")
    first = service.read_checkpoint(request)
    second = service.read_checkpoint(request)

    assert first == result.checkpoint
    assert second == first
    assert first.entries == working_memory().entries
    assert result.audit_committed is True
    assert repository.audit_count == 1


@pytest.mark.parametrize(
    ("tenant_id", "area_id"),
    [("tenant-condata", "area-website"), ("tenant-other", "area-neural-brain")],
)
def test_checkpoint_is_invisible_outside_authenticated_context(
    service: MemoryService,
    context_provider: MutableContextProvider,
    tenant_id: str,
    area_id: str,
) -> None:
    """The same opaque checkpoint ID reveals nothing across tenant or Area boundaries."""
    service.record_observation_and_checkpoint(
        transition_request_id="transition-1",
        observation=observation(),
        working_memory=working_memory(),
        checkpoint=CheckpointRequest(checkpoint_id="checkpoint-1"),
    )
    context_provider.context = RuntimeContext(
        actor_id="actor-2",
        tenant_id=tenant_id,
        area_id=area_id,
        project_id="project-stage-1",
        session_id="session-1",
    )

    with pytest.raises(CheckpointUnavailableError):
        service.read_checkpoint(CheckpointRequest(checkpoint_id="checkpoint-1"))


def test_stale_working_memory_version_is_rejected(
    service: MemoryService, repository: InMemoryMemoryRepository
) -> None:
    """Compare-and-set prevents a stale caller from overwriting a committed version."""
    service.record_observation_and_checkpoint(
        transition_request_id="transition-1",
        observation=observation(),
        working_memory=working_memory(),
        checkpoint=CheckpointRequest(checkpoint_id="checkpoint-1"),
    )

    with pytest.raises(StaleWorkingMemoryVersionError):
        service.record_observation_and_checkpoint(
            transition_request_id="transition-2",
            observation=observation(),
            working_memory=working_memory(expected_version=0),
            checkpoint=CheckpointRequest(checkpoint_id="checkpoint-2"),
        )

    assert len(repository.checkpoints) == 1
    assert repository.audit_count == 1


def test_cycle_rejects_working_memory_unrelated_to_observation(
    service: MemoryService, repository: InMemoryMemoryRepository
) -> None:
    """A caller cannot commit an observation that is absent from the new memory state."""
    unrelated_memory = WorkingMemoryRequest(
        working_memory_id="working-memory-1",
        expected_version=0,
        entries=(
            WorkingMemoryEntryRequest(
                entry_id="entry-1",
                source_observation_id="observation-other",
                content="Other evidence",
            ),
        ),
    )

    with pytest.raises(InvalidMemoryCycleError):
        service.record_observation_and_checkpoint(
            transition_request_id="transition-1",
            observation=observation(),
            working_memory=unrelated_memory,
            checkpoint=CheckpointRequest(checkpoint_id="checkpoint-1"),
        )

    assert repository.observations == {}
    assert repository.audit_count == 0


def test_atomic_failure_leaves_no_partial_cycle(
    service: MemoryService, repository: InMemoryMemoryRepository
) -> None:
    """Observation, memory, checkpoint, and audit all roll back together."""
    repository.fail_next_cycle = True

    with pytest.raises(AtomicPersistenceError):
        service.record_observation_and_checkpoint(
            transition_request_id="transition-1",
            observation=observation(),
            working_memory=working_memory(),
            checkpoint=CheckpointRequest(checkpoint_id="checkpoint-1"),
        )

    assert repository.observations == {}
    assert repository.working_memories == {}
    assert repository.checkpoints == {}
    assert repository.audit_count == 0


def test_dreaming_is_unavailable_without_calling_repository_or_mutating_state(
    service: MemoryService, repository: InMemoryMemoryRepository
) -> None:
    """The service rejects Dreaming before any repository or state interaction."""
    area_key = ("tenant-condata", "area-neural-brain")
    repository.active_pointers[area_key] = "active-memory-v1"
    audit_count = repository.audit_count

    with pytest.raises(
        DreamingUnavailableError,
        match="persistent lease, immutable snapshot, and independent validation",
    ):
        service.run_dreaming_dry_run(
            DreamingRequest(
                dreaming_run_id="dream-1",
                requested_reason="scheduled dry run",
            )
        )

    assert repository.dreaming_calls == 0
    assert repository.audit_count == audit_count
    assert repository.observations == {}
    assert repository.active_pointers[area_key] == "active-memory-v1"


def test_postgres_repository_rejects_dreaming_before_opening_a_connection(
    context_provider: MutableContextProvider,
) -> None:
    """Direct adapter use is unavailable even when callers bypass the service."""
    repository = PostgresMemoryRepository("postgresql://must-not-be-contacted.invalid/test")

    with pytest.raises(
        DreamingUnavailableError,
        match="persistent lease, immutable snapshot, and independent validation",
    ):
        repository.execute_dreaming_dry_run(
            context=context_provider.context,
            request=DreamingRequest(
                dreaming_run_id="dream-direct",
                requested_reason="direct adapter call",
            ),
        )
