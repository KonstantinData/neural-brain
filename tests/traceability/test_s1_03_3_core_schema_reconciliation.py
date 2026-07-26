"""Regression checks for the bounded S1-03.3 schema reconciliation record."""

from pathlib import Path

ROOT = Path(__file__).parents[2]
EVIDENCE = (ROOT / "docs" / "traceability" / "S1-03.3-core-schema-reconciliation.md").read_text(
    encoding="utf-8"
)
MIGRATIONS = "\n".join(
    path.read_text(encoding="utf-8") for path in sorted((ROOT / "migrations").glob("*.sql"))
)


def test_s1_03_3_maps_all_accepted_ms1_schema_categories() -> None:
    """The task record cannot lose a required category or its bounded evidence."""

    for category in (
        "Authenticated catalog scope",
        "Sources and observations",
        "Bounded working memory and versions",
        "Checkpoints and recovery readback",
        "Memory transitions and audit",
        "Candidate lifecycle boundary",
        "Recovery and reconciliation boundary",
        "No early Goal or Action runtime",
    ):
        assert category in EVIDENCE

    for reference in (
        "migrations/0001_scope_catalog.sql",
        "migrations/0002_stage1_memory_kernel.sql",
        "migrations/0003_dreaming_dry_run.sql",
        "migrations/0004_nb1_cognitive_checkpoints.sql",
        "tests/database/test_stage1_memory_kernel.py::test_audit_failure_rolls_back_the_complete_transition",
        "tests/database/test_postgres_cognitive_repository.py::test_corrupt_checkpoint_is_denied_during_recovery",
    ):
        assert reference in EVIDENCE


def test_s1_03_3_does_not_introduce_goal_or_action_runtime_schema() -> None:
    """MS-1 stays a Memory Core foundation despite the complete-system target."""

    assert "create table goal_" not in MIGRATIONS.lower()
    assert "create table action_" not in MIGRATIONS.lower()
    assert "early protected Goal or Action runtime" in EVIDENCE
    assert "NB-5" in EVIDENCE


def test_s1_03_3_keeps_later_lifecycle_capabilities_out_of_the_claim() -> None:
    """A schema mapping does not silently become a release claim for later stages."""

    assert "MS-2/MS-3" in EVIDENCE
    assert "MIGRATION_ADMIN_DSN" in EVIDENCE
    assert "cannot be substituted" in EVIDENCE
