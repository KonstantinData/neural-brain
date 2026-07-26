"""Unit evidence for S1-06.1 fail-closed Memory Core authority grants."""

from datetime import UTC, datetime, timedelta

import pytest

from neural_brain.security.authority import (
    GrantStatus,
    MemoryAuthorityDeniedError,
    MemoryAuthorityGrant,
    MemoryAuthorityResolver,
    MemoryAuthoritySnapshot,
    TrustedMemoryAuthorityContext,
    TrustedMemoryAuthorityRequest,
    authorize_memory_authority,
    derive_memory_authority_context,
)
from neural_brain.security.memory_risk import MemoryLifecycleOperation

NOW = datetime(2026, 7, 26, tzinfo=UTC)


def _request(**changes: object) -> TrustedMemoryAuthorityRequest:
    values: dict[str, object] = {
        "principal_id": "operator-a",
        "tenant_id": "tenant-a",
        "area_id": "area-a",
        "project_id": "project-a",
        "session_id": "session-a",
        "operation": MemoryLifecycleOperation.INTAKE,
        "resource": "memory_core/observations/42",
        "data_class": "internal",
        "purpose": "memory_intake",
        "environment": "test",
    }
    return TrustedMemoryAuthorityRequest.model_validate(values | changes)


def _grant(**changes: object) -> MemoryAuthorityGrant:
    values: dict[str, object] = {
        "grant_id": "grant-a",
        "issuer_id": "security-officer",
        "principal_id": "operator-a",
        "tenant_id": "tenant-a",
        "area_id": "area-a",
        "project_id": "project-a",
        "session_id": "session-a",
        "operations": (MemoryLifecycleOperation.INTAKE,),
        "resource_patterns": ("memory_core/observations/*",),
        "data_classes": ("internal",),
        "purposes": ("memory_intake",),
        "environments": ("test",),
        "valid_from": NOW - timedelta(minutes=1),
        "valid_until": NOW + timedelta(minutes=1),
    }
    return MemoryAuthorityGrant.model_validate(values | changes)


def test_current_exact_grant_produces_digest_bound_snapshot() -> None:
    grant = _grant()
    snapshot = authorize_memory_authority(grant, _request(), now=NOW)
    assert snapshot.grant_id == grant.grant_id
    assert snapshot.grant_digest == grant.digest()
    assert snapshot.request == _request()


@pytest.mark.parametrize(
    ("grant_changes", "request_changes", "message"),
    [
        ({"status": GrantStatus.REVOKED}, {}, "not active"),
        ({"valid_until": NOW}, {}, "expired"),
        ({}, {"tenant_id": "tenant-b"}, "trusted scope"),
        ({}, {"operation": MemoryLifecycleOperation.DELETION}, "operation"),
        ({}, {"resource": "memory_core/checkpoints/42"}, "resource"),
        ({}, {"data_class": "restricted"}, "data class"),
        ({}, {"purpose": "memory_retrieval"}, "purpose or environment"),
        ({}, {"environment": "production"}, "purpose or environment"),
    ],
)
def test_unknown_revoked_expired_or_widened_request_is_denied(
    grant_changes: dict[str, object], request_changes: dict[str, object], message: str
) -> None:
    with pytest.raises(MemoryAuthorityDeniedError, match=message):
        authorize_memory_authority(_grant(**grant_changes), _request(**request_changes), now=NOW)


def test_session_grant_requires_a_project_and_non_authoritative_extra_fields_are_rejected() -> None:
    with pytest.raises(ValueError, match="session authority requires project"):
        _grant(project_id=None)
    with pytest.raises(ValueError, match="Extra inputs are not permitted"):
        TrustedMemoryAuthorityRequest.model_validate(
            {**_request().model_dump(), "consumer_id": "x"}
        )


def _context(
    grant_ids: tuple[str, ...] = ("grant-a",), **changes: object
) -> TrustedMemoryAuthorityContext:
    values: dict[str, object] = {
        "issuer_id": "security-officer",
        "grant_ids": grant_ids,
        "request": _request(),
    }
    return TrustedMemoryAuthorityContext.model_validate(values | changes)


def test_resolver_is_deterministic_and_snapshot_digests_are_canonical_and_immutable() -> None:
    first = _grant(grant_id="grant-a")
    second = _grant(grant_id="grant-b")
    context = _context(("grant-b", "grant-a"))
    snapshot = MemoryAuthorityResolver((second, first)).resolve(context, now=NOW)
    reordered = MemoryAuthorityResolver((first, second)).resolve(context, now=NOW)

    assert snapshot == reordered
    assert snapshot.snapshot_id == f"authority-{snapshot.snapshot_digest}"
    assert len(snapshot.request_digest) == 64
    assert snapshot.snapshot_digest == snapshot.canonical_digest()
    with pytest.raises(ValueError, match="snapshot digest is not canonical"):
        MemoryAuthoritySnapshot.model_validate(
            {**snapshot.model_dump(), "snapshot_digest": "0" * 64}
        )


@pytest.mark.parametrize(
    ("context", "message"),
    [
        (_context(("unknown-grant",)), "unknown"),
        (_context(issuer_id="untrusted-issuer"), "issuer"),
        (_context(request=_request(tenant_id="tenant-b")), "trusted scope"),
    ],
)
def test_resolver_denies_unknown_issuer_or_scope_mismatched_context(
    context: TrustedMemoryAuthorityContext, message: str
) -> None:
    with pytest.raises(MemoryAuthorityDeniedError, match=message):
        MemoryAuthorityResolver((_grant(),)).resolve(context, now=NOW)


def test_resolver_does_not_ignore_a_revoked_grant_presented_by_trusted_context() -> None:
    with pytest.raises(MemoryAuthorityDeniedError, match="not active"):
        MemoryAuthorityResolver(
            (_grant(grant_id="grant-a"), _grant(grant_id="grant-b", status=GrantStatus.REVOKED))
        ).resolve(_context(("grant-a", "grant-b")), now=NOW)


def test_derived_context_can_only_reduce_grants_and_preserve_authenticated_scope() -> None:
    parent = _context(("grant-a", "grant-b"))
    child = derive_memory_authority_context(
        parent, request=_request(resource="memory_core/observations/43"), grant_ids=("grant-a",)
    )
    assert child.issuer_id == parent.issuer_id
    assert child.grant_ids == ("grant-a",)
    with pytest.raises(MemoryAuthorityDeniedError, match="widens grants"):
        derive_memory_authority_context(
            parent, request=_request(), grant_ids=("grant-a", "foreign-grant")
        )
    with pytest.raises(MemoryAuthorityDeniedError, match="changes trusted scope"):
        derive_memory_authority_context(
            parent, request=_request(area_id="area-b"), grant_ids=("grant-a",)
        )
    with pytest.raises(ValueError, match="Extra inputs are not permitted"):
        TrustedMemoryAuthorityContext.model_validate(
            {**parent.model_dump(), "payload_authority": "allow"}
        )
