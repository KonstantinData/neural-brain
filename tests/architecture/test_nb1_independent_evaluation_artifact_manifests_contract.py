"""Fail-closed schema evidence for future EVAL-01 artifact manifests only."""

import json
from hashlib import sha256
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = (
    ROOT / "docs/architecture/contracts/nb1-independent-evaluation-artifact-manifests-v1.json"
)
PREPARATION_CONTRACT = (
    ROOT / "docs/architecture/contracts/nb1-independent-evaluation-preparation-v1.json"
)
PROPOSAL = ROOT / "docs/architecture/nb1-independent-evaluation-adr-018-revalidation-proposal-v1.md"
TRACEABILITY = ROOT / "docs/traceability/EVAL-01-artifact-manifests.md"


def _load() -> dict[str, Any]:
    loaded = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _load_preparation() -> dict[str, Any]:
    loaded = json.loads(PREPARATION_CONTRACT.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def test_v4_only_non_instantiating_claim_boundary_and_receipt_fields() -> None:
    contract = _load()

    assert contract["status"] == "preparation_only_non_instantiating"
    assert contract["decision"] == "ADR-018"
    assert contract["evaluation_spec"] == {
        "id": "EVAL-01.NB-1.safe-serial-cognition.v4",
        "required_status": "frozen_before_candidate_training_and_hidden_attachment",
        "rejected_historical_spec": "EVAL-01.NB-1.safe-serial-cognition.v3",
    }
    assert all(value is False for value in contract["claim_boundary"].values())
    receipt = contract["candidate_freeze_receipt_schema"]
    assert receipt["receipt_status"] == "template_only_reviewer_acceptance_required"
    assert {
        "source_commit",
        "candidate_artifact_reference",
        "model_manifest_reference",
        "evaluation_manifest_reference",
        "reviewer_recomputation_record_reference",
        "receipt_signature_reference",
    } <= set(receipt["required_fields"])


def test_manifest_schemas_bind_public_and_hidden_custody_without_disclosure() -> None:
    contract = _load()
    model = contract["model_manifest_schema"]
    evaluation = contract["evaluation_manifest_schema"]
    dataset = contract["dataset_and_generator_manifest_schema"]

    assert "parameter_artifact_reference" in model["required_fields"]
    assert {"hidden_dataset_reference", "hidden_seed", "expected_label"} <= set(
        model["prohibitions"]
    )
    assert {"candidate_freeze_receipt_reference", "split_definition_reference"} <= set(
        evaluation["required_fields"]
    )
    assert {"hidden_seed", "hidden_labels", "gate_pass"} <= set(evaluation["prohibitions"])
    assert {"generator_identifier_and_version", "split_definition_reference"} <= set(
        dataset["public_dataset_required_fields"]
    )
    assert {"seed_value", "raw_examples", "labels"} <= set(
        dataset["hidden_dataset_forbidden_fields"]
    )
    assert dataset["hidden_dataset_custodian"] == "independent_evaluator_only"
    assert dataset["separate_hidden_dataset_provider"] == "prohibited_pending_accepted_revalidation"
    assert "independent evaluator" in dataset["seed_custody_rule"]
    assert "separate hidden-dataset provider" in dataset["seed_custody_rule"]


def test_canonical_digest_signature_and_registry_rules_fail_closed() -> None:
    contract = _load()
    canonical = contract["canonicalization"]
    reference = contract["artifact_reference_schema"]
    registry = contract["registry_and_attestation_schema"]

    assert canonical["profile_id"] == "nb1-eval-canonical-json-v1"
    assert canonical["serialization"] == "nb1-eval-canonical-json-v1 only"
    assert canonical["digest_algorithm"] == "SHA-256"
    assert canonical["signature_algorithm"] == "Ed25519 detached signature"
    assert canonical["unknown_or_noncanonical_encoding"] == "reject"
    assert canonical["byte_profile"] == {
        "root_value": "object only",
        "encoding": "UTF-8 without BOM",
        "unicode_normalization": "NFC before serialization",
        "object_member_order": "ascending Unicode scalar value order of normalized member names",
        "whitespace": "no whitespace outside strings",
        "string_escaping": "escape quotation-mark and reverse-solidus as short escapes; escape U+0000 through U+001F as lowercase six-character \\u00xx escapes; emit every other normalized Unicode scalar as UTF-8 without optional escapes",
        "number_encoding": "only non-negative integers; encode zero as 0 and every other integer as shortest base-10 digits without leading zero, sign, decimal point, or exponent",
        "literals": "true, false, and null in lowercase ASCII",
        "trailing_bytes": "forbidden",
    }
    rules = canonical["artifact_kind_byte_rules"]
    assert set(rules) == {
        "canonical_json_object",
        "utf8_text",
        "binary",
        "deterministic_bundle_manifest",
    }
    assert "root JSON object" in rules["canonical_json_object"]["rule"]
    assert "do not normalize Unicode, line endings" in rules["utf8_text"]["rule"]
    assert "no decoding, encoding" in rules["binary"]["rule"]
    assert "Symlinks" in rules["deterministic_bundle_manifest"]["rule"]
    assert canonical["undefined_artifact_kind_or_transformation"] == "reject"
    assert reference["digest_format"] == "sha256:<64 lowercase hexadecimal characters>"
    assert {"private_key", "credential", "evaluation_score", "gate_pass"} <= set(
        reference["forbidden_fields"]
    )
    assert registry["reviewer_controlled_registry_required"] is True
    assert "ed25519_public_key_and_revocation_status" in registry["registry_bindings"]
    assert "cannot establish independence" in registry["self_attestation_limit"]


def test_artifact_kind_rules_cross_contract_bindings_are_consistent() -> None:
    contract = _load()
    preparation = _load_preparation()
    canonical = contract["canonicalization"]
    reference = contract["artifact_reference_schema"]

    assert preparation["candidate_freeze"]["hash_algorithm"] == canonical["digest_algorithm"]
    assert reference["artifact_kind_required"] is True
    assert set(reference["allowed_artifact_kinds"]) == set(canonical["artifact_kind_byte_rules"])
    vectors = canonical["deterministic_test_vector_descriptors"]
    assert {vector["id"] for vector in vectors} == {
        "NB1-EVAL-CJ-001",
        "NB1-EVAL-CJ-002",
        "NB1-EVAL-CJ-003",
        "NB1-EVAL-CJ-004",
    }
    assert {vector["artifact_kind"] for vector in vectors} == set(
        reference["allowed_artifact_kinds"]
    )


def test_literal_non_sensitive_vectors_recompute_sha256_for_all_artifact_kinds() -> None:
    vectors = {
        vector["id"]: vector
        for vector in _load()["canonicalization"]["deterministic_test_vector_descriptors"]
    }

    json_vector = vectors["NB1-EVAL-CJ-001"]
    json_bytes = bytes.fromhex(json_vector["literal_canonical_utf8_hex"])
    assert json_bytes.decode("utf-8") == '{"alpha":"café","control":"\\u000a","z":7}'
    assert sha256(json_bytes).hexdigest() == json_vector["expected_sha256"]

    text_vector = vectors["NB1-EVAL-CJ-002"]
    text_bytes = bytes.fromhex(text_vector["literal_input_hex"])
    assert text_bytes.decode("utf-8") == "café\n"
    assert sha256(text_bytes).hexdigest() == text_vector["expected_sha256"]

    binary_vector = vectors["NB1-EVAL-CJ-003"]
    binary_bytes = bytes.fromhex(binary_vector["literal_input_hex"])
    assert binary_bytes == b"\x00\x01\xff\x10A"
    assert sha256(binary_bytes).hexdigest() == binary_vector["expected_sha256"]

    bundle_vector = vectors["NB1-EVAL-CJ-004"]
    members = bundle_vector["literal_member_inputs"]
    assert [member["normalized_relative_path"] for member in members] == [
        "alpha-café.txt",
        "nested/blob.bin",
    ]
    for member in members:
        assert (
            sha256(bytes.fromhex(member["literal_input_hex"])).hexdigest()
            == member["expected_sha256"]
        )
    bundle_bytes = bytes.fromhex(bundle_vector["literal_canonical_utf8_hex"])
    assert "alpha-café.txt" in bundle_bytes.decode("utf-8")
    assert sha256(bundle_bytes).hexdigest() == bundle_vector["expected_sha256"]


def test_chain_of_custody_and_attestation_requirements_are_complete() -> None:
    contract = _load()
    custody = contract["chain_of_custody_schema"]
    attestation = contract["registry_and_attestation_schema"]["attestation_required_fields"]

    assert {"previous_event_digest_or_genesis", "event_digest", "artifact_reference"} <= set(
        custody["required_event_fields"]
    )
    assert {"verify_digest", "revoke_or_quarantine", "destroy_or_retire"} <= set(
        custody["required_actions"]
    )
    assert "inadmissible" in custody["integrity_rule"]
    assert {"conflict_disclosure", "independence_statement", "detached_signature_reference"} <= set(
        attestation
    )


def test_version_drift_unsigned_and_hidden_repository_states_are_denied() -> None:
    contract = _load()
    failures = contract["fail_closed"]
    receipt = contract["candidate_freeze_receipt_schema"]

    assert "version_drift_or_post_freeze_change" in failures
    assert failures["unsigned_or_untrusted_signature"] == "reject_evidence"
    assert (
        failures["digest_or_canonicalization_mismatch"] == "invalidate_freeze_and_reject_evidence"
    )
    assert failures["hidden_material_in_repository_or_implementer_bundle"] == (
        "stop_and_escalate_contamination_incident"
    )
    assert failures["attempted_runtime_release_or_recognition_claim"] == "prohibited"
    assert "post_freeze_training_or_selection" in receipt["invalidation_events"]
    assert "not runtime authorization" in PROPOSAL.read_text(encoding="utf-8")
    assert "No candidate, dataset" in TRACEABILITY.read_text(encoding="utf-8")
