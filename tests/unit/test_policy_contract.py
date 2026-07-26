"""Evidence for the bounded, canonical, expiry-bound policy compiler."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from neural_brain.security import (
    POLICY_SCHEMA_VERSION,
    MemoryLifecycleOperation,
    PolicyCompilationError,
    PolicyDocument,
    canonical_policy_json,
    compile_policy,
)

_NOW = datetime(2026, 7, 26, 14, 0, tzinfo=UTC)


def _policy(**changes: object) -> PolicyDocument:
    values: dict[str, object] = {
        "schema_version": POLICY_SCHEMA_VERSION,
        "policy_id": "memory.intake.default",
        "expires_at": _NOW + timedelta(days=1),
        "allowed_operations": (MemoryLifecycleOperation.INTAKE,),
        "allowed_classifications": ("public", "internal"),
    }
    values.update(changes)
    return PolicyDocument.model_validate(values)


def test_compile_binds_a_canonical_digest_and_expiry() -> None:
    policy = _policy()

    compiled = compile_policy(policy, now=_NOW)

    assert compiled.schema_version == POLICY_SCHEMA_VERSION
    assert len(compiled.policy_digest) == 64
    assert compiled.expires_at == policy.expires_at
    assert canonical_policy_json(policy) == canonical_policy_json(_policy())


def test_canonical_digest_changes_when_any_policy_fact_changes() -> None:
    first = compile_policy(_policy(), now=_NOW)
    second = compile_policy(_policy(allowed_classifications=("public",)), now=_NOW)

    assert first.policy_digest != second.policy_digest


def test_expired_policy_and_naive_compiler_clock_are_denied() -> None:
    with pytest.raises(PolicyCompilationError, match="expired"):
        compile_policy(_policy(expires_at=_NOW), now=_NOW)
    with pytest.raises(PolicyCompilationError, match="timezone-aware"):
        compile_policy(_policy(), now=_NOW.replace(tzinfo=None))


@pytest.mark.parametrize(
    "operation",
    (MemoryLifecycleOperation.RETRIEVAL, MemoryLifecycleOperation.PROMOTION),
)
def test_policy_cannot_widen_the_current_security_floor(
    operation: MemoryLifecycleOperation,
) -> None:
    with pytest.raises(PolicyCompilationError, match="cannot widen"):
        compile_policy(_policy(allowed_operations=(operation,)), now=_NOW)


def test_schema_rejects_unknown_fields_duplicates_and_naive_expiry() -> None:
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        PolicyDocument.model_validate({**_policy().model_dump(), "override": True})
    with pytest.raises(ValidationError, match="unique"):
        _policy(allowed_classifications=("public", "public"))
    with pytest.raises(ValidationError, match="timezone"):
        _policy(expires_at=_NOW.replace(tzinfo=None))
