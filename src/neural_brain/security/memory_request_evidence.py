"""Fail-closed binding of Memory Core authority and policy evidence.

This module deliberately validates evidence before a future Memory Transition
Gate integration.  It never invokes a gate, writes protected state, or turns a
policy activation approval into per-request authority.
"""

from __future__ import annotations

from datetime import UTC, datetime

from neural_brain.security.activation import IndependentPolicyApproval
from neural_brain.security.authority import (
    MemoryAuthorityDeniedError,
    MemoryAuthorityResolver,
    MemoryAuthoritySnapshot,
    TrustedMemoryAuthorityContext,
)
from neural_brain.security.decision import PolicyDecisionBinding, PolicyDecisionRecord
from neural_brain.security.memory_risk import MemoryRiskOutcome


class MemoryRequestEvidenceDeniedError(PermissionError):
    """Raised when current authority, policy, approval, or audit evidence is incomplete."""


def validate_memory_request_evidence(
    *,
    resolver: MemoryAuthorityResolver,
    context: TrustedMemoryAuthorityContext,
    snapshot: MemoryAuthoritySnapshot,
    policy_decision: PolicyDecisionRecord,
    policy_activation_approval: IndependentPolicyApproval | None,
    now: datetime,
) -> None:
    """Require current, mutually-bound evidence without performing a transition.

    The resolver is consulted again so a captured snapshot cannot survive grant
    revocation, expiry, or a trusted-context change.  ``audit`` is an existing
    Memory Core policy obligation; this preflight validator cannot claim the
    later atomic gate audit has been committed.
    """

    if now.tzinfo is None or now.utcoffset() is None:
        raise MemoryRequestEvidenceDeniedError("evidence clock must be timezone-aware")
    current = now.astimezone(UTC)
    if current >= snapshot.valid_until:
        raise MemoryRequestEvidenceDeniedError("authority snapshot is expired")
    try:
        resolved = resolver.resolve(context, now=current)
    except MemoryAuthorityDeniedError as error:
        raise MemoryRequestEvidenceDeniedError("current authority evidence is denied") from error
    if (
        resolved.grant_id != snapshot.grant_id
        or resolved.grant_digest != snapshot.grant_digest
        or resolved.context_digest != snapshot.context_digest
        or resolved.request_digest != snapshot.request_digest
        or resolved.request != snapshot.request
        or resolved.valid_until != snapshot.valid_until
    ):
        raise MemoryRequestEvidenceDeniedError("authority snapshot does not match current context")

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
        policy_digest=policy_decision.binding.policy_digest,
    )
    if policy_decision.outcome is not MemoryRiskOutcome.ALLOW:
        raise MemoryRequestEvidenceDeniedError("policy decision does not allow the memory request")
    if not policy_decision.is_valid_for(binding, now=current):
        raise MemoryRequestEvidenceDeniedError(
            "policy decision is expired or not bound to authority"
        )
    if "audit" not in policy_decision.obligations:
        raise MemoryRequestEvidenceDeniedError(
            "policy decision lacks the required audit obligation"
        )

    _validate_required_policy_activation_approval(
        policy_decision=policy_decision,
        approval=policy_activation_approval,
        now=current,
    )


def _validate_required_policy_activation_approval(
    *,
    policy_decision: PolicyDecisionRecord,
    approval: IndependentPolicyApproval | None,
    now: datetime,
) -> None:
    """Bind only the existing policy-activation four-eyes record when required."""

    required_roles = set(policy_decision.required_approver_roles)
    if not required_roles:
        if approval is not None:
            raise MemoryRequestEvidenceDeniedError("unexpected policy activation approval")
        return
    if approval is None:
        raise MemoryRequestEvidenceDeniedError("required policy activation approval is missing")
    if approval.policy_digest != policy_decision.binding.policy_digest:
        raise MemoryRequestEvidenceDeniedError("policy activation approval has a different policy")
    if approval.approver_role not in required_roles:
        raise MemoryRequestEvidenceDeniedError("policy activation approval role is not required")
    if approval.approved_at > now:
        raise MemoryRequestEvidenceDeniedError("policy activation approval is from the future")
