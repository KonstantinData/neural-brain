"""Unit evidence for the local PostgreSQL verification entrypoint."""

from pathlib import Path

import pytest

from tools.postgres_smoke import main


def test_cli_emits_structured_secret_free_success(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Both fixed local scopes are reported without rendering connection material."""

    environment_file = tmp_path / "dev.env"
    environment_file.write_text("NEURAL_BRAIN_DEV_PASSWORD=secret\n", encoding="utf-8")

    def fake_verify(environment: dict[str, str], scope: str) -> str:
        assert environment["NEURAL_BRAIN_DEV_PASSWORD"] == "secret"
        return "18.4" if scope == "dev" else "18.4-test"

    monkeypatch.setattr("tools.postgres_smoke._verify_database", fake_verify)

    assert main(["--environment-file", str(environment_file)]) == 0
    captured = capsys.readouterr()
    assert captured.err == ""
    assert captured.out == (
        '{"status": "passed", "transaction_boundaries_verified": true, '
        '"verified_scopes": [{"postgresql_version": "18.4", "scope": "dev"}, '
        '{"postgresql_version": "18.4-test", "scope": "test"}]}\n'
    )
    assert "secret" not in captured.out


def test_cli_fails_with_secret_free_error_envelope(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Connection failures remain non-diagnostic and return a nonzero status."""

    secret = "connection-secret-that-must-not-appear"
    environment_file = tmp_path / "dev.env"
    environment_file.write_text(f"NEURAL_BRAIN_DEV_PASSWORD={secret}\n", encoding="utf-8")

    def fail_verify(environment: dict[str, str], scope: str) -> str:
        raise RuntimeError(f"failed with {environment} {scope}")

    monkeypatch.setattr("tools.postgres_smoke._verify_database", fail_verify)

    assert main(["--environment-file", str(environment_file)]) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == '{"code": "NB-MC-INTERNAL", "status": "failed"}\n'
    assert secret not in captured.err
