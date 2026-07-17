"""Build an NB-1 freeze receipt; reject export of historical invalid candidates."""

import argparse
import hashlib
import json
import subprocess
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from neural_brain.cognition.hidden_contract import CandidateEvaluationBundle

ROOT: Final = Path(__file__).resolve().parents[1]
TRAINING_ARTIFACT: Final = (
    ROOT
    / "docs"
    / "architecture"
    / "evaluations"
    / "artifacts"
    / "nb1-v1-offline-training-bundle.json"
)
CANDIDATE_EXPORT_PATH: Final = "tools/export_nb1_evaluation_candidate.py"
REJECTED_EVALUATION_SPEC_DIGESTS: Final = frozenset(
    {"3ac6d895d3f33b5d63c462471ca335d6d538cc379ae8eb3ad0611c81271b3fc8"}
)


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode()


def _digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _text_digest(path: Path) -> str:
    canonical = path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
    return _digest_bytes(canonical.encode())


def candidate_code_digest(root: Path) -> str:
    """Bind the complete executable package and candidate-export implementation."""
    package_root = root.resolve() / "src" / "neural_brain"
    package_paths = tuple(sorted(package_root.rglob("*.py")))
    export_path = root.resolve() / CANDIDATE_EXPORT_PATH
    if not package_paths:
        raise ValueError("candidate package contains no Python source files")
    if not export_path.is_file():
        raise ValueError("candidate export implementation is missing")
    executable_paths = (*package_paths, export_path)
    return _digest_bytes(
        _canonical_bytes(
            {
                path.relative_to(root.resolve()).as_posix(): _text_digest(path)
                for path in executable_paths
            }
        )
    )


def build_candidate_bundle(
    *,
    root: Path,
    source_commit: str,
    source_tree_digest: str,
    frozen_at: datetime,
) -> CandidateEvaluationBundle:
    """Build a self-verifying bundle from checked-in training evidence."""
    source_root = root.resolve() / "src"
    if str(source_root) not in sys.path:
        sys.path.insert(0, str(source_root))
    from neural_brain.cognition.adapters import model_manifest_digest
    from neural_brain.cognition.hidden_contract import (
        CandidateEvaluationBundle,
        candidate_evaluation_bundle_digest,
    )
    from neural_brain.cognition.training import (
        OfflineTrainingBundle,
        generate_training_dataset,
    )

    root = root.resolve()
    document: object = json.loads(
        (root / TRAINING_ARTIFACT.relative_to(ROOT)).read_text(encoding="utf-8")
    )
    if not isinstance(document, dict) or not isinstance(document.get("bundle"), dict):
        raise ValueError("checked-in training evidence is invalid")
    training_bundle = OfflineTrainingBundle.model_validate_json(
        json.dumps(document["bundle"], separators=(",", ":"))
    )
    manifest = training_bundle.model_manifest
    parameters = training_bundle.parameter_artifact.parameters
    manifest_digest = model_manifest_digest(manifest)
    majority_counts = Counter(
        sequence.expected_label for sequence in generate_training_dataset().sequences
    )
    fixed_majority_label = min(
        majority_counts,
        key=lambda label: (-majority_counts[label], label),
    )
    code_digest = candidate_code_digest(root)
    contract_digest = _text_digest(
        root / "docs" / "architecture" / "contracts" / "nb1-hidden-evaluation.json"
    )
    lock_digest = _text_digest(root / "uv.lock")
    artifact_digest = candidate_evaluation_bundle_digest(
        model_manifest=manifest,
        model_manifest_digest_value=manifest_digest,
        parameters=parameters,
        source_commit=source_commit,
        source_tree_digest=source_tree_digest,
        training_code_digest=manifest.code_digest,
        candidate_code_digest=code_digest,
        evaluation_contract_digest=contract_digest,
        dependency_lock_digest=lock_digest,
        fixed_train_majority_label=fixed_majority_label,
        frozen_at=frozen_at,
    )
    return CandidateEvaluationBundle(
        artifact_digest=artifact_digest,
        source_commit=source_commit,
        source_tree_digest=source_tree_digest,
        training_code_digest=manifest.code_digest,
        candidate_code_digest=code_digest,
        evaluation_contract_digest=contract_digest,
        dependency_lock_digest=lock_digest,
        fixed_train_majority_label=fixed_majority_label,
        frozen_at=frozen_at,
        model_manifest=manifest,
        model_manifest_digest=manifest_digest,
        parameters=parameters,
    )


def _git(root: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ("git", *arguments),
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--frozen-at", type=datetime.fromisoformat, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    """Export only from a clean committed tree and never attach hidden data."""
    arguments = _parser().parse_args(argv)
    root = arguments.root.resolve()
    try:
        if _git(root, "status", "--porcelain"):
            raise ValueError("candidate export requires a clean committed worktree")
        source_commit = _git(root, "rev-parse", "HEAD")
        source_tree = _git(root, "ls-tree", "-r", "--full-tree", source_commit)
        source_tree_digest = _digest_bytes(source_tree.encode())
        bundle = build_candidate_bundle(
            root=root,
            source_commit=source_commit,
            source_tree_digest=source_tree_digest,
            frozen_at=arguments.frozen_at,
        )
        if bundle.model_manifest.evaluation_spec_digest in REJECTED_EVALUATION_SPEC_DIGESTS:
            raise ValueError(
                "candidate uses rejected EVAL-01 v3; freeze a replacement specification and "
                "versioned training artifact before export"
            )
        payload = (
            json.dumps(
                bundle.model_dump(mode="json"),
                ensure_ascii=True,
                indent=2,
                sort_keys=True,
            )
            + "\n"
        )
        arguments.output.parent.mkdir(parents=True, exist_ok=True)
        arguments.output.write_text(payload, encoding="utf-8", newline="\n")
        print(f"NB-1 candidate bundle written: {arguments.output}")
        print(f"NB-1 candidate bundle digest: {bundle.artifact_digest}")
        print("Claim boundary: candidate freeze only; no hidden run or gate pass")
        return 0
    except (OSError, ValueError, subprocess.CalledProcessError, json.JSONDecodeError) as error:
        print(f"NB-1 candidate export failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
