"""Code-owned, fail-closed Security Floor for implemented runtime operations.

This module deliberately has no policy input, configuration hook, or caller
override. It is a minimum boundary, not a substitute for database gates,
authority checks, approvals, or the later versioned policy engine.
"""

from __future__ import annotations

from enum import StrEnum

SECURITY_FLOOR_VERSION = "security-floor-v1"


class MemoryOperation(StrEnum):
    """The only Memory Core operations presently admitted by the floor."""

    INGEST = "memory_ingest"
    READ = "memory_read"


class SecurityFloorDeniedError(PermissionError):
    """Raised when a non-overridable runtime safety invariant is not met."""


def authorize_memory_operation(context: object, operation: object) -> None:
    """Deny incomplete trusted context and every operation outside this release.

    The caller cannot supply a policy, scope replacement, override flag, or
    allow-list. ``RuntimeContext`` is established by the authentication
    boundary; database gates remain independent enforcement layers.
    """

    if not _has_runtime_identity(context):
        raise SecurityFloorDeniedError("security floor requires authenticated runtime context")
    if not isinstance(operation, MemoryOperation):
        raise SecurityFloorDeniedError("security floor denies unknown memory operation")
    if getattr(context, "project_id", None) is None or getattr(context, "session_id", None) is None:
        raise SecurityFloorDeniedError("security floor requires complete session scope")


def _has_runtime_identity(context: object) -> bool:
    """Accept only the immutable-context shape without importing Memory Core."""

    required_values = tuple(
        getattr(context, attribute, None) for attribute in ("actor_id", "tenant_id", "area_id")
    )
    return all(
        isinstance(value, str) and value.strip() == value and value for value in required_values
    )
