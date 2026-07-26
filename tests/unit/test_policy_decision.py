"""Evidence that policy decisions bind every protected input and expiry."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from neural_brain.security.decision import PolicyDecisionBinding, PolicyDecisionRecord
from neural_brain.security.memory_risk import MemoryRiskOutcome

_NOW = datetime(2026, 7, 26, 14, 0, tzinfo=UTC)


def _binding(**changes: str) -> PolicyDecisionBinding:
    values = {
        "actor_id": "principal-a",
        "tenant_id": "tenant-a",
        "area_id": "area-a",
        "project_id": "project-a",
        "session_id": "session-a",
        "authority_digest": "a" * 64,
        "parameter_digest": "b" * 64,
        "checkpoint_id": "checkpoint-a",
        "policy_digest": "c" * 64,
    }
    values.update(changes)
    return PolicyDecisionBinding(**values)


def _decision() -> PolicyDecisionRecord:
    return PolicyDecisionRecord(
        decision_id="decision-a",
        binding=_binding(),
        outcome=MemoryRiskOutcome.ALLOW,
        reason_codes=("gated_intake_admitted",),
        obligations=("audit",),
        required_approver_roles=("security_reviewer",),
        valid_until=_NOW + timedelta(minutes=5),
    )


def test_decision_is_valid_only_for_its_exact_binding_before_expiry() -> None:
    decision = _decision()

    assert decision.is_valid_for(_binding(), now=_NOW) is True
    assert decision.is_valid_for(_binding(), now=_NOW + timedelta(minutes=5)) is False


def test_changed_protected_inputs_invalidate_the_decision() -> None:
    decision = _decision()

    for change in (
        {"tenant_id": "tenant-b"},
        {"area_id": "area-b"},
        {"project_id": "project-b"},
        {"session_id": "session-b"},
        {"authority_digest": "d" * 64},
        {"parameter_digest": "d" * 64},
        {"checkpoint_id": "checkpoint-b"},
        {"policy_digest": "d" * 64},
    ):
        assert decision.is_valid_for(_binding(**change), now=_NOW) is False


def test_naive_time_is_never_valid() -> None:
    assert _decision().is_valid_for(_binding(), now=_NOW.replace(tzinfo=None)) is False
