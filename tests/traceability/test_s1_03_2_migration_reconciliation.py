"""Regression checks for the bounded S1-03.2 migration reconciliation record."""

from __future__ import annotations

from pathlib import Path

EVIDENCE = (
    Path(__file__).parents[2] / "docs" / "traceability" / "S1-03.2-migration-reconciliation.md"
).read_text(encoding="utf-8")


def test_s1_03_2_maps_each_acceptance_criterion_to_live_or_static_evidence() -> None:
    """The reconciliation cannot silently lose its clean-install or privilege proof."""

    for reference in (
        "tools/validate_migrations.py",
        ".github/workflows/migrations.yml",
        "tests/migrations/test_migration_validation.py::test_ci_pins_postgresql_18_and_proves_both_migration_paths",
        "tests/database/test_memory_demo.py::test_clean_concurrent_install_round_trip_and_fail_closed_guards",
        "tests/database/test_stage1_memory_kernel.py::test_runtime_role_cannot_mutate_protected_tables_directly",
        "tests/database/test_stage1_memory_kernel.py::test_gate_commits_observation_working_context_checkpoint_and_audit_atomically",
    ):
        assert reference in EVIDENCE


def test_s1_03_2_keeps_live_database_limit_and_stage_boundary_explicit() -> None:
    """Skipped local PostgreSQL tests and target-stage capabilities stay non-evidence."""

    assert "MIGRATION_ADMIN_DSN" in EVIDENCE
    assert "skips live PostgreSQL proof" in EVIDENCE
    assert "does not enable" in EVIDENCE
    assert "Memory Transition Gate remains the sole writer" in EVIDENCE
