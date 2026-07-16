"""Deterministic and fail-closed tests for the PostgreSQL migration validator."""

from __future__ import annotations

from pathlib import Path

import pytest

from tools.validate_migrations import (
    DATABASE_PREFIX,
    discover_migrations,
    migration_plan_digest,
    validate_disposable_database_name,
)

FIXTURES = Path(__file__).parent / "fixtures" / "forward"
WORKFLOW = (Path(__file__).parents[2] / ".github" / "workflows" / "migrations.yml").read_text(
    encoding="utf-8"
)
MIGRATIONS_README = (Path(__file__).parents[2] / "migrations" / "README.md").read_text(
    encoding="utf-8"
)


def test_fixture_plan_is_contiguous_and_normalized() -> None:
    migrations = discover_migrations(FIXTURES)

    assert [item.sequence for item in migrations] == [1, 2]
    assert [item.name for item in migrations] == [
        "0001_create_fixture.sql",
        "0002_add_fixture_version.sql",
    ]
    assert all("\r" not in item.sql for item in migrations)
    assert all(len(item.content_sha256) == 64 for item in migrations)


def test_plan_digest_is_deterministic() -> None:
    first = discover_migrations(FIXTURES)
    second = discover_migrations(FIXTURES)

    assert migration_plan_digest(first) == migration_plan_digest(second)
    assert migration_plan_digest(first) == (
        "5aed8c6c573cd13ae81b7cde1c600dbfea3440b6d067b98db0792a2ce0894046"
    )


def test_empty_plan_requires_explicit_opt_in(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="No migration files found"):
        discover_migrations(tmp_path)

    assert discover_migrations(tmp_path, allow_empty=True) == ()


@pytest.mark.parametrize(
    "filename",
    ("0002_gap.sql", "1_short.sql", "0001_UPPER.sql", "0001-invalid.sql"),
)
def test_invalid_or_noncontiguous_filename_fails_closed(tmp_path: Path, filename: str) -> None:
    (tmp_path / filename).write_text("SELECT 1;\n", encoding="utf-8")

    with pytest.raises(ValueError):
        discover_migrations(tmp_path)


@pytest.mark.parametrize("statement", ("BEGIN;", "COMMIT;", "ROLLBACK;", "SAVEPOINT x;"))
def test_migration_cannot_control_its_transaction(tmp_path: Path, statement: str) -> None:
    (tmp_path / "0001_bad_transaction.sql").write_text(statement + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match="transaction control"):
        discover_migrations(tmp_path)


def test_plpgsql_function_body_may_contain_begin_and_rollback_words(tmp_path: Path) -> None:
    """Transaction keywords inside a dollar-quoted routine body are not top-level control."""

    (tmp_path / "0001_function.sql").write_text(
        """CREATE FUNCTION example() RETURNS void LANGUAGE plpgsql AS $$
BEGIN
    RAISE NOTICE 'ROLLBACK is descriptive text';
END;
$$;
""",
        encoding="utf-8",
    )

    migrations = discover_migrations(tmp_path)

    assert len(migrations) == 1


def test_disposable_database_guard_accepts_only_exact_generated_namespace() -> None:
    validate_disposable_database_name(f"{DATABASE_PREFIX}0123456789abcdef")

    for unsafe_name in (
        "postgres",
        "neural_brain_dev",
        "neural_brain_test",
        DATABASE_PREFIX,
        f"{DATABASE_PREFIX}0123456789abcdeg",
        f"other_{DATABASE_PREFIX}0123456789abcdef",
    ):
        with pytest.raises(ValueError, match="Refusing database cleanup"):
            validate_disposable_database_name(unsafe_name)


def test_ci_pins_postgresql_18_and_proves_both_migration_paths() -> None:
    expected_image = (
        "docker.io/library/postgres:18.4-bookworm@sha256:"
        "1961f96e6029a02c3812d7cb329a3b03a3ac2bb067058dec17b0f5596aca9296"
    )

    assert f"image: {expected_image}" in WORKFLOW
    assert "uses: actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10 # v6" in WORKFLOW
    assert "persist-credentials: false" in WORKFLOW
    assert "uses: astral-sh/setup-uv@37802adc94f370d6bfd71619e3f0bf239e1f3b78 # v7.6.0" in WORKFLOW
    assert "version: 0.11.28" in WORKFLOW
    assert "uv sync --locked --all-groups" in WORKFLOW
    assert WORKFLOW.count("uv run --locked --all-groups") == 5
    assert "tools/bootstrap_database_roles.py" in WORKFLOW
    assert "--migrations-dir migrations" in WORKFLOW
    assert "--migrations-dir tests/migrations/fixtures/forward" in WORKFLOW
    assert "--allow-empty" not in WORKFLOW


def test_migration_runbook_describes_the_nonempty_ms1_plan() -> None:
    normalized = " ".join(MIGRATIONS_README.split())
    assert "migrations `0001` through `0003`" in normalized
    assert "Empty migration plans are no longer accepted" in normalized
    assert "--allow-empty" not in normalized
    assert "pytest tests/database" in WORKFLOW
