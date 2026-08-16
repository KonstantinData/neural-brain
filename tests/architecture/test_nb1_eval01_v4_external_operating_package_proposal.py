"""Regression checks for the proposed-only EVAL-01 v4 external operating package."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROPOSAL = (
    ROOT
    / "docs"
    / "architecture"
    / "contracts"
    / "nb1-eval01-v4-external-operating-package-proposal-v1.json"
)
GENERATOR = ROOT / "docs" / "architecture" / "evaluations" / "nb1-serial-context-generator-v4.json"
LEGACY_RUNBOOK = ROOT / "docs" / "runbooks" / "nb1-hidden-evaluation.md"
LEGACY_EVIDENCE_SCHEMA = ROOT / "src" / "neural_brain" / "cognition" / "hidden_evidence.py"
LEGACY_UNIT_TEST = ROOT / "tests" / "unit" / "test_nb1_hidden_evidence.py"


def _load() -> dict[str, object]:
    loaded: object = json.loads(PROPOSAL.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def test_proposal_is_non_authorizing_and_cannot_claim_operation_or_nb2() -> None:
    proposal = _load()

    assert proposal["status"] == "proposed_pending_accepted_architecture_clarification"
    assert proposal["authority"] == "non_authorizing"
    claims = proposal["claim_boundary"]
    assert isinstance(claims, dict)
    assert claims["role_appointment_or_attestation_issued"] is False
    assert claims["candidate_created_or_accepted"] is False
    assert claims["hidden_artifact_created_or_attached"] is False
    assert claims["registry_or_signing_key_created"] is False
    assert claims["evaluation_executed"] is False
    assert claims["evidence_admissible"] is False
    assert claims["evaluation_gates_passed"] == []
    assert claims["recognition_gates_passed"] == []
    assert claims["stage_release_authorized"] is False
    assert claims["neural_brain_candidate_claimed"] is False
    assert claims["nb2_activated"] is False
    assert claims["runtime_or_external_effect_enabled"] is False


def test_blockers_are_owned_and_fail_closed_before_external_work() -> None:
    blockers = _load()["blocking_preconditions"]
    assert isinstance(blockers, list)
    assert [blocker["id"] for blocker in blockers] == ["OP-B1", "OP-B2", "OP-B3"]
    assert [blocker["owner"] for blocker in blockers] == [
        "architecture_decision_owner",
        "designated_independent_review_authority",
        "implementation_owner_and_independent_reviewer",
    ]
    assert all(blocker["action"] and blocker["evidence"] for blocker in blockers)
    assert (
        blockers[0]["failure_outcome"]
        == "no_v4_candidate_freeze_hidden_attachment_or_external_operation"
    )
    assert blockers[1]["failure_outcome"] == "independent_evaluation_blocked"
    assert (
        blockers[2]["failure_outcome"] == "candidate_not_admissible_and_hidden_attachment_blocked"
    )
    assert "does not define their evaluation criteria or values" in blockers[0]["action"]


def test_v4_sole_evaluator_custody_rejects_legacy_separate_provider_route() -> None:
    reconciliation = _load()["v4_custody_reconciliation_proposal"]
    assert isinstance(reconciliation, dict)
    assert reconciliation["current_v4_model"].endswith("independent_evaluator_only.")
    assert "proposed replacement only" in reconciliation["legacy_surface_treatment"]
    assert set(reconciliation["prohibited_until_acceptance"]) == {
        "separate_provider_appointment",
        "separate_provider_organization_or_transfer",
        "v4_execution_through_inherited_provider_evaluator_schema",
        "retroactive_edit_of_frozen_v4_specification",
    }
    assert reconciliation["failure_outcome"].endswith("nb2_activation_blocked")


def test_inherited_separate_provider_surfaces_remain_blocked_pending_revalidation() -> None:
    proposal = _load()
    inventory = proposal["inherited_separate_provider_surface_inventory"]
    assert isinstance(inventory, list)
    assert [entry["path"] for entry in inventory] == [
        "docs/architecture/evaluations/nb1-serial-context-generator-v4.json",
        "docs/runbooks/nb1-hidden-evaluation.md",
        "src/neural_brain/cognition/hidden_evidence.py",
        "tests/unit/test_nb1_hidden_evidence.py",
    ]
    assert {entry["v4_status"] for entry in inventory} == {
        "conflicting_inherited_surface_blocked_pending_accepted_revalidation"
    }
    assert '"seed_visibility": "independent_provider_only"' in GENERATOR.read_text(encoding="utf-8")
    assert "A separate artifact provider" in LEGACY_RUNBOOK.read_text(encoding="utf-8")
    assert "evaluator, provider, and implementation ownership must be separate" in (
        LEGACY_EVIDENCE_SCHEMA.read_text(encoding="utf-8")
    )
    assert "test_provider_evaluator_and_split_identity_must_remain_separate" in (
        LEGACY_UNIT_TEST.read_text(encoding="utf-8")
    )


def test_workflow_is_ordered_external_and_never_auto_passes_a_gate() -> None:
    workflow = _load()["ordered_external_workflow"]
    assert isinstance(workflow, list)
    assert [step["id"] for step in workflow] == [f"OP-{index:02d}" for index in range(1, 10)]
    assert all(step["owner"] and step["action"] and step["admission_rule"] for step in workflow)
    assert workflow[4]["owner"] == "independent_evaluator"
    assert "sole v4 hidden-material custodian" in workflow[4]["action"]
    assert "network-disabled" in workflow[5]["action"]
    assert "append-only ledger" in workflow[5]["admission_rule"]
    assert "detached Ed25519 signature" in workflow[6]["action"]
    assert "automatically passes G0, G1" in workflow[-1]["admission_rule"]
