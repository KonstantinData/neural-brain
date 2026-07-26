"""Regression checks for the bounded S1-03.7 redacted audit contract."""

from pathlib import Path

ROOT = Path(__file__).parents[2]
MIGRATION = (ROOT / "migrations" / "0014_memory_audit_redaction.sql").read_text(encoding="utf-8")
EVIDENCE = (ROOT / "docs" / "traceability" / "S1-03.7-audit-redaction.md").read_text(
    encoding="utf-8"
)
INSTALLER = (ROOT / "tools" / "install_memory_core.py").read_text(encoding="utf-8")


def test_s1_03_7_redacts_before_hashing_and_exposes_only_a_scoped_read_gate() -> None:
    """Future audit rows are fixed envelopes before integrity-chain ownership."""

    assert "CREATE FUNCTION memory_audit.redact_event_evidence()" in MIGRATION
    assert "CREATE FUNCTION memory_audit.contains_sensitive_evidence_field" in MIGRATION
    assert "CREATE TRIGGER audit_a_redaction_before_hash_chain" in MIGRATION
    assert "audit event type has no approved redaction contract" in MIGRATION
    assert "audit evidence contains a prohibited sensitive payload field" in MIGRATION
    assert "'audit_schema_version', 's1-03-7-v1'" in MIGRATION
    assert "'evidence_references'" in MIGRATION
    assert "CREATE FUNCTION memory_gate.read_redacted_memory_audit_event" in MIGRATION
    assert "PERFORM brain_security.assert_scope_authority('read')" in MIGRATION
    assert (
        "GRANT EXECUTE ON FUNCTION memory_gate.read_redacted_memory_audit_event(bigint)"
        in MIGRATION
    )
    assert '"read_redacted_memory_audit_event"' in INSTALLER


def test_s1_03_7_preserves_ms1_boundary_and_does_not_forge_policy_evidence() -> None:
    """The current absence of a policy runtime remains explicit and fail-closed."""

    assert "'not_implemented'" in MIGRATION
    assert "does not implement a\nPolicy Decision runtime" in EVIDENCE
    assert "Goal or Action runtime" in EVIDENCE
    assert "external effect" in EVIDENCE
    assert "sole implemented Memory" in EVIDENCE
