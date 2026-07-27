"""Deterministic evidence for the non-authorizing Kill-Switch revalidation proposal."""

from pathlib import Path

ROOT = Path(__file__).parents[2]
PROPOSAL = (
    ROOT
    / "docs"
    / "architecture"
    / "protected-control-kill-switch-adr-018-revalidation-proposal-v1.md"
)
TRACEABILITY = ROOT / "docs" / "traceability" / "S1-02.5-protected-control-kill-switch.md"


def test_historical_kill_switch_adr_remains_unaccepted_and_not_reactivated() -> None:
    proposal = PROPOSAL.read_text(encoding="utf-8")
    normalized = " ".join(proposal.split())

    assert "Status: Proposed; not accepted and not runtime authorization" in proposal
    assert "ADR-006 is historical evidence." in proposal
    assert "is not reactivated" in normalized
    assert "cannot authorize a runtime implementation" in normalized


def test_proposal_requires_complete_protected_control_plane_boundary() -> None:
    proposal = PROPOSAL.read_text(encoding="utf-8")
    normalized = " ".join(proposal.split())

    for required in (
        "`enabled`, `drain`, `disabled`, and `recovery`",
        "Immutable authenticated Brain/Tenant/Area/Project/Session scope",
        "Separate kill operator, independent Safety Supervisor",
        "Atomic compare-and-swap transitions with monotonic revisions",
        "crash, restart, partition, timeout, and indeterminate effects",
        "remains disabled by default",
    ):
        assert required in normalized


def test_proposal_excludes_early_runtime_and_requires_authorized_acceptance() -> None:
    proposal = PROPOSAL.read_text(encoding="utf-8")
    traceability = TRACEABILITY.read_text(encoding="utf-8")
    normalized = " ".join(proposal.split())

    assert "NB-1 is limited to internal cognition" in normalized
    for excluded in (
        "a Kill Switch runtime, database table, migration, state writer",
        "Action Intent commitment, tool invocation",
        "supplies authority, safety, availability, release readiness, or recognition",
    ):
        assert excluded in normalized
    assert "architecture decision owner must accept" in normalized
    assert "independent security/safety reviewer" in normalized
    assert "does not authorize runtime" in traceability
