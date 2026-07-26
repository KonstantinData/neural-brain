"""Static contract checks for S1-06.1 grant catalog and snapshot migration."""

from pathlib import Path

MIGRATION = (
    Path(__file__).parents[2] / "migrations" / "0009_memory_authority_grants.sql"
).read_text(encoding="utf-8")


def test_grant_catalog_binds_issuer_principal_scope_and_bounded_authority() -> None:
    assert "CREATE TABLE brain_security.memory_authority_grants" in MIGRATION
    assert "issuer_id text NOT NULL REFERENCES brain_security.principals" in MIGRATION
    assert "principal_id text NOT NULL REFERENCES brain_security.principals" in MIGRATION
    assert "issuer_id <> principal_id" in MIGRATION
    assert "resource_pattern text NOT NULL" in MIGRATION
    assert "data_class text NOT NULL" in MIGRATION
    assert "purpose text NOT NULL" in MIGRATION
    assert "environment text NOT NULL" in MIGRATION
    assert "valid_until > valid_from" in MIGRATION


def test_snapshots_are_immutable_and_general_roles_receive_no_access() -> None:
    assert "CREATE TABLE brain_security.memory_authority_snapshots" in MIGRATION
    assert "memory_authority_snapshot_is_immutable" in MIGRATION
    assert "BEFORE UPDATE OR DELETE" in MIGRATION
    assert "REVOKE ALL ON brain_security.memory_authority_grants" in MIGRATION
