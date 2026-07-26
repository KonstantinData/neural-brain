"""Fail-closed Memory Core authority grants and immutable authorization snapshots.

These types are intentionally a protected-control-plane input.  They do not
accept consumer, integration, payload, or model supplied authority, and they
do not perform a Memory Transition Gate operation themselves.
"""

from __future__ import annotations

import fnmatch
import hashlib
import json
from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from neural_brain.security.memory_risk import DataClassification, MemoryLifecycleOperation

MEMORY_AUTHORITY_CONTRACT_VERSION = "memory-authority-grants-v1"


class MemoryAuthorityDeniedError(PermissionError):
    """Raised when no current protected authority grant admits an operation."""


class GrantStatus(StrEnum):
    """Lifecycle state for a catalogued authority grant."""

    ACTIVE = "active"
    REVOKED = "revoked"
    EXPIRED = "expired"


class _StrictAuthorityModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)


class MemoryAuthorityGrant(_StrictAuthorityModel):
    """One issuer-bound, scope-bound, expiry-bound Memory Core grant.

    A grant is necessary but not sufficient: the Security Floor, lifecycle
    policy, risk decision, and Memory Transition Gate retain their independent
    responsibilities.
    """

    grant_id: str = Field(min_length=1, max_length=128)
    issuer_id: str = Field(min_length=1, max_length=128)
    principal_id: str = Field(min_length=1, max_length=128)
    tenant_id: str = Field(min_length=1, max_length=128)
    area_id: str = Field(min_length=1, max_length=128)
    project_id: str | None = Field(default=None, min_length=1, max_length=128)
    session_id: str | None = Field(default=None, min_length=1, max_length=128)
    operations: tuple[MemoryLifecycleOperation, ...] = Field(min_length=1)
    resource_patterns: tuple[str, ...] = Field(min_length=1)
    data_classes: tuple[DataClassification, ...] = Field(min_length=1)
    purposes: tuple[str, ...] = Field(min_length=1)
    environments: tuple[str, ...] = Field(min_length=1)
    valid_from: datetime
    valid_until: datetime
    status: GrantStatus = GrantStatus.ACTIVE

    @field_validator("resource_patterns", "purposes", "environments")
    @classmethod
    def nonempty_unique_values(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if len(value) != len(set(value)) or any(not item.strip() for item in value):
            raise ValueError("grant values must be non-empty and unique")
        return value

    @field_validator("operations", "data_classes")
    @classmethod
    def unique_values(cls, value: tuple[object, ...]) -> tuple[object, ...]:
        if len(value) != len(set(value)):
            raise ValueError("grant values must be unique")
        return value

    @field_validator("valid_from", "valid_until")
    @classmethod
    def timezone_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("grant validity must include a timezone offset")
        return value.astimezone(UTC)

    @model_validator(mode="after")
    def bounded_scope_and_validity(self) -> MemoryAuthorityGrant:
        if self.session_id is not None and self.project_id is None:
            raise ValueError("session authority requires project authority")
        if self.valid_until <= self.valid_from:
            raise ValueError("grant valid_until must be after valid_from")
        return self

    def digest(self) -> str:
        """Return the canonical grant digest that binds an authority snapshot."""

        body = json.dumps(
            self.model_dump(mode="json"), sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        return hashlib.sha256(body).hexdigest()


class TrustedMemoryAuthorityRequest(_StrictAuthorityModel):
    """Protected request facts derived from runtime context, never payload input."""

    principal_id: str = Field(min_length=1, max_length=128)
    tenant_id: str = Field(min_length=1, max_length=128)
    area_id: str = Field(min_length=1, max_length=128)
    project_id: str = Field(min_length=1, max_length=128)
    session_id: str = Field(min_length=1, max_length=128)
    operation: MemoryLifecycleOperation
    resource: str = Field(min_length=1, max_length=256)
    data_class: DataClassification
    purpose: str = Field(min_length=1, max_length=128)
    environment: str = Field(min_length=1, max_length=128)


class MemoryAuthoritySnapshot(_StrictAuthorityModel):
    """Immutable evidence that a particular current grant admitted one request."""

    snapshot_id: str = Field(min_length=1, max_length=128)
    grant_id: str = Field(min_length=1, max_length=128)
    grant_digest: str = Field(pattern=r"^[0-9a-f]{64}$")
    request: TrustedMemoryAuthorityRequest
    captured_at: datetime
    valid_until: datetime

    @field_validator("captured_at", "valid_until")
    @classmethod
    def timezone_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("snapshot validity must include a timezone offset")
        return value.astimezone(UTC)


def authorize_memory_authority(
    grant: MemoryAuthorityGrant,
    request: TrustedMemoryAuthorityRequest,
    *,
    now: datetime,
) -> MemoryAuthoritySnapshot:
    """Validate a grant against protected request facts and return bound evidence.

    Unknown, inactive, expired, scope-mismatched, or widened requests deny by
    default.  In particular, a grant can only narrow the authenticated runtime
    scope; it cannot replace it or turn an integration into an authority issuer.
    """

    if now.tzinfo is None or now.utcoffset() is None:
        raise MemoryAuthorityDeniedError("authority clock must be timezone-aware")
    current = now.astimezone(UTC)
    if grant.status is not GrantStatus.ACTIVE:
        raise MemoryAuthorityDeniedError("memory authority grant is not active")
    if not grant.valid_from <= current < grant.valid_until:
        raise MemoryAuthorityDeniedError("memory authority grant is expired or not yet valid")
    if (
        grant.principal_id != request.principal_id
        or grant.tenant_id != request.tenant_id
        or grant.area_id != request.area_id
        or (grant.project_id is not None and grant.project_id != request.project_id)
        or (grant.session_id is not None and grant.session_id != request.session_id)
    ):
        raise MemoryAuthorityDeniedError("memory authority grant does not match trusted scope")
    if request.operation not in grant.operations:
        raise MemoryAuthorityDeniedError("memory operation is not granted")
    if not any(
        fnmatch.fnmatchcase(request.resource, pattern) for pattern in grant.resource_patterns
    ):
        raise MemoryAuthorityDeniedError("memory resource is not granted")
    if request.data_class not in grant.data_classes:
        raise MemoryAuthorityDeniedError("memory data class is not granted")
    if request.purpose not in grant.purposes or request.environment not in grant.environments:
        raise MemoryAuthorityDeniedError("memory purpose or environment is not granted")
    return MemoryAuthoritySnapshot(
        snapshot_id=f"authority-{grant.grant_id}-{request.operation}",
        grant_id=grant.grant_id,
        grant_digest=grant.digest(),
        request=request,
        captured_at=current,
        valid_until=grant.valid_until,
    )
