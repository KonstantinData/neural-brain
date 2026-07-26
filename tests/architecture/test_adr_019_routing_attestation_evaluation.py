from pathlib import Path

ROOT = Path(__file__).parents[2]
ADR_019_PATH = (
    ROOT / "docs" / "adr" / "ADR-019-tenant-bound-runtime-database-identities-and-pools.md"
)
EVALUATION_PATH = ROOT / "docs" / "governance" / "adr-019-routing-attestation-evaluation.md"
READINESS_PATH = ROOT / "docs" / "traceability" / "memory-core-production-readiness.md"


def _normalized(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


def test_routing_attestation_evaluation_preserves_adr_019_source_boundary() -> None:
    adr_019 = _normalized(ADR_019_PATH)
    evaluation = _normalized(EVALUATION_PATH)

    source_boundary = (
        "Workload- or channel-bound routing attestation is compatible later hardening, "
        "but is not part of FND-06 and requires a separate accepted decision before "
        "becoming mandatory."
    )
    assert source_boundary in adr_019
    assert source_boundary in evaluation
    assert "does not amend ADR-019" in evaluation
    assert "one restricted Runtime login and one dedicated pool per Tenant" in evaluation
    assert "protected `session_user` mapping" in evaluation


def test_routing_attestation_evaluation_covers_spoofing_and_confused_deputy_paths() -> None:
    evaluation = _normalized(EVALUATION_PATH).lower()

    for required in (
        "oidc tenant claim",
        "workload identity",
        "mtls or channel binding",
        "gateway assertion",
        "dedicated database routing",
        "spoofing or confused-deputy path",
        "foreign-pool route fails",
        "replayed",
        "audience-confused",
        "tenant-confused",
    ):
        assert required in evaluation


def test_routing_attestation_evaluation_does_not_change_fnd_06_or_release_gates() -> None:
    evaluation = _normalized(EVALUATION_PATH)
    readiness = _normalized(READINESS_PATH)

    assert "no FND-06 or release-gate change" in evaluation
    assert "This evaluation neither removes a release stop" in evaluation
    assert "general cryptographic context attestation is not selected" in readiness
    assert "FND-06 pull request may claim" in readiness


def test_future_attestation_requires_a_separate_accepted_adr_and_complete_contract() -> None:
    evaluation = _normalized(EVALUATION_PATH).lower()

    for required in (
        "a new adr is required before routing attestation becomes mandatory",
        "residual spoofing or confused-deputy risk",
        "trusted issuer",
        "nonce or replay protection",
        "fails closed",
        "independent adversarial tests",
        "accountable operator",
    ):
        assert required in evaluation
