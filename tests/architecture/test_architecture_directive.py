from pathlib import Path

import pytest

REPOSITORY_ROOT = Path(__file__).parents[2]
CURRENT_DIRECTIVE = REPOSITORY_ROOT / "docs" / "architecture" / "architecture-directive-v2.0.md"
HISTORICAL_DIRECTIVE = REPOSITORY_ROOT / "docs" / "architecture" / "architecture-directive-v1.1.md"


@pytest.fixture(scope="module")
def directive_text() -> str:
    return CURRENT_DIRECTIVE.read_text(encoding="utf-8")


def test_v2_directive_declares_normative_memory_identity(directive_text: str) -> None:
    assert "# Neural Brain Architecture Directive v2.0" in directive_text
    assert "- Status: Normative memory-system baseline" in directive_text
    assert "- Governing decision: ADR-015" in directive_text
    assert "It is not an agent" in directive_text


def test_v1_1_is_preserved_as_superseded_history() -> None:
    text = HISTORICAL_DIRECTIVE.read_text(encoding="utf-8")
    assert "# Neural Brain Architecture Directive v1.1" in text
    assert "- Status: Superseded by Architecture Directive v2.0 and ADR-015" in text
    assert "This directive is no longer implementation authority" in text


@pytest.mark.parametrize(
    "required_section",
    [
        "## 2. System boundary",
        "## 3. Scope and authenticated context",
        "## 4. Trust, validation, and consumer ports",
        "## 5. Memory lifecycle and protected state",
        "## 6. Memory forms and retrieval",
        "## 7. Security and governance",
        "## 8. PostgreSQL, audit, and crash consistency",
        "## 9. Privacy, retention, and deletion",
        "## 10. Local inference boundary",
        "## 11. Delivery stages",
        "## 12. Verification and release stops",
        "## 13. Traceability and architecture change",
    ],
)
def test_v2_contains_required_memory_sections(directive_text: str, required_section: str) -> None:
    assert required_section in directive_text


def test_v2_maps_every_decision_record(directive_text: str) -> None:
    for number in range(1, 16):
        assert f"| ADR-{number:03d} |" in directive_text


def test_v2_preserves_memory_only_delivery_order(directive_text: str) -> None:
    delivery_table = [
        "| Foundation / MS-0 |",
        "| Stage 1 / MS-1 |",
        "| Stage 2 / MS-2 |",
        "| Stage 3 / MS-3 |",
        "| Stage 4 / MS-4 |",
    ]
    offsets = [directive_text.index(row) for row in delivery_table]
    assert offsets == sorted(offsets)
    assert "No agent planning, action execution, tools, goal completion" in directive_text


@pytest.mark.parametrize(
    "external_responsibility",
    [
        "goals",
        "planning",
        "actions",
        "tool use",
        "execution",
        "verification",
        "completion",
        "autonomy",
    ],
)
def test_v2_assigns_agent_responsibilities_to_external_consumers(
    directive_text: str, external_responsibility: str
) -> None:
    paragraph = (
        "External consumers own their goals, planning, actions, tool use, execution,\n"
        "verification, completion, and autonomy."
    )
    assert paragraph in directive_text
    assert external_responsibility in paragraph


def test_v2_keeps_tenant_root_conflict_explicitly_open(directive_text: str) -> None:
    assert (
        "Tenant-root persistence and all\ndependent implementation remain blocked" in directive_text
    )
    assert (
        "Synthetic or sentinel Areas and silent\nnullability exceptions are prohibited"
        in directive_text
    )


@pytest.mark.parametrize(
    "release_stop",
    [
        "Neural Brain owns or executes a consumer goal, plan, action, tool, completion",
        "Scope or principal can be taken from untrusted input.",
        "Protected memory state is writable outside its owning typed boundary.",
        "Inactive, quarantined, expired, deleted, or out-of-scope memory is retrievable.",
        "Cross-area memory use lacks an explicit audited transfer contract.",
        "Deletion omits an index, cache, embedding, claim, summary, or other derivative.",
        "Startup or restore reports readiness before reconciliation.",
        "Backup or restore has not been proven.",
        "The unresolved Tenant-root scope conflict affects the proposed implementation.",
    ],
)
def test_v2_contains_memory_release_stops(directive_text: str, release_stop: str) -> None:
    assert release_stop in directive_text


def test_v2_keeps_local_inference_fail_closed(directive_text: str) -> None:
    normalized = " ".join(directive_text.split())
    assert "Inference is an optional memory-processing dependency" in normalized
    assert "OpenAI APIs and SDKs" in normalized
    assert "automatic cloud fallback are prohibited" in normalized
    assert "Model output cannot write memory directly" in normalized
