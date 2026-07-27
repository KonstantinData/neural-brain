"""Fail-closed preparation tests for the NB-1 candidate-freeze lifecycle."""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "docs/architecture/contracts/nb1-candidate-freeze-lifecycle-v1.json"
ARTIFACT_MANIFESTS = (
    ROOT / "docs/architecture/contracts/nb1-independent-evaluation-artifact-manifests-v1.json"
)


def _load() -> dict[str, Any]:
    loaded = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _load_artifact_manifests() -> dict[str, Any]:
    loaded = json.loads(ARTIFACT_MANIFESTS.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def test_lifecycle_is_preparation_only_and_never_authorizes_runtime_or_release() -> None:
    contract = _load()

    assert contract["status"] == "preparation_only_no_candidate_or_release_authority"
    assert contract["decisions"] == ["ADR-018"]
    assert (
        contract["applies_to"]
        == "EVAL-01.NB-1.safe-serial-cognition.v4 public-only candidate preparation"
    )
    assert all(value is False for value in contract["non_authorization"].values())
    assert set(contract["freeze_states"]) == {
        "draft",
        "submitted",
        "accepted",
        "invalidated",
        "superseded",
    }


def test_receipt_hash_manifest_and_versioning_require_complete_immutable_v4_bindings() -> None:
    contract = _load()
    hashing = contract["canonicalization_and_hashing"]
    receipt = contract["required_receipt"]

    assert hashing["profile_id"] == "nb1-eval-canonical-json-v1"
    assert (
        hashing["artifact_kind_mapping_source"]
        == "docs/architecture/contracts/nb1-independent-evaluation-artifact-manifests-v1.json#/canonicalization/artifact_kind_byte_rules"
    )
    assert hashing["digest_algorithm"] == "SHA-256"
    assert hashing["digest_encoding"] == "lowercase hexadecimal"
    assert (
        hashing["profile_definition_source"]
        == "docs/architecture/contracts/nb1-independent-evaluation-artifact-manifests-v1.json#/canonicalization/byte_profile"
    )
    assert "no local alternative" in hashing["canonical_json"].lower()
    assert set(hashing["profile_requirements"]) == {
        "UTF-8 without byte-order mark",
        "LF line endings",
        "deterministic Unicode code-point ordering",
        "sorted object keys",
        "compact JSON separators",
        "no NaN",
        "no Infinity",
        "v4-defined decimal values are strings",
    }
    assert "nb1-eval-canonical-json-v1" in " ".join(hashing["hash_workflow"])
    manifests = _load_artifact_manifests()
    canonicalization = manifests["canonicalization"]
    assert isinstance(canonicalization, dict)
    artifact_kind_rules = canonicalization["artifact_kind_byte_rules"]
    assert isinstance(artifact_kind_rules, dict)
    assert set(artifact_kind_rules) == {
        "canonical_json_object",
        "utf8_text",
        "binary",
        "deterministic_bundle_manifest",
    }
    assert "only a root JSON object" in artifact_kind_rules["canonical_json_object"]["rule"]
    assert "exact stored text bytes" in artifact_kind_rules["utf8_text"]["digest_input"]
    assert "exact stored byte sequence" in artifact_kind_rules["binary"]["rule"]
    assert (
        "every listed regular-file content_sha256"
        in artifact_kind_rules["deterministic_bundle_manifest"]["digest_input"]
    )
    assert {"hidden_seed", "expected_labels", "private_keys"} <= set(
        hashing["prohibited_hash_inputs"]
    )
    assert receipt["immutable_after_submission"] is True
    assert {
        "source_commit",
        "candidate_semver",
        "candidate_bundle_manifest_digest",
        "model_manifest_digest",
        "evaluation_manifest_digest",
        "generator_contract_digest",
        "dependency_lock_digest",
        "artifact_registry_reference",
    } <= set(receipt["required_fields"])
    assert "never proves" in receipt["claim_boundary"]
    manifests = contract["required_manifests"]
    assert {"candidate_semver", "parameter_digest", "resource_bound_declaration"} <= set(
        manifests["model_manifest"]
    )
    assert {
        "candidate_bundle_digest",
        "evaluation_executable_digest",
        "hidden_input_exclusion_declaration",
    } <= set(manifests["evaluation_manifest"])
    versioning = contract["versioning_and_supersession"]
    assert versioning["candidate_version_scheme"] == "Semantic Versioning 2.0.0"
    assert {"silent_rebuild", "mutable_tag", "using_rejected_eval_v3"} <= set(
        versioning["prohibited"]
    )


def test_only_independent_external_custody_can_accept_and_handoff_public_bindings() -> None:
    contract = _load()
    transitions = contract["transition_rules"]

    submitted = transitions[0]
    accepted = transitions[1]
    assert submitted["from"] == "draft"
    assert "hidden_artifact_attachment" in submitted["forbids"]
    assert accepted["to"] == "accepted"
    assert "reviewer_recomputed_all_bindings" in accepted["requires"]
    assert "self_acceptance" in accepted["forbids"]
    registry = contract["registry_and_immutable_storage"]
    assert (
        registry["artifact_registry_owner"]
        == "independent_reviewer_or_designated_registry_custodian"
    )
    assert "immutable or write-once retention" in registry["storage_requirement"]
    assert registry["unknown_registry_state"] == "not_admissible"
    handoff = contract["verification_and_handoff"]
    assert {"hidden_seed", "expected_labels", "private_key", "gate_or_release_decision"} <= set(
        handoff["handoff_forbidden"]
    )
    assert "cannot itself attach hidden material" in handoff["downstream_boundary"]


def test_invalidation_and_preregistered_negative_cases_fail_closed() -> None:
    contract = _load()
    invalidation = contract["invalidation_and_rollback"]
    negatives = contract["preregistered_negative_tests"]

    assert {
        "artifact_digest_mismatch",
        "manifest_or_version_drift",
        "untrusted_signature_status",
    } <= set(invalidation["invalidation_triggers"])
    assert "never mutates or deletes" in invalidation["rollback_semantics"]
    assert {case["id"] for case in negatives} == {
        "CF-N1",
        "CF-N2",
        "CF-N3",
        "CF-N4",
        "CF-N5",
        "CF-N6",
        "CF-N7",
        "CF-N8",
    }
    rendered = " ".join(f"{case['case']} {case['expected']}" for case in negatives).lower()
    for required in (
        "tampered",
        "manifest",
        "version",
        "absent",
        "unsigned",
        "invalid",
        "registry",
        "hidden",
    ):
        assert required in rendered
    assert "not admissible" in contract["fail_closed"]


def test_external_blockers_have_evidence_approval_and_exact_unblockers() -> None:
    blockers = _load()["external_blockers"]

    assert {blocker["id"] for blocker in blockers} == {"CF-B1", "CF-B2"}
    for blocker in blockers:
        assert blocker["description"]
        assert blocker["cause"]
        assert blocker["owner"]
        assert blocker["required_evidence"]
        assert blocker["required_approval"]
        assert blocker["impact"]
        assert blocker["unblocker"]
        assert blocker["follow_on"]
