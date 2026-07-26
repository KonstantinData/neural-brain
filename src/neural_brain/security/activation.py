"""Fail-closed policy activation evidence and four-eyes separation."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import override

from pydantic import BaseModel, ConfigDict, Field, field_validator

from neural_brain.security.policy import CompiledPolicy


class PolicyActivationDeniedError(ValueError):
    """Raised when a policy lacks complete activation evidence."""


class _StrictActivationModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)


class PolicyRegressionEvidence(_StrictActivationModel):
    """Immutable result of the invariant suite bound to one policy digest."""

    policy_digest: str = Field(pattern=r"^[0-9a-f]{64}$")
    suite_digest: str = Field(pattern=r"^[0-9a-f]{64}$")
    passed: bool
    executed_at: datetime

    @field_validator("executed_at")
    @classmethod
    def execution_time_is_timezone_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("regression execution time must include a timezone offset")
        return value.astimezone(UTC)


class IndependentPolicyApproval(_StrictActivationModel):
    """A distinct reviewer approval; a policy author can never self-approve."""

    policy_digest: str = Field(pattern=r"^[0-9a-f]{64}$")
    author_id: str = Field(min_length=1, max_length=128)
    approver_id: str = Field(min_length=1, max_length=128)
    approver_role: str = Field(min_length=1, max_length=128)
    approved_at: datetime

    @field_validator("approved_at")
    @classmethod
    def approval_time_is_timezone_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("approval time must include a timezone offset")
        return value.astimezone(UTC)

    @override
    def model_post_init(self, __context: object) -> None:
        if self.author_id == self.approver_id:
            raise ValueError("policy author cannot provide independent approval")


def authorize_policy_activation(
    policy: CompiledPolicy,
    *,
    regression: PolicyRegressionEvidence,
    approval: IndependentPolicyApproval,
    now: datetime,
) -> None:
    """Require current matching invariant evidence and a distinct approver."""

    if now.tzinfo is None or now.utcoffset() is None:
        raise PolicyActivationDeniedError("activation clock must be timezone-aware")
    if (
        regression.policy_digest != policy.policy_digest
        or approval.policy_digest != policy.policy_digest
    ):
        raise PolicyActivationDeniedError("activation evidence is not bound to this policy")
    if not regression.passed:
        raise PolicyActivationDeniedError("policy invariant regression suite did not pass")
    if approval.approved_at < regression.executed_at:
        raise PolicyActivationDeniedError("approval predates regression evidence")
    if now.astimezone(UTC) >= policy.expires_at:
        raise PolicyActivationDeniedError("expired policy cannot activate")
