"""Static safety checks for the isolated Foundation PostgreSQL environment."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COMPOSE = (ROOT / "compose.yaml").read_text(encoding="utf-8")
DEV_TOOL = (ROOT / "tools" / "dev.ps1").read_text(encoding="utf-8")


def test_postgresql_image_is_exact_and_foundation_scopes_are_isolated() -> None:
    expected_image = (
        "docker.io/library/postgres:18.4-bookworm@sha256:"
        "1961f96e6029a02c3812d7cb329a3b03a3ac2bb067058dec17b0f5596aca9296"
    )
    assert f"image: {expected_image}" in COMPOSE
    assert "postgres-dev:" in COMPOSE
    assert "postgres-test:" in COMPOSE
    assert "postgres_dev_data:/var/lib/postgresql" in COMPOSE
    assert "postgres_test_data:/var/lib/postgresql" in COMPOSE
    assert "name: neural-brain-postgres-dev-data" in COMPOSE
    assert "name: neural-brain-postgres-test-data" in COMPOSE


def test_postgresql_ports_are_loopback_only_and_passwords_are_not_committed() -> None:
    assert "127.0.0.1:${NEURAL_BRAIN_DEV_PORT" in COMPOSE
    assert "127.0.0.1:${NEURAL_BRAIN_TEST_PORT" in COMPOSE
    assert "POSTGRES_HOST_AUTH_METHOD: trust" not in COMPOSE
    assert "NEURAL_BRAIN_DEV_PASSWORD=" not in COMPOSE
    assert "NEURAL_BRAIN_TEST_PASSWORD=" not in COMPOSE
    assert ".local/" in (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert "icacls $EnvironmentFile /inheritance:r /grant:r $grant" in DEV_TOOL
    assert "chmod 600 $EnvironmentFile" in DEV_TOOL


def test_reset_command_is_fail_closed_and_targets_only_test_storage() -> None:
    reset_block = DEV_TOOL.split('"reset-test" {', maxsplit=1)[1]
    assert 'EndsWith("_test"' in reset_block
    assert '$TestVolume = "neural-brain-postgres-test-data"' in DEV_TOOL
    assert '"com.docker.compose.project" -ne "neural-brain"' in reset_block
    assert '"com.docker.compose.volume" -ne "postgres_test_data"' in reset_block
    assert "if ($LASTEXITCODE -ne 0)" in reset_block
    assert "$DockerCommand volume rm $TestVolume" in reset_block
    assert "neural-brain-postgres-dev-data" not in reset_block
