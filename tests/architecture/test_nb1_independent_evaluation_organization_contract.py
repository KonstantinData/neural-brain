"""Fail-closed organization preparation for a future independent EVAL-01 run."""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "docs/architecture/contracts/nb1-independent-evaluation-organization-v1.json"


def _load() -> dict[str, Any]:
    loaded = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def test_organization_contract_is_preparation_only_and_non_authorizing() -> None:
    contract = _load()

    assert contract["status"] == "preparation_only_roles_unappointed"
    assert contract["decision"] == "ADR-018"
    assert contract["scope"]["evaluation_spec"] == "EVAL-01.NB-1.safe-serial-cognition.v4"
    assert set(contract["scope"]["prohibited"]) == {
        "role_appointment",
        "authority_grant",
        "candidate_acceptance",
        "hidden_data_attachment",
        "evaluation_execution",
        "gate_passage",
        "stage_release",
        "recognition_claim",
        "runtime_or_external_effect",
    }


def test_all_nine_roles_define_full_boundaries_and_evidence() -> None:
    roles = _load()["roles"]
    assert set(roles) == {
        "implementation_owner",
        "hidden_dataset_provider",
        "independent_evaluator",
        "independent_reviewer",
        "registry_custodian",
        "key_custodian",
        "audit_owner",
        "release_authority",
        "recognition_authority",
    }
    for role in roles.values():
        assert role["responsibilities"]
        assert role["rights"]
        assert role["prohibitions"]
        assert role["independent_from"]
        assert role["required_evidence"]
    assert "hidden seed" in " ".join(roles["implementation_owner"]["prohibitions"])
    assert "network-disabled" in " ".join(roles["independent_evaluator"]["responsibilities"])
    assert "EVAL-01 alone" in " ".join(roles["recognition_authority"]["prohibitions"])


def test_v4_keeps_hidden_dataset_provider_as_evaluator_only_logical_duty() -> None:
    contract = _load()
    binding = contract["v4_custody_binding"]
    provider = contract["roles"]["hidden_dataset_provider"]
    evaluator = contract["roles"]["independent_evaluator"]

    assert binding["logical_duty"] == "hidden_dataset_provider"
    assert binding["performed_by"] == "independent_evaluator_only"
    assert binding["separate_provider_organization"].startswith("prohibited")
    assert provider["role_type"] == "logical_duty_not_a_separate_organizational_role_under_v4"
    assert provider["performed_by"] == "independent_evaluator_only"
    assert (
        "exist_as_a_separate_provider_organization_or_actor_under_frozen_v4"
        in provider["prohibitions"]
    )
    assert "hidden_dataset_provider" not in evaluator["independent_from"]
    assert set(binding["independence_preserved"]) == {
        "independent_evaluator_from_implementation_owner",
        "independent_evaluator_from_independent_reviewer",
    }


def test_common_independence_deputy_handoff_and_escalation_fail_closed() -> None:
    common = _load()["common_role_requirements"]
    assert "never evidence of independence" in common["independence"]
    assert "never inherits authority implicitly" in common["deputy"]
    assert "Incomplete handoffs block" in common["handoff"]
    assert "inadmissible" in common["escalation"]
    failures = _load()["fail_closed"]
    assert failures == {
        "unappointed_or_unattested_role": "blocked",
        "role_conflict_or_insufficient_independence": "blocked",
        "missing_deputy_or_handoff_record": "blocked",
        "unclear_decision_owner_or_scope": "blocked",
        "attempt_to_derive_authority_from_this_contract": "prohibited",
    }


def test_all_required_matrices_are_complete_and_keep_decisions_external() -> None:
    matrices = _load()["matrices"]
    assert set(matrices) == {"raci", "approval", "review", "deputy", "escalation", "decision"}
    assert {row["activity"] for row in matrices["raci"]} == {
        "public_candidate_freeze_submission",
        "hidden_commitment",
        "hidden_scoring_and_ledger",
        "evidence_admissibility_recommendation",
        "registry_integrity",
        "key_lifecycle",
        "audit_exception_closure",
        "stage_release_decision",
        "recognition_decision",
    }
    assert {row["decision"] for row in matrices["approval"]} == {
        "role_and_separation_acceptance",
        "freeze_admissibility",
        "evidence_admissibility",
        "stage_release",
        "recognition",
    }
    assert all(row["must_be_external"] is True for row in matrices["review"])
    assert matrices["deputy"][0]["implicit_delegation"] is False
    assert {row["effect"] for row in matrices["escalation"]} >= {
        "block_affected_decision",
        "invalidate_evidence_and_block_gate_review",
        "revoke_or_reject_key_and_block_evidence",
        "evidence_not_admissible",
    }
    assert all(row["repository_authorization"] is False for row in matrices["decision"])
