"""Static contract checks for the S1-01.1 identity-governance migration."""

from __future__ import annotations

from pathlib import Path

MIGRATION = (
    Path(__file__).parents[2] / "migrations" / "0008_principal_roles_and_service_identities.sql"
).read_text(encoding="utf-8")


def test_identity_migration_adds_typed_principals_and_validity_windows() -> None:
    assert "principal_kind IN ('human', 'service')" in MIGRATION
    assert "principals_validity_window_check" in MIGRATION
    assert "valid_until IS NULL OR valid_until > valid_from" in MIGRATION


def test_identity_migration_requires_scoped_role_bindings() -> None:
    assert "CREATE TABLE brain_security.roles" in MIGRATION
    assert "CREATE TABLE brain_security.principal_role_bindings" in MIGRATION
    assert "REFERENCES brain_catalog.areas (tenant_id, area_id)" in MIGRATION
    assert "REFERENCES brain_catalog.projects (tenant_id, area_id, project_id)" in MIGRATION
    assert (
        "REFERENCES brain_catalog.sessions (tenant_id, area_id, project_id, session_id)"
        in MIGRATION
    )
    assert "session_id IS NULL OR project_id IS NOT NULL" in MIGRATION


def test_service_identity_requires_active_valid_service_principal() -> None:
    assert "CREATE TABLE brain_security.service_identities" in MIGRATION
    assert "assert_service_identity_principal_kind" in MIGRATION
    assert "principal.principal_kind = 'service'" in MIGRATION
    assert "principal.status = 'active'" in MIGRATION
    assert "service_identity_principal_kind_guard" in MIGRATION
