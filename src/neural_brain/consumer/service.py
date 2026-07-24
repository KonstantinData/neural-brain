"""Consumer library that binds an OIDC-authenticated context to Memory Core gates."""

from __future__ import annotations

from dataclasses import dataclass

from neural_brain.consumer.oidc import OidcJwtAuthenticator
from neural_brain.memory import (
    CheckpointRecord,
    CheckpointRequest,
    MemoryCycleResult,
    MemoryRepository,
    MemoryService,
    ObservationRecord,
    ObservationRequest,
    RuntimeContext,
    WorkingMemoryRecord,
    WorkingMemoryRequest,
)
from neural_brain.memory.models import OpaqueId


@dataclass(frozen=True, slots=True)
class _FixedContextProvider:
    """Bind one already-authenticated context to a single consumer operation."""

    context: RuntimeContext

    def current_context(self) -> RuntimeContext:
        """Return the immutable context established by JWT validation."""
        return self.context


class OidcMemoryCoreConsumer:
    """Expose only existing Memory Gate operations to OIDC-authenticated callers."""

    def __init__(
        self, *, authenticator: OidcJwtAuthenticator, repository: MemoryRepository
    ) -> None:
        self._authenticator = authenticator
        self._repository = repository

    def record_observation_and_checkpoint(
        self,
        *,
        bearer_token: str,
        transition_request_id: OpaqueId,
        observation: ObservationRequest,
        working_memory: WorkingMemoryRequest,
        checkpoint: CheckpointRequest,
    ) -> MemoryCycleResult:
        """Write one atomic memory cycle through the existing Memory Transition Gate."""
        return self._service(bearer_token).record_observation_and_checkpoint(
            transition_request_id=transition_request_id,
            observation=observation,
            working_memory=working_memory,
            checkpoint=checkpoint,
        )

    def read_checkpoint(self, *, bearer_token: str, checkpoint_id: OpaqueId) -> CheckpointRecord:
        """Read one checkpoint through authenticated session scope."""
        return self._service(bearer_token).read_checkpoint(
            CheckpointRequest(checkpoint_id=checkpoint_id)
        )

    def read_observation(self, *, bearer_token: str, observation_id: OpaqueId) -> ObservationRecord:
        """Read one observation through authenticated session scope."""
        return self._service(bearer_token).read_observation(observation_id)

    def read_working_memory(
        self, *, bearer_token: str, working_memory_id: OpaqueId
    ) -> WorkingMemoryRecord:
        """Read one current Working Memory value through authenticated session scope."""
        return self._service(bearer_token).read_working_memory(working_memory_id)

    def _service(self, bearer_token: str) -> MemoryService:
        context = self._authenticator.authenticate(bearer_token)
        return MemoryService(
            context_provider=_FixedContextProvider(context), repository=self._repository
        )
