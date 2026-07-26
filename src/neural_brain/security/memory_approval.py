"""Fail-closed approval evidence for one bounded Memory Core operation.

This module validates an immutable approval record against already protected
authority and policy evidence.  It is deliberately not a Memory Transition
Gate, an approval channel, or an authority source.
"""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from neural_brain.security.authority import MemoryAuthoritySnapshot
from neural_brain.security.decision import PolicyDecisionBinding, PolicyDecisionRecord
from neural_brain.security.memory_risk import MemoryRiskOutcome

MEMORY_OPERATION_APPROVAL_CONTRACT_VERSION = "memory-operation-approvals-v1"


class MemoryOperationApprovalDeniedError(PermissionError):
    """Raised when approval evidence is absent, stale, or bound to other facts."""


class _StrictApprovalModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)


class MemoryOperationApproval(_StrictApprovalModel):
    """Immutable approval evidence bound to exactly one protected request.

    The record attests a human review only when it is supplied through a future
    authenticated approval channel.  It neither resolves authority nor calls a
    gate, so it cannot authorize a transition by itself.
    """

    approval_id: str = Field(min_length=1, max_length=128)
    actor_id: str = Field(min_length=1, max_length=128)
    approver_id: str = Field(min_length=1, max_length=128)
    approver_role: str = Field(min_length=1, max_length=128)
    tenant_id: str = Field(min_length=1, max_length=128)
    area_id: str = Field(min_length=1, max_length=128)
    project_id: str = Field(min_length=1, max_length=128)
    session_id: str = Field(min_length=1, max_length=128)
    checkpoint_id: str = Field(min_length=1, max_length=128)
    operation: str = Field(min_length=1, max_length=64)
    resource: str = Field(min_length=1, max_length=256)
    data_class: str = Field(min_length=1, max_length=64)
    purpose: str = Field(min_length=1, max_length=128)
    environment: str = Field(min_length=1, max_length=128)
    authority_snapshot_digest: str = Field(pattern=r"^[0-9a-f]{64}$")
    request_digest: str = Field(pattern=r"^[0-9a-f]{64}$")
    policy_decision_id: str = Field(min_length=1, max_length=128)
    policy_digest: str = Field(pattern=r"^[0-9a-f]{64}$")
    approved_at: datetime
    valid_until: datetime

    @field_validator("approved_at", "valid_until")
    @classmethod
    def timezone_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("approval validity must include a timezone offset")
        return value.astimezone(UTC)

    @model_validator(mode="after")
    def independent_and_bounded(self) -> MemoryOperationApproval:
        if self.actor_id == self.approver_id:
            raise ValueError("memory operation actor cannot self-approve")
        if self.valid_until <= self.approved_at:
            raise ValueError("approval valid_until must be after approved_at")
        return self

    def digest(self) -> str:
        """Return canonical approval evidence digest for future durable custody."""

        body = json.dumps(self.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(body.encode("utf-8")).hexdigest()


def validate_memory_operation_approval_evidence(
    *,
    approval: MemoryOperationApproval,
    snapshot: MemoryAuthoritySnapshot,
    policy_decision: PolicyDecisionRecord,
    now: datetime,
) -> None:
    """Validate exact, current approval binding without authorizing a transition.

    Callers must separately run the S1-06.3 current-authority and policy
    evidence validation.  This bounded check cannot revive a revoked grant,
    create policy, or replace the Memory Transition Gate's atomic audit.
    """

    if now.tzinfo is None or now.utcoffset() is None:
        raise MemoryOperationApprovalDeniedError("approval clock must be timezone-aware")
    current = now.astimezone(UTC)
    if current >= approval.valid_until:
        raise MemoryOperationApprovalDeniedError("memory operation approval is expired")
    if approval.approved_at > current:
        raise MemoryOperationApprovalDeniedError("memory operation approval is from the future")
    if approval.approved_at < snapshot.captured_at:
        raise MemoryOperationApprovalDeniedError("approval predates authority evidence")
    if current >= snapshot.valid_until:
        raise MemoryOperationApprovalDeniedError("authority snapshot is expired")

    request = snapshot.request
    expected = {
        "actor_id": request.principal_id,
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
        "policy_decision_id": policy_decision.decision_id,
        "policy_digest": policy_decision.binding.policy_digest,
    }
    for field, value in expected.items():
        if getattr(approval, field) != value:
            raise MemoryOperationApprovalDeniedError(
                f"approval is not bound to the current {field}"
            )

    binding = PolicyDecisionBinding(
        actor_id=request.principal_id,
        tenant_id=request.tenant_id,
        area_id=request.area_id,
        project_id=request.project_id,
        session_id=request.session_id,
        authority_digest=snapshot.snapshot_digest,
        parameter_digest=snapshot.request_digest,
        checkpoint_id=request.checkpoint_id,
        policy_digest=policy_decision.binding.policy_digest,
    )
    if policy_decision.outcome is not MemoryRiskOutcome.ALLOW:
        raise MemoryOperationApprovalDeniedError(
            "policy decision does not allow the memory request"
        )
    if not policy_decision.is_valid_for(binding, now=current):
        raise MemoryOperationApprovalDeniedError(
            "policy decision is expired or not bound to approval"
        )
    if not policy_decision.required_approver_roles:
        raise MemoryOperationApprovalDeniedError("policy decision does not require this approval")
    if approval.approver_role not in policy_decision.required_approver_roles:
        raise MemoryOperationApprovalDeniedError("approval role is not required by policy")
