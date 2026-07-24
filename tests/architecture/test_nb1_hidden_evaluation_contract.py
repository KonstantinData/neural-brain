"""Normative trust-boundary tests for independent NB-1 hidden evaluation."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "docs" / "architecture" / "contracts" / "nb1-hidden-evaluation.json"
GENERATOR = ROOT / "docs" / "architecture" / "evaluations" / "nb1-serial-context-generator-v4.json"
REJECTION = (
    ROOT / "docs" / "architecture" / "evaluations" / "nb1-safe-serial-cognition-v3-rejection.json"
)


def _load(path: Path) -> dict[str, object]:
    loaded: object = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def test_candidate_boundary_never_accepts_hidden_labels_or_gate_decisions() -> None:
    contract = _load(CONTRACT)
    assert contract["evaluation_spec"] == "EVAL-01.NB-1.safe-serial-cognition.v4"
    assert (
        contract["evaluation_spec_status"]
        == "frozen_before_candidate_training_and_hidden_attachment"
    )
    assert contract["generator_contract"] == "nb1-serial-context-generator-v4"
    assert contract["candidate_export_status"] == "blocked_until_v4_candidate_freeze_receipt_exists"
    assert contract["rejected_historical_spec"] == "EVAL-01.NB-1.safe-serial-cognition.v3"
    candidate = contract["candidate_boundary"]
    assert isinstance(candidate, dict)

    forbidden_inputs = set(candidate["forbidden_inputs"])
    forbidden_outputs = set(candidate["forbidden_outputs"])
    assert {"expected_label", "hidden_seed", "score", "threshold_decision"} <= forbidden_inputs
    assert {"correctness", "gate_pass", "recognition_claim", "stage_release"} <= (forbidden_outputs)


def test_external_evaluator_owns_labels_scoring_and_complete_attempt_ledger() -> None:
    contract = _load(CONTRACT)
    evaluator = contract["independent_evaluator_boundary"]
    assert isinstance(evaluator, dict)

    assert evaluator["outside_candidate_repository"] is True
    assert evaluator["holds_hidden_seed_and_labels"] is True
    assert evaluator["baseline_and_ablation_scoring_owned_by_evaluator"] is True
    assert evaluator["all_attempts_recorded"] is True
    assert evaluator["candidate_network_calls"] == 0
    assert evaluator["candidate_external_effects"] == 0


def test_v4_generator_contract_is_modular_non_enumerable_and_hides_hidden_seed() -> None:
    generator = _load(GENERATOR)
    assert generator["generator_contract_id"] == "nb1-serial-context-generator-v4"
    runtime = generator["runtime"]
    assert isinstance(runtime, dict)
    assert runtime["python_random_allowed"] is False
    modules = generator["modular_generation_pipeline"]
    assert isinstance(modules, list)
    assert {module["module"] for module in modules if isinstance(module, dict)} == {
        "world_generator",
        "scenario_generator",
        "constraint_generator",
        "noise_generator",
        "serialization_generator",
    }
    floor = generator["search_space_floor"]
    assert isinstance(floor, dict)
    assert floor["minimum_hidden_seed_entropy_bits"] >= 256
    assert floor["minimum_accepted_hidden_artifact_lower_bound_bits"] >= 128
    assert floor["minimum_train_unique_canonical_sequences"] >= 2048
    splits = generator["split_policy"]
    assert isinstance(splits, dict)
    train = splits["train"]
    development = splits["development"]
    hidden = splits["hidden_test"]
    assert isinstance(train, dict)
    assert isinstance(development, dict)
    assert isinstance(hidden, dict)

    assert train["size"] == 2048
    assert train["seed_visibility"] == "public_repository"
    assert development["size"] == 1024
    assert development["seed_visibility"] == "public_repository"
    assert hidden["minimum_size"] == 2048
    assert hidden["maximum_size"] == 4096
    assert hidden["seed_visibility"] == "independent_provider_only"
    sequence = generator["sequence"]
    assert isinstance(sequence, dict)
    assert "expected_label" in sequence["candidate_hidden_fields"]


def test_contract_explicitly_denies_self_certified_independence_or_gate_passes() -> None:
    contract = _load(CONTRACT)
    signed = contract["signed_evidence"]
    assert isinstance(signed, dict)
    assert signed["signature_algorithm"] == "Ed25519"
    assert signed["trusted_key_registry_supplied_by_reviewer"] is True
    assert signed["trusted_attestation_registry_supplied_by_reviewer"] is True
    assert signed["candidate_registry_contains_full_freeze_receipt"] is True
    assert signed["hidden_commitment_registry_supplied_by_reviewer"] is True
    assert signed["attempts_bind_input_and_prediction_digests"] is True
    non_claims = contract["non_claims"]
    assert isinstance(non_claims, list)
    joined = " ".join(non_claims)
    assert "subagent" in joined.lower()
    assert "automatically passes" in joined
    failure_rule = contract["failure_rule"]
    assert isinstance(failure_rule, str)
    assert failure_rule.endswith("fails closed.")


def test_v3_is_rejected_before_hidden_attachment_without_rewriting_the_frozen_spec() -> None:
    rejection = _load(REJECTION)

    assert rejection["decision"] == "rejected_before_hidden_artifact_attachment"
    reproduction = rejection["reproduction"]
    assert isinstance(reproduction, dict)
    assert reproduction["training_sequence_count"] == 512
    assert reproduction["unique_feature_label_pattern_count"] == 6
    assert reproduction["hidden_run_attempted"] is False
    assert reproduction["hidden_artifact_attached"] is False
    assert rejection["claim_boundary"] == {
        "evaluation_gates_passed": [],
        "recognition_gates_passed": [],
        "stage_release_authorized": False,
        "neural_brain_candidate_claimed": False,
    }
