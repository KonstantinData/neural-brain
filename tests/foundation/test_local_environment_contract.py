"""Static safety checks for the isolated Foundation PostgreSQL environment."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COMPOSE = (ROOT / "compose.yaml").read_text(encoding="utf-8")
DEV_TOOL = (ROOT / "tools" / "dev.ps1").read_text(encoding="utf-8")
POSTGRES_INIT = (ROOT / "docker" / "postgres" / "init" / "001-create-scope-role.sh").read_text(
    encoding="utf-8"
)


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
    assert "name: ${NEURAL_BRAIN_COMPOSE_PROJECT" in COMPOSE
    assert (
        "${NEURAL_BRAIN_COMPOSE_PROJECT:?local environment not initialized}-postgres-dev-data"
        in COMPOSE
    )
    assert (
        "${NEURAL_BRAIN_COMPOSE_PROJECT:?local environment not initialized}-postgres-test-data"
        in COMPOSE
    )
    assert "./docker/postgres/init:/docker-entrypoint-initdb.d:ro" in COMPOSE


def test_postgresql_ports_are_loopback_only_and_passwords_are_not_committed() -> None:
    assert "127.0.0.1:${NEURAL_BRAIN_DEV_PORT" in COMPOSE
    assert "127.0.0.1:${NEURAL_BRAIN_TEST_PORT" in COMPOSE
    assert "POSTGRES_HOST_AUTH_METHOD: trust" not in COMPOSE
    assert "NEURAL_BRAIN_DEV_PASSWORD=" not in COMPOSE
    assert "NEURAL_BRAIN_TEST_PASSWORD=" not in COMPOSE
    assert "NEURAL_BRAIN_POSTGRES_ADMIN_PASSWORD=" not in COMPOSE
    assert "POSTGRES_USER: ${NEURAL_BRAIN_POSTGRES_ADMIN_USER" in COMPOSE
    assert "NEURAL_BRAIN_SCOPE_USER: ${NEURAL_BRAIN_DEV_USER" in COMPOSE
    assert "NEURAL_BRAIN_SCOPE_USER: ${NEURAL_BRAIN_TEST_USER" in COMPOSE
    assert ".local/" in (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert "icacls $EnvironmentFile /inheritance:r /grant:r $grant" in DEV_TOOL
    assert "chmod 600 $EnvironmentFile" in DEV_TOOL


def test_reset_command_is_fail_closed_and_targets_only_test_storage() -> None:
    reset_block = DEV_TOOL.split('"reset-test" {', maxsplit=1)[1]
    assert 'EndsWith("_test"' in reset_block
    assert 'return "$composeProject-postgres-test-data"' in DEV_TOOL
    assert '"com.docker.compose.project" -ne $composeProject' in reset_block
    assert '"com.docker.compose.volume" -ne "postgres_test_data"' in reset_block
    assert "if ($LASTEXITCODE -ne 0)" in reset_block
    assert "$DockerCommand volume rm $testVolume" in reset_block
    assert "postgres-dev-data" not in reset_block
    assert reset_block.index("volume inspect") < reset_block.index('"stop", "postgres-test"')


def test_verify_passes_the_selected_environment_file_to_smoke_check() -> None:
    verify_block = DEV_TOOL.split('"verify" {', maxsplit=1)[1].split('"reset-test" {', maxsplit=1)[
        0
    ]
    assert "--environment-file $EnvironmentFile" in verify_block
    assert 'run --locked python (Join-Path $Root "tools/postgres_smoke.py")' in verify_block


def test_postgresql_scope_roles_are_not_superusers() -> None:
    assert 'CREATE ROLE :"scope_user"' in POSTGRES_INIT
    assert "NOSUPERUSER" in POSTGRES_INIT
    assert "NOCREATEDB" in POSTGRES_INIT
    assert "NOCREATEROLE" in POSTGRES_INIT
    assert "NOREPLICATION" in POSTGRES_INIT
    assert 'CREATE DATABASE :"scope_db" OWNER :"scope_user"' in POSTGRES_INIT
