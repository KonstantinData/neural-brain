"""Domain errors exposed by the synchronous Stage 1 memory kernel."""


class MemoryKernelError(Exception):
    """Base class for fail-closed memory-kernel failures."""


class InvalidMemoryCycleError(MemoryKernelError):
    """Raised when a cycle does not connect its observation to working memory."""


class ScopeIsolationError(MemoryKernelError):
    """Raised when repository output does not match authenticated runtime scope."""


class StaleWorkingMemoryVersionError(MemoryKernelError):
    """Raised when the expected working-memory version is stale."""


class CheckpointUnavailableError(MemoryKernelError):
    """Raised when a checkpoint is absent or outside authenticated scope."""


class AtomicPersistenceError(MemoryKernelError):
    """Raised when an atomic repository operation cannot commit."""
