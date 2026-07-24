"""Synchronous application service for the MS-1 Memory Core kernel."""

from neural_brain.memory.errors import (
    DreamingUnavailableError,
    InvalidMemoryCycleError,
    ScopeIsolationError,
)
from neural_brain.memory.models import (
    CheckpointRecord,
    CheckpointRequest,
    DreamingRequest,
    DreamingResult,
    MemoryCycleResult,
    MemoryScope,
    ObservationRecord,
    ObservationRequest,
    OpaqueId,
    RuntimeContext,
    WorkingMemoryRecord,
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
                "MS-1 memory cycles require authenticated project and session scope"
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

    def read_observation(self, observation_id: OpaqueId) -> ObservationRecord:
        """Read one observation without accepting scope from the caller."""
        context = self._context_provider.current_context()
        observation = self._repository.read_observation(
            context=context, observation_id=observation_id
        )
        self._assert_scope(context, observation.scope)
        return observation

    def read_working_memory(self, working_memory_id: OpaqueId) -> WorkingMemoryRecord:
        """Read current working memory without accepting scope from the caller."""
        context = self._context_provider.current_context()
        working_memory = self._repository.read_working_memory(
            context=context, working_memory_id=working_memory_id
        )
        self._assert_scope(context, working_memory.scope)
        return working_memory

    def run_dreaming_dry_run(self, request: DreamingRequest) -> DreamingResult:
        """Reject Dreaming until its persistent safety prerequisites are implemented."""
        raise DreamingUnavailableError(
            "Dreaming is unavailable: persistent lease, immutable snapshot, and "
            "independent validation are not implemented"
        )

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
