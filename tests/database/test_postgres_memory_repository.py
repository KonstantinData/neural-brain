"""End-to-end evidence for the synchronous Psycopg MS-1 adapter."""

# ruff: noqa: SIM117

from dataclasses import dataclass
from datetime import UTC, datetime

import psycopg
import pytest

from neural_brain.memory import (
    CheckpointRequest,
    DreamingRequest,
    DreamingUnavailableError,
    MemoryService,
    ObservationRequest,
    RuntimeContext,
    WorkingMemoryEntryRequest,
    WorkingMemoryRequest,
)
from neural_brain.postgres import PostgresMemoryRepository


@dataclass(frozen=True)
class FixedContextProvider:
    """Provide an authenticated context without accepting request-supplied scope."""

    context: RuntimeContext

    def current_context(self) -> RuntimeContext:
        """Return the fixed test principal and immutable scope."""
        return self.context


def _service(database_dsn: str) -> MemoryService:
    context = RuntimeContext(
        actor_id="principal-a",
        tenant_id="tenant-a",
        area_id="area-a",
        project_id="project-a",
        session_id="session-a",
    )
    return MemoryService(
        context_provider=FixedContextProvider(context),
        repository=PostgresMemoryRepository(database_dsn),
    )


def _record_cycle(service: MemoryService, suffix: str) -> CheckpointRequest:
    observation = ObservationRequest(
        observation_id=f"observation-{suffix}",
        source_kind="consumer_event",
        source_ref=f"consumer-message-{suffix}",
        classification="internal",
        purpose="working_context",
        content="Adapter evidence",
        occurred_at=datetime(2026, 7, 15, 12, 0, tzinfo=UTC),
    )
    working_memory = WorkingMemoryRequest(
        working_memory_id="primary",
        expected_version=0,
        entries=(
            WorkingMemoryEntryRequest(
                entry_id=f"entry-{suffix}",
                source_observation_id=observation.observation_id,
                content=observation.content,
            ),
        ),
    )
    checkpoint = CheckpointRequest(checkpoint_id=f"checkpoint-{suffix}")
    service.record_observation_and_checkpoint(
        transition_request_id=f"transition-{suffix}",
        observation=observation,
        working_memory=working_memory,
        checkpoint=checkpoint,
    )
    return checkpoint


def test_psycopg_adapter_commits_and_reads_the_atomic_cycle(database_dsn: str) -> None:
    """The public service round-trips only through the protected database functions."""
    service = _service(database_dsn)
    checkpoint = _record_cycle(service, "adapter")
    result = service.read_checkpoint(checkpoint)

    assert result.checkpoint_id == checkpoint.checkpoint_id
    assert service.read_checkpoint(checkpoint) == result


def test_psycopg_adapter_rejects_dreaming_without_persisting_any_output(
    database_dsn: str,
) -> None:
    """Service and direct adapter calls fail before any Dreaming persistence."""
    service = _service(database_dsn)
    _record_cycle(service, "dreaming")

    with psycopg.connect(database_dsn, autocommit=True) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT "
                "(SELECT count(*) FROM memory_core.dreaming_runs), "
                "(SELECT count(*) FROM memory_core.memory_candidates), "
                "(SELECT count(*) FROM memory_audit.events)"
            )
            before = cursor.fetchone()

    request = DreamingRequest(
        dreaming_run_id="dream-adapter-unavailable",
        requested_reason="test unavailable boundary",
    )
    with pytest.raises(DreamingUnavailableError):
        service.run_dreaming_dry_run(request)
    with pytest.raises(DreamingUnavailableError):
        PostgresMemoryRepository(database_dsn).execute_dreaming_dry_run(
            context=RuntimeContext(
                actor_id="principal-a",
                tenant_id="tenant-a",
                area_id="area-a",
                project_id="project-a",
                session_id="session-a",
            ),
            request=request,
        )

    with psycopg.connect(database_dsn, autocommit=True) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT "
                "(SELECT count(*) FROM memory_core.dreaming_runs), "
                "(SELECT count(*) FROM memory_core.memory_candidates), "
                "(SELECT count(*) FROM memory_audit.events)"
            )
            assert cursor.fetchone() == before
