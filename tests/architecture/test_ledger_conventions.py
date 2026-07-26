from pathlib import Path

ROOT = Path(__file__).parents[2]
CONVENTIONS = (ROOT / "docs" / "architecture" / "ledger-conventions-v1.md").read_text(
    encoding="utf-8"
)
MIGRATIONS = "\n".join(
    path.read_text(encoding="utf-8") for path in sorted((ROOT / "migrations").glob("*.sql"))
)
MIGRATION_WORKFLOW = (ROOT / ".github" / "workflows" / "migrations.yml").read_text(encoding="utf-8")


def test_ledger_conventions_fix_existing_representation_and_postgres_baseline() -> None:
    assert "PostgreSQL **18**" in CONVENTIONS
    assert "postgres:18.4-bookworm" in CONVENTIONS
    assert "postgres:18.4-bookworm" in MIGRATION_WORKFLOW
    assert "`text` identifiers, not the PostgreSQL `uuid` type" in CONVENTIONS
    assert "uuid" not in MIGRATIONS.lower()
    assert "text NOT NULL" in MIGRATIONS
    assert "length(tenant_id) <= 128" in MIGRATIONS


def test_ledger_conventions_match_current_scope_time_and_payload_schema() -> None:
    assert "immutable `tenant_id` and `area_id`" in CONVENTIONS
    assert "`session_user`" in CONVENTIONS
    assert "`timestamptz`" in CONVENTIONS
    assert "`transaction_timestamp()`" in CONVENTIONS
    assert "timestamp without time zone" in CONVENTIONS
    assert "timestamptz NOT NULL DEFAULT transaction_timestamp()" in MIGRATIONS
    assert "jsonb NOT NULL" in MIGRATIONS
    assert "jsonb_typeof" in MIGRATIONS
    assert "numeric(20,6) NOT NULL CHECK (amount >= 0)" in CONVENTIONS
    assert "real" not in MIGRATIONS.lower()
    assert "double precision" not in MIGRATIONS.lower()


def test_ledger_conventions_keep_future_budget_and_goal_action_state_unimplemented() -> None:
    assert "does not imply that one exists" in CONVENTIONS
    assert "neither authorizes a protected state writer nor introduces Goal, Action" in CONVENTIONS
    assert "CREATE TABLE goal" not in MIGRATIONS.lower()
    assert "CREATE TABLE action" not in MIGRATIONS.lower()
