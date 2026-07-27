"""Cross-package traceability for preparation-only governance blocker artifacts."""

from pathlib import Path

ROOT = Path(__file__).parents[2]

PACKAGES = {
    "eval": [
        "docs/architecture/contracts/nb1-independent-evaluation-preparation-v1.json",
        "docs/architecture/contracts/nb1-independent-evaluation-artifact-manifests-v1.json",
        "docs/architecture/contracts/nb1-independent-evaluation-organization-v1.json",
        "docs/architecture/contracts/nb1-candidate-freeze-lifecycle-v1.json",
        "docs/governance/nb1-independent-evaluation-preparation-v1.md",
        "docs/governance/nb1-independent-evaluation-organization-v1.md",
        "docs/governance/nb1-candidate-freeze-lifecycle-v1.md",
        "docs/runbooks/nb1-independent-evaluation-preparation.md",
        "docs/runbooks/nb1-candidate-freeze-lifecycle.md",
        "docs/traceability/EVAL-01-independent-evaluation-preparation.md",
        "docs/traceability/EVAL-01-artifact-manifests.md",
        "docs/traceability/EVAL-01-independent-evaluation-organization.md",
        "docs/traceability/EVAL-01-candidate-freeze-lifecycle.md",
        "tests/architecture/test_nb1_independent_evaluation_preparation_contract.py",
        "tests/architecture/test_nb1_independent_evaluation_artifact_manifests_contract.py",
        "tests/architecture/test_nb1_independent_evaluation_organization_contract.py",
        "tests/architecture/test_nb1_candidate_freeze_lifecycle_contract.py",
    ],
    "kill_switch": [
        "docs/architecture/contracts/protected-control-kill-switch-v1.json",
        "docs/architecture/contracts/protected-control-kill-switch-test-plan-v1.json",
        "docs/architecture/protected-control-kill-switch-adr-018-revalidation-proposal-v1.md",
        "docs/architecture/protected-control-kill-switch-scope-resolution-decision-v1.md",
        "docs/governance/protected-control-kill-switch-v1.md",
        "docs/runbooks/protected-control-kill-switch.md",
        "docs/traceability/S1-02.5-protected-control-kill-switch.md",
        "tests/architecture/test_protected_control_kill_switch_contract.py",
        "tests/architecture/test_protected_control_kill_switch_test_plan_contract.py",
        "tests/architecture/test_protected_control_kill_switch_adr_018_revalidation_proposal.py",
    ],
    "privacy": [
        "docs/architecture/contracts/data-object-catalogue-intake-v1.json",
        "docs/architecture/contracts/future-deployment-data-inventory-v1.json",
        "docs/governance/data-object-catalogue-intake-v1.md",
        "docs/governance/future-deployment-data-inventory-v1.md",
        "docs/governance/future-deployment-subject-export-review-checklist-v1.md",
        "docs/runbooks/future-deployment-subject-export-readiness.md",
        "docs/traceability/S1-11.1-data-object-catalogue-intake.md",
        "docs/traceability/S1-14.9-future-deployment-export-readiness.md",
        "tests/architecture/test_data_object_catalogue_intake_contract.py",
        "tests/architecture/test_future_deployment_data_inventory_contract.py",
        "tests/architecture/test_future_deployment_subject_export_review_checklist.py",
    ],
}


def test_governance_blocker_package_artifacts_exist() -> None:
    for package, paths in PACKAGES.items():
        missing = [path for path in paths if not (ROOT / path).is_file()]
        assert not missing, f"{package} traceability paths missing: {missing}"


def test_traceability_and_index_documents_preserve_preparation_only_boundary() -> None:
    traceability = (ROOT / "docs/traceability/README.md").read_text(encoding="utf-8")
    contracts = (ROOT / "docs/architecture/contracts/README.md").read_text(encoding="utf-8")

    for marker in (
        "governance-blocker-integration-evidence.md",
        "EVAL-01-artifact-manifests.md",
        "EVAL-01-independent-evaluation-organization.md",
        "EVAL-01-candidate-freeze-lifecycle.md",
        "S1-02.5-protected-control-kill-switch.md",
        "S1-14.9-future-deployment-export-readiness.md",
    ):
        assert marker in traceability
    integration_evidence = (
        ROOT / "docs/traceability/governance-blocker-integration-evidence.md"
    ).read_text(encoding="utf-8")
    assert "preparation only" in integration_evidence
    assert "N/A for these" in integration_evidence
    for marker in (
        "nb1-independent-evaluation-artifact-manifests-v1.json",
        "nb1-independent-evaluation-organization-v1.json",
        "nb1-candidate-freeze-lifecycle-v1.json",
        "protected-control-kill-switch-test-plan-v1.json",
        "future-deployment-data-inventory-v1.json",
    ):
        assert marker in contracts
    for trace_path in (
        "docs/traceability/EVAL-01-independent-evaluation-preparation.md",
        "docs/traceability/S1-02.5-protected-control-kill-switch.md",
        "docs/traceability/S1-14.9-future-deployment-export-readiness.md",
    ):
        text = (ROOT / trace_path).read_text(encoding="utf-8").lower()
        assert "runtime" in text
        assert "release" in text
