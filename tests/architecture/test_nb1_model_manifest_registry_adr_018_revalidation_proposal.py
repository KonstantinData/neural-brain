"""Deterministic evidence for the non-authorizing NB-1 manifest-registry proposal."""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).parents[2]
PROPOSAL = (
    ROOT
    / "docs"
    / "architecture"
    / "nb1-model-manifest-registry-adr-018-revalidation-proposal-v1.md"
)
CONTRACT = (
    ROOT
    / "docs"
    / "architecture"
    / "contracts"
    / "nb1-model-manifest-registry-adr-018-revalidation-v1.json"
)


def _contract() -> dict[str, Any]:
    loaded = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def test_proposal_is_not_an_accepted_adr_or_runtime_authorization() -> None:
    proposal = PROPOSAL.read_text(encoding="utf-8")
    normalized = " ".join(proposal.split())

    assert "Status: Proposed prerequisite; not accepted and not runtime authorization" in proposal
    assert "This is not an accepted ADR." in proposal
    assert "authorizes no migration, registry, runtime path, model activation" in normalized
    assert "No migration or runtime implementation is authorized by this proposal." in proposal
    for exclusion in (
        "no hidden data is created, accessed, or stored",
        "no independent party is appointed or claimed",
        "no NB-2 capability is enabled",
        "no stage, release, recognition, or production-readiness claim is made",
    ):
        assert exclusion in normalized


def test_proposal_requires_database_authority_and_separates_gate_roles() -> None:
    contract = _contract()
    gap = contract["current_gap"]
    boundary = contract["proposed_registry_boundary"]
    separation = contract["authority_separation"]

    assert gap == {
        "trusted_by_postgresql_cognitive_gate": ["training_artifact_digest"],
        "caller_supplied_active_model_provenance": [
            "model_version",
            "parameter_digest",
            "training_code_digest",
            "contract_digest",
            "evaluation_spec_digest",
        ],
        "required_remediation": "database_authoritative_immutable_manifest_and_scope_bound_runtime_binding",
    }
    assert boundary["sole_protected_writer"] == "Learning and Model Promotion Gate"
    assert boundary["registration_activates_or_promotes"] is False
    assert boundary["caller_envelope_may_supply_trusted_provenance"] is False
    assert boundary["events"] == "append_only"
    assert boundary["revocation_blocks_new_cognitive_commits"] is True
    assert boundary["recovery_retargets_checkpoint"] is False
    assert separation["general_application_roles"] == "direct_dml_denied"
    assert separation["evaluation_roles"] == "no_runtime_registry_write_or_runtime_authority"


def test_proposal_preserves_scope_fencing_and_eval01_custody_separation() -> None:
    contract = _contract()
    binding = contract["proposed_registry_boundary"]["runtime_binding_required_bindings"]
    custody = contract["candidate_evaluation_custody_boundary"]

    assert {
        "authenticated_tenant_id",
        "authenticated_area_id",
        "project_and_session_when_narrower",
        "manifest_identity_and_digest",
        "monotonic_binding_fence_epoch",
    } == set(binding)
    assert custody["is_eval01_candidate_freeze_or_reviewer_registry"] is False
    assert custody["runtime_registry_substitutes_for_independent_evaluation"] is False
    assert custody["opaque_external_evidence_reference_interprets_or_authorizes"] is False
    assert {
        "hidden_seed",
        "hidden_examples",
        "hidden_labels",
        "scores",
        "thresholds",
        "evaluator_keys",
        "evaluator_identity",
        "independence_assertions",
        "custody_attestations",
        "evaluation_acceptance",
        "promotion_approval",
        "release_outcome",
    } == set(custody["forbidden_fields"])


def test_proposal_requires_acceptance_and_complete_post_acceptance_evidence() -> None:
    contract = _contract()
    acceptance = contract["acceptance"]

    assert contract["status"] == "proposed_prerequisite_not_accepted_not_runtime_authorization"
    assert contract["governing_decisions"] == [
        "ADR-003",
        "ADR-005",
        "ADR-016",
        "ADR-018",
        "ADR-019",
        "architecture-directive-v4.0",
    ]
    assert contract["successor_packages_after_accepted_adr"] == [
        "A_schema_and_authority",
        "B_gate_integration",
        "C_runtime_adapter",
        "D_operations_and_recovery",
        "E_independent_verification_evidence",
    ]
    assert len(contract["required_test_evidence_after_acceptance"]) == 6
    assert all(
        value is False
        for key, value in acceptance.items()
        if key != "required_before_successor_implementation"
    )
    assert acceptance["required_before_successor_implementation"] is True
