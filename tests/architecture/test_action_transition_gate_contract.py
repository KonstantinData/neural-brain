"""Evidence for the bounded, non-runtime NB-5 Action Gate prerequisite."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).parents[2]
CONTRACT_PATH = ROOT / "docs" / "architecture" / "contracts" / "action-transition-gate-v1.json"


def _contract() -> dict[str, object]:
    loaded: object = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _strings(value: object) -> set[str]:
    assert isinstance(value, list)
    assert all(isinstance(item, str) for item in value)
    return set(value)


def _stages(value: object) -> dict[str, dict[str, object]]:
    assert isinstance(value, list)
    assert all(isinstance(item, dict) for item in value)
    return {str(item["stage"]): item for item in value if isinstance(item, dict)}


def test_action_gate_is_blocked_nb5_prerequisite_not_runtime_authorization() -> None:
    contract = _contract()
    assert contract["contract_id"] == "neural-brain.action-transition-gate"
    assert contract["status"] == "nb5_prerequisite_contract_not_runtime_authorization"
    assert contract["governing_decisions"] == ["ADR-018", "ADR-019"]
    boundary = contract["aggregate_boundary"]
    assert isinstance(boundary, dict)
    assert boundary["sole_protected_state_writer"] == "Action Transition Gate"
    assert boundary["trusted_context_source"] == "authenticated_runtime_context"


def test_action_gate_requires_every_precommit_and_independent_posteffect_control() -> None:
    contract = _contract()
    assert _strings(contract["required_precommit_evidence"]) == {
        "committed_action_intent_with_immutable_purpose_and_provenance",
        "authenticated_principal_and_immutable_scope",
        "authority_snapshot",
        "policy_decision_bound_to_exact_operation",
        "required_approval_claims_with_separation_of_duties",
        "budget_reservation",
        "resource_claims",
        "valid_runtime_fence",
        "enabled_kill_switch_state",
        "sandbox_policy_and_exact_executor_binding",
        "atomic_audit_evidence",
    }
    assert {
        "independent_effect_verifier_decision",
        "independent_goal_verifier_decision_before_Achieved",
        "authoritative_reconciliation_for_indeterminate_effect",
        "retained_budget_and_resource_claims_until_reconciliation",
    } <= _strings(contract["independent_posteffect_requirements"])
    invariants = _strings(contract["noncompensable_invariants"])
    assert any("not blindly retried" in item for item in invariants)
    assert any("cannot compensate" in item for item in invariants)


def test_nb4_cannot_enable_nb5_action_and_nb5_remains_bounded() -> None:
    stages = _stages(_contract()["stage_boundary_map"])
    assert set(stages) == {"NB-0", "NB-1", "NB-4", "NB-5", "NB-8"}
    assert "tool execution" in _strings(stages["NB-4"]["prohibited"])
    assert "using learning evidence to waive NB-5 authority or control prerequisites" in _strings(
        stages["NB-4"]["prohibited"]
    )
    assert "single-goal bounded action in simulation" in _strings(
        stages["NB-5"]["allowed_only_after_all_prior_stage_and_action_gate_evidence"]
    )
    assert {"unbounded tools", "parallel goals", "blind retry"} <= _strings(
        stages["NB-5"]["prohibited"]
    )


def test_legacy_tasks_are_not_reactivated_and_have_bounded_successors() -> None:
    tasks = _contract()["legacy_task_disposition"]
    assert isinstance(tasks, list)
    assert all(isinstance(task, dict) for task in tasks)
    by_task = {str(task["legacy_task"]): task for task in tasks if isinstance(task, dict)}
    assert set(by_task) == {"S1-07", "S1-08", "S1-09"}
    assert by_task["S1-07"]["disposition"] == "blocked_not_reactivated"
    assert by_task["S1-08"]["disposition"] == "blocked_not_reactivated"
    assert by_task["S1-09"]["disposition"] == "split_blocked_successors"
    assert "NB-8" in str(by_task["S1-09"]["successor"])


def test_runtime_and_migration_remain_blocked_until_authorized_revalidation() -> None:
    contract = _contract()
    blocker = contract["implementation_blocker"]
    assert isinstance(blocker, dict)
    assert (
        blocker["status"]
        == "blocked_pending_authorized_complete_system_action_and_goal_gate_revalidation"
    )
    assert "FND-ENT-02" in str(blocker["dependency"])
    assert "do not add runtime, migration, executor" in str(blocker["next_step"])
    assert any("Action runtime" in item for item in _strings(contract["explicit_exclusions"]))
