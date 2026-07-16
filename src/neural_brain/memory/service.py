"""Synchronous application service for the Stage 1 memory kernel."""

from neural_brain.memory.errors import InvalidMemoryCycleError, ScopeIsolationError
from neural_brain.memory.models import (
    CheckpointRecord,
    CheckpointRequest,
    DreamingRequest,
    DreamingResult,
    MemoryCycleResult,
    MemoryScope,
    ObservationRequest,
    OpaqueId,
    RuntimeContext,
    WorkingMemoryRequest,
)
from neural_brain.memory.ports import MemoryRepository, RuntimeContextProvider


class MemoryService:
    """Attach trusted context and delegate protected writes to atomic repository gates."""

    def __init__(
        self, *, context_provider: RuntimeContextProvider, repository: MemoryRepository
    ) -> None:
        self._context_provider = context_provider
        self._repository = repository

    def record_observation_and_checkpoint(
        self,
        *,
        transition_request_id: OpaqueId,
        observation: ObservationRequest,
        working_memory: WorkingMemoryRequest,
        checkpoint: CheckpointRequest,
    ) -> MemoryCycleResult:
        """Commit one observation-backed working-memory version and checkpoint."""
        if not any(
            entry.source_observation_id == observation.observation_id
            for entry in working_memory.entries
        ):
            raise InvalidMemoryCycleError(
                "working memory must contain an entry derived from the cycle observation"
            )

        context = self._context_provider.current_context()
        if context.project_id is None or context.session_id is None:
            raise ScopeIsolationError(
                "Stage 1 memory cycles require authenticated project and session scope"
            )
        result = self._repository.commit_memory_cycle(
            context=context,
            transition_request_id=transition_request_id,
            observation=observation,
            working_memory=working_memory,
            checkpoint=checkpoint,
        )
        self._assert_scope(context, result.observation.scope)
        self._assert_scope(context, result.working_memory.scope)
        self._assert_scope(context, result.checkpoint.scope)
        return result

    def read_checkpoint(self, request: CheckpointRequest) -> CheckpointRecord:
        """Read back a checkpoint without accepting scope from the caller."""
        context = self._context_provider.current_context()
        checkpoint = self._repository.read_checkpoint(
            context=context, checkpoint_id=request.checkpoint_id
        )
        self._assert_scope(context, checkpoint.scope)
        return checkpoint

    def run_dreaming_dry_run(self, request: DreamingRequest) -> DreamingResult:
        """Run Stage 1 Dreaming without activation, promotion, or cross-Area access."""
        context = self._context_provider.current_context()
        result = self._repository.execute_dreaming_dry_run(context=context, request=request)
        self._assert_area_scope(context, result.report.scope)
        for candidate in result.candidates:
            self._assert_area_scope(context, candidate.scope)
        return result

    @staticmethod
    def _assert_scope(context: RuntimeContext, scope: MemoryScope) -> None:
        expected = MemoryScope(
            tenant_id=context.tenant_id,
            area_id=context.area_id,
            project_id=context.project_id,
            session_id=context.session_id,
        )
        if scope != expected:
            raise ScopeIsolationError("repository output crossed authenticated memory scope")

    @staticmethod
    def _assert_area_scope(context: RuntimeContext, scope: MemoryScope) -> None:
        expected = MemoryScope(tenant_id=context.tenant_id, area_id=context.area_id)
        if scope != expected:
            raise ScopeIsolationError("repository output crossed authenticated Area scope")
