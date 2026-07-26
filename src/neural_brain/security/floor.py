"""Code-owned, fail-closed Security Floor for implemented runtime operations.

This module deliberately has no policy input, configuration hook, or caller
override. It is a minimum boundary, not a substitute for database gates,
authority checks, approvals, or the later versioned policy engine.
"""

from __future__ import annotations

from enum import StrEnum

from neural_brain.memory.errors import ScopeIsolationError
from neural_brain.memory.models import RuntimeContext

SECURITY_FLOOR_VERSION = "security-floor-v1"


class MemoryOperation(StrEnum):
    """The only Memory Core operations presently admitted by the floor."""

    INGEST = "memory_ingest"
    READ = "memory_read"


class SecurityFloorDeniedError(ScopeIsolationError):
    """Raised when a non-overridable runtime safety invariant is not met."""


def authorize_memory_operation(context: object, operation: object) -> None:
    """Deny incomplete trusted context and every operation outside this release.

    The caller cannot supply a policy, scope replacement, override flag, or
    allow-list. ``RuntimeContext`` is established by the authentication
    boundary; database gates remain independent enforcement layers.
    """

    if not isinstance(context, RuntimeContext):
        raise SecurityFloorDeniedError("security floor requires authenticated runtime context")
    if not isinstance(operation, MemoryOperation):
        raise SecurityFloorDeniedError("security floor denies unknown memory operation")
    if context.project_id is None or context.session_id is None:
        raise SecurityFloorDeniedError("security floor requires complete session scope")
