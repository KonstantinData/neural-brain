"""Deterministic evidence for the non-authorizing Goal Gate revalidation proposal."""

from pathlib import Path

ROOT = Path(__file__).parents[2]
PROPOSAL = ROOT / "docs" / "architecture" / "goal-gate-adr-018-revalidation-proposal-v1.md"
TRACEABILITY = ROOT / "docs" / "traceability" / "FND-ENT-02-goal-gate-adr-revalidation.md"


def test_historical_goal_adrs_remain_explicitly_superseded_not_reactivated() -> None:
    proposal = PROPOSAL.read_text(encoding="utf-8")
    normalized = " ".join(proposal.split())

    assert "Status: Proposed; not accepted and not runtime authorization" in proposal
    assert "None of ADR-004, ADR-007, or ADR-011 is accepted as-is." in proposal
    assert proposal.count("Explicitly superseded historical evidence") == 3
    assert "does not supersede, amend, or reactivate them" in normalized


def test_proposal_preserves_authenticated_goal_gate_boundary_and_nb1_exclusions() -> None:
    proposal = PROPOSAL.read_text(encoding="utf-8")
    normalized = " ".join(proposal.split())

    assert "session-bound aggregate, not an isolation dimension" in normalized
    assert "Only a future Goal Transition Gate may write protected Goal state" in normalized
    assert "authenticated Protected Control Plane context" in normalized
    assert "Unknown, missing, stale, conflicting, unverifiable, or scope-mismatched" in normalized
    assert "At NB-1, only internal Goal and plan proposals" in normalized
    for exclusion in (
        "protected Goal lifecycle state",
        "`Achieved`",
        "Action Intent commitment",
        "approval-claim issuance",
        "production-autonomy claim",
    ):
        assert exclusion in normalized


def test_proposal_requires_authorized_acceptance_and_complete_future_evidence() -> None:
    proposal = PROPOSAL.read_text(encoding="utf-8")
    traceability = TRACEABILITY.read_text(encoding="utf-8")
    normalized = " ".join(proposal.split())

    assert (
        "Before any Goal runtime or migration, an authorized architecture owner must" in normalized
    )
    assert "state model, permitted transitions" in normalized
    assert "atomic transition plus audit" in normalized
    assert "independent verification, complete evidence, quiescence" in normalized
    assert "positive, negative, scope, authority, audit-failure, crash-boundary" in normalized
    assert (
        "does not create protected state, authority, policy activation, external effect"
        in traceability
    )
