"""Regression checks for the bounded S1-03.8 audit reconstruction read Gate."""

from pathlib import Path

ROOT = Path(__file__).parents[2]
MIGRATION = (ROOT / "migrations" / "0015_scoped_memory_audit_timeline.sql").read_text(
    encoding="utf-8"
)
EVIDENCE = (ROOT / "docs" / "traceability" / "S1-03.8-scoped-audit-timeline.md").read_text(
    encoding="utf-8"
)
INSTALLER = (ROOT / "tools" / "install_memory_core.py").read_text(encoding="utf-8")


def test_s1_03_8_is_authenticated_bounded_and_hash_verified_read_gate() -> None:
    """Timeline reconstruction must not bypass authority, scope, or integrity checks."""

    assert "CREATE FUNCTION memory_gate.read_scoped_memory_audit_timeline" in MIGRATION
    assert "PERFORM brain_security.assert_scope_authority('read')" in MIGRATION
    assert "PERFORM memory_gate.verify_memory_audit_chain()" in MIGRATION
    assert "audit timeline cursor must be non-negative" in MIGRATION
    assert "maximum_events must be between 1 and 100" in MIGRATION
    assert "WHERE scoped_event.tenant_id = context_tenant" in MIGRATION
    assert "AND scoped_event.area_id = context_area" in MIGRATION
    assert "GRANT EXECUTE ON FUNCTION memory_gate.read_scoped_memory_audit_timeline" in MIGRATION
    assert '"read_scoped_memory_audit_timeline"' in INSTALLER


def test_s1_03_8_only_projects_redacted_audit_evidence_and_preserves_ms1_boundary() -> None:
    """The reconstruction surface must never become a protected payload or lifecycle API."""

    assert "FROM memory_audit.events AS scoped_event" in MIGRATION
    assert "memory_core.observations" not in MIGRATION
    assert "memory_core.checkpoints" not in MIGRATION
    assert "memory_core.transition_receipts" not in MIGRATION
    assert "raw\nsensitive data" in EVIDENCE
    assert "deletion,\nquarantine" in EVIDENCE
    assert "does not claim their implementation" in EVIDENCE
    assert "sole implemented Memory\nTransition Gate writer" in EVIDENCE
