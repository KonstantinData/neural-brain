"""Unit evidence for the code-owned, non-overridable runtime Security Floor."""

from __future__ import annotations

import pytest

from neural_brain.memory import RuntimeContext
from neural_brain.security import (
    MemoryOperation,
    SecurityFloorDeniedError,
    authorize_memory_operation,
)


def _context(
    *, project_id: str | None = "project-a", session_id: str | None = "session-a"
) -> RuntimeContext:
    return RuntimeContext(
        actor_id="principal-a",
        tenant_id="tenant-a",
        area_id="area-a",
        project_id=project_id,
        session_id=session_id,
    )


@pytest.mark.parametrize("operation", tuple(MemoryOperation))
def test_authenticated_complete_context_admits_only_implemented_memory_operations(
    operation: MemoryOperation,
) -> None:
    authorize_memory_operation(_context(), operation)


@pytest.mark.parametrize("operation", ("memory_delete", "action_dispatch", "model_promotion"))
def test_unknown_or_unreleased_operations_are_non_overridably_denied(operation: str) -> None:
    with pytest.raises(SecurityFloorDeniedError, match="unknown memory operation"):
        authorize_memory_operation(_context(), operation)


def test_missing_project_or_session_scope_is_denied() -> None:
    with pytest.raises(SecurityFloorDeniedError, match="complete session scope"):
        authorize_memory_operation(
            _context(project_id=None, session_id=None), MemoryOperation.INGEST
        )


def test_untrusted_context_shape_is_denied() -> None:
    with pytest.raises(SecurityFloorDeniedError, match="authenticated runtime context"):
        authorize_memory_operation(object(), MemoryOperation.READ)
