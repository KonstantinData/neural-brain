"""End-to-end evidence for the synchronous Psycopg Stage 1 adapter."""

# ruff: noqa: SIM117

from dataclasses import dataclass
from datetime import UTC, datetime

import psycopg

from neural_brain.memory import (
    CheckpointRequest,
    DreamingRequest,
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


def test_psycopg_adapter_exposes_only_guarded_inactive_dreaming_output(
    database_dsn: str,
) -> None:
    """The adapter cannot ask Dreaming to promote or create caller-selected candidates."""
    service = _service(database_dsn)
    _record_cycle(service, "dreaming")

    skipped = service.run_dreaming_dry_run(
        DreamingRequest(dreaming_run_id="dream-adapter-active", requested_reason="test guard")
    )
    assert skipped.report.status == "skipped"
    assert skipped.candidates == ()

    with psycopg.connect(database_dsn, autocommit=True) as connection, connection.transaction():
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE brain_catalog.sessions SET activity_state = 'inactive', "
                "activity_expires_at = NULL WHERE tenant_id = 'tenant-a' AND area_id = 'area-a'"
            )

    completed = service.run_dreaming_dry_run(
        DreamingRequest(dreaming_run_id="dream-adapter-complete", requested_reason="test dry run")
    )
    assert completed.report.status == "completed"
    assert completed.report.active_pointer_updated is False
    assert completed.report.candidate_count == 1
    assert all(candidate.state == "inactive" for candidate in completed.candidates)
    assert all(candidate.retrievable is False for candidate in completed.candidates)
