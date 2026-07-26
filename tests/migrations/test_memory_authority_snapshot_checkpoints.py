"""Static contract checks for S1-06.3 checkpoint-bound authority evidence."""

from pathlib import Path

MIGRATION = (
    Path(__file__).parents[2] / "migrations" / "0011_memory_authority_snapshot_checkpoints.sql"
).read_text(encoding="utf-8")


def test_checkpoint_binding_is_forward_only_and_refuses_unreconciled_evidence() -> None:
    assert "ADD COLUMN checkpoint_id text" in MIGRATION
    assert "existing rows require audited reconciliation" in MIGRATION
    assert "ALTER COLUMN checkpoint_id SET NOT NULL" in MIGRATION


def test_checkpoint_evidence_is_bounded_and_non_public() -> None:
    assert "memory_authority_snapshot_checkpoint_id_nonempty" in MIGRATION
    assert "length(checkpoint_id) <= 128" in MIGRATION
    assert "REVOKE ALL ON brain_security.memory_authority_snapshots FROM PUBLIC" in MIGRATION
