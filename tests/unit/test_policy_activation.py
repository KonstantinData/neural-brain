"""Regression evidence for fail-closed four-eyes policy activation."""

from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from neural_brain.security.activation import (
    IndependentPolicyApproval,
    PolicyActivationDeniedError,
    PolicyRegressionEvidence,
    authorize_policy_activation,
)
from neural_brain.security.memory_risk import MemoryLifecycleOperation
from neural_brain.security.policy import CompiledPolicy, PolicyDocument, compile_policy

NOW = datetime(2026, 7, 26, 15, 30, tzinfo=UTC)


def policy() -> CompiledPolicy:
    return compile_policy(
        PolicyDocument(
            schema_version="policy-v1",
            policy_id="memory.intake.default",
            expires_at=NOW + timedelta(hours=1),
            allowed_operations=(MemoryLifecycleOperation.INTAKE,),
            allowed_classifications=("public",),
        ),
        now=NOW,
    )


def evidence(digest: str, **changes: object) -> PolicyRegressionEvidence:
    values = {"policy_digest": digest, "suite_digest": "a" * 64, "passed": True, "executed_at": NOW}
    values.update(changes)
    return PolicyRegressionEvidence.model_validate(values)


def approval(digest: str, **changes: object) -> IndependentPolicyApproval:
    values = {
        "policy_digest": digest,
        "author_id": "author-a",
        "approver_id": "reviewer-b",
        "approver_role": "security_reviewer",
        "approved_at": NOW + timedelta(minutes=1),
    }
    values.update(changes)
    return IndependentPolicyApproval.model_validate(values)


def test_activation_requires_matching_passing_regression_and_independent_approval() -> None:
    compiled = policy()
    authorize_policy_activation(
        compiled,
        regression=evidence(compiled.policy_digest),
        approval=approval(compiled.policy_digest),
        now=NOW,
    )


@pytest.mark.parametrize(
    "regression_changes, approval_changes, message",
    [
        ({"passed": False}, {}, "did not pass"),
        ({"policy_digest": "b" * 64}, {}, "not bound"),
        ({}, {"policy_digest": "b" * 64}, "not bound"),
        ({}, {"approved_at": NOW - timedelta(minutes=1)}, "predates"),
    ],
)
def test_activation_fails_closed_for_incomplete_or_stale_evidence(
    regression_changes: dict[str, object], approval_changes: dict[str, object], message: str
) -> None:
    compiled = policy()
    with pytest.raises(PolicyActivationDeniedError, match=message):
        authorize_policy_activation(
            compiled,
            regression=evidence(compiled.policy_digest, **regression_changes),
            approval=approval(compiled.policy_digest, **approval_changes),
            now=NOW,
        )


def test_author_cannot_self_approve_and_unknown_fields_are_rejected() -> None:
    compiled = policy()
    with pytest.raises(ValidationError, match="cannot provide independent"):
        approval(compiled.policy_digest, approver_id="author-a")
    with pytest.raises(ValidationError, match="Extra inputs"):
        PolicyRegressionEvidence.model_validate(
            {**evidence(compiled.policy_digest).model_dump(), "override": True}
        )
