"""Executable negative evidence for the local test-data reset guards."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
DEV_TOOL = ROOT / "tools" / "dev.ps1"
POWERSHELL = shutil.which("pwsh") or shutil.which("powershell")

FAKE_DOCKER = r"""param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$DockerArguments
)

$line = $DockerArguments -join " "
[System.IO.File]::AppendAllText(
    $env:FAKE_DOCKER_LOG,
    $line + [System.Environment]::NewLine
)

if ($DockerArguments[0] -eq "info") {
    Write-Output "test-daemon"
    exit 0
}
if ($DockerArguments[0] -eq "compose") {
    exit 0
}
if ($DockerArguments[0] -eq "volume" -and $DockerArguments[1] -eq "ls") {
    if ($env:FAKE_DOCKER_MODE -eq "list-failure") {
        exit 2
    }
    Write-Output $env:FAKE_DOCKER_VOLUME
    exit 0
}
if ($DockerArguments[0] -eq "volume" -and $DockerArguments[1] -eq "inspect") {
    if ($env:FAKE_DOCKER_MODE -eq "inspect-failure") {
        exit 2
    }
    if ($env:FAKE_DOCKER_MODE -eq "valid") {
        Write-Output $env:FAKE_DOCKER_VALID_INSPECT
        exit 0
    }
    Write-Output '[{"Labels":{"com.docker.compose.project":"untrusted","com.docker.compose.volume":"postgres_test_data"}}]'
    exit 0
}
if ($DockerArguments[0] -eq "volume" -and $DockerArguments[1] -eq "rm") {
    exit 0
}
exit 3
"""


def _write_environment(path: Path, *, test_database: str) -> None:
    path.write_text(
        "\n".join(
            (
                "NEURAL_BRAIN_DEV_DB=neural_brain_dev",
                "NEURAL_BRAIN_DEV_USER=neural_brain_dev",
                "NEURAL_BRAIN_DEV_PASSWORD=test-only-dev-secret",
                "NEURAL_BRAIN_DEV_PORT=55432",
                "NEURAL_BRAIN_COMPOSE_PROJECT=neural-brain-test-abcdef123456",
                "NEURAL_BRAIN_POSTGRES_ADMIN_USER=postgres",
                "NEURAL_BRAIN_POSTGRES_ADMIN_PASSWORD=test-only-admin-secret",
                f"NEURAL_BRAIN_TEST_DB={test_database}",
                "NEURAL_BRAIN_TEST_USER=neural_brain_test",
                "NEURAL_BRAIN_TEST_PASSWORD=test-only-test-secret",
                "NEURAL_BRAIN_TEST_PORT=55433",
            )
        )
        + "\n",
        encoding="utf-8",
    )


def _run_reset(tmp_path: Path, *, mode: str, test_database: str) -> tuple[int, str]:
    if POWERSHELL is None:
        pytest.skip("PowerShell is required for the Windows development-tool contract.")

    fake_docker = tmp_path / "fake-docker.ps1"
    fake_docker.write_text(FAKE_DOCKER, encoding="utf-8")
    environment_file = tmp_path / "dev.env"
    _write_environment(environment_file, test_database=test_database)
    log_file = tmp_path / "docker.log"
    environment = os.environ.copy()
    environment["FAKE_DOCKER_VOLUME"] = "neural-brain-test-abcdef123456-postgres-test-data"
    environment["FAKE_DOCKER_VALID_INSPECT"] = (
        '[{"Labels":{"com.docker.compose.project":"neural-brain-test-abcdef123456",'
        '"com.docker.compose.volume":"postgres_test_data"}}]'
    )
    environment["FAKE_DOCKER_LOG"] = str(log_file)
    environment["FAKE_DOCKER_MODE"] = mode

    result = subprocess.run(
        (
            POWERSHELL,
            "-NoProfile",
            "-File",
            str(DEV_TOOL),
            "reset-test",
            "-DockerCommand",
            str(fake_docker),
            "-LocalEnvironmentFile",
            str(environment_file),
        ),
        cwd=ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    log = log_file.read_text(encoding="utf-8") if log_file.exists() else ""
    return result.returncode, log


def test_reset_rejects_non_disposable_database_before_volume_removal(
    tmp_path: Path,
) -> None:
    returncode, log = _run_reset(
        tmp_path,
        mode="wrong-labels",
        test_database="neural_brain_dev",
    )

    assert returncode != 0
    assert "stop postgres-test" not in log
    assert "rm --force postgres-test" not in log
    assert "volume rm" not in log


@pytest.mark.parametrize("mode", ("wrong-labels", "list-failure", "inspect-failure"))
def test_reset_does_not_mutate_docker_state_when_ownership_cannot_be_proven(
    tmp_path: Path,
    mode: str,
) -> None:
    returncode, log = _run_reset(
        tmp_path,
        mode=mode,
        test_database="neural_brain_test",
    )

    assert returncode != 0
    assert "stop postgres-test" not in log
    assert "rm --force postgres-test" not in log
    assert "volume rm" not in log


def test_reset_removes_test_volume_only_after_successful_preflight(tmp_path: Path) -> None:
    returncode, log = _run_reset(
        tmp_path,
        mode="valid",
        test_database="neural_brain_test",
    )

    assert returncode == 0
    assert (
        "volume ls --quiet --filter name=^neural-brain-test-abcdef123456-postgres-test-data$" in log
    )
    assert "volume inspect neural-brain-test-abcdef123456-postgres-test-data" in log
    assert log.index("volume inspect") < log.index("stop postgres-test")
    assert log.index("rm --force postgres-test") < log.index(
        "volume rm neural-brain-test-abcdef123456-postgres-test-data"
    )
    assert "up --detach --wait postgres-test" in log
