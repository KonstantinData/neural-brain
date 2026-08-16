"""Deterministic evidence for the non-authorizing NB-8 preparation package."""

import json
from pathlib import Path

ROOT = Path(__file__).parents[2]
PROPOSAL = ROOT / "docs/architecture/nb8-distributed-operation-adr-018-revalidation-proposal-v1.md"
CONTRACT = ROOT / "docs/architecture/contracts/nb8-distributed-operation-preparation-v1.json"
PLAN = ROOT / "docs/architecture/contracts/nb8-distributed-operation-test-plan-v1.json"
TRACEABILITY = ROOT / "docs/traceability/NB-8-distributed-operation-preparation.md"


def _load(path: Path) -> dict[str, object]:
    loaded: object = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def test_nb8_preparation_is_blocked_and_non_authorizing() -> None:
    proposal = PROPOSAL.read_text(encoding="utf-8")
    contract = _load(CONTRACT)

    assert "Status: Proposed prerequisite; not accepted and not runtime authorization" in proposal
    assert contract["status"] == "proposed_not_accepted_not_runtime_authorization"
    assert contract["hard_predecessors"] == [
        "NB-7 complete exit evidence",
        "accepted ADR-018-conformant Goal and Action Gate decisions",
        "NB-5 serial action-control, independent verification, indeterminate-effect, and reconciliation evidence",
    ]
    exclusions = contract["explicit_exclusions"]
    assert isinstance(exclusions, list)
    assert {"runtime implementation", "external effect", "stage release authorization"} <= set(
        exclusions
    )


def test_nb8_contract_preserves_scope_gate_and_cross_area_boundaries() -> None:
    contract = _load(CONTRACT)
    authority = contract["authority_boundary"]
    scope = contract["immutable_scope_lineage"]
    future = contract["future_state_and_actor_contract"]
    assert isinstance(authority, dict)
    assert isinstance(scope, dict)
    assert isinstance(future, dict)
    assert authority["default_on_unknown_or_stale_fact"] == "deny_or_contain_and_reconcile"
    assert scope["hierarchy"] == ["brain_id", "tenant_id", "area_id", "project_id", "session_id"]
    assert "may never infer, replace, broaden, or repair it" in str(scope["binding"])
    cross_area = future["governed_cross_area_abstraction"]
    assert isinstance(cross_area, dict)
    assert cross_area["default"] == "deny"
    assert {"raw memory sharing", "implicit scope expansion"} <= set(cross_area["prohibitions"])
    queue = future["durable_queue"]
    assert isinstance(queue, dict)
    assert "untrusted transport data" in str(queue["rules"])
    rules = contract["non_regression_rules"]
    assert isinstance(rules, list)
    assert any("atomic" in rule and "audit" in rule for rule in rules)


def test_nb8_test_plan_covers_required_evidence_and_immutable_results() -> None:
    plan = _load(PLAN)
    assert plan["status"] == "proposed_not_accepted_not_runtime_authorization"
    assert plan["required_lineage"] == [
        "brain_id",
        "tenant_id",
        "area_id",
        "project_id",
        "session_id",
    ]
    cases = plan["cases"]
    assert isinstance(cases, list)
    assert {case["category"] for case in cases if isinstance(case, dict)} == {
        "partition_and_lease_expiry",
        "split_brain_and_stale_fence",
        "duplicate_delivery_and_effect",
        "reconciliation_leadership",
        "restore_and_generation_fencing",
        "semantic_equivalence",
        "tenant_area_and_cross_area_isolation",
    }
    result = plan["result_schema"]
    assert isinstance(result, dict)
    refs = result["required_immutable_artifact_refs"]
    assert isinstance(refs, list)
    assert {"serial_reference_artifact_ref", "independent_witness_artifact_ref"} <= set(refs)
    oracles = plan["common_oracles"]
    assert isinstance(oracles, dict)
    assert "hash-chain continuity" in str(oracles["semantic_equivalence_oracle"])


def test_nb8_traceability_records_static_contract_test_boundary() -> None:
    traceability = TRACEABILITY.read_text(encoding="utf-8")
    assert "Deterministic documentation-contract tests" in traceability
    assert (
        "uv run pytest -q tests/architecture/test_nb8_distributed_operation_preparation.py"
        in traceability
    )
    assert "passed for the versioned preparation boundary only" in traceability
    assert "a migration would violate the NB-8 implementation blocker" in traceability
