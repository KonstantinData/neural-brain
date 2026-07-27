"""Deterministic evidence for the non-authorizing NB-1 planner proposal."""

import json
from pathlib import Path

ROOT = Path(__file__).parents[2]
PROPOSAL = (
    ROOT / "docs" / "architecture" / "nb1-planner-verification-adr-018-revalidation-proposal-v1.md"
)
CONTRACT = (
    ROOT / "docs" / "architecture" / "contracts" / "nb1-planner-verification-revalidation-v1.json"
)


def test_proposal_does_not_reactivate_historical_authority_or_enable_runtime() -> None:
    proposal = PROPOSAL.read_text(encoding="utf-8")
    normalized = " ".join(proposal.split())

    assert "Status: Proposed prerequisite; not accepted and not runtime authorization" in proposal
    assert "does not amend, reactivate, or replace historical S1/S4 material" in normalized
    assert "not an accepted ADR" in normalized
    assert "No migration is authorized by this proposal." in proposal
    for exclusion in (
        "protected Goal checkpoint",
        "dispatch a tool",
        "Goal/Action runtime",
        "model mutation",
        "production-autonomy claim",
    ):
        assert exclusion in normalized


def test_proposal_preserves_the_adr_018_two_plane_and_verification_boundary() -> None:
    proposal = PROPOSAL.read_text(encoding="utf-8")
    normalized = " ".join(proposal.split())

    assert (
        "Cognitive Plane planner may emit an immutable typed internal plan proposal" in normalized
    )
    assert "authenticated Protected Control Plane context" in normalized
    assert "Unknown, missing, stale, conflicting, unverifiable, or scope-mismatched" in normalized
    assert (
        "Planner output, model confidence, executor output, HTTP status, or tool success"
        in normalized
    )
    assert "Only the revalidated Goal Transition Gate may write `Achieved`" in normalized
    assert "independent verification, complete evidence, and quiescence" in normalized


def test_machine_readable_proposal_has_fail_closed_successor_mapping() -> None:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))

    assert contract["status"] == "proposed_prerequisite_not_accepted_not_runtime_authorization"
    assert contract["governing_decisions"] == ["ADR-018", "ADR-019", "architecture-directive-v4.0"]
    assert contract["successor_tasks"] == ["S1-10.1", "S1-10.3", "S1-10.6"]
    assert contract["trust_boundary"]["default_on_unknown_or_stale_fact"] == "deny"
    assert contract["verification_boundary"]["planner_or_tool_success_is_goal_success"] is False
    assert contract["acceptance"]["required_before_successor_implementation"] is True
    assert contract["migrations_authorized"] is False
    assert contract["runtime_enabled"] is False
    assert contract["external_effects_enabled"] is False
    assert contract["stage_release_authorized"] is False
