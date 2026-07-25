"""Executable Windows PowerShell evidence for clean local environment creation."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEV_TOOL = ROOT / "tools" / "dev.ps1"
WINDOWS_POWERSHELL = shutil.which("powershell") if os.name == "nt" else None

FAKE_DOCKER = r"""param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$DockerArguments
)

if ($DockerArguments[0] -eq "info") {
    Write-Output "test-daemon"
    exit 0
}
if ($DockerArguments[0] -eq "compose") {
    exit 0
}
exit 3
"""


def test_clean_environment_generation_runs_under_windows_powershell_51(tmp_path: Path) -> None:
    """The documented entrypoint can create secrets on stock Windows PowerShell."""

    if WINDOWS_POWERSHELL is None:
        source = DEV_TOOL.read_text(encoding="utf-8")
        assert "RandomNumberGenerator]::Fill" not in source
        assert "[Convert]::ToHexString" not in source
        return
    fake_docker = tmp_path / "fake-docker.ps1"
    fake_docker.write_text(FAKE_DOCKER, encoding="utf-8")
    environment_file = tmp_path / "dev.env"

    result = subprocess.run(
        (
            WINDOWS_POWERSHELL,
            "-NoProfile",
            "-File",
            str(DEV_TOOL),
            "up",
            "-DockerCommand",
            str(fake_docker),
            "-LocalEnvironmentFile",
            str(environment_file),
        ),
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    values = dict(
        line.split("=", maxsplit=1)
        for line in environment_file.read_text(encoding="utf-8").splitlines()
    )
    for name in (
        "NEURAL_BRAIN_DEV_PASSWORD",
        "NEURAL_BRAIN_TEST_PASSWORD",
        "NEURAL_BRAIN_POSTGRES_ADMIN_PASSWORD",
    ):
        assert re.fullmatch(r"[0-9a-f]{64}", values[name]) is not None
        assert values[name] not in result.stdout
        assert values[name] not in result.stderr


def test_backup_restore_entrypoint_is_local_and_fail_closed() -> None:
    """The drill writes only local evidence and deletes only generated databases."""

    source = DEV_TOOL.read_text(encoding="utf-8")
    compose = (ROOT / "compose.yaml").read_text(encoding="utf-8")

    assert '"backup-restore"' in source
    assert 'Join-Path $LocalDirectory "backups"' in source
    assert "./.local/backups:/backups" in compose
    assert "--format=custom" in source
    assert "--no-owner" in source
    assert "--no-privileges" in source
    assert "archive_sha256" in source
    assert "neural_brain_restore_drill_" in source
    assert "^neural_brain_restore_drill_[0-9a-f]{16}$" in source
    assert "DROP DATABASE $DatabaseName WITH (FORCE)" in source
    assert "neural_brain_install.schema_migrations" in source
    assert "NB-MC-BACKUP-RESTORE-FAILED" in source
    assert "VerifyMigrationRollback" in source
    assert "migration_rollback_probe_" in source
    assert "Remove-RestoreDrillDatabase -DatabaseName $restoreDatabase" in source
    assert "rollback_verified" in source
