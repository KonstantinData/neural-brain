from pathlib import Path

import pytest

REPOSITORY_ROOT = Path(__file__).parents[2]
CURRENT_DIRECTIVE = REPOSITORY_ROOT / "docs" / "architecture" / "architecture-directive-v3.0.md"
V2_DIRECTIVE = REPOSITORY_ROOT / "docs" / "architecture" / "architecture-directive-v2.0.md"
V1_DIRECTIVE = REPOSITORY_ROOT / "docs" / "architecture" / "architecture-directive-v1.1.md"


@pytest.fixture(scope="module")
def directive_text() -> str:
    return CURRENT_DIRECTIVE.read_text(encoding="utf-8")


def test_v3_directive_declares_normative_memory_identity(directive_text: str) -> None:
    assert "# Neural Brain Architecture Directive v3.0" in directive_text
    assert "- Status: Normative memory-system baseline" in directive_text
    assert "- Governing decisions: ADR-015, ADR-016, and ADR-017" in directive_text
    assert "It is not an agent" in directive_text


def test_earlier_directives_are_preserved_as_superseded_history() -> None:
    v2 = V2_DIRECTIVE.read_text(encoding="utf-8")
    v1 = V1_DIRECTIVE.read_text(encoding="utf-8")
    assert "- Status: Superseded by Architecture Directive v3.0" in v2
    assert "- Status: Superseded by Architecture Directives v2.0 and v3.0" in v1
    assert "This directive is no longer implementation authority" in v1


@pytest.mark.parametrize(
    "required_section",
    [
        "## 2. System and consumer boundary",
        "## 3. Hierarchy catalog and operational scope",
        "## 4. Trust, validation, and consumer ports",
        "## 5. Memory lifecycle and protected state",
        "## 6. Memory forms and retrieval",
        "## 7. Governed Dreaming",
        "## 8. Security and governance",
        "## 9. PostgreSQL, audit, and crash consistency",
        "## 10. Privacy, retention, and deletion",
        "## 11. Local inference boundary",
        "## 12. Delivery stages",
        "## 13. Verification and release stops",
        "## 14. Traceability and architecture change",
    ],
)
def test_v3_contains_required_memory_sections(directive_text: str, required_section: str) -> None:
    assert required_section in directive_text


def test_v3_maps_every_decision_record(directive_text: str) -> None:
    for number in range(1, 18):
        assert f"| ADR-{number:03d} |" in directive_text


def test_v3_preserves_memory_only_delivery_order(directive_text: str) -> None:
    rows = [
        "| Foundation / MS-0 |",
        "| Stage 1 / MS-1 |",
        "| Stage 2 / MS-2 |",
        "| Stage 3 / MS-3 |",
        "| Stage 4 / MS-4 |",
    ]
    offsets = [directive_text.index(row) for row in rows]
    assert offsets == sorted(offsets)
    assert "No agent planning, action execution, tools, goal completion" in directive_text


def test_v3_resolves_catalog_scope_without_sentinel_area(directive_text: str) -> None:
    assert "| Tenant | `brain_id`, `tenant_id` |" in directive_text
    assert "| Session | `tenant_id`, `area_id`, `project_id`, `session_id` |" in directive_text
    assert "Sentinel Areas, nullable required\nscope, implicit root scope" in directive_text


def test_v3_defines_guarded_stage_1_dreaming(directive_text: str) -> None:
    normalized = " ".join(directive_text.split())
    assert "Dreaming is an Area-local offline memory-analysis process" in normalized
    assert "Stage 1 permits only a dry run" in normalized
    assert "MUST NOT create or activate a successor memory version" in normalized


def test_v3_keeps_local_inference_fail_closed(directive_text: str) -> None:
    normalized = " ".join(directive_text.split())
    assert "Inference is an optional memory-processing dependency" in normalized
    assert "OpenAI APIs and SDKs" in normalized
    assert "automatic cloud fallback are prohibited" in normalized
    assert "Model output cannot write memory directly" in normalized
