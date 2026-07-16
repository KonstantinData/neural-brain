from pathlib import Path

import pytest

REPOSITORY_ROOT = Path(__file__).parents[2]
ADR_DIRECTORY = REPOSITORY_ROOT / "docs" / "adr"


def _adr_paths() -> list[Path]:
    return sorted(ADR_DIRECTORY.glob("ADR-[0-9][0-9][0-9]-*.md"))


def test_repository_contains_current_accepted_adr_sequence() -> None:
    paths = _adr_paths()
    identifiers = [path.name[:7] for path in paths]
    assert identifiers == [f"ADR-{number:03d}" for number in range(1, 18)]


def test_fnd_02_7_foundation_baseline_is_adr_001_through_adr_013() -> None:
    paths = _adr_paths()
    identifiers = [path.name[:7] for path in paths[:13]]
    assert identifiers == [f"ADR-{number:03d}" for number in range(1, 14)]
    assert paths[13].name.startswith("ADR-014-local-ollama-only-inference")


@pytest.mark.parametrize("adr_path", _adr_paths(), ids=lambda path: path.name[:7])
def test_adr_has_traceable_decision_record(adr_path: Path) -> None:
    text = adr_path.read_text(encoding="utf-8")
    assert text.startswith(f"# {adr_path.name[:7]}:")
    assert "- Status: Accepted" in text or "- Status: Superseded by ADR-015" in text
    assert "- Date: 2026-07-15" in text
    assert "https://app.notion.com/p/" in text
    assert "## Context" in text
    assert "## Decision" in text
    assert "## Consequences" in text


def test_adr_index_records_complete_continuous_sequence() -> None:
    index = (ADR_DIRECTORY / "README.md").read_text(encoding="utf-8")
    for number in range(1, 18):
        assert f"[ADR-{number:03d}]" in index
    assert "continuous decision sequence from ADR-001 through\nADR-017" in index


def test_adr_015_is_current_governing_boundary_decision() -> None:
    text = (ADR_DIRECTORY / "ADR-015-memory-system-not-agent-runtime.md").read_text(
        encoding="utf-8"
    )
    assert "- Status: Accepted" in text
    assert "Neural Brain is a product- and domain-neutral memory system" in text
    assert "Goals, plans, action intents, tools, execution" in text
    assert "resolves the Tenant-root conflict" in text


def test_adr_016_and_017_are_current_scope_and_dreaming_decisions() -> None:
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
    assert "cannot change an active-version pointer" in dreaming


@pytest.mark.parametrize("number", [4, 6, 7, 8, 9, 11])
def test_agent_runtime_adrs_are_superseded(number: int) -> None:
    path = next(ADR_DIRECTORY.glob(f"ADR-{number:03d}-*.md"))
    text = path.read_text(encoding="utf-8")
    assert "- Status: Superseded by ADR-015" in text
    assert "## Supersession" in text


@pytest.mark.parametrize("number", [1, 2, 3, 5, 10, 12, 13, 14])
def test_retained_adrs_record_memory_system_amendment(number: int) -> None:
    path = next(ADR_DIRECTORY.glob(f"ADR-{number:03d}-*.md"))
    text = path.read_text(encoding="utf-8")
    assert "- Status: Accepted" in text
    assert "## Amendment by ADR-015" in text
