"""Contract evidence for the proposed, non-effective EVAL-01 v4.1 amendment."""

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
AMENDMENT = (
    ROOT
    / "docs"
    / "architecture"
    / "evaluations"
    / "nb1-safe-serial-cognition-v4-clarification-amendment-v1.json"
)
PROPOSAL = ROOT / "docs" / "architecture" / "eval-01-v4-clarification-adr-proposal-v1.md"


def _load() -> dict[str, Any]:
    loaded = json.loads(AMENDMENT.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def test_amendment_is_explicitly_proposed_and_non_effective() -> None:
    amendment = _load()

    assert amendment["status"] == "proposed_not_accepted_not_effective"
    assert amendment["decision_required"] == "architecture_decision_owner_acceptance"
    assert amendment["base_specification"]["immutable_history_preserved"] is True
    successor = amendment["proposed_successor"]
    assert successor["created_only_after_acceptance"] is True
    assert all(value is False for key, value in successor.items() if key.endswith("authorized"))
    assert successor["candidate_training_permitted_by_this_amendment"] is False
    assert successor["hidden_attachment_permitted_by_this_amendment"] is False
    assert successor["evaluation_gate_passed"] is False


def test_public_split_commitments_are_literal_and_recomputable() -> None:
    commitments = _load()["public_split_seed_commitments"]

    assert commitments["encoding"].startswith("64 lowercase hexadecimal")
    assert commitments["train"]["sequence_count"] == 2048
    assert commitments["development"]["sequence_count"] == 1024
    assert commitments["train"]["seed_hex"] != commitments["development"]["seed_hex"]
    for split in (commitments["train"], commitments["development"]):
        assert (
            hashlib.sha256(split["derivation_input"].encode("utf-8")).hexdigest()
            == split["seed_hex"]
        )


def test_hmac_mapping_and_baseline_ceiling_are_complete_and_fixed() -> None:
    amendment = _load()
    mapping = amendment["deterministic_hmac_mapping"]
    ceiling = amendment["baseline_ceiling"]

    assert mapping["algorithm"] == "HMAC-SHA-256"
    assert "unsigned 16-bit big-endian" in mapping["message_encoding"]
    assert set(mapping["domains"]) == {
        "world",
        "scenario",
        "constraint",
        "noise",
        "feature",
        "baseline-random",
    }
    assert "2^32" in mapping["draw_rule"]
    vector = mapping["public_test_vector"]
    assert vector["message_hex"] == (
        "4e42312d4556414c30312d56342e31000005776f726c640005747261696e000130000130000130"
    )
    assert (
        vector["hmac_sha256_hex"]
        == "1a4d8139ef23b754b9671939baffba1b44ed21b56b8426374bcd38fd68d53cf3"
    )
    assert vector["first_u32_big_endian"] == 441286969
    assert set(mapping) >= {
        "world_mapping",
        "scenario_mapping",
        "feature_and_state_mapping",
        "constraint_mapping",
    }
    assert ceiling["ceiling"] == "0.750000"
    assert ceiling["baseline_schedule_id"] == "EVAL-01.NB-1.safe-serial-cognition.v4.1-baselines"
    assert set(ceiling["algorithms"]) == {
        "majority_class",
        "seeded_random",
        "stateless_last_observation",
        "uniform_pooling",
        "non_neural_finite_state",
        "parameter_matched_stateless",
        "public_generator_family_heuristic",
    }
    assert "less than or equal to 0.750000" in ceiling["comparison"]


def test_receipt_delta_and_custody_supersession_remain_fail_closed() -> None:
    amendment = _load()
    delta = amendment["candidate_and_freeze_receipt_delta"]
    custody = amendment["custody_reconciliation"]

    assert {
        "amendment_digest",
        "public_train_seed_commitment",
        "public_development_seed_commitment",
        "public_train_baseline_ceiling_report_digest",
        "public_development_baseline_ceiling_report_digest",
    } <= set(delta["required_additional_bindings"])
    assert "invalidated" in delta["receipt_rejection"]
    assert custody["effective_only_after_acceptance"] is True
    assert "sole hidden-dataset custodian" in custody["v4_1_rule"]
    assert len(custody["legacy_rules_to_supersede_for_v4_1"]) == 3
    assert "No v4.1 hidden run is admissible" in custody["implementation_gate"]


def test_proposal_keeps_implementation_and_stage_progression_blocked() -> None:
    proposal = PROPOSAL.read_text(encoding="utf-8")

    assert "Status: Proposed; not accepted and not effective" in proposal
    assert "does not train a candidate" in proposal
    assert "or begin NB-2" in proposal
    assert "Minimal authorized next package after acceptance" in proposal
