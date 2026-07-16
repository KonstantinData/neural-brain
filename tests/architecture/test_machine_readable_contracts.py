import json
from pathlib import Path

ROOT = Path(__file__).parents[2]
CONTRACTS = ROOT / "docs" / "architecture" / "contracts"


def _load(name: str) -> dict[str, object]:
    loaded: object = json.loads((CONTRACTS / name).read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _maps(value: object) -> list[dict[str, object]]:
    assert isinstance(value, list)
    assert all(isinstance(item, dict) for item in value)
    return [item for item in value if isinstance(item, dict)]


def _strings(value: object) -> list[str]:
    assert isinstance(value, list)
    assert all(isinstance(item, str) for item in value)
    return [item for item in value if isinstance(item, str)]


def test_contract_inventory_covers_the_complete_cognitive_system() -> None:
    assert {path.name for path in CONTRACTS.glob("*.json")} == {
        "cognitive-cycle.json",
        "dreaming.json",
        "envelopes.json",
        "evaluation-gates.json",
        "inference-provider.json",
        "ledger-invariants.json",
        "memory-lifecycle.json",
        "memory-release-stops.json",
        "memory-stage-capabilities.json",
        "nb1-safe-serial-cognition.json",
        "recognition-gates.json",
        "release-stops.json",
        "scope-catalog.json",
        "stage-capabilities.json",
        "system-boundary.json",
    }


def test_system_boundary_declares_target_and_honest_current_maturity() -> None:
    contract = _load("system-boundary.json")
    assert contract["system_kind"] == "integrated_neural_cognitive_system"
    assert contract["current_maturity"] == "memory_core_foundation"
    capabilities = set(_strings(contract["target_capabilities"]))
    assert {
        "active perception and multimodal binding",
        "neural cognitive workspace",
        "world self and value models",
        "goal lifecycle and executive control",
        "planning and action selection",
        "closed-loop effect observation and independent verification",
        "continual learning consolidation transfer and metacognition",
    } <= capabilities


def test_cognitive_plane_cannot_bypass_protected_control_plane() -> None:
    contract = _load("system-boundary.json")
    cognitive = contract["cognitive_plane"]
    assert isinstance(cognitive, dict)
    assert cognitive["may_directly_write_protected_state"] is False
    assert cognitive["may_directly_execute_external_effects"] is False

    control = contract["protected_control_plane"]
    assert isinstance(control, dict)
    assert control["sole_writers"] == {
        "goal_state": "Goal Transition Gate",
        "action_state": "Action Transition Gate",
        "memory_state": "Memory Transition Gate",
        "active_model_state": "Learning and Model Promotion Gate",
    }
    requirements = set(control["external_effect_requirements"])
    assert {
        "authenticated principal and immutable scope",
        "committed action intent",
        "authority snapshot",
        "required approval",
        "valid runtime fence",
        "enabled kill switch",
        "sandbox policy",
        "atomic auditability",
    } <= requirements


def test_scope_and_memory_core_invariants_remain_explicit() -> None:
    contract = _load("system-boundary.json")
    scope = contract["scope"]
    assert isinstance(scope, dict)
    assert scope["object_hierarchy"] == ["brain", "tenant", "area", "project", "session", "goal"]
    assert scope["isolation_scope_order"] == ["brain", "tenant", "area", "project", "session"]
    assert scope["goal_is_scope_dimension"] is False
    assert scope["trusted_source"] == "authenticated runtime context"

    memory = contract["memory_core"]
    assert isinstance(memory, dict)
    assert memory["governing_decisions"] == ["ADR-015", "ADR-016", "ADR-017"]
    assert memory["role"] == "protected subsystem"
    assert "Memory Transition Gate sole writer" in memory["retained_invariants"]


def test_full_system_stages_are_ordered_and_cumulative() -> None:
    contract = _load("stage-capabilities.json")
    semantics = contract["semantics"]
    assert isinstance(semantics, dict)
    stages = [f"nb_{number}" for number in range(9)]
    assert semantics["stage_order"] == stages
    assert semantics["domain"] == "integrated_neural_cognitive_system"
    assert semantics["cumulative"] is True
    assert semantics["unknown_operation"] == "denied"
    assert semantics["failed_or_unknown_gate"] == "release_stop"

    definitions = _maps(contract["stages"])
    assert [stage["id"] for stage in definitions] == stages
    assert all(stage["capabilities"] for stage in definitions)
    assert all(stage["prohibited"] for stage in definitions)


def test_memory_core_stages_are_separately_namespaced() -> None:
    contract = _load("memory-stage-capabilities.json")
    namespace = contract["namespace"]
    assert isinstance(namespace, dict)
    assert namespace["subsystem"] == "Memory Core"
    assert namespace["stage_prefix"] == "MS"
    assert namespace["product_stage_contract"] == "stage-capabilities.json"

    semantics = contract["semantics"]
    assert isinstance(semantics, dict)
    memory_stages = [f"ms_{number}" for number in range(5)]
    assert semantics["stage_order"] == memory_stages
    assert semantics["domain"] == "protected_memory_core_subsystem"
    assert semantics["cumulative"] is True
    assert semantics["unknown_operation"] == "denied"

    definitions = _maps(contract["stages"])
    assert [stage["id"] for stage in definitions] == memory_stages
    assert [stage["label"] for stage in definitions] == [f"MS-{number}" for number in range(5)]
    assert all(stage["capabilities"] for stage in definitions)
    assert all(stage["prohibited"] for stage in definitions)

    operation_families = _maps(contract["operation_families"])
    assert {operation["minimum_memory_stage"] for operation in operation_families} <= set(
        memory_stages
    )
    prohibitions = set(_strings(contract["absolute_prohibitions"]))
    assert "An MS stage never satisfies or advances an NB product stage by itself." in prohibitions


def test_candidate_recognition_requires_nb6_and_independent_evaluation() -> None:
    contract = _load("stage-capabilities.json")
    recognition = contract["recognition"]
    assert isinstance(recognition, dict)
    assert recognition == {
        "minimum_stage_for_candidate_label": "nb_6",
        "required_evaluation_gate": "g8",
        "production_autonomy_is_separate_approval": True,
    }


def test_recognition_gates_are_all_required_and_fail_closed() -> None:
    contract = _load("recognition-gates.json")
    assert contract["aggregation"] == "all_required_non_compensatory"
    result_semantics = contract["result_semantics"]
    assert isinstance(result_semantics, dict)
    assert result_semantics == {
        "allowed": ["pass", "fail", "unknown"],
        "unknown": "fail",
        "failed_gate": "recognition_prohibited",
        "score_compensation": "prohibited",
    }
    assert contract["evidence_reference_required"] is True
    gates = _maps(contract["gates"])
    assert [gate["id"] for gate in gates] == [f"R{number}" for number in range(1, 11)]
    assert all(gate["required"] is True for gate in gates)
    assert all(gate["required_evaluation_gates"] for gate in gates)
    assert all(gate["evidence_requirements"] for gate in gates)
    assert {gate["name"] for gate in gates} >= {
        "neural_substance",
        "integrated_cognition",
        "closed_perception_action_loop",
        "independent_adaptation",
        "held_out_transfer",
        "causal_component_evidence",
        "safety_control_and_independent_validation",
    }


def test_evaluation_gates_are_ordered_and_non_compensatory() -> None:
    contract = _load("evaluation-gates.json")
    assert contract["aggregation"] == "ordered_non_compensatory"
    result_semantics = contract["result_semantics"]
    assert isinstance(result_semantics, dict)
    assert result_semantics["unknown"] == "fail_and_release_stop"
    assert result_semantics["fail"] == "release_stop"
    assert result_semantics["score_compensation"] == "prohibited"
    gates = _maps(contract["gates"])
    assert [gate["id"] for gate in gates] == [f"g{number}" for number in range(9)]
    assert gates[0]["depends_on"] == []
    for number, gate in enumerate(gates[1:], start=1):
        assert gate["depends_on"] == [f"g{number - 1}"]
    assert all(gate["threshold_source"] for gate in gates)
    assert all(gate["evidence_requirements"] for gate in gates)
    assert all(gate["release_stop_conditions"] for gate in gates)
    assert contract["candidate_label"] == {
        "requires_gate": "g8",
        "requires_recognition_gates": [f"R{number}" for number in range(1, 11)],
        "label": "Neural Brain Candidate",
    }


def test_evaluation_and_recognition_gate_cross_references_are_bidirectional() -> None:
    evaluation = _maps(_load("evaluation-gates.json")["gates"])
    recognition = _maps(_load("recognition-gates.json")["gates"])
    evaluation_by_id = {str(gate["id"]): gate for gate in evaluation}
    recognition_by_id = {str(gate["id"]): gate for gate in recognition}
    for recognition_id, recognition_gate in recognition_by_id.items():
        evaluation_ids = recognition_gate["required_evaluation_gates"]
        assert isinstance(evaluation_ids, list)
        for evaluation_id in evaluation_ids:
            assert isinstance(evaluation_id, str)
            linked_recognition = evaluation_by_id[evaluation_id]["recognition_gates"]
            assert isinstance(linked_recognition, list)
            assert recognition_id in linked_recognition
