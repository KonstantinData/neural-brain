"""S1-06.4 evidence tests for bounded Memory Core human approvals."""

from datetime import UTC, datetime, timedelta

import pytest

from neural_brain.security.authority import (
    MemoryAuthorityGrant,
    MemoryAuthorityResolver,
    MemoryAuthoritySnapshot,
    TrustedMemoryAuthorityContext,
    TrustedMemoryAuthorityRequest,
)
from neural_brain.security.decision import PolicyDecisionBinding, PolicyDecisionRecord
from neural_brain.security.memory_approval import (
    MemoryOperationApproval,
    MemoryOperationApprovalDeniedError,
    validate_memory_operation_approval_evidence,
)
from neural_brain.security.memory_risk import MemoryLifecycleOperation, MemoryRiskOutcome

NOW = datetime(2026, 7, 26, 19, 0, tzinfo=UTC)


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


def _snapshot() -> MemoryAuthoritySnapshot:
    request = _request()
    grant = MemoryAuthorityGrant(
        grant_id="grant-a",
        issuer_id="security-officer",
        principal_id=request.principal_id,
        tenant_id=request.tenant_id,
        area_id=request.area_id,
        project_id=request.project_id,
        session_id=request.session_id,
        operations=(request.operation,),
        resource_patterns=("memory_core/observations/*",),
        data_classes=(request.data_class,),
        purposes=(request.purpose,),
        environments=(request.environment,),
        valid_from=NOW - timedelta(minutes=1),
        valid_until=NOW + timedelta(minutes=5),
    )
    return MemoryAuthorityResolver((grant,)).resolve(
        TrustedMemoryAuthorityContext(
            issuer_id="security-officer", grant_ids=("grant-a",), request=request
        ),
        now=NOW,
    )


def _decision(snapshot: MemoryAuthoritySnapshot, **changes: object) -> PolicyDecisionRecord:
    request = snapshot.request
    binding = PolicyDecisionBinding(
        actor_id=request.principal_id,
        tenant_id=request.tenant_id,
        area_id=request.area_id,
        project_id=request.project_id,
        session_id=request.session_id,
        authority_digest=snapshot.snapshot_digest,
        parameter_digest=snapshot.request_digest,
        checkpoint_id=request.checkpoint_id,
        policy_digest="d" * 64,
    )
    values: dict[str, object] = {
        "decision_id": "decision-a",
        "binding": binding,
        "outcome": MemoryRiskOutcome.ALLOW,
        "reason_codes": ("human_review_required",),
        "obligations": ("audit",),
        "required_approver_roles": ("memory_reviewer",),
        "valid_until": NOW + timedelta(minutes=2),
    }
    return PolicyDecisionRecord.model_validate(values | changes)


def _approval(
    snapshot: MemoryAuthoritySnapshot, decision: PolicyDecisionRecord, **changes: object
) -> MemoryOperationApproval:
    request = snapshot.request
    values: dict[str, object] = {
        "approval_id": "approval-a",
        "actor_id": request.principal_id,
        "approver_id": "reviewer-b",
        "approver_role": "memory_reviewer",
        "tenant_id": request.tenant_id,
        "area_id": request.area_id,
        "project_id": request.project_id,
        "session_id": request.session_id,
        "checkpoint_id": request.checkpoint_id,
        "operation": request.operation.value,
        "resource": request.resource,
        "data_class": request.data_class,
        "purpose": request.purpose,
        "environment": request.environment,
        "authority_snapshot_digest": snapshot.snapshot_digest,
        "request_digest": snapshot.request_digest,
        "policy_decision_id": decision.decision_id,
        "policy_digest": decision.binding.policy_digest,
        "approved_at": NOW,
        "valid_until": NOW + timedelta(minutes=1),
    }
    return MemoryOperationApproval.model_validate(values | changes)


def test_approval_binds_one_memory_operation_without_authorizing_a_transition() -> None:
    snapshot = _snapshot()
    decision = _decision(snapshot)
    approval = _approval(snapshot, decision)

    validate_memory_operation_approval_evidence(
        approval=approval, snapshot=snapshot, policy_decision=decision, now=NOW
    )
    assert len(approval.digest()) == 64


@pytest.mark.parametrize(
    ("approval_changes", "decision_changes", "message"),
    [
        ({"tenant_id": "tenant-b"}, {}, "tenant_id"),
        ({"actor_id": "operator-b"}, {}, "actor_id"),
        ({"operation": "deletion"}, {}, "operation"),
        ({"resource": "memory_core/observations/43"}, {}, "resource"),
        ({"purpose": "memory_retrieval"}, {}, "purpose"),
        ({"data_class": "restricted"}, {}, "data_class"),
        ({"authority_snapshot_digest": "a" * 64}, {}, "authority_snapshot_digest"),
        ({"policy_digest": "b" * 64}, {}, "policy_digest"),
        ({"approver_role": "operator"}, {}, "role"),
        ({}, {"outcome": MemoryRiskOutcome.DENY}, "does not allow"),
        ({}, {"required_approver_roles": ()}, "does not require"),
    ],
)
def test_scope_actor_operation_resource_purpose_data_policy_role_and_expiry_mismatch_deny(
    approval_changes: dict[str, object], decision_changes: dict[str, object], message: str
) -> None:
    snapshot = _snapshot()
    decision = _decision(snapshot, **decision_changes)
    approval = _approval(snapshot, decision, **approval_changes)
    with pytest.raises(MemoryOperationApprovalDeniedError, match=message):
        validate_memory_operation_approval_evidence(
            approval=approval, snapshot=snapshot, policy_decision=decision, now=NOW
        )


def test_actor_cannot_self_approve_and_unknown_payload_fields_are_rejected() -> None:
    snapshot = _snapshot()
    decision = _decision(snapshot)
    with pytest.raises(ValueError, match="cannot self-approve"):
        _approval(snapshot, decision, approver_id="operator-a")
    with pytest.raises(ValueError, match="Extra inputs are not permitted"):
        MemoryOperationApproval.model_validate(
            _approval(snapshot, decision).model_dump() | {"payload_authority": "allow"}
        )


def test_expired_approval_is_denied_after_valid_construction() -> None:
    snapshot = _snapshot()
    decision = _decision(snapshot)
    approval = _approval(snapshot, decision, valid_until=NOW + timedelta(seconds=1))
    with pytest.raises(MemoryOperationApprovalDeniedError, match="expired"):
        validate_memory_operation_approval_evidence(
            approval=approval,
            snapshot=snapshot,
            policy_decision=decision,
            now=NOW + timedelta(seconds=1),
        )


def test_future_or_pre_authority_evidence_approval_is_denied() -> None:
    snapshot = _snapshot()
    decision = _decision(snapshot)
    for approval in (
        _approval(snapshot, decision, approved_at=NOW + timedelta(seconds=1)),
        _approval(
            snapshot,
            decision,
            approved_at=NOW - timedelta(seconds=1),
            valid_until=NOW + timedelta(minutes=1),
        ),
    ):
        with pytest.raises(MemoryOperationApprovalDeniedError, match=r"future|predates"):
            validate_memory_operation_approval_evidence(
                approval=approval, snapshot=snapshot, policy_decision=decision, now=NOW
            )
