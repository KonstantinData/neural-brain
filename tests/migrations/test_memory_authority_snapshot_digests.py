"""Static contract checks for S1-06.2 immutable authority snapshot digests."""

from pathlib import Path

MIGRATION = (
    Path(__file__).parents[2] / "migrations" / "0010_memory_authority_snapshot_digests.sql"
).read_text(encoding="utf-8")


def test_snapshot_digest_migration_is_forward_only_and_reconciles_unexpected_rows() -> None:
    assert "ADD COLUMN context_digest char(64)" in MIGRATION
    assert "ADD COLUMN request_digest char(64)" in MIGRATION
    assert "ADD COLUMN snapshot_digest char(64)" in MIGRATION
    assert "existing rows require audited reconciliation" in MIGRATION
    assert "SET NOT NULL" in MIGRATION


def test_snapshot_digests_are_canonical_shaped_unique_and_non_public() -> None:
    assert "memory_authority_snapshot_context_digest_format" in MIGRATION
    assert "memory_authority_snapshot_request_digest_format" in MIGRATION
    assert "memory_authority_snapshot_digest_format" in MIGRATION
    assert "UNIQUE (snapshot_digest)" in MIGRATION
    assert "REVOKE ALL ON brain_security.memory_authority_snapshots FROM PUBLIC" in MIGRATION
