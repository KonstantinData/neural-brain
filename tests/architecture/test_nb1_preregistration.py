"""Architecture evidence that NB-1 evaluation is frozen before implementation."""

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = ROOT / "docs/architecture/contracts/nb1-safe-serial-cognition.json"
SPEC_PATH = ROOT / "docs/architecture/evaluations/nb1-safe-serial-cognition-v1.json"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


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
    assert specification["recognition_gates"] == ["G0", "G1"]
    assert specification["spec_digest"] == _canonical_digest(specification)
    assert specification["thresholds"]["external_effect_surface_count"] == 0
    assert specification["resource_budget"]["network_calls"] == 0
    assert len(specification["ablations"]) == 2
    assert specification["independent_evaluation"]["stage_release_authorized_by_this_slice"] is False
