"""Evidence for the bounded, non-runtime Goal Transition Gate prerequisite."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).parents[2]
CONTRACT_PATH = ROOT / "docs" / "architecture" / "contracts" / "goal-transition-gate-v1.json"


def _contract() -> dict[str, object]:
    loaded: object = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _strings(value: object) -> set[str]:
    assert isinstance(value, list)
    assert all(isinstance(item, str) for item in value)
    return set(value)


def test_goal_aggregate_is_scope_bound_gate_owned_and_fail_closed() -> None:
    contract = _contract()
    assert contract["contract_id"] == "neural-brain.goal-transition-gate"
    assert contract["status"] == "nb1_prerequisite_contract_not_runtime_authorization"
    assert contract["governing_decisions"] == ["ADR-018", "ADR-019"]
    assert contract["historical_inputs_requiring_revalidation"] == ["ADR-004", "ADR-007", "ADR-011"]
    boundary = contract["aggregate_boundary"]
    assert isinstance(boundary, dict)
    assert boundary["aggregate"] == "goal"
    assert boundary["isolation_dimension"] is False
    assert boundary["binding"] == "session_bound_protected_aggregate"
    assert boundary["sole_protected_state_writer"] == "Goal Transition Gate"
    assert boundary["trusted_context_source"] == "authenticated_runtime_context"
    assert boundary["default_on_unknown_or_missing"] == "deny_before_protected_transition"
    assert _strings(contract["immutable_authenticated_scope_fields"]) == {
        "tenant_id",
        "area_id",
        "project_id",
        "session_id",
    }


def test_goal_lineage_and_evidence_references_cannot_create_authority() -> None:
    contract = _contract()
    lineage = contract["identity_and_lineage_fields"]
    assert isinstance(lineage, dict)
    assert {
        "goal_id",
        "origin_ref",
        "creator_principal_id",
        "creator_request_ref",
        "parent_goal_id_or_root_marker",
    } <= _strings(lineage["required"])
    assert any("never an isolation scope" in item for item in _strings(lineage["invariants"]))
    assert _strings(contract["required_evidence_reference_fields"]) == {
        "authority_snapshot_ref",
        "success_criterion_ref",
        "proposal_provenance_ref",
        "audit_evidence_ref",
    }
    requirements = _strings(contract["transition_requirements"])
    assert any("none independently creates authority or success" in item for item in requirements)
    assert any(
        "Only a future revalidated Goal Transition Gate may write Achieved" in item
        for item in requirements
    )


def test_nb1_allows_checkpoint_bound_proposals_not_deadline_or_budget_runtime() -> None:
    fields = _contract()["bounded_timing_budget_and_checkpoint_fields"]
    assert isinstance(fields, list)
    assert all(isinstance(field, dict) for field in fields)
    by_name = {str(field["field"]): field for field in fields if isinstance(field, dict)}
    assert set(by_name) == {"deadline_ref_or_null", "budget_ref_or_null", "checkpoint_ref_or_null"}
    assert (
        by_name["deadline_ref_or_null"]["minimum_authorization"]
        == "explicit_accepted_nb1_revalidation"
    )
    assert (
        by_name["budget_ref_or_null"]["minimum_authorization"]
        == "explicit_accepted_nb1_revalidation"
    )
    assert (
        by_name["checkpoint_ref_or_null"]["minimum_authorization"] == "nb1_internal_proposal_only"
    )
    checkpoint_semantics = by_name["checkpoint_ref_or_null"]["nb1_semantics"]
    assert isinstance(checkpoint_semantics, str)
    assert (
        "neither a protected Goal-state checkpoint nor a transition authorization"
        in checkpoint_semantics
    )


def test_stage_map_and_explicit_exclusions_prevent_early_goal_runtime_or_effects() -> None:
    stages = _contract()["stage_boundary_map"]
    assert isinstance(stages, list)
    assert all(isinstance(stage, dict) for stage in stages)
    by_stage = {str(stage["stage"]): stage for stage in stages if isinstance(stage, dict)}
    assert {"NB-0", "NB-1", "NB-5", "NB-7"} == set(by_stage)
    assert "Goal runtime" in _strings(by_stage["NB-0"]["prohibited"])
    assert "action execution" in _strings(by_stage["NB-1"]["prohibited"])
    assert "Achieved transition" in _strings(by_stage["NB-1"]["prohibited"])
    assert "independent effect and goal verification" in _strings(
        by_stage["NB-5"]["allowed_only_after_earlier_gates"]
    )
    exclusions = _strings(_contract()["explicit_exclusions"])
    assert {
        "action execution or tool invocation",
        "approval claim issuance, validation, or consumption",
        "budget reservation, resource locking, claim release, or fence issuance",
        "Goal runtime, protected Goal table, migration, or database writer",
    } <= exclusions


def test_historical_goal_adrs_block_runtime_and_migration_until_revalidation() -> None:
    blocker = _contract()["implementation_blocker"]
    assert isinstance(blocker, dict)
    assert blocker["status"] == "blocked_pending_accepted_complete_system_goal_gate_revalidation"
    assert "ADR-004, ADR-007, and ADR-011 are historical" in str(blocker["reason"])
    assert "do not add a Goal runtime or migration" in str(blocker["next_step"])
