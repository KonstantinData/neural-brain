"""Candidate export evidence tests for the external hidden-evaluator handoff."""

from datetime import UTC, datetime
from pathlib import Path

import pytest

from neural_brain.cognition.hidden_contract import CandidateEvaluationBundle
from tools import export_nb1_evaluation_candidate as candidate_export
from tools.export_nb1_evaluation_candidate import build_candidate_bundle, candidate_code_digest

ROOT = Path(__file__).resolve().parents[2]


def test_candidate_export_is_deterministic_and_binds_the_complete_surface() -> None:
    frozen_at = datetime(2026, 7, 17, 10, 0, tzinfo=UTC)
    first = build_candidate_bundle(
        root=ROOT,
        source_commit="1" * 40,
        source_tree_digest="2" * 64,
        frozen_at=frozen_at,
    )
    second = build_candidate_bundle(
        root=ROOT,
        source_commit="1" * 40,
        source_tree_digest="2" * 64,
        frozen_at=frozen_at,
    )

    assert isinstance(first, CandidateEvaluationBundle)
    assert first == second
    assert first.source_commit == "1" * 40
    assert first.candidate_code_digest == candidate_code_digest(ROOT)
    assert first.training_code_digest == first.model_manifest.code_digest
    assert first.fixed_train_majority_label == "negative"
    assert first.model_manifest.training_artifact_digest == (
        first.parameters.training_provenance_ref
    )


def test_candidate_code_digest_changes_when_any_surface_digest_changes() -> None:
    original = candidate_code_digest(ROOT)
    assert len(original) == 64
    assert original != "0" * 64


@pytest.mark.parametrize(
    "changed_path",
    [
        ROOT / "src" / "neural_brain" / "memory" / "models.py",
        ROOT / "tools" / "export_nb1_evaluation_candidate.py",
    ],
)
def test_candidate_code_digest_binds_complete_package_and_exporter(
    monkeypatch: pytest.MonkeyPatch, changed_path: Path
) -> None:
    original_text_digest = candidate_export._text_digest
    original = candidate_code_digest(ROOT)

    def changed_text_digest(path: Path) -> str:
        if path == changed_path:
            return "f" * 64
        return original_text_digest(path)

    monkeypatch.setattr(candidate_export, "_text_digest", changed_text_digest)

    assert candidate_code_digest(ROOT) != original


def test_cli_refuses_the_historical_v3_candidate(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    def fake_git(_root: Path, *arguments: str) -> str:
        if arguments == ("status", "--porcelain"):
            return ""
        if arguments == ("rev-parse", "HEAD"):
            return "1" * 40
        return "historical-tree"

    monkeypatch.setattr(candidate_export, "_git", fake_git)
    output = tmp_path / "candidate.json"

    assert (
        candidate_export.main(
            [
                "--root",
                str(ROOT),
                "--output",
                str(output),
                "--frozen-at",
                "2026-07-17T10:00:00+02:00",
            ]
        )
        == 1
    )
    assert not output.exists()
    assert "candidate uses rejected EVAL-01 v3" in capsys.readouterr().err
