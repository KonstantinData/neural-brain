"""Tests for versioned, non-authorizing Codex development model routing."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from tools.select_codex_model import (
    EXPLICIT_TRIGGER_CODES,
    RATIONALE_CODE_BY_TRIGGER,
    RationaleCode,
    RoutingDecision,
    RoutingPolicy,
    TaskPhase,
    TriggerCode,
    append_decision,
    load_policy,
    select_route,
)

ROOT = Path(__file__).resolve().parents[2]
RECORDED_AT = datetime(2026, 7, 24, 9, 30, tzinfo=UTC)


def _decision(
    policy: RoutingPolicy,
    *,
    task_id: str = "NB-ROUTING-TEST",
    explicit_triggers: tuple[str, ...] = (),
    rationale_code: RationaleCode = "routine_bounded_task",
    budget_limit: int = 120_000,
    failed_attempts: int = 0,
    attempt_limit: int = 2,
    task_phase: TaskPhase = "safe_task_start",
    runtime_switch_supported: bool = False,
) -> RoutingDecision:
    return select_route(
        policy,
        task_id=task_id,
        explicit_triggers=explicit_triggers,
        rationale_code=rationale_code,
        budget_limit=budget_limit,
        budget_unit="tokens",
        attempt_limit=attempt_limit,
        failed_attempts=failed_attempts,
        task_phase=task_phase,
        runtime_switch_supported=runtime_switch_supported,
        recorded_at=RECORDED_AT,
    )


def test_versioned_policy_has_exact_routes_and_escalation_set() -> None:
    policy = load_policy()

    assert policy.version == 1
    assert policy.default_route.model == "gpt-5.6-terra"
    assert policy.default_route.reasoning_depth == "medium"
    assert policy.escalation_route.model == "gpt-5.6-sol"
    assert policy.escalation_route.reasoning_depth == "high"
    assert [trigger.code for trigger in policy.escalation_triggers] == [
        "security_contract",
        "major_architecture_decision",
        "claude_alignment_conflict",
        "repeated_unsuccessful_attempts",
        "high_context_complexity",
    ]


def test_policy_and_decision_collections_are_immutable_and_revalidated() -> None:
    policy = load_policy()
    decision = _decision(policy)
    reordered_policy = policy.model_copy(
        update={"escalation_triggers": tuple(reversed(policy.escalation_triggers))}
    )
    threshold_tampered = policy.model_copy(update={"failed_attempts_threshold": 10})

    assert isinstance(policy.escalation_triggers, tuple)
    assert isinstance(decision.trigger_codes, tuple)
    with pytest.raises(ValueError, match="canonical v1 digest"):
        _decision(reordered_policy)
    with pytest.raises(ValueError, match="canonical v1 digest"):
        _decision(threshold_tampered)


def test_default_route_is_terra_medium_with_complete_limits() -> None:
    decision = _decision(load_policy())

    assert decision.selected_model == "gpt-5.6-terra"
    assert decision.reasoning_depth == "medium"
    assert decision.trigger_codes == ("default_standard",)
    assert decision.rationale_code == "routine_bounded_task"
    assert decision.budget_limit == 120_000
    assert decision.budget_unit == "tokens"
    assert decision.attempt_limit == 2
    assert decision.application_status == "external_runtime_application_required"


@pytest.mark.parametrize("trigger", EXPLICIT_TRIGGER_CODES)
def test_each_explicit_escalation_trigger_selects_only_sol(trigger: TriggerCode) -> None:
    decision = _decision(
        load_policy(),
        explicit_triggers=(trigger,),
        rationale_code=RATIONALE_CODE_BY_TRIGGER[trigger],
    )

    assert decision.selected_model == "gpt-5.6-sol"
    assert decision.reasoning_depth == "high"
    assert decision.trigger_codes == (trigger,)


def test_repeated_failed_attempts_derive_sol_but_respect_attempt_limit() -> None:
    policy = load_policy()
    allowed = _decision(
        policy,
        failed_attempts=2,
        attempt_limit=3,
        rationale_code="standard_attempts_exhausted",
    )
    blocked = _decision(
        policy,
        failed_attempts=2,
        attempt_limit=2,
        rationale_code="standard_attempts_exhausted",
    )

    assert allowed.selected_model == "gpt-5.6-sol"
    assert allowed.trigger_codes == ("repeated_unsuccessful_attempts",)
    assert allowed.application_status == "external_runtime_application_required"
    assert blocked.selected_model == "gpt-5.6-sol"
    assert blocked.application_status == "blocked_attempt_limit"


def test_in_progress_unsupported_switch_defers_to_next_safe_start() -> None:
    decision = _decision(
        load_policy(),
        task_phase="in_progress",
        runtime_switch_supported=False,
    )

    assert decision.application_status == "deferred_to_next_safe_task_start"
    assert decision.next_safe_task_start_required is True


def test_tool_never_claims_that_external_runtime_application_succeeded() -> None:
    safe_start = _decision(load_policy(), task_phase="safe_task_start")
    switch_supported = _decision(
        load_policy(), task_phase="in_progress", runtime_switch_supported=True
    )

    assert safe_start.application_status == "external_runtime_application_required"
    assert switch_supported.application_status == "external_runtime_application_required"


def test_routing_evidence_has_no_authority_or_boundary_bypass() -> None:
    safety = _decision(
        load_policy(),
        explicit_triggers=("security_contract",),
        rationale_code="security_contract_change",
    ).safety

    assert safety.advisory_process_evidence_only is True
    assert safety.model_application_is_external is True
    assert safety.can_change_authenticated_scope is False
    assert safety.can_cross_tenant_or_area_boundary is False
    assert safety.can_create_authority_or_approval is False
    assert safety.can_bypass_memory_or_human_gate is False
    assert safety.can_mutate_protected_product_state is False


def test_invalid_or_unapproved_routing_input_fails_closed() -> None:
    policy = load_policy()

    with pytest.raises(ValueError, match="budget_limit"):
        _decision(policy, budget_limit=0)
    with pytest.raises(ValueError, match="attempt_limit"):
        _decision(policy, attempt_limit=0)
    with pytest.raises(ValueError, match="failed_attempts"):
        _decision(policy, failed_attempts=-1)
    with pytest.raises(ValueError, match="task_id"):
        _decision(policy, task_id="contains a space")
    with pytest.raises(ValueError, match="rationale_code"):
        _decision(policy, rationale_code="security_contract_change")
    with pytest.raises(ValueError, match="unapproved"):
        _decision(policy, explicit_triggers=("cost_optimization",))


def test_evidence_log_appends_without_rewriting_prior_record(tmp_path: Path) -> None:
    evidence_path = tmp_path / "routing.jsonl"
    first = _decision(load_policy())
    second = _decision(
        load_policy(),
        explicit_triggers=("high_context_complexity",),
        rationale_code="context_capacity_exceeded",
    )

    append_decision(evidence_path, first)
    first_bytes = evidence_path.read_bytes()
    append_decision(evidence_path, second)
    final_bytes = evidence_path.read_bytes()
    lines = evidence_path.read_text(encoding="utf-8").splitlines()

    assert final_bytes.startswith(first_bytes)
    assert len(lines) == 2
    first_record: object = json.loads(lines[0])
    second_record: object = json.loads(lines[1])
    assert isinstance(first_record, dict)
    assert isinstance(second_record, dict)
    assert first_record["selected_model"] == "gpt-5.6-terra"
    assert second_record["selected_model"] == "gpt-5.6-sol"


def test_append_revalidates_schema_safety_and_cross_field_semantics(tmp_path: Path) -> None:
    evidence_path = tmp_path / "routing.jsonl"
    valid = _decision(load_policy())
    invalid_status = valid.model_copy(update={"application_status": "applied"})
    invalid_safety = valid.model_copy(
        update={"safety": valid.safety.model_copy(update={"can_bypass_memory_or_human_gate": True})}
    )
    invalid_model = valid.model_copy(update={"selected_model": "gpt-unapproved"})

    with pytest.raises(ValueError, match="schema validation"):
        append_decision(evidence_path, invalid_status)
    with pytest.raises(ValueError, match="schema validation"):
        append_decision(evidence_path, invalid_safety)
    with pytest.raises(ValueError, match="semantic validation"):
        append_decision(evidence_path, invalid_model)
    assert not evidence_path.exists()


def test_repository_instructions_keep_process_and_product_routing_separate() -> None:
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    normalized_agents = " ".join(agents.split())
    tool_source = (ROOT / "tools" / "select_codex_model.py").read_text(encoding="utf-8")

    assert "Codex Development Model Routing" in agents
    assert "does not amend ADR-014" in normalized_agents
    assert "cannot apply it to the Codex runtime" in normalized_agents
    assert "neural_brain.cognition" not in tool_source
    assert "neural_brain.memory" not in tool_source
