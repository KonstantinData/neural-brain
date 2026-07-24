"""Unit evidence for the local Memory Core operator entrypoint."""

from pathlib import Path

import pytest

from tools.install_memory_core import _verify_applied_prefix
from tools.memory_demo import FixedLocalContextProvider, main, read_local_environment
from tools.validate_migrations import Migration


def _environment_text(secret: str = "do-not-print-this") -> str:
    return "\n".join(
        (
            "NEURAL_BRAIN_POSTGRES_ADMIN_USER=postgres",
            f"NEURAL_BRAIN_POSTGRES_ADMIN_PASSWORD={secret}",
            "NEURAL_BRAIN_DEV_DB=neural_brain_dev",
            "NEURAL_BRAIN_DEV_USER=neural_brain_dev",
            "NEURAL_BRAIN_DEV_PASSWORD=runtime-secret",
            "NEURAL_BRAIN_DEV_PORT=55432",
        )
    )


def test_local_context_is_fixed_and_session_scoped() -> None:
    """The demo exposes no request field that can replace authenticated scope."""

    context = FixedLocalContextProvider().current_context()

    assert context.actor_id == "principal-local-demo"
    assert context.tenant_id == "tenant-local-demo"
    assert context.area_id == "area-local-demo"
    assert context.project_id == "project-local-demo"
    assert context.session_id == "session-local-demo"


def test_environment_reader_rejects_duplicate_or_missing_values(tmp_path: Path) -> None:
    """Ambiguous local configuration fails before a connection is attempted."""

    duplicate = tmp_path / "duplicate.env"
    duplicate.write_text(_environment_text() + "\nNEURAL_BRAIN_DEV_PORT=65432\n", encoding="utf-8")
    missing = tmp_path / "missing.env"
    missing.write_text("NEURAL_BRAIN_DEV_PORT=55432\n", encoding="utf-8")

    with pytest.raises(ValueError, match="malformed"):
        read_local_environment(duplicate)
    with pytest.raises(ValueError, match="incomplete"):
        read_local_environment(missing)


def test_cli_prints_only_secret_free_result(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Successful output contains evidence but never renders local credentials."""

    secret = "admin-secret-that-must-not-appear"
    environment_file = tmp_path / "dev.env"
    environment_file.write_text(_environment_text(secret), encoding="utf-8")

    def fake_run_memory_demo(
        admin_dsn: str, runtime_dsn: str, runtime_role: str
    ) -> dict[str, object]:
        assert secret in admin_dsn
        assert "runtime-secret" in runtime_dsn
        assert runtime_role == "neural_brain_dev"
        return {"status": "passed", "audit_committed": True}

    monkeypatch.setattr("tools.memory_demo.run_memory_demo", fake_run_memory_demo)

    assert main(["--environment-file", str(environment_file)]) == 0
    captured = capsys.readouterr()
    assert '"status": "passed"' in captured.out
    assert secret not in captured.out
    assert "runtime-secret" not in captured.out
    assert captured.err == ""


def test_cli_redacts_failure_details(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """A database error cannot echo a credential-bearing connection string."""

    secret = "failure-secret-that-must-not-appear"
    environment_file = tmp_path / "dev.env"
    environment_file.write_text(_environment_text(secret), encoding="utf-8")

    def fail_with_secret(admin_dsn: str, runtime_dsn: str, runtime_role: str) -> dict[str, object]:
        raise RuntimeError(f"failed with {admin_dsn} {runtime_dsn} {runtime_role}")

    monkeypatch.setattr("tools.memory_demo.run_memory_demo", fail_with_secret)

    assert main(["--environment-file", str(environment_file)]) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == "memory demo failed: RuntimeError\n"
    assert secret not in captured.err
    assert "runtime-secret" not in captured.err


def test_migration_prefix_rejects_checksum_drift(tmp_path: Path) -> None:
    """An applied migration cannot be silently replaced by checkout contents."""

    migration = Migration(
        sequence=1,
        name="0001_example.sql",
        path=tmp_path / "0001_example.sql",
        sql="SELECT 1;\n",
        content_sha256="a" * 64,
    )

    with pytest.raises(RuntimeError, match="checksum drift"):
        _verify_applied_prefix(((1, migration.name, "b" * 64),), (migration,))
