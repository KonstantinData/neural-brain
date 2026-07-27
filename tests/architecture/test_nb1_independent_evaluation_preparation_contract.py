"""Fail-closed preparation evidence for a future independent EVAL-01 run."""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "docs/architecture/contracts/nb1-independent-evaluation-preparation-v1.json"


def _load() -> dict[str, Any]:
    loaded = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def test_preparation_is_v4_only_and_cannot_claim_execution_or_release() -> None:
    contract = _load()

    assert contract["status"] == "preparation_only_external_execution_blocked"
    assert contract["decision"] == "ADR-018"
    evaluation_spec = contract["evaluation_spec"]
    assert evaluation_spec["id"] == "EVAL-01.NB-1.safe-serial-cognition.v4"
    assert (
        evaluation_spec["required_status"]
        == "frozen_before_candidate_training_and_hidden_attachment"
    )
    assert evaluation_spec["rejected_historical_spec"] == "EVAL-01.NB-1.safe-serial-cognition.v3"
    claim_boundary = contract["claim_boundary"]
    assert claim_boundary["evaluation_performed"] is False
    assert claim_boundary["candidate_created"] is False
    assert claim_boundary["hidden_artifact_created_or_attached"] is False
    assert claim_boundary["signing_key_created_or_registered"] is False
    assert claim_boundary["signature_or_attestation_issued"] is False
    assert claim_boundary["evaluation_gates_passed"] == []
    assert claim_boundary["recognition_gates_passed"] == []
    assert claim_boundary["stage_release_authorized"] is False
    assert claim_boundary["neural_brain_candidate_claimed"] is False
    assert claim_boundary["runtime_or_external_effect_enabled"] is False


def test_candidate_freeze_requires_all_v4_bindings_and_reproducibility() -> None:
    freeze = _load()["candidate_freeze"]

    assert freeze["required_before_hidden_attachment"] is True
    assert freeze["candidate_must_be_v4_bound"] is True
    assert freeze["clean_committed_source_tree_required"] is True
    assert freeze["hash_algorithm"] == "SHA-256"
    assert freeze["canonicalization_profile_id"] == "nb1-eval-canonical-json-v1"
    assert (
        freeze["canonicalization_artifact_kind_mapping_source"]
        == "docs/architecture/contracts/nb1-independent-evaluation-artifact-manifests-v1.json#/canonicalization/artifact_kind_byte_rules"
    )
    assert set(freeze["required_freeze_receipt_bindings"]) == {
        "source_commit",
        "source_tree_digest",
        "candidate_artifact_digest",
        "model_manifest_digest",
        "parameter_digest",
        "training_artifact_digest",
        "public_train_artifact_digest",
        "public_development_artifact_digest",
        "dataset_and_split_digests",
        "training_code_digest",
        "candidate_code_digest",
        "evaluation_contract_digest",
        "evaluation_spec_digest",
        "generator_contract_digest",
        "dependency_lock_digest",
        "fixed_train_derived_majority_label",
        "frozen_at",
    }
    requirements = " ".join(freeze["reproducibility_requirements"])
    assert "recompute" in requirements
    assert "invalidates" in requirements
    assert "hidden" in requirements
    assert set(freeze["model_manifest_required_fields"]) == {
        "model_version_and_architecture_identifier",
        "candidate_code_digest",
        "parameter_digest",
        "training_code_digest",
        "training_artifact_digest",
        "public_train_artifact_digest",
        "public_development_artifact_digest",
        "dataset_and_split_digests",
        "evaluation_spec_digest",
        "generator_contract_digest",
        "resource_bound_declaration",
    }
    assert set(freeze["evaluation_manifest_required_fields"]) == {
        "evaluation_protocol_identifier_and_digest",
        "evaluation_spec_digest",
        "generator_contract_digest",
        "candidate_bundle_digest",
        "baseline_and_ablation_declarations",
        "threshold_and_failure_criterion_declarations",
        "confidence_interval_method_declaration",
        "resource_budget_declaration",
        "environment_digest",
        "evaluation_executable_digest",
    }


def test_custody_and_separation_prohibit_hidden_disclosure_and_self_certification() -> None:
    custody = _load()["custody_and_separation"]
    hidden = custody["hidden_dataset_and_seed"]
    assert hidden["custodian"] == "independent_evaluator_only"
    assert "separate provider/evaluator organization is prohibited" in hidden["v4_custody_binding"]
    assert {
        "hidden_seed",
        "hidden_examples",
        "expected_labels",
        "latent_variables",
        "per_sequence_correctness",
    } <= set(hidden["never_disclosed_to_implementer"])
    roles = custody["required_roles"]
    assert set(roles) == {
        "implementation_owner",
        "hidden_artifact_provider",
        "independent_evaluator",
        "independent_reviewer",
    }
    rules = " ".join(custody["separation_rules"])
    assert "subagent" in rules.lower()
    assert "cannot hold the hidden seed" in rules
    assert "may not modify the frozen candidate" in rules
    assert "separate provider/evaluator identity is rejected" in rules


def test_registry_ledger_and_signatures_are_reviewer_and_evaluator_owned() -> None:
    requirements = _load()["registry_and_evidence_requirements"]

    assert requirements["registry_custodian"] == "independent_reviewer"
    assert {
        "accepted_specification_id_to_digest",
        "accepted_candidate_bundle_digest_to_complete_freeze_receipt",
        "accepted_hidden_commitment_id_to_canonical_commitment_digest",
        "provider_evaluator_reviewer_identity_to_attestation_digest",
        "signer_id_to_trusted_ed25519_public_key_and_key_status",
        "evaluation_protocol_digest_to_accepted_protocol_version",
    } <= set(requirements["required_external_registries"])
    key_requirements = " ".join(requirements["public_key_registry_requirements"])
    assert "revocation status" in key_requirements
    assert "Private keys" in key_requirements
    ledger = requirements["evidence_ledger"]
    assert ledger["owner"] == "independent_evaluator"
    assert ledger["append_only"] is True
    assert ledger["all_attempts_mandatory"] is True
    assert {"previous_entry_digest", "entry_digest", "failure_summary_digest_or_null"} <= set(
        ledger["required_attempt_fields"]
    )
    signature = requirements["attestation_and_signature"]
    assert signature["digest_algorithm"] == "SHA-256"
    assert signature["signature_algorithm"] == "Ed25519 detached signature"
    assert "does not prove independence" in signature["structural_validity_limit"]


def test_workflow_tests_failures_and_external_blockers_are_concrete() -> None:
    contract = _load()

    workflow = contract["review_workflow"]
    assert len(workflow) == 6
    assert "automatically passes G0" in workflow[-1]
    test_plan = contract["test_plan"]
    assert len(test_plan["repository_contract_tests"]) >= 5
    assert len(test_plan["external_independent_tests"]) >= 5
    failures = contract["fail_closed"]
    assert failures["unknown_or_missing_candidate_freeze_binding"].endswith("blocked")
    assert failures["any_unknown_failure_or_contamination_result"] == "evidence_not_admissible"
    assert failures["attempted_runtime_release_or_recognition_claim"] == "prohibited"
    blockers = contract["external_blockers"]
    assert {blocker["id"] for blocker in blockers} == {"EVAL-01-B1", "EVAL-01-B2", "EVAL-01-B3"}
    for blocker in blockers:
        assert blocker["cause"]
        assert blocker["owner"]
        assert blocker["required_evidence"]
        assert blocker["required_approval"]
        assert blocker["impact"]
        assert blocker["unblocker"]
