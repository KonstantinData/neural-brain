"""Domain errors exposed by the synchronous MS-1 Memory Core kernel."""


class MemoryKernelError(Exception):
    """Base class for fail-closed memory-kernel failures."""

    code = "NB-MC-INTERNAL"


class InvalidMemoryCycleError(MemoryKernelError):
    """Raised when a cycle does not connect its observation to working memory."""

    code = "NB-MC-INVALID-CYCLE"


class ScopeIsolationError(MemoryKernelError):
    """Raised when repository output does not match authenticated runtime scope."""

    code = "NB-MC-SCOPE-DENIED"


class StaleWorkingMemoryVersionError(MemoryKernelError):
    """Raised when the expected working-memory version is stale."""

    code = "NB-MC-STALE-WORKING-MEMORY"


class CheckpointUnavailableError(MemoryKernelError):
    """Raised when a checkpoint is absent or outside authenticated scope."""

    code = "NB-MC-RECORD-UNAVAILABLE"


class DreamingUnavailableError(MemoryKernelError):
    """Raised while Dreaming lacks the required lease, snapshot, and validation gates."""

    code = "NB-MC-DREAMING-UNAVAILABLE"


class AtomicPersistenceError(MemoryKernelError):
    """Raised when an atomic repository operation cannot commit."""

    code = "NB-MC-PERSISTENCE-FAILED"
