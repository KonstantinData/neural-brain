"""S1-06.3 evidence binding tests without Memory Transition Gate integration."""

from datetime import UTC, datetime, timedelta

import pytest

from neural_brain.security.activation import IndependentPolicyApproval
from neural_brain.security.authority import (
    GrantStatus,
    MemoryAuthorityGrant,
    MemoryAuthorityResolver,
    MemoryAuthoritySnapshot,
    TrustedMemoryAuthorityContext,
    TrustedMemoryAuthorityRequest,
)
from neural_brain.security.decision import PolicyDecisionBinding, PolicyDecisionRecord
from neural_brain.security.memory_request_evidence import (
    MemoryRequestEvidenceDeniedError,
    validate_memory_request_evidence,
)
from neural_brain.security.memory_risk import MemoryLifecycleOperation, MemoryRiskOutcome

NOW = datetime(2026, 7, 26, 18, 30, tzinfo=UTC)


def _request(**changes: object) -> TrustedMemoryAuthorityRequest:
    values: dict[str, object] = {
        "principal_id": "operator-a",
        "tenant_id": "tenant-a",
        "area_id": "area-a",
        "project_id": "project-a",
        "session_id": "session-a",
        "checkpoint_id": "checkpoint-a",
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
        "valid_until": NOW + timedelta(minutes=5),
    }
    return MemoryAuthorityGrant.model_validate(values | changes)


def _context(request: TrustedMemoryAuthorityRequest | None = None) -> TrustedMemoryAuthorityContext:
    return TrustedMemoryAuthorityContext(
        issuer_id="security-officer", grant_ids=("grant-a",), request=request or _request()
    )


def _decision(snapshot_digest: str, request_digest: str, **changes: object) -> PolicyDecisionRecord:
    binding = PolicyDecisionBinding(
        actor_id="operator-a",
        tenant_id="tenant-a",
        area_id="area-a",
        project_id="project-a",
        session_id="session-a",
        authority_digest=snapshot_digest,
        parameter_digest=request_digest,
        checkpoint_id="checkpoint-a",
        policy_digest="c" * 64,
    )
    values: dict[str, object] = {
        "decision_id": "decision-a",
        "binding": binding,
        "outcome": MemoryRiskOutcome.ALLOW,
        "reason_codes": ("gated_intake_admitted",),
        "obligations": ("audit",),
        "required_approver_roles": ("security_reviewer",),
        "valid_until": NOW + timedelta(minutes=1),
    }
    return PolicyDecisionRecord.model_validate(values | changes)


def _approval(**changes: object) -> IndependentPolicyApproval:
    values: dict[str, object] = {
        "policy_digest": "c" * 64,
        "author_id": "policy-author",
        "approver_id": "security-reviewer",
        "approver_role": "security_reviewer",
        "approved_at": NOW - timedelta(minutes=1),
    }
    return IndependentPolicyApproval.model_validate(values | changes)


def _evidence() -> tuple[
    MemoryAuthorityResolver, TrustedMemoryAuthorityContext, MemoryAuthoritySnapshot
]:
    resolver = MemoryAuthorityResolver((_grant(),))
    context = _context()
    return resolver, context, resolver.resolve(context, now=NOW)


def test_current_snapshot_policy_approval_and_audit_obligation_bind_exact_request() -> None:
    resolver, context, snapshot = _evidence()
    assert hasattr(snapshot, "snapshot_digest")
    validate_memory_request_evidence(
        resolver=resolver,
        context=context,
        snapshot=snapshot,
        policy_decision=_decision(snapshot.snapshot_digest, snapshot.request_digest),
        policy_activation_approval=_approval(),
        now=NOW,
    )


@pytest.mark.parametrize(
    ("changed_context", "decision_changes", "approval_changes", "message"),
    [
        ({"tenant_id": "tenant-b"}, {}, {}, "current authority"),
        ({}, {"valid_until": NOW}, {}, "policy decision"),
        ({}, {"obligations": ()}, {}, "audit obligation"),
        ({}, {}, {"approver_role": "operator"}, "role"),
        ({}, {}, {"approved_at": NOW + timedelta(seconds=1)}, "future"),
    ],
)
def test_scope_policy_approval_and_audit_mismatch_deny(
    changed_context: dict[str, object],
    decision_changes: dict[str, object],
    approval_changes: dict[str, object],
    message: str,
) -> None:
    resolver, _, snapshot = _evidence()
    candidate_context = _context(_request(**changed_context))
    with pytest.raises(MemoryRequestEvidenceDeniedError, match=message):
        validate_memory_request_evidence(
            resolver=resolver,
            context=candidate_context,
            snapshot=snapshot,
            policy_decision=_decision(
                snapshot.snapshot_digest, snapshot.request_digest, **decision_changes
            ),
            policy_activation_approval=_approval(**approval_changes),
            now=NOW,
        )


def test_revoked_or_expired_current_grant_invalidates_captured_snapshot() -> None:
    _, context, snapshot = _evidence()
    for grant in (_grant(status=GrantStatus.REVOKED), _grant(valid_until=NOW)):
        with pytest.raises(MemoryRequestEvidenceDeniedError, match="current authority"):
            validate_memory_request_evidence(
                resolver=MemoryAuthorityResolver((grant,)),
                context=context,
                snapshot=snapshot,
                policy_decision=_decision(snapshot.snapshot_digest, snapshot.request_digest),
                policy_activation_approval=_approval(),
                now=NOW,
            )


def test_snapshot_or_policy_binding_digest_substitution_is_denied() -> None:
    resolver, context, snapshot = _evidence()
    substituted = _decision("d" * 64, snapshot.request_digest)
    with pytest.raises(MemoryRequestEvidenceDeniedError, match="policy decision"):
        validate_memory_request_evidence(
            resolver=resolver,
            context=context,
            snapshot=snapshot,
            policy_decision=substituted,
            policy_activation_approval=_approval(),
            now=NOW,
        )
