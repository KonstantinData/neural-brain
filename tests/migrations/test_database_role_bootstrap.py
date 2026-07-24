"""Contract tests for the cluster-global database role bootstrap."""

from pathlib import Path

from psycopg.conninfo import conninfo_to_dict

from tools.bootstrap_database_roles import ROLE_NAMES, coordination_dsn


def test_role_set_is_fixed_and_separates_runtime_responsibilities() -> None:
    """The migration plan depends on explicit non-login ownership and runtime roles."""

    assert ROLE_NAMES == (
        "neural_brain_owner",
        "neural_brain_gate",
        "neural_brain_reader",
        "neural_brain_dreamer",
    )


def test_role_bootstrap_is_invoked_before_repository_migrations() -> None:
    """CI must prepare cluster roles before per-database migrations reference them."""

    workflow = (Path(__file__).parents[2] / ".github" / "workflows" / "migrations.yml").read_text(
        encoding="utf-8"
    )

    assert workflow.index("Bootstrap fixed database roles") < workflow.index(
        "Validate repository migration plan"
    )


def test_role_bootstrap_uses_one_lock_domain_across_databases() -> None:
    """Cluster-global roles must not race under per-database advisory locks."""

    first = conninfo_to_dict(coordination_dsn("dbname=first user=postgres"))
    second = conninfo_to_dict(coordination_dsn("dbname=second user=postgres"))

    assert first["dbname"] == "postgres"
    assert second["dbname"] == "postgres"
