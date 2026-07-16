"""Ports separating trusted context, active models, and protected memory writes."""

from typing import Protocol

from neural_brain.cognition.adapters import ActiveCognitiveModel
from neural_brain.cognition.models import (
    CognitiveCheckpoint,
    CognitiveTransitionEnvelope,
    RecordedObservation,
)
from neural_brain.memory.models import MemoryCycleResult, OpaqueId, RuntimeContext


class ActiveNeuralWorkspaceProvider(Protocol):
    """Resolve the immutable active model from trusted runtime configuration."""

    def active_model(self, *, context: RuntimeContext) -> ActiveCognitiveModel:
        """Return the active model without consulting the request payload."""
        ...


class CognitiveMemoryGate(Protocol):
    """Persist cognition state only through the protected MS-1 Memory Transition Gate."""

    def load_checkpoint(
        self, *, context: RuntimeContext, checkpoint_id: OpaqueId
    ) -> CognitiveCheckpoint:
        """Load an immutable predecessor through authenticated Memory Core scope."""
        ...

    def commit_checkpoint(
        self,
        *,
        context: RuntimeContext,
        cycle_id: OpaqueId,
        expected_version: int,
        transition: CognitiveTransitionEnvelope,
        observation: RecordedObservation,
    ) -> MemoryCycleResult:
        """Commit observation, state, checkpoint, receipt, and audit atomically."""
        ...
