"""Evidence for the fail-closed model and inference inventory contract."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).parents[2]
CONTRACT_PATH = ROOT / "docs" / "architecture" / "contracts" / "model-inference-inventory-v1.json"


def _contract() -> dict[str, object]:
    loaded: object = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _strings(value: object) -> set[str]:
    assert isinstance(value, list)
    assert all(isinstance(item, str) for item in value)
    return set(value)


def test_inventory_requires_complete_immutable_model_and_inference_evidence() -> None:
    contract = _contract()
    assert contract["contract_id"] == "neural-brain.model-inference-inventory"
    assert contract["contract_version"] == "1.0.0"
    assert contract["governing_decisions"] == [
        "ADR-018",
        "architecture-directive-v4.0",
        "neural-brain-recognition-standard",
    ]
    record = contract["inventory_record"]
    assert isinstance(record, dict)
    required = _strings(record["required_fields"])
    assert {
        "model_identifier",
        "model_version",
        "immutable_model_or_artifact_digest",
        "provenance_and_source_reference",
        "supplier_or_producer_identity",
        "licence_or_usage_terms_reference",
        "model_card_or_equivalent_documentation_reference",
        "quantisation_or_precision_configuration",
        "context_window_or_input_bound",
        "inference_boundary_and_deployment_status",
        "evaluation_status_and_evidence_references",
    } <= required
    assert "active_without_gate" in _strings(record["forbidden_lifecycle_statuses"])


def test_unknown_inventory_or_evaluation_evidence_fails_closed() -> None:
    validation = _contract()["validation"]
    assert isinstance(validation, dict)
    assert (
        validation["unknown_inventory_entry"]
        == "inventory_record_incomplete_and_model_or_inference_use_denied"
    )
    assert (
        validation["unknown_missing_stale_contradictory_or_scope_mismatched_field"]
        == "inventory_record_incomplete_and_model_or_inference_use_denied"
    )
    assert (
        validation["unknown_evaluation_status"]
        == "inventory_record_incomplete_and_capability_deployment_promotion_and_recognition_claim_denied"
    )
    assert (
        validation["target_or_not_deployed_status"]
        == "no_runtime_activation_or_deployment_authorized"
    )
    assert validation["inventory_record_is_not_authority"] is True
    assert validation["inventory_record_is_not_release_approval"] is True
    assert validation["inventory_record_is_not_model_promotion"] is True
    assert validation["inventory_record_is_not_recognition_evidence"] is True


def test_current_absence_and_ollama_boundary_cannot_be_represented_as_activation() -> None:
    contract = _contract()
    facts = contract["repository_facts_at_contract_creation"]
    assert isinstance(facts, dict)
    verified = _strings(facts["verified_facts"])
    assert (
        "The repository has no approved production model deployment or runtime inference adapter."
        in verified
    )
    assert any(
        "no Ollama adapter, activation, fallback, or deployment record" in fact for fact in verified
    )
    prohibitions = _strings(contract["prohibitions"])
    assert any("No inventory record enables Ollama" in item for item in prohibitions)
    assert any("No productive model mutates itself" in item for item in prohibitions)
    current_blocker = contract["current_blocker"]
    assert isinstance(current_blocker, dict)
    assert current_blocker["status"] == "no_productive_model_or_inference_deployment_record"
