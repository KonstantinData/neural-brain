"""Fail-closed Memory Core authority grants and immutable authorization snapshots.

These types are intentionally a protected-control-plane input.  They do not
accept consumer, integration, payload, or model supplied authority, and they
do not perform a Memory Transition Gate operation themselves.
"""

from __future__ import annotations

import fnmatch
import hashlib
import json
from collections.abc import Iterable
from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from neural_brain.security.memory_risk import DataClassification, MemoryLifecycleOperation

MEMORY_AUTHORITY_CONTRACT_VERSION = "memory-authority-grants-v1"


class MemoryAuthorityDeniedError(PermissionError):
    """Raised when no current protected authority grant admits an operation."""


def _canonical_digest(value: BaseModel) -> str:
    """Hash a strict model using the repository's canonical JSON encoding."""

    body = json.dumps(value.model_dump(mode="json"), sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )
    return hashlib.sha256(body).hexdigest()


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

        return _canonical_digest(self)


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


class TrustedMemoryAuthorityContext(_StrictAuthorityModel):
    """Authenticated resolver input, deliberately separate from payload metadata.

    ``issuer_id`` and ``grant_ids`` are Protected Control Plane facts.  They
    identify which catalogued grants the authenticated runtime is allowed to
    present; neither a request payload nor a derived context may add a grant.
    """

    issuer_id: str = Field(min_length=1, max_length=128)
    grant_ids: tuple[str, ...] = Field(min_length=1)
    request: TrustedMemoryAuthorityRequest

    @field_validator("grant_ids")
    @classmethod
    def unique_grant_ids(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if len(value) != len(set(value)) or any(not item.strip() for item in value):
            raise ValueError("trusted grant identifiers must be non-empty and unique")
        return tuple(sorted(value))

    def digest(self) -> str:
        """Return a canonical digest of the authenticated resolver input."""

        return _canonical_digest(self)


def derive_memory_authority_context(
    parent: TrustedMemoryAuthorityContext,
    *,
    request: TrustedMemoryAuthorityRequest,
    grant_ids: tuple[str, ...],
) -> TrustedMemoryAuthorityContext:
    """Create a child context that cannot change authenticated identity or scope.

    A child may select a strict subset of the parent's grants.  Operation and
    resource admission remains the resolver's responsibility against that
    subset, so a child cannot turn payload metadata into a broader grant.
    """

    if not grant_ids or len(grant_ids) != len(set(grant_ids)):
        raise MemoryAuthorityDeniedError("derived authority grants are invalid")
    if not set(grant_ids).issubset(parent.grant_ids):
        raise MemoryAuthorityDeniedError("derived authority context widens grants")
    parent_request = parent.request
    if (
        request.principal_id != parent_request.principal_id
        or request.tenant_id != parent_request.tenant_id
        or request.area_id != parent_request.area_id
        or request.project_id != parent_request.project_id
        or request.session_id != parent_request.session_id
    ):
        raise MemoryAuthorityDeniedError("derived authority context changes trusted scope")
    return TrustedMemoryAuthorityContext(
        issuer_id=parent.issuer_id,
        grant_ids=grant_ids,
        request=request,
    )


class MemoryAuthoritySnapshot(_StrictAuthorityModel):
    """Immutable evidence that a particular current grant admitted one request."""

    snapshot_id: str = Field(min_length=1, max_length=128)
    grant_id: str = Field(min_length=1, max_length=128)
    grant_digest: str = Field(pattern=r"^[0-9a-f]{64}$")
    context_digest: str = Field(pattern=r"^[0-9a-f]{64}$")
    request_digest: str = Field(pattern=r"^[0-9a-f]{64}$")
    snapshot_digest: str = Field(pattern=r"^[0-9a-f]{64}$")
    request: TrustedMemoryAuthorityRequest
    captured_at: datetime
    valid_until: datetime

    @field_validator("captured_at", "valid_until")
    @classmethod
    def timezone_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("snapshot validity must include a timezone offset")
        return value.astimezone(UTC)

    def canonical_digest(self) -> str:
        """Return the canonical digest for this immutable evidence record."""

        body = self.model_dump(mode="json", exclude={"snapshot_id", "snapshot_digest"})
        encoded = json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    @model_validator(mode="after")
    def verify_canonical_digests(self) -> MemoryAuthoritySnapshot:
        if self.request_digest != _canonical_digest(self.request):
            raise ValueError("snapshot request digest is not canonical")
        if self.snapshot_digest != self.canonical_digest():
            raise ValueError("snapshot digest is not canonical")
        return self


class MemoryAuthorityResolver:
    """Resolve only authenticated, catalogued Memory Core grants fail-closed."""

    def __init__(self, grants: Iterable[MemoryAuthorityGrant]) -> None:
        catalog: dict[str, MemoryAuthorityGrant] = {}
        for grant in grants:
            existing = catalog.get(grant.grant_id)
            if existing is not None and existing.digest() != grant.digest():
                raise MemoryAuthorityDeniedError("authority grant catalog is ambiguous")
            catalog[grant.grant_id] = grant
        self._catalog = catalog

    def resolve(
        self,
        context: TrustedMemoryAuthorityContext,
        *,
        now: datetime,
    ) -> MemoryAuthoritySnapshot:
        """Return one deterministic snapshot or deny before a protected transition.

        A resolver never accepts payload identity, scope, issuer, or authority
        metadata.  It only considers the exact authenticated grant identifiers
        in ``context`` and chooses the canonical lowest matching grant digest.
        """

        if now.tzinfo is None or now.utcoffset() is None:
            raise MemoryAuthorityDeniedError("authority clock must be timezone-aware")
        candidates: list[MemoryAuthorityGrant] = []
        for grant_id in context.grant_ids:
            grant = self._catalog.get(grant_id)
            if grant is None:
                raise MemoryAuthorityDeniedError("memory authority grant is unknown")
            if grant.issuer_id != context.issuer_id:
                raise MemoryAuthorityDeniedError(
                    "memory authority issuer does not match trusted context"
                )
            _validate_memory_authority_grant(grant, context.request, now=now)
            candidates.append(grant)
        if not candidates:
            raise MemoryAuthorityDeniedError("no current memory authority grant admits request")
        selected = min(candidates, key=lambda grant: (grant.digest(), grant.grant_id))
        current = now.astimezone(UTC)
        request_digest = _canonical_digest(context.request)
        context_digest = context.digest()
        preliminary = {
            "grant_id": selected.grant_id,
            "grant_digest": selected.digest(),
            "context_digest": context_digest,
            "request_digest": request_digest,
            "request": context.request.model_dump(mode="json"),
            "captured_at": current.isoformat().replace("+00:00", "Z"),
            "valid_until": selected.valid_until.isoformat().replace("+00:00", "Z"),
        }
        snapshot_digest = hashlib.sha256(
            json.dumps(preliminary, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        return MemoryAuthoritySnapshot(
            snapshot_id=f"authority-{snapshot_digest}",
            grant_id=selected.grant_id,
            grant_digest=selected.digest(),
            context_digest=context_digest,
            request_digest=request_digest,
            snapshot_digest=snapshot_digest,
            request=context.request,
            captured_at=current,
            valid_until=selected.valid_until,
        )


def _validate_memory_authority_grant(
    grant: MemoryAuthorityGrant,
    request: TrustedMemoryAuthorityRequest,
    *,
    now: datetime,
) -> None:
    """Validate a grant against protected request facts without producing evidence.

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
    return None


def authorize_memory_authority(
    grant: MemoryAuthorityGrant,
    request: TrustedMemoryAuthorityRequest,
    *,
    now: datetime,
) -> MemoryAuthoritySnapshot:
    """Authorize one isolated grant through the deterministic resolver seam."""

    _validate_memory_authority_grant(grant, request, now=now)
    context = TrustedMemoryAuthorityContext(
        issuer_id=grant.issuer_id,
        grant_ids=(grant.grant_id,),
        request=request,
    )
    # The legacy one-grant helper remains a narrow test seam.  Resolver callers
    # must pass an independently authenticated issuer and catalog selection.
    return MemoryAuthorityResolver((grant,)).resolve(context, now=now)
