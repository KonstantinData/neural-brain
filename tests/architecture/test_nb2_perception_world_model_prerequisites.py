import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).parents[2]
CONTRACTS = ROOT / "docs" / "architecture" / "contracts"
EVALUATIONS = ROOT / "docs" / "architecture" / "evaluations"


def _load(path: Path) -> dict[str, object]:
    content: object = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(content, dict)
    return content


def _strings(value: object) -> set[str]:
    assert isinstance(value, list)
    assert all(isinstance(item, str) for item in value)
    return set(value)


def _canonical_digest(specification: dict[str, object]) -> str:
    canonical = dict(specification)
    canonical.pop("spec_digest")
    payload = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def test_nb2_prerequisite_contract_is_blocked_and_non_activating() -> None:
    contract = _load(CONTRACTS / "nb2-perception-world-model-prerequisites-v1.json")
    assert contract["stage"] == "NB-2"
    assert contract["status"] == "blocked_on_independently_accepted_nb1_exit"
    activation = contract["activation"]
    assert isinstance(activation, dict)
    assert activation == {
        "runtime_enabled": False,
        "stage_release_authorized": False,
        "required_precondition": "NB-1 independently accepted exit with all stage evidence and gates complete",
    }
    assert {
        "external_effect",
        "tool_call",
        "protected_memory_write",
        "runtime_activation",
    } <= _strings(contract["prohibited_surfaces"])


def test_nb2_contract_preserves_perception_and_scope_separation() -> None:
    contract = _load(CONTRACTS / "nb2-perception-world-model-prerequisites-v1.json")
    separation = contract["record_separation"]
    assert isinstance(separation, dict)
    assert separation["ordered_kinds"] == [
        "raw_signal",
        "observation",
        "inferred_feature",
        "belief",
        "prediction",
    ]
    assert any("never an observation" in item for item in _strings(separation["invariants"]))
    assert {
        "source_identity",
        "modality",
        "occurred_at",
        "immutable_authenticated_scope_reference",
        "uncertainty",
        "replay_identity",
    } <= _strings(contract["admission_requirements"])


def test_nb2_contract_requires_temporal_non_language_attention_and_world_model_boundaries() -> None:
    contract = _load(CONTRACTS / "nb2-perception-world-model-prerequisites-v1.json")
    modalities = contract["modalities"]
    assert isinstance(modalities, dict)
    assert modalities["temporal_non_language_stream_required"] is True
    attention = contract["attention"]
    assert isinstance(attention, dict)
    assert attention["bounded"] is True
    assert attention["calibration_required"] is True
    assert attention["may_change_authority_or_policy"] is False
    assert {"safety", "contradiction", "shutdown", "supervisor"} <= _strings(
        attention["non_suppressible_channels"]
    )
    world_model = contract["world_model"]
    assert isinstance(world_model, dict)
    assert world_model["environment"] == "simulation_only"
    assert {"temporal_dynamics", "action_conditioning", "uncertainty"} <= _strings(
        world_model["required_representation"]
    )


def test_nb2_evaluation_preregistration_requires_non_compensatory_evidence() -> None:
    evaluation = _load(EVALUATIONS / "nb2-perception-world-model-v1.json")
    assert evaluation["status"] == "preimplementation_blocked_on_independently_accepted_nb1_exit"
    activation = evaluation["activation"]
    assert isinstance(activation, dict)
    assert activation["runtime_enabled"] is False
    assert activation["stage_release_authorized"] is False
    assert activation["passes_evaluation_gates"] == []
    assert evaluation["spec_digest_algorithm"] == "sha256-canonical-json-without-spec-digest"
    assert evaluation["spec_digest"] == _canonical_digest(evaluation)
    assert evaluation["confidence_method"] == "paired_nonparametric_bootstrap_10000_replicates"
    thresholds = evaluation["thresholds"]
    assert isinstance(thresholds, dict)
    assert (
        thresholds["maximum_attention_expected_calibration_error_under_distribution_shift"] == 0.1
    )
    assert {
        "model_free_planner",
        "action_blind_predictor",
        "shuffled_action_predictor",
    } <= _strings(evaluation["baselines"])
    assert {
        "temporal_stream_removed",
        "binding_removed",
        "attention_removed_or_uniform",
        "action_conditioning_removed",
    } <= _strings(evaluation["ablations"])
    assert {
        "held_out_multi_step_prediction",
        "uncertainty_calibration_under_dynamics_shift",
        "attention_calibration_under_distribution_shift",
        "ood_robustness",
        "contradiction_visibility",
        "simulated_planning_lift",
    } <= _strings(evaluation["required_test_classes"])
    test_gate_criteria = evaluation["test_gate_criteria"]
    assert isinstance(test_gate_criteria, dict)
    assert set(test_gate_criteria) == _strings(evaluation["required_test_classes"])
    for criterion in test_gate_criteria.values():
        assert isinstance(criterion, dict)
        assert {"metric", "pass_criterion", "confidence_interval_rule", "failure_condition"} <= set(
            criterion
        )
    future_evidence = _load(CONTRACTS / "nb2-perception-world-model-prerequisites-v1.json")[
        "future_evidence"
    ]
    assert isinstance(future_evidence, dict)
    assert _strings(future_evidence["required_tests"]) <= _strings(
        evaluation["required_test_classes"]
    )
    assert any("failed or unknown" in item for item in _strings(evaluation["failure_criteria"]))
