"""Evidence for the fail-closed AI Act obligation-matrix template."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).parents[2]
CONTRACT_PATH = ROOT / "docs" / "architecture" / "contracts" / "ai-act-obligation-matrix-v1.json"


def _contract() -> dict[str, object]:
    loaded: object = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _strings(value: object) -> set[str]:
    assert isinstance(value, list)
    assert all(isinstance(item, str) for item in value)
    return set(value)


def test_matrix_covers_roles_external_facts_and_obligation_accountability() -> None:
    contract = _contract()
    assert contract["contract_id"] == "neural-brain.ai-act-obligation-matrix"
    assert contract["contract_version"] == "1.0.0"
    assert contract["governing_decisions"] == ["ADR-001", "ADR-005", "ADR-018"]
    external = contract["authoritative_external_reference"]
    assert isinstance(external, dict)
    assert external["official_url"] == "https://eur-lex.europa.eu/eli/reg/2024/1689/oj"
    matrix = contract["matrix_template"]
    assert isinstance(matrix, dict)
    assert _strings(matrix["role_categories_for_review_only"]) == {
        "provider",
        "deployer",
        "model_supplier",
        "downstream_actor",
        "non_applicability_candidate",
        "not_assessed",
    }
    fields = _strings(matrix["required_matrix_record_fields"])
    assert {
        "authenticated_tenant_area_project_scope_reference",
        "external_facts_and_official_source_references",
        "role_basis_evidence_and_candidate_role",
        "obligation_owner_due_date_review_status_and_evidence_reference",
        "reassessment_triggers_next_review_date_and_linked_reassessment_work",
    } <= fields
    rows = _strings(matrix["required_row_fields"])
    assert {
        "role_basis_evidence_reference_or_explicit_absence",
        "external_fact_reference_and_official_source",
        "candidate_obligation_and_article_reference",
        "accountable_obligation_owner_or_explicit_absence",
        "due_date_or_qualified_non_applicability_basis",
        "reassessment_trigger_and_next_review_date",
    } <= rows


def test_unknown_role_or_evidence_fails_closed_without_enablement() -> None:
    semantics = _contract()["fail_closed_semantics"]
    assert isinstance(semantics, dict)
    assert (
        semantics["unknown_role_or_role_basis_evidence"]
        == "obligation_matrix_incomplete_and_deployment_specific_release_blocked"
    )
    assert (
        semantics["unknown_missing_stale_contradictory_or_scope_mismatched_obligation_evidence"]
        == "obligation_matrix_incomplete_and_deployment_specific_release_blocked"
    )
    assert (
        semantics["missing_owner_due_date_review_rationale_or_reassessment_data"]
        == "obligation_matrix_incomplete_and_deployment_specific_release_blocked"
    )
    assert (
        semantics["unqualified_or_unverified_non_applicability_basis"]
        == "obligation_matrix_incomplete_and_deployment_specific_release_blocked"
    )
    assert semantics["no_automatic_role_or_obligation_assignment"] is True
    assert semantics["no_automatic_non_applicability_conclusion"] is True
    assert semantics["no_model_deployment_or_runtime_enablement"] is True
    assert semantics["no_allow_outcome"] is True


def test_boundary_excludes_legal_status_authority_and_real_deployment_outcomes() -> None:
    boundary = _contract()["authority_boundary"]
    assert isinstance(boundary, dict)
    excluded = _strings(boundary["template_is_not"])
    assert {
        "a real provider, deployer, model supplier or downstream-actor assignment",
        "a conclusion that an obligation applies, is satisfied, is due, is delegated, is waived or is non-applicable",
        "a model supplier approval, model promotion, deployment, productive-use or release approval",
        "an authority grant, policy decision, approval, authenticated identity or trusted scope",
        "a protected-state mutation, external effect, runtime capability enablement, maturity, safety or compliance claim",
    } <= excluded


def test_documentation_preserves_product_neutral_evidence_only_boundary() -> None:
    documentation = (ROOT / "docs" / "governance" / "ai-act-obligation-matrix-v1.md").read_text(
        encoding="utf-8"
    )
    traceability = (
        ROOT / "docs" / "traceability" / "S1-15.1-ai-act-obligation-matrix.md"
    ).read_text(encoding="utf-8")
    assert "does not assign a real role or obligation" in documentation
    assert "has no allow outcome" in documentation
    assert (
        "cannot narrow ADR-018's complete protected cognitive-system product boundary"
        in documentation
    )
    assert (
        "no protected state, identity, authority, policy, approval, model deployment"
        in traceability
    )
    assert "external effect, or release state" in traceability
