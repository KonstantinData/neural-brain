"""Regression evidence that S1-06.6 remains blocked without a Gate contract."""

from pathlib import Path

ROOT = Path(__file__).parents[2]
BLOCKER = (ROOT / "docs" / "traceability" / "S1-06.6-separation-of-duties-blocker.md").read_text(
    encoding="utf-8"
)
NORMALIZED_BLOCKER = " ".join(BLOCKER.split())
OIDC = (ROOT / "src" / "neural_brain" / "consumer" / "oidc.py").read_text(encoding="utf-8")
PRINCIPAL_RESOLVER = (
    ROOT / "src" / "neural_brain" / "postgres" / "oidc_principal_resolver.py"
).read_text(encoding="utf-8")
APPROVAL = (ROOT / "src" / "neural_brain" / "security" / "memory_approval.py").read_text(
    encoding="utf-8"
)
REPOSITORY = (ROOT / "src" / "neural_brain" / "postgres" / "memory_repository.py").read_text(
    encoding="utf-8"
)


def test_s1_06_6_blocker_records_all_required_separation_boundaries() -> None:
    assert "`Blocked`." in NORMALIZED_BLOCKER
    assert "candidate producer cannot be the sole promoter" in NORMALIZED_BLOCKER
    assert "retrieval consumer cannot bypass source and policy assessment" in NORMALIZED_BLOCKER
    assert (
        "Automated lifecycle handling cannot act as human incident resolver." in NORMALIZED_BLOCKER
    )
    assert "Planner, executor, approver, and verifier cannot self-approve" in NORMALIZED_BLOCKER
    assert "S1-06.6a Gate-owned separation-decision contract" in NORMALIZED_BLOCKER


def test_current_identity_and_approval_seams_cannot_be_relabelled_as_a_channel() -> None:
    assert "return RuntimeContext(" in OIDC
    assert "roles=" not in OIDC
    assert "resolve_authenticated_principal" in PRINCIPAL_RESOLVER
    assert "principal_role_bindings" not in PRINCIPAL_RESOLVER
    assert "not a Memory Transition" in APPROVAL
    assert "approval channel" in APPROVAL
    assert "commit_memory_cycle(" in REPOSITORY
    assert "approve_memory" not in REPOSITORY
    assert "promote_candidate" not in REPOSITORY


def test_blocker_prohibits_standalone_role_or_approval_authority() -> None:
    assert (
        "standalone promotion/reconciliation service would create an untrusted"
        in NORMALIZED_BLOCKER
    )
    assert (
        "A general service or standalone approval repository is prohibited." in NORMALIZED_BLOCKER
    )
    assert (
        "payloads, model output, and approval evidence cannot supply or widen them"
        in NORMALIZED_BLOCKER
    )
