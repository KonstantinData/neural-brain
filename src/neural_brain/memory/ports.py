"""Ports that isolate trusted runtime context and atomic persistence."""

from typing import Protocol

from neural_brain.memory.models import (
    CheckpointRecord,
    CheckpointRequest,
    DreamingRequest,
    DreamingResult,
    MemoryCycleResult,
    ObservationRequest,
    OpaqueId,
    RuntimeContext,
    WorkingMemoryRequest,
)


class RuntimeContextProvider(Protocol):
    """Resolve authenticated identity and scope outside untrusted request payloads."""

    def current_context(self) -> RuntimeContext:
        """Return the authenticated immutable context for the current call."""
        ...


class MemoryRepository(Protocol):
    """Atomic persistence boundary for protected MS-1 memory operations."""

    def commit_memory_cycle(
        self,
        *,
        context: RuntimeContext,
        transition_request_id: OpaqueId,
        observation: ObservationRequest,
        working_memory: WorkingMemoryRequest,
        checkpoint: CheckpointRequest,
    ) -> MemoryCycleResult:
        """Commit observation, memory version, checkpoint, and audit together."""
        ...

    def read_checkpoint(
        self, *, context: RuntimeContext, checkpoint_id: OpaqueId
    ) -> CheckpointRecord:
        """Read one checkpoint only within authenticated operational scope."""
        ...

    def execute_dreaming_dry_run(
        self, *, context: RuntimeContext, request: DreamingRequest
    ) -> DreamingResult:
        """Atomically guard activity and persist only a report and inactive candidates."""
        ...
