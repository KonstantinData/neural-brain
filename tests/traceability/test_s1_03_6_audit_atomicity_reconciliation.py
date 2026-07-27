"""Regression checks for S1-03.6 complete audit-failure rollback evidence."""

from pathlib import Path

ROOT = Path(__file__).parents[2]
MIGRATION = (ROOT / "migrations" / "0002_stage1_memory_kernel.sql").read_text(encoding="utf-8")
EVIDENCE = (ROOT / "docs" / "traceability" / "S1-03.6-audit-atomicity-reconciliation.md").read_text(
    encoding="utf-8"
)
DATABASE_TEST = (ROOT / "tests" / "database" / "test_stage1_memory_kernel.py").read_text(
    encoding="utf-8"
)


def test_s1_03_6_keeps_audit_and_every_memory_transition_artifact_in_one_gate() -> None:
    """The original gate is the only writer and appends audit before its receipt."""

    commit_start = MIGRATION.index("CREATE FUNCTION memory_gate.commit_memory_cycle(")
    commit_end = MIGRATION.index("CREATE FUNCTION memory_gate.read_checkpoint", commit_start)
    commit_function = MIGRATION[commit_start:commit_end]

    assert "PERFORM brain_security.assert_scope_authority('ingest')" in commit_function
    assert "INSERT INTO memory_core.observations" in commit_function
    assert "INSERT INTO memory_core.working_context_versions" in commit_function
    assert "INSERT INTO memory_core.checkpoints" in commit_function
    assert "INSERT INTO memory_audit.events" in commit_function
    assert "INSERT INTO memory_core.transition_receipts" in commit_function
    assert commit_function.index("INSERT INTO memory_audit.events") < commit_function.index(
        "INSERT INTO memory_core.transition_receipts"
    )


def test_s1_03_6_documents_complete_rollback_and_scope_preservation() -> None:
    """The live fault injection covers all state and evidence artefacts, not one row."""

    assert "PR #6" in EVIDENCE
    assert "no second writer" in EVIDENCE
    assert (
        "no failed-scope observation, current working context, version, checkpoint, receipt"
        in EVIDENCE
    )
    assert "chain head" in EVIDENCE
    assert "Area A transition remains present" in EVIDENCE
    assert "injected audit failure" in DATABASE_TEST
    for relation in (
        "memory_core.working_contexts",
        "memory_core.working_context_versions",
        "memory_core.checkpoints",
        "memory_core.transition_receipts",
        "memory_audit.events",
        "memory_audit.chain_heads",
    ):
        assert relation in DATABASE_TEST
