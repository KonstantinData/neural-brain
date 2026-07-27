"""Static evidence for the protected-ledger backup and PITR target contract."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).parents[2]
CONTRACT_PATH = ROOT / "docs" / "architecture" / "contracts" / "protected-ledger-backup-recovery-v1.json"


def _contract() -> dict[str, object]:
    loaded: object = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _strings(value: object) -> set[str]:
    assert isinstance(value, list)
    assert all(isinstance(item, str) for item in value)
    return set(value)


def test_contract_is_foundation_control_not_deployment_evidence() -> None:
    contract = _contract()
    assert contract["contract_id"] == "neural-brain.protected-ledger-backup-recovery"
    assert contract["contract_version"] == "1.0.0"
    assert contract["governing_decisions"] == ["ADR-003", "ADR-018", "ADR-019"]
    assert contract["delivery_stage"] == "nb_0_foundation_operational_control"
    assert contract["current_state"] == "contract_only_no_deployment_or_restore_evidence"
    assert any("No backup target" in claim for claim in _strings(contract["non_claims"]))


def test_backup_contract_requires_encryption_wal_pitr_and_deployment_parameters() -> None:
    contract = _contract()
    requirements = contract["backup_requirements"]
    assert isinstance(requirements, dict)
    confidentiality = _strings(requirements["confidentiality_and_integrity"])
    assert any("encrypt backup and WAL material" in rule for rule in confidentiality)
    assert any("key custody" in rule for rule in confidentiality)
    assert any("immutable" in rule for rule in confidentiality)
    pitr = _strings(requirements["pitr"])
    assert any("continuous validated WAL archive" in rule for rule in pitr)
    assert any("isolated non-serving environment" in rule for rule in pitr)
    parameters = contract["deployment_parameters"]
    assert isinstance(parameters, dict)
    required = _strings(parameters["must_be_approved_and_recorded_before_productive_admission"])
    assert any("RPO target" in item for item in required)
    assert any("RTO target" in item for item in required)
    assert parameters["repository_defaults"] == "none"


def test_access_separation_and_restore_success_are_non_bypassable() -> None:
    contract = _contract()
    separation = contract["access_separation"]
    assert isinstance(separation, dict)
    roles = _strings(separation["required_roles"])
    assert {"restricted backup operator", "separate encryption-key custodian", "separate restore or recovery operator", "independent restore-test witness"} <= roles
    prohibitions = _strings(separation["prohibitions"])
    assert any("Cognitive Plane" in rule for rule in prohibitions)
    assert any("cannot cut over" in rule for rule in prohibitions)
    acceptance = contract["restore_acceptance"]
    assert isinstance(acceptance, dict)
    assert "tool exit is not restore success" in str(acceptance["success_semantics"])


def test_fail_closed_recovery_retention_and_protected_ledger_invariants() -> None:
    contract = _contract()
    semantics = contract["fail_closed_semantics"]
    assert isinstance(semantics, dict)
    assert semantics["unknown_backup_or_wal_coverage"] == "productive_admission_and_recovery_cutover_blocked"
    assert semantics["missing_or_failed_restore_test"] == "productive_admission_blocked"
    assert semantics["ambiguous_restore_outcome"] == "indeterminate_pending_authoritative_reconciliation_no_blind_retry"
    assert semantics["incomplete_reconciliation_or_audit_continuity"] == "not_ready_no_service_cutover"
    assert semantics["missing_or_expired_retention_hold_or_deletion_evidence"] == "destructive_expiry_blocked"
    invariants = _strings(contract["invariants"])
    assert any("authoritative protected ledger" in rule for rule in invariants)
    assert any("owning Gate" in rule for rule in invariants)
    assert any("Tenant and Area isolation" in rule for rule in invariants)


def test_runbook_and_traceability_retain_non_claim_and_release_stop_boundary() -> None:
    runbook = (ROOT / "docs" / "runbooks" / "protected-ledger-backup-recovery.md").read_text(encoding="utf-8")
    traceability = (ROOT / "docs" / "traceability" / "S1-13.5-protected-ledger-backup-pitr.md").read_text(encoding="utf-8")
    assert "is not evidence that a backup\ntarget" in runbook
    assert "isolated non-serving" in runbook
    assert "Tool exit or self-report as proof" in runbook
    assert "does not prove encryption" in traceability
    assert "NB-0 Foundation operational control" in traceability
