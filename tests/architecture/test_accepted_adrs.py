from pathlib import Path

import pytest

REPOSITORY_ROOT = Path(__file__).parents[2]
ADR_DIRECTORY = REPOSITORY_ROOT / "docs" / "adr"


def _adr_paths() -> list[Path]:
    return sorted(ADR_DIRECTORY.glob("ADR-[0-9][0-9][0-9]-*.md"))


def test_repository_contains_current_accepted_adr_sequence() -> None:
    paths = _adr_paths()
    identifiers = [path.name[:7] for path in paths]
    assert identifiers == [f"ADR-{number:03d}" for number in range(1, 19)]


def test_fnd_02_7_foundation_baseline_is_adr_001_through_adr_013() -> None:
    paths = _adr_paths()
    identifiers = [path.name[:7] for path in paths[:13]]
    assert identifiers == [f"ADR-{number:03d}" for number in range(1, 14)]
    assert paths[13].name.startswith("ADR-014-local-ollama-only-inference")


@pytest.mark.parametrize("adr_path", _adr_paths(), ids=lambda path: path.name[:7])
def test_adr_has_traceable_decision_record(adr_path: Path) -> None:
    text = adr_path.read_text(encoding="utf-8")
    assert text.startswith(f"# {adr_path.name[:7]}:")
    assert (
        "- Status: Accepted" in text
        or "- Status: Superseded by ADR-015" in text
        or "- Status: Superseded as product boundary by ADR-018" in text
        or "- Status: Superseded as product delivery model by ADR-018" in text
    )
    expected_date = "2026-07-16" if adr_path.name.startswith("ADR-018") else "2026-07-15"
    assert f"- Date: {expected_date}" in text
    assert "https://app.notion.com/p/" in text
    assert "## Context" in text
    assert "## Decision" in text
    assert "## Consequences" in text


def test_adr_index_records_complete_continuous_sequence() -> None:
    index = (ADR_DIRECTORY / "README.md").read_text(encoding="utf-8")
    for number in range(1, 19):
        assert f"[ADR-{number:03d}]" in index
    assert "continuous decision sequence from ADR-001 through\nADR-018" in index
    assert "ADR-018 governs the complete cognitive-system boundary" in index


def test_adr_018_is_current_complete_system_boundary_decision() -> None:
    text = (ADR_DIRECTORY / "ADR-018-complete-cognitive-system.md").read_text(encoding="utf-8")
    normalized = " ".join(text.split())
    assert "- Status: Accepted" in text
    assert "integrated, neural, plastic cognitive system" in normalized
    assert "The existing governed memory system becomes the `Memory Core` subsystem" in normalized
    assert "Trainable neural mechanisms must make a causal contribution" in normalized
    assert "Learning produces immutable candidates" in normalized
    assert "target architecture from implemented maturity" in normalized


def test_adr_015_is_retained_only_as_memory_core_boundary() -> None:
    text = (ADR_DIRECTORY / "ADR-015-memory-system-not-agent-runtime.md").read_text(
        encoding="utf-8"
    )
    assert "- Status: Superseded as product boundary by ADR-018" in text
    assert "authoritative only for the governed Memory Core subsystem" in text
    assert "no longer applies\nto Neural Brain as a whole" in text


def test_adr_016_and_017_remain_scope_and_dreaming_decisions() -> None:
    scope = (ADR_DIRECTORY / "ADR-016-hierarchy-catalog-and-operational-memory-scope.md").read_text(
        encoding="utf-8"
    )
    dreaming = (ADR_DIRECTORY / "ADR-017-governed-area-local-dreaming.md").read_text(
        encoding="utf-8"
    )
    assert "exactly one Brain catalog row" in scope
    assert "Tenant carries `brain_id` and `tenant_id`; it does not carry `area_id`" in scope
    assert "Session carries `tenant_id`, `area_id`, `project_id`, and `session_id`" in scope
    assert "Stage 1 permits only a Dreaming dry run" in dreaming
    assert "map to the namespaced MS-1 through MS-4 subsystem stages" in dreaming
    assert "cannot change an active-version pointer" in dreaming


@pytest.mark.parametrize("number", [4, 6, 7, 8, 9, 11])
def test_agent_runtime_adrs_remain_historical_pending_revalidation(number: int) -> None:
    path = next(ADR_DIRECTORY.glob(f"ADR-{number:03d}-*.md"))
    text = path.read_text(encoding="utf-8")
    assert "- Status: Superseded by ADR-015" in text
    assert "## Supersession" in text


def test_adr_010_is_retained_as_memory_core_stage_order_only() -> None:
    text = (ADR_DIRECTORY / "ADR-010-staged-memory-capabilities.md").read_text(encoding="utf-8")
    assert "- Status: Superseded as product delivery model by ADR-018" in text
    assert "memory-specific ordering below is now explicitly namespaced as MS-0 through" in text
    assert "MS-4, remains binding inside the Memory Core" in text
    assert "An MS stage is not an NB stage" in text


@pytest.mark.parametrize(
    ("number", "amendments"),
    [
        (1, ("ADR-018", "ADR-015")),
        (2, ("ADR-015",)),
        (3, ("ADR-018", "ADR-015")),
        (5, ("ADR-018", "ADR-015")),
        (12, ("ADR-015",)),
        (13, ("ADR-018", "ADR-015")),
        (14, ("ADR-018", "ADR-015 and ADR-017")),
    ],
)
def test_retained_adrs_preserve_historical_and_current_amendments(
    number: int, amendments: tuple[str, ...]
) -> None:
    path = next(ADR_DIRECTORY.glob(f"ADR-{number:03d}-*.md"))
    text = path.read_text(encoding="utf-8")
    assert "- Status: Accepted" in text
    for amendment in amendments:
        assert f"## Amendment by {amendment}" in text
