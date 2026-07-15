from pathlib import Path

import pytest

REPOSITORY_ROOT = Path(__file__).parents[2]
DIRECTIVE = REPOSITORY_ROOT / "docs" / "architecture" / "architecture-directive-v1.1.md"


@pytest.fixture(scope="module")
def directive_text() -> str:
    return DIRECTIVE.read_text(encoding="utf-8")


def test_directive_declares_its_normative_identity(directive_text: str) -> None:
    assert "# Neural Brain Architecture Directive v1.1" in directive_text
    assert "- Status: Normative Foundation baseline" in directive_text
    assert "- Work item: FND-02.1 / NB-10" in directive_text


@pytest.mark.parametrize(
    "required_section",
    [
        "## 5. Scope and authenticated runtime context",
        "## 8. Security floor, policy, approval, and kill switches",
        "## 9. Protected state and transition contracts",
        "## 14. Crash consistency, cancellation, reconciliation, and readiness",
        "## 15. Memory architecture and stage separation",
        "## 16. Privacy and data governance",
        "## 17. Intended-purpose contract",
        "## 18. Prohibited and unsupported use",
        "## 19. Regulatory applicability and role contract",
        "## 20. Per-scope compliance-release contract",
        "## 23. Release-stop criteria",
        "## 24. Engineering runtime and inference hold",
    ],
)
def test_directive_contains_required_contract_sections(
    directive_text: str, required_section: str
) -> None:
    assert required_section in directive_text


def test_directive_maps_every_current_accepted_adr(directive_text: str) -> None:
    for number in range(1, 14):
        assert f"| ADR-{number:03d} " in directive_text


def test_directive_preserves_delivery_order(directive_text: str) -> None:
    delivery_table = [
        "| Foundation / MS-0 |",
        "| Stage 1 / MS-1 |",
        "| Stage 2 / MS-2 |",
        "| Stage 3 / MS-3 |",
        "| Stage 4 / MS-4 |",
    ]
    offsets = [directive_text.index(row) for row in delivery_table]
    assert offsets == sorted(offsets)


@pytest.mark.parametrize(
    "release_stop",
    [
        "A forbidden transition is possible.",
        "Scope or principal can be taken from untrusted input.",
        "`Achieved` is reachable without independent evidence.",
        "Approval replay is possible.",
        "Budget can be charged twice or become negative.",
        "A non-idempotent ambiguous action can be retried automatically.",
        "Startup or restore can report `ready=true` before reconciliation.",
        "A kill switch can be bypassed.",
        "Backup or restore has not been proven.",
        "A stage gate is incomplete.",
    ],
)
def test_directive_contains_release_stops(directive_text: str, release_stop: str) -> None:
    assert release_stop in directive_text


def test_directive_keeps_inference_disabled_without_separate_adr(directive_text: str) -> None:
    normalized = " ".join(directive_text.split())
    assert "prohibits OpenAI use and automatic cloud fallback" in normalized
    assert "does not implement or authorize an inference adapter" in normalized
