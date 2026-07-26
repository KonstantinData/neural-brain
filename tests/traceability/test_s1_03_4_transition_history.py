"""Regression checks for bounded S1-03.4 MS-1 transition history evidence."""

from pathlib import Path

ROOT = Path(__file__).parents[2]
MIGRATION = (ROOT / "migrations" / "0012_memory_transition_history_immutability.sql").read_text(
    encoding="utf-8"
)
EVIDENCE = (ROOT / "docs" / "traceability" / "S1-03.4-transition-history.md").read_text(
    encoding="utf-8"
)


def test_s1_03_4_makes_only_ms1_history_immutable() -> None:
    """Historical evidence is immutable without creating later lifecycle runtime."""

    assert "memory transition history is immutable; committed transitions are terminal" in MIGRATION
    assert "working_context_versions_are_immutable" in MIGRATION
    assert "checkpoints_are_immutable" in MIGRATION
    assert "transition_receipts_are_immutable" in MIGRATION
    assert "ERRCODE = '55000'" in MIGRATION
    assert "CREATE TABLE" not in MIGRATION
    assert "Goal or Action runtime" in EVIDENCE
    assert "does not introduce a Goal or Action runtime" in EVIDENCE


def test_s1_03_4_records_terminal_receipts_without_claiming_later_lifecycle() -> None:
    """A receipt is terminal evidence, not a prematurely enabled state machine."""

    assert "committed terminal outcome" in EVIDENCE
    assert "candidate promotion, quarantine, deletion, retrieval, external effects" in EVIDENCE
    assert "Memory Transition Gate" in EVIDENCE
    assert "MIGRATION_ADMIN_DSN" in EVIDENCE
