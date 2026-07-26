"""Regression checks for bounded S1-03.5 audit-chain evidence."""

from pathlib import Path

ROOT = Path(__file__).parents[2]
MIGRATION = (ROOT / "migrations" / "0013_memory_audit_hash_chain.sql").read_text(encoding="utf-8")
EVIDENCE = (ROOT / "docs" / "traceability" / "S1-03.5-audit-hash-chain.md").read_text(
    encoding="utf-8"
)
INSTALLER = (ROOT / "tools" / "install_memory_core.py").read_text(encoding="utf-8")


def test_s1_03_5_installs_canonical_scoped_hash_chain_and_verifier() -> None:
    """The bounded control detects evidence tampering without adding a writer."""

    assert "CREATE EXTENSION IF NOT EXISTS pgcrypto" in MIGRATION
    assert "previous_event_hash" in MIGRATION
    assert "event_hash" in MIGRATION
    assert "memory_audit.chain_heads" in MIGRATION
    assert "'sha256'" in MIGRATION
    assert "CREATE TRIGGER audit_events_are_hash_chained" in MIGRATION
    assert "CREATE FUNCTION memory_gate.verify_memory_audit_chain()" in MIGRATION
    assert "PERFORM brain_security.assert_scope_authority('read')" in MIGRATION
    assert "audit hash chain head mismatch" in MIGRATION
    assert "REVOKE ALL ON ALL FUNCTIONS IN SCHEMA memory_audit FROM PUBLIC" in MIGRATION
    assert '"verify_memory_audit_chain"' in INSTALLER
    assert 'for role_name in ("neural_brain_gate", "neural_brain_reader")' in INSTALLER
    assert "chr(0)" not in MIGRATION
    assert "length(NEW.tenant_id)::text" in MIGRATION


def test_s1_03_5_fails_closed_for_legacy_evidence_and_avoids_later_runtime() -> None:
    """Historical hashes are not fabricated and later capabilities remain absent."""

    assert "requires audited reconciliation before hashing existing audit evidence" in MIGRATION
    assert "Goal or Action runtime" in EVIDENCE
    assert "does not\nintroduce a Goal or Action runtime" in EVIDENCE
    assert "external effect" in EVIDENCE
    assert "second protected-state writer" in EVIDENCE
    assert "owner-only internal routines" in EVIDENCE
