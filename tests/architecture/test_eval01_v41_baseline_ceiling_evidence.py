"""Fail-closed evidence boundary for the proposed EVAL-01 v4.1 ceiling rule."""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
RULE = (
    ROOT
    / "docs"
    / "architecture"
    / "evaluations"
    / "nb1-safe-serial-cognition-v4.1-baseline-ceiling-decision-rule-proposal-v1.json"
)
PROPOSAL = ROOT / "docs" / "architecture" / "eval-01-v4.1-baseline-ceiling-evidence-proposal-v1.md"


def _load_rule() -> dict[str, Any]:
    payload = json.loads(RULE.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def test_ceiling_rule_rejects_unsupported_number_and_creates_nothing() -> None:
    rule = _load_rule()

    assert rule["status"] == "proposed_not_accepted_not_effective"
    assert rule["current_disposition"]["proposed_ceiling"] == "0.750000"
    assert rule["current_disposition"]["decision"] == "rejected_as_unsupported"
    assert rule["scope_and_non_authorization"] == {
        "public_train_and_development_only": True,
        "candidate_training_runs": 0,
        "candidate_freezes": 0,
        "hidden_artifacts": 0,
        "evaluation_gates_passed": [],
        "stage_release_authorized": False,
        "nb2_authorized": False,
    }


def test_calibration_panel_and_baselines_are_exact_and_public_only() -> None:
    rule = _load_rule()
    calibration = rule["public_calibration"]

    assert calibration["seed_pairs"] == 132
    assert calibration["train_sequences_per_pair"] == 2048
    assert calibration["development_sequences_per_pair"] == 1024
    assert calibration["candidate_runs"] == 0
    assert calibration["development_score_reports"] == 132 * 8
    assert "exact rational" in calibration["metric"]
    assert "0.9908" in calibration["aggregation"]["coverage"]
    assert set(rule["required_baselines"]) == {
        "majority_class",
        "seeded_random",
        "stateless_last_observation",
        "uniform_pooling",
        "non_neural_finite_state",
        "parameter_matched_stateless",
        "public_generator_family_heuristic",
        "parameter_matched_recurrent_non_neural",
    }


def test_decision_rule_keeps_statistical_margin_and_fail_closed_boundary() -> None:
    rule = _load_rule()
    decision = rule["ceiling_decision_rule"]

    assert decision["operational_ceiling_not_set_by_this_package"] is True
    assert decision["maximum_admissible_ceiling"] == "0.700000"
    bands = {band["ceiling"]: band for band in decision["sensitivity_bands"]}
    assert bands["0.750000"]["assessment"].startswith("rejected")
    assert bands["0.700000"]["nominal_gap_at_full_accuracy_0.800000"] == "0.100000"
    assert "fails closed" in rule["future_hidden_scoring_precision"]["failure_rule"]
    proposal = PROPOSAL.read_text(encoding="utf-8")
    assert "candidate attainability" in proposal
    assert "Only the Architecture Decision Owner" in proposal
