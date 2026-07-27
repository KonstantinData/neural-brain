"""Deterministic evidence for the preparation-only Relationship Memory boundary."""

import importlib
import json
import re
from pathlib import Path
from typing import Protocol

import pytest

ROOT = Path(__file__).parents[2]
PROPOSAL = ROOT / "docs/architecture/relationship-memory-adr-018-revalidation-proposal-v1.md"
CONTRACT = ROOT / "docs/architecture/contracts/relationship-memory-signal-contract-v1.json"
RUNBOOK = ROOT / "docs/runbooks/relationship-memory-governance-preparation.md"
TRACEABILITY = ROOT / "docs/traceability/REL-MEM-01-08-relationship-memory-preparation.md"

_jsonschema = importlib.import_module("jsonschema")
_validation_error = importlib.import_module("jsonschema.exceptions").ValidationError
assert isinstance(_validation_error, type) and issubclass(_validation_error, Exception)
VALIDATION_ERROR: type[Exception] = _validation_error


class _Validator(Protocol):
    def validate(self, instance: object) -> None: ...


def _text(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


def test_positions_remain_preparation_only_and_non_authorizing() -> None:
    text = _text(PROPOSAL)
    for term in (
        "never a Goal, Authority, Gate",
        "cannot authorize a transition",
        "no customer self-service",
        "service-managed intake and response path",
        "separately authorizable future technical enforcement package",
        "runtime-disabled",
    ):
        assert term in text
    for exclusion in (
        "migration",
        "runtime component",
        "retrieval endpoint",
        "Dreaming execution",
        "Planner integration",
        "deployment",
        "release",
    ):
        assert exclusion in text


def test_signal_contract_is_fail_closed_and_non_runtime() -> None:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    _jsonschema.Draft202012Validator.check_schema(contract)
    assert contract["runtime_enabled"] is False
    assert contract["migrations_authorized"] is False
    validator: _Validator = _jsonschema.Draft202012Validator(contract)
    with pytest.raises(VALIDATION_ERROR):
        validator.validate(None)


def test_position_three_and_runtime_boundaries_are_explicit() -> None:
    proposal = _text(PROPOSAL)
    threat_plan = _text(
        ROOT / "docs/architecture/relationship-memory-threat-model-and-test-plan-v1.md"
    )
    runbook = _text(ROOT / "docs/runbooks/relationship-memory-governance-preparation.md")
    planner = _text(
        ROOT / "docs/architecture/nb1-planner-verification-adr-018-revalidation-proposal-v1.md"
    )
    for term in (
        "schema",
        "Memory Gate",
        "deletion propagation",
        "negative Scope/Purpose tests",
        "independent verification",
    ):
        assert term in threat_plan
    assert "deny_and_do_not_use" in runbook
    assert (
        "approved, minimized, provenance-bound Relationship Memory signals as untrusted context"
        in planner
    )
    assert proposal.index("Position 2: service-operated default after onboarding") < proposal.index(
        "Position 3: future enforcement package"
    )
    for term in (
        "future enforcement package REL-MEM-16",
        "derived from Position 2",
        "runtime-disabled until separately accepted and independently verified",
        "Retrieval, Planner, and Dreaming runtimes remain separately contracted",
    ):
        assert term in proposal


def test_supporting_governance_boundaries_are_explicit() -> None:
    access_matrix = _text(
        ROOT / "docs/governance/relationship-memory-access-purpose-agent-scope-matrix-v1.md"
    )
    privacy_matrix = _text(
        ROOT / "docs/governance/relationship-memory-privacy-retention-correction-matrix-v1.md"
    )
    dreaming = _text(ROOT / "docs/architecture/relationship-memory-dreaming-boundary-v1.md")
    threat_plan = _text(
        ROOT / "docs/architecture/relationship-memory-threat-model-and-test-plan-v1.md"
    )

    for term in ("Reader", "Candidate proposer", "Reviewer", "Dreaming worker", "NB-1 Planner"):
        assert term in access_matrix
    assert (
        "unknown actor, scope, purpose, classification, review, or policy denies" in access_matrix
    )

    for term in (
        "Explicit correction",
        "expires by default",
        "deletion must propagate",
        "Pseudonymization alone is not anonymization",
        "Qualified privacy review",
    ):
        assert term in privacy_matrix

    for term in ("Area-local", "inactive, non-retrievable candidates", "cross-scope linking"):
        assert term in dreaming

    for term in (
        "Cross-Company, Area, or Project leakage",
        "Purpose bypass",
        "Profile inference",
        "Direct write",
        "Dreaming bypass",
        "Deletion remnants",
        "Correction conflict",
        "Planner authority escalation",
    ):
        assert term in threat_plan


def test_runbook_covers_candidate_review_and_lifecycle_handoffs() -> None:
    runbook = _text(RUNBOOK)
    for term in (
        "Candidate review handoff",
        "inactive and non-retrievable",
        "Memory Transition Gate",
        "independent future Reviewer",
        "Correction, retention, and deletion handoff",
        "provenance-bearing successor candidate",
        "uncertain legal-hold state",
        "On a future deletion request",
        "Escalate prohibited content",
        "deny_and_do_not_use",
    ):
        assert term in runbook
    for disposition in (
        "protected review",
        "correction or supersession",
        "expiry",
        "deletion-pending",
        "deletion-complete",
    ):
        assert disposition in runbook
    for gate_input in (
        "authenticated actor",
        "immutable Tenant and Area scope",
        "verified authority",
        "applicable policy",
        "atomic audit evidence",
    ):
        assert gate_input in runbook
    assert "Memory Transition Gate remains the sole future writer" in runbook
    assert "downstream deletion reconciler" in runbook
    assert "reconciler cannot write protected memory state or mark deletion complete" in runbook
    assert "not an executable review or Memory transition procedure" in runbook
    assert "does not activate schema, Gate, retrieval, Planner, or Dreaming" in runbook


def test_runbook_covers_adr_019_productive_tenant_anchor() -> None:
    runbook = _text(RUNBOOK)
    for term in (
        "Tenant-bound Runtime login",
        "Tenant-specific connection pool",
        "protected state keyed by immutable `session_user`",
        "expected active Tenant, database target, and credential revision match",
        "subordinate lineage below the database-bound Tenant",
        "`current_user`, writable settings, candidate content, and request payloads are not identity anchors",
    ):
        assert term in runbook


def _traceability_rows() -> dict[str, tuple[str, str, str]]:
    rows: dict[str, tuple[str, str, str]] = {}
    for line in TRACEABILITY.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| REL-MEM-"):
            continue
        cells = tuple(cell.strip() for cell in line.strip().strip("|").split("|"))
        assert len(cells) == 4
        package, decision, tests, acceptance = cells
        assert package not in rows
        rows[package] = (decision, tests, acceptance)
    return rows


def test_traceability_maps_every_preparation_package() -> None:
    traceability = _text(TRACEABILITY)
    rows = _traceability_rows()
    assert set(rows) == {*(f"REL-MEM-{index:02d}" for index in range(1, 9)), "REL-MEM-16"}
    for heading in (
        "Decision and contract evidence",
        "Test evidence",
        "Acceptance evidence and boundary",
    ):
        assert heading in traceability
    for evidence in (
        "relationship-memory-adr-018-revalidation-proposal-v1.md",
        "relationship-memory-signal-contract-v1.json",
        "relationship-memory-access-purpose-agent-scope-matrix-v1.md",
        "relationship-memory-privacy-retention-correction-matrix-v1.md",
        "nb1-planner-verification-revalidation-v1.json",
        "relationship-memory-dreaming-boundary-v1.md",
        "relationship-memory-threat-model-and-test-plan-v1.md",
        "relationship-memory-governance-preparation.md",
    ):
        assert evidence in traceability
    references = re.findall(r"`((?:docs|tests)/[^`]+)`", TRACEABILITY.read_text(encoding="utf-8"))
    assert references
    for reference in references:
        path_text, separator, function_name = reference.partition("::")
        repository_path = ROOT / path_text
        assert repository_path.is_file(), reference
        if separator:
            assert function_name.startswith("test_")
            test_source = repository_path.read_text(encoding="utf-8")
            assert f"def {function_name}(" in test_source, reference
    assert "test_runbook_covers_candidate_review_and_lifecycle_handoffs" in traceability
    assert "no operational procedure is executed" in traceability
