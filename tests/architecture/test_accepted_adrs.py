from pathlib import Path

import pytest

REPOSITORY_ROOT = Path(__file__).parents[2]
ADR_DIRECTORY = REPOSITORY_ROOT / "docs" / "adr"


def _accepted_adr_paths() -> list[Path]:
    return sorted(ADR_DIRECTORY.glob("ADR-[0-9][0-9][0-9]-*.md"))


def test_repository_contains_current_accepted_adr_sequence() -> None:
    paths = _accepted_adr_paths()
    identifiers = [path.name[:7] for path in paths]
    assert identifiers == [f"ADR-{number:03d}" for number in range(1, 15)]


def test_fnd_02_7_foundation_baseline_is_adr_001_through_adr_013() -> None:
    paths = _accepted_adr_paths()
    identifiers = [path.name[:7] for path in paths[:13]]
    assert identifiers == [f"ADR-{number:03d}" for number in range(1, 14)]
    assert paths[13].name.startswith("ADR-014-local-ollama-only-inference")


@pytest.mark.parametrize("adr_path", _accepted_adr_paths(), ids=lambda path: path.name[:7])
def test_accepted_adr_has_traceable_decision_record(adr_path: Path) -> None:
    text = adr_path.read_text(encoding="utf-8")
    assert text.startswith(f"# {adr_path.name[:7]}:")
    assert "- Status: Accepted" in text
    assert "- Date: 2026-07-15" in text
    assert "https://app.notion.com/p/" in text
    assert "## Context" in text
    assert "## Decision" in text
    assert "## Consequences" in text


def test_adr_index_records_complete_continuous_sequence() -> None:
    index = (ADR_DIRECTORY / "README.md").read_text(encoding="utf-8")
    for number in range(1, 15):
        assert f"[ADR-{number:03d}]" in index
    assert "continuous from ADR-001 through ADR-014" in index
