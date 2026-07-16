"""Build deterministic non-promoted NB-1 offline training evidence."""

import argparse
import hashlib
import json
import platform
import sys
from pathlib import Path
from typing import Final

ROOT: Final = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT: Final = (
    ROOT
    / "docs"
    / "architecture"
    / "evaluations"
    / "artifacts"
    / "nb1-v1-offline-training-bundle.json"
)


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_text_file(path: Path) -> str:
    """Hash repository text independently of checkout line-ending policy."""
    canonical_text = path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
    return _sha256_bytes(canonical_text.encode())


def _canonical_bytes(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode()


def _canonical_spec_digest(path: Path) -> str:
    value: object = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("evaluation specification must be a JSON object")
    canonical = dict(value)
    canonical.pop("spec_digest", None)
    return _sha256_bytes(json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode())


def build_training_evidence(root: Path) -> dict[str, object]:
    """Build a deterministic evidence document from authoritative repository inputs."""
    source_root = root.resolve() / "src"
    if str(source_root) not in sys.path:
        sys.path.insert(0, str(source_root))
    from neural_brain.cognition.training import (
        SPEC_DIGEST,
        generate_training_dataset,
        train_offline,
    )

    root = root.resolve()
    specification_path = (
        root / "docs" / "architecture" / "evaluations" / "nb1-safe-serial-cognition-v3.json"
    )
    contract_path = root / "docs" / "architecture" / "contracts" / "nb1-safe-serial-cognition.json"
    training_path = root / "src" / "neural_brain" / "cognition" / "training.py"
    calculated_spec_digest = _canonical_spec_digest(specification_path)
    if calculated_spec_digest != SPEC_DIGEST:
        raise ValueError("frozen EVAL-01 v3 specification digest mismatch")
    environment = {
        "implementation": platform.python_implementation(),
        "python_version": platform.python_version(),
        "uv_lock_sha256": _sha256_text_file(root / "uv.lock"),
    }
    dataset = generate_training_dataset()
    bundle = train_offline(
        dataset=dataset,
        training_code_digest=_sha256_text_file(training_path),
        contract_digest=_sha256_text_file(contract_path),
        environment_digest=_sha256_bytes(_canonical_bytes(environment).rstrip(b"\n")),
    )
    return {
        "document_type": "nb1_offline_training_evidence",
        "format_version": 1,
        "dataset_manifest": {
            "artifact_digest": dataset.artifact_digest,
            "generator_contract": dataset.generator_contract,
            "role": dataset.role,
            "seed": dataset.seed,
            "sequence_count": len(dataset.sequences),
        },
        "environment": environment,
        "bundle": bundle.model_dump(mode="json"),
        "claim_boundary": {
            "active_model_promoted": False,
            "evaluation_gates_passed": [],
            "hidden_data_included": False,
            "recognition_gates_passed": [],
            "stage_release_authorized": False,
        },
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Write or verify the deterministic checked-in evidence artifact."""
    arguments = _parser().parse_args(argv)
    try:
        payload = _canonical_bytes(build_training_evidence(arguments.root))
        if arguments.check:
            if not arguments.output.is_file() or arguments.output.read_bytes() != payload:
                raise ValueError("checked-in NB-1 training evidence is absent or stale")
            print(f"NB-1 training evidence verified: {arguments.output}")
            return 0
        arguments.output.parent.mkdir(parents=True, exist_ok=True)
        arguments.output.write_bytes(payload)
        print(f"NB-1 training evidence written: {arguments.output}")
        print(f"NB-1 training evidence sha256: {_sha256_bytes(payload)}")
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"NB-1 offline training failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
