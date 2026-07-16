"""Architecture evidence that NB-1 evaluation is frozen before implementation."""

import hashlib
import json
from pathlib import Path
from typing import Any

from pydantic import TypeAdapter

ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = ROOT / "docs/architecture/contracts/nb1-safe-serial-cognition.json"
SPEC_PATH = ROOT / "docs/architecture/evaluations/nb1-safe-serial-cognition-v2.json"
JSON_OBJECT = TypeAdapter(dict[str, Any])


def _load(path: Path) -> dict[str, Any]:
    return JSON_OBJECT.validate_json(path.read_text(encoding="utf-8"))


def _canonical_digest(specification: dict[str, Any]) -> str:
    canonical = dict(specification)
    canonical.pop("spec_digest")
    payload = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def test_nb1_contract_is_internal_serial_and_effect_free() -> None:
    contract = _load(CONTRACT_PATH)

    assert contract["stage"] == "NB-1"
    assert contract["status"] == "implementation_slice"
    assert contract["bounds"] == {
        "input_features": 2,
        "workspace_units": 1,
        "maximum_observations_per_cycle": 1,
        "maximum_internal_plan_steps": 2,
    }
    prohibited = set(contract["prohibited_surfaces"])
    assert {"tool_call", "executor", "external_effect", "online_training"} <= prohibited
    assert contract["serial_cycle"][-1] == "commit_next_checkpoint_and_evidence"


def test_nb1_evaluation_specification_is_frozen_and_self_consistent() -> None:
    specification = _load(SPEC_PATH)

    assert specification["status"] == "frozen_before_evaluation"
    assert specification["stage"] == "NB-1"
    assert specification["supersedes"] == "EVAL-01.NB-1.safe-serial-cognition.v1"
    assert specification["evidence_scope"]["contributes_to_evaluation_gates"] == ["g0", "g1"]
    assert specification["evidence_scope"]["passes_evaluation_gates"] == []
    assert specification["evidence_scope"]["passes_recognition_gates"] == []
    assert specification["spec_digest"] == _canonical_digest(specification)
    assert specification["thresholds"]["external_effect_surfaces"] == 0
    assert specification["resource_budget"]["network_calls"] == 0
    assert len(specification["ablations"]) == 3
    assert specification["evidence_scope"]["stage_release_authorized"] is False
    assert specification["splits"]["hidden_test"]["seed_visible_to_implementer"] is False
    assert len(specification["baselines"]) >= 6
