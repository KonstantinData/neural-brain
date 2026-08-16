# Fail-closed preparation contract tests for a future NB-6 evaluation.

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "docs/architecture/contracts/nb6-predecessor-gated-evaluation-v1.json"


def _load() -> dict[str, Any]:
    loaded = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def test_contract_is_preparation_only_and_predecessor_blocked() -> None:
    contract = _load()

    assert contract["status"] == "preparation_only_predecessor_blocked"
    assert contract["decision"] == "ADR-018"
    prohibited = set(contract["scope"]["prohibited"])
    assert {
        "NB-6 runtime implementation or activation",
        "evaluation-spec registration",
        "candidate freeze or model promotion",
        "hidden-artifact generation or attachment",
        "evaluation execution or score publication",
        "gate passage or stage release",
        "recognition claim",
        "production-autonomy claim",
        "external effect or authority grant",
    } <= prohibited
    dependencies = " ".join(contract["entry_dependencies"]["all_required"])
    assert "NB-1 through NB-5" in dependencies
    assert "G0 through G4" in dependencies
    assert contract["entry_dependencies"]["fail_closed"].startswith("Any missing")
    assert "cannot compensate" in contract["entry_dependencies"]["non_compensation"]
    scope = contract["scope_and_authority_binding"]
    assert set(scope["required_lineage"]) == {
        "brain_id",
        "tenant_id",
        "area_id",
        "project_id",
        "session_id",
        "candidate_id",
        "evaluation_spec_digest",
    }
    assert scope["runtime_trusted_source"] == "Authenticated runtime context only."
    assert (
        "cannot define, repair, widen, or override runtime scope"
        in scope["evaluation_attestation_source"]
    )
    assert "model output" in scope["untrusted_sources"]
    assert set(scope["required_attestation_binding"]) == {
        "authenticated principal identity",
        "role and mandate identity",
        "independence and conflict attestation identity",
        "validity interval",
        "evaluation-policy and specification digests",
        "scope-bound trust-registry reference and signature reference",
    }
    assert "denied" in scope["rule"]


def test_future_preregistration_is_immutable_and_binds_all_evidence() -> None:
    preregistration = _load()["required_future_preregistration"]

    assert "SHA-256 spec_digest" in preregistration["artifact"]
    assert {
        "falsifiable hypotheses and primary metrics per evaluation family",
        "immutable train, development, hidden-test, and transfer-domain splits",
        "strongest relevant baselines and no-transfer controls",
        "component interventions and predicted directional impairments",
        "contamination controls and disclosure checks",
        "candidate, source tree, dependency lock, environment, executable, and protocol digests",
    } <= set(preregistration["must_bind"])
    assert "invalidates" in preregistration["post_hoc_change"]


def test_transfer_causal_calibration_and_response_families_are_complete() -> None:
    families = {family["id"]: family for family in _load()["evaluation_families"]}

    assert set(families) == {"NB6-F1", "NB6-F2", "NB6-F3", "NB6-F4"}
    assert {"R6", "R7", "R9"} <= set(families["NB6-F1"]["claims"])
    assert "task-specific rewiring is prohibited" in " ".join(
        families["NB6-F1"]["required_conditions"]
    )
    assert {"R8", "R9"} <= set(families["NB6-F2"]["claims"])
    causal_conditions = " ".join(families["NB6-F2"]["required_conditions"])
    assert "shuffled-action" in causal_conditions
    assert "evaluator-custodied sealed simulation or sandbox" in causal_conditions
    assert "cannot write protected state" in causal_conditions
    assert {"NC-15", "NC-16", "R9"} <= set(families["NB6-F3"]["claims"])
    assert "actual correctness and actual outcomes" in " ".join(
        families["NB6-F3"]["required_conditions"]
    )
    response_requirements = " ".join(families["NB6-F4"]["required_conditions"])
    for response in (
        "continue",
        "seek_information",
        "ask",
        "explore",
        "defer",
        "fallback",
        "escalate",
        "stop",
    ):
        assert response in response_requirements
    assert "never creates authority" in response_requirements
    assert "strict no-effect semantics" in response_requirements
    assert "non-authorizing safe_mode_id" in response_requirements
    assert "Protected Control Plane resolves it" in response_requirements
    assert "zero-tolerance failure" in families["NB6-F4"]["failure"]


def test_hidden_custody_and_g8_reproduction_are_independent_and_non_compensatory() -> None:
    contract = _load()
    custody = contract["hidden_evidence_custody"]
    repository_boundary = custody["repository_boundary"]

    for forbidden in (
        "hidden seeds",
        "hidden tasks",
        "labels",
        "latent structures",
        "detailed scoring",
        "evaluator code",
        "private keys",
    ):
        assert forbidden in repository_boundary
    separation = custody["separation"]
    assert "must not access hidden artifacts" in " ".join(separation["implementation_owner"])
    assert "must be independent" in " ".join(separation["independent_evaluator"])
    assert "cannot be the implementation owner" in " ".join(separation["recognition_authority"])
    assert "owns the trusted registry" in " ".join(separation["registry_custodian"])
    assert "inadmissible" in custody["fail_closed"]
    custody_order = custody["admissibility"][0]
    assert "candidate freeze before" in custody_order
    assert "all attempts start only after" in custody_order
    assert not custody_order.startswith(
        "Hidden commitments are timestamped before candidate freeze"
    )
    allocation = custody["admissibility"][1]
    assert "maximum attempts" in allocation
    assert "complete allowed-submission set" in allocation
    assert "undeclared attempts or candidates" in allocation
    feedback = custody["admissibility"][3]
    assert "No per-attempt score" in feedback
    assert "retired or replaced" in feedback

    g8 = contract["g8_independent_reproduction"]
    assert any("G0 through G7" in item for item in g8["required"])
    assert any("all R1 through R10" in item for item in g8["required"])
    assert any("second declared runtime environment" in item for item in g8["required"])
    assert g8["result_semantics"] == {
        "allowed": ["pass", "fail", "unknown"],
        "unknown": "fail",
        "aggregation": "all_required_non_compensatory",
    }
    assert set(g8["prohibited_inferences"]) == {
        "G8 preparation proves G8",
        "G8 proves consciousness",
        "G8 proves sentience",
        "G8 proves human equivalence",
        "G8 authorizes production autonomy",
    }


def test_acceptance_package_does_not_complete_nb6_or_grant_recognition() -> None:
    package = _load()["acceptance_package"]

    assert (
        "future immutable NB-6 evaluation specification with digest"
        in package["repository_evidence"]
    )
    assert (
        "two-environment reproduction and independent admissibility review"
        in package["external_evidence"]
    )
    completion = package["completion_rule"]
    assert "does not complete NB-6" in completion
    assert "G5/G6/G8" in completion
    assert "recognition label" in completion
