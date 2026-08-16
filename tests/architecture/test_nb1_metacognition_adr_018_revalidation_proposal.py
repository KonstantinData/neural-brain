"""Regression checks for the non-authorizing NB-1 metacognition proposal."""

from pathlib import Path

ROOT = Path(__file__).parents[2]
PROPOSAL = ROOT / "docs" / "architecture" / "nb1-metacognition-adr-018-revalidation-proposal-v1.md"


def test_proposal_remains_non_authorizing_and_preserves_stage_boundaries() -> None:
    proposal = PROPOSAL.read_text(encoding="utf-8")
    normalized = " ".join(proposal.split())

    assert "Status: Proposed prerequisite; not accepted and not runtime authorization" in proposal
    assert "does not amend the contract, enable a runtime decision" in normalized
    assert "remains an NB-6 prerequisite" in normalized
    for exclusion in (
        "Action Intent",
        "external effect",
        "model mutation",
        "evaluation-gate result",
        "NB-2 activation",
        "production claim",
    ):
        assert exclusion in normalized


def test_proposal_does_not_invent_calibration_or_eval_01_criteria() -> None:
    proposal = PROPOSAL.read_text(encoding="utf-8")
    normalized = " ".join(proposal.split())

    assert (
        "No numeric cutoff, metric, threshold, calibration claim, candidate criterion" in normalized
    )
    assert "separate accepted EVAL-01 v4 clarification is required" in normalized
    assert "nor permits reuse or relabelling of rejected v3 artifacts" in normalized
