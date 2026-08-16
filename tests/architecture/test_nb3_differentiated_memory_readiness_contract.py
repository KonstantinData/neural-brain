"""Regression guards for the non-activating NB-3 readiness contract."""

import json
from pathlib import Path

ROOT = Path(__file__).parents[2]
PATH = ROOT / "docs" / "architecture" / "contracts" / "nb3-differentiated-memory-readiness-v1.json"


def _contract() -> dict[str, object]:
    loaded: object = json.loads(PATH.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _mapping(value: object) -> dict[str, object]:
    assert isinstance(value, dict)
    return value


def _strings(value: object) -> set[str]:
    assert isinstance(value, list)
    assert all(isinstance(item, str) for item in value)
    return set(value)


def test_nb3_readiness_contract_remains_preparation_only_and_denied() -> None:
    contract = _contract()
    assert contract["stage"] == "NB-3"
    assert contract["status"] == "preparation_only_not_activated"

    boundary = _mapping(contract["current_boundary"])
    assert boundary["implemented_memory_core_stage"] == "ms_1"
    assert boundary["nb1_exit_evidence_complete"] is False
    assert boundary["nb3_runtime_enabled"] is False
    assert boundary["productive_activation_allowed"] is False

    activation = _mapping(contract["activation"])
    assert activation["current_result"] == "denied"
    assert activation["requires_separate_accepted_runtime_change"] is True


def test_nb3_memory_kinds_retain_distinct_truth_and_lifecycle_semantics() -> None:
    kinds = _contract()["memory_kinds"]
    assert isinstance(kinds, list)
    indexed = {str(item["id"]): item for item in kinds if isinstance(item, dict)}
    assert set(indexed) == {"working", "episodic", "semantic", "procedural"}
    assert all(item["truth_semantics"] and item["lifecycle_semantics"] for item in indexed.values())
    assert "not a durable fact" in str(indexed["working"]["truth_semantics"])
    assert "does not prove" in str(indexed["episodic"]["truth_semantics"])
    assert "contradicting evidence" in str(indexed["semantic"]["truth_semantics"])
    assert "never creates execution authority" in str(indexed["procedural"]["truth_semantics"])


def test_nb2_nb3_coordination_uses_a_versioned_no_shared_state_boundary() -> None:
    coordination = _mapping(_contract()["nb2_coordination_boundary"])
    assert coordination["integration_mode"] == "versioned_contract_only"
    ownership = _mapping(coordination["ownership"])
    assert ownership["shared_mutable_state"] == "prohibited"
    assert "typed_signal_or_observation_or_inference_or_belief_or_prediction" in _strings(
        coordination["nb2_to_nb3_input"]
    )
    assert "non_authorizing_memory_evidence" in _strings(coordination["nb3_to_nb2_output"])
    prohibited = " ".join(_strings(coordination["prohibited"]))
    assert "expanding_scope_authority_or_policy" in prohibited


def test_nb3_retrieval_deletion_restore_and_evaluation_are_fail_closed() -> None:
    contract = _contract()
    retrieval = _mapping(contract["retrieval_contract"])
    assert retrieval["default"] == "deny"
    assert {
        "memory_kind",
        "source_provenance",
        "freshness_state",
        "uncertainty",
        "contradiction_state",
    } <= _strings(retrieval["result_must_bind"])
    excluded = " ".join(_strings(retrieval["normal_cognition_excludes"]))
    assert "out-of-scope" in excluded
    assert "procedural content as action" in excluded

    deletion = _mapping(contract["deletion_and_restore"])
    assert deletion["restore_default"] == "quarantined_and_not_ready"
    assert "No derivative may remain retrievable" in str(deletion["derivative_deletion_oracle"])
    assert any("cannot reappear" in item for item in _strings(deletion["restore_release_requires"]))

    evaluation = _mapping(contract["preregistered_evaluation"])
    assert _strings(evaluation["baselines"]) == {
        "no_memory",
        "naive_rag",
        "strongest_practical_non_memory_baseline",
    }
    families = " ".join(_strings(evaluation["required_families"]))
    for required in (
        "interference",
        "false_memory",
        "derivative_deletion",
        "restore_non_reappearance",
    ):
        assert required in families
    assert "cannot be averaged away" in str(evaluation["pass_semantics"])
