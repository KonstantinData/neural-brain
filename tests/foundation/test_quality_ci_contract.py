"""Contract tests for the shared local and CI quality gate."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from unittest.mock import Mock, call

import pytest

from tools import quality

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = (ROOT / ".github" / "workflows" / "quality.yml").read_text(encoding="utf-8")
TOOLS_README = (ROOT / "tools" / "README.md").read_text(encoding="utf-8")
LOCKED_COMMAND = "uv run --locked --all-groups python tools/quality.py --locked"


def test_quality_commands_are_complete_and_use_locked_interpreter() -> None:
    expected_commands = (
        (sys.executable, "-m", "ruff", "format", "--check", "."),
        (sys.executable, "-m", "ruff", "check", "."),
        (sys.executable, "-m", "mypy"),
        (sys.executable, "tools/type_exception_audit.py"),
        (sys.executable, "-m", "pytest"),
    )
    assert expected_commands == quality.COMMANDS
    assert " ".join(quality.LOCKED_QUALITY_COMMAND) == LOCKED_COMMAND


def test_quality_runner_uses_repository_root_check_mode_and_declared_order(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    run = Mock(return_value=subprocess.CompletedProcess(args=(), returncode=0))
    monkeypatch.setattr(subprocess, "run", run)

    assert quality.main(["--locked"]) == 0
    assert run.call_args_list == [
        call(command, cwd=quality.ROOT, check=True) for command in quality.COMMANDS
    ]


def test_quality_runner_rejects_unlocked_or_extra_arguments(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    run = Mock()
    monkeypatch.setattr(subprocess, "run", run)

    assert quality.main([]) == 2
    assert quality.main(["--locked", "--skip-tests"]) == 2
    run.assert_not_called()


def test_quality_runner_fails_fast_on_first_failed_command(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    failure = subprocess.CalledProcessError(returncode=1, cmd=quality.COMMANDS[0])
    run = Mock(side_effect=failure)
    monkeypatch.setattr(subprocess, "run", run)

    with pytest.raises(subprocess.CalledProcessError):
        quality.main(["--locked"])
    run.assert_called_once_with(quality.COMMANDS[0], cwd=quality.ROOT, check=True)


def test_ci_uses_fixed_uv_and_the_documented_locked_commands() -> None:
    assert "name: Quality" in WORKFLOW
    assert "  quality:\n    name: quality" in WORKFLOW
    assert "permissions:\n  contents: read" in WORKFLOW
    assert "timeout-minutes: 20" in WORKFLOW
    assert "uses: actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10 # v6" in WORKFLOW
    assert "persist-credentials: false" in WORKFLOW
    assert "uses: astral-sh/setup-uv@37802adc94f370d6bfd71619e3f0bf239e1f3b78 # v7.6.0" in WORKFLOW
    assert 'version: "0.11.28"' in WORKFLOW
    assert "run: uv python install" in WORKFLOW
    assert "run: uv sync --locked --all-groups" in WORKFLOW
    assert f"run: {LOCKED_COMMAND}" in WORKFLOW
    assert "run: ruff" not in WORKFLOW
    assert "run: mypy" not in WORKFLOW
    assert "run: pytest" not in WORKFLOW


def test_local_documentation_matches_ci_commands_exactly() -> None:
    for command in (
        "uv python install",
        "uv sync --locked --all-groups",
        LOCKED_COMMAND,
    ):
        assert command in WORKFLOW
        assert command in TOOLS_README
