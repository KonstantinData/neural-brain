"""Select and record the versioned Codex development-process model route."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "docs" / "governance" / "codex-model-routing-v1.json"
EVIDENCE_PATH = ROOT / ".local" / "codex-model-routing.jsonl"
POLICY_MODEL_SHA256 = "53ee19fbfe6ffc508a575e855e6b65be498df1bb4f8b4e1f1125187f3ea4779f"
TASK_ID_PATTERN = re.compile(r"[A-Z][A-Z0-9]{0,15}(?:-[A-Z0-9]{1,16}){1,5}")

ReasoningDepth = Literal["low", "medium", "high", "extra_high"]
BudgetUnit = Literal["tokens", "seconds", "cost_units"]
TaskPhase = Literal["safe_task_start", "in_progress"]
ApplicationStatus = Literal[
    "external_runtime_application_required",
    "deferred_to_next_safe_task_start",
    "blocked_attempt_limit",
]
TriggerCode = Literal[
    "security_contract",
    "major_architecture_decision",
    "claude_alignment_conflict",
    "repeated_unsuccessful_attempts",
    "high_context_complexity",
]
RationaleCode = Literal[
    "routine_bounded_task",
    "security_contract_change",
    "architecture_decision_required",
    "claude_alignment_conflict",
    "standard_attempts_exhausted",
    "context_capacity_exceeded",
]

EXPLICIT_TRIGGER_CODES: tuple[TriggerCode, ...] = (
    "security_contract",
    "major_architecture_decision",
    "claude_alignment_conflict",
    "high_context_complexity",
)
DEFAULT_TRIGGER = "default_standard"
RATIONALE_CODE_BY_TRIGGER: dict[TriggerCode, RationaleCode] = {
    "security_contract": "security_contract_change",
    "major_architecture_decision": "architecture_decision_required",
    "claude_alignment_conflict": "claude_alignment_conflict",
    "repeated_unsuccessful_attempts": "standard_attempts_exhausted",
    "high_context_complexity": "context_capacity_exceeded",
}
RATIONALE_CODES: tuple[RationaleCode, ...] = (
    "routine_bounded_task",
    "security_contract_change",
    "architecture_decision_required",
    "claude_alignment_conflict",
    "standard_attempts_exhausted",
    "context_capacity_exceeded",
)


class ImmutableRecord(BaseModel):
    """Reject unknown fields and prevent mutation after validation."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class ModelRoute(ImmutableRecord):
    """One externally applicable model and reasoning-depth pair."""

    model: str = Field(min_length=1, max_length=80)
    reasoning_depth: ReasoningDepth


class EscalationTrigger(ImmutableRecord):
    """One narrowly authorized Sol escalation condition."""

    code: TriggerCode
    rationale: str = Field(min_length=1, max_length=240)


class RoutingPolicy(ImmutableRecord):
    """Versioned source for deterministic Codex process selection."""

    policy_id: Literal["neural-brain-codex-development-model-routing"]
    version: Literal[1]
    record_schema_version: Literal[1]
    default_route: ModelRoute
    escalation_route: ModelRoute
    failed_attempts_threshold: int = Field(ge=2, le=10)
    escalation_triggers: tuple[EscalationTrigger, ...] = Field(min_length=5, max_length=5)


class RoutingSafetyEvidence(ImmutableRecord):
    """Non-negotiable non-authority boundary of a routing decision."""

    advisory_process_evidence_only: Literal[True] = True
    model_application_is_external: Literal[True] = True
    can_change_authenticated_scope: Literal[False] = False
    can_cross_tenant_or_area_boundary: Literal[False] = False
    can_create_authority_or_approval: Literal[False] = False
    can_bypass_memory_or_human_gate: Literal[False] = False
    can_mutate_protected_product_state: Literal[False] = False


class RoutingDecision(ImmutableRecord):
    """Append-only step evidence emitted by the process router."""

    record_type: Literal["codex_process_model_routing_decision"]
    record_schema_version: Literal[1]
    policy_id: str
    policy_version: int
    task_id: str
    recorded_at: datetime
    selected_model: str
    reasoning_depth: ReasoningDepth
    trigger_codes: tuple[str, ...]
    rationale_code: RationaleCode
    rationale: str
    budget_limit: int
    budget_unit: BudgetUnit
    attempt_limit: int
    failed_attempts: int
    task_phase: TaskPhase
    runtime_switch_supported: bool
    application_status: ApplicationStatus
    next_safe_task_start_required: bool
    safety: RoutingSafetyEvidence


def _validate_policy(policy: RoutingPolicy) -> None:
    """Revalidate the complete immutable v1 selection contract at each use."""

    model_digest = hashlib.sha256(policy.model_dump_json().encode("utf-8")).hexdigest()
    if model_digest != POLICY_MODEL_SHA256:
        raise ValueError("The model-routing policy does not match the canonical v1 digest")
    trigger_codes = [trigger.code for trigger in policy.escalation_triggers]
    expected = [
        "security_contract",
        "major_architecture_decision",
        "claude_alignment_conflict",
        "repeated_unsuccessful_attempts",
        "high_context_complexity",
    ]
    if trigger_codes != expected or len(trigger_codes) != len(set(trigger_codes)):
        raise ValueError("The model-routing escalation trigger set is not the approved v1 set")
    if policy.default_route != ModelRoute(model="gpt-5.6-terra", reasoning_depth="medium"):
        raise ValueError("The model-routing default is not GPT-5.6 Terra medium")
    if policy.escalation_route != ModelRoute(model="gpt-5.6-sol", reasoning_depth="high"):
        raise ValueError("The model-routing escalation is not GPT-5.6 Sol high")


def load_policy(path: Path = POLICY_PATH) -> RoutingPolicy:
    """Load the fixed policy and reject missing, duplicate, or changed trigger sets."""

    policy = RoutingPolicy.model_validate_json(path.read_text(encoding="utf-8"))
    _validate_policy(policy)
    return policy


def select_route(
    policy: RoutingPolicy,
    *,
    task_id: str,
    explicit_triggers: Sequence[str],
    rationale_code: RationaleCode,
    budget_limit: int,
    budget_unit: BudgetUnit,
    attempt_limit: int,
    failed_attempts: int,
    task_phase: TaskPhase,
    runtime_switch_supported: bool,
    recorded_at: datetime | None = None,
) -> RoutingDecision:
    """Select a route without applying a model or changing protected authority."""

    _validate_policy(policy)
    if TASK_ID_PATTERN.fullmatch(task_id) is None:
        raise ValueError("task_id must be a bounded non-secret process identifier")
    if budget_limit <= 0:
        raise ValueError("budget_limit must be positive")
    if attempt_limit <= 0:
        raise ValueError("attempt_limit must be positive")
    if failed_attempts < 0:
        raise ValueError("failed_attempts cannot be negative")
    approved_codes = [trigger.code for trigger in policy.escalation_triggers]
    unknown = sorted(set(explicit_triggers) - set(EXPLICIT_TRIGGER_CODES))
    if unknown:
        raise ValueError("An unapproved model-routing trigger was supplied")
    selected_codes = set(explicit_triggers)
    if failed_attempts >= policy.failed_attempts_threshold:
        selected_codes.add("repeated_unsuccessful_attempts")
    ordered_codes = [code for code in approved_codes if code in selected_codes]
    if ordered_codes:
        allowed_rationale_codes = {RATIONALE_CODE_BY_TRIGGER[code] for code in ordered_codes}
        if rationale_code not in allowed_rationale_codes:
            raise ValueError("rationale_code does not match an active Sol escalation trigger")
    elif rationale_code != "routine_bounded_task":
        raise ValueError("The standard route requires the routine_bounded_task rationale_code")
    selected_route = policy.escalation_route if ordered_codes else policy.default_route
    trigger_codes = tuple(ordered_codes) if ordered_codes else (DEFAULT_TRIGGER,)
    rationale_by_code = {trigger.code: trigger.rationale for trigger in policy.escalation_triggers}
    rationale = (
        "No Sol escalation trigger is present; use the standard Terra route."
        if not ordered_codes
        else " ".join(rationale_by_code[code] for code in ordered_codes)
    )
    if failed_attempts >= attempt_limit:
        application_status: ApplicationStatus = "blocked_attempt_limit"
    elif task_phase == "in_progress" and not runtime_switch_supported:
        application_status = "deferred_to_next_safe_task_start"
    else:
        application_status = "external_runtime_application_required"
    return RoutingDecision(
        record_type="codex_process_model_routing_decision",
        record_schema_version=policy.record_schema_version,
        policy_id=policy.policy_id,
        policy_version=policy.version,
        task_id=task_id,
        recorded_at=recorded_at or datetime.now(UTC),
        selected_model=selected_route.model,
        reasoning_depth=selected_route.reasoning_depth,
        trigger_codes=trigger_codes,
        rationale_code=rationale_code,
        rationale=rationale,
        budget_limit=budget_limit,
        budget_unit=budget_unit,
        attempt_limit=attempt_limit,
        failed_attempts=failed_attempts,
        task_phase=task_phase,
        runtime_switch_supported=runtime_switch_supported,
        application_status=application_status,
        next_safe_task_start_required=(application_status == "deferred_to_next_safe_task_start"),
        safety=RoutingSafetyEvidence(),
    )


def append_decision(path: Path, decision: RoutingDecision) -> None:
    """Append one complete JSON record without reading or rewriting prior evidence."""

    if path.suffix != ".jsonl":
        raise ValueError("Routing evidence must use an append-only .jsonl path")
    if path.is_symlink():
        raise ValueError("Routing evidence cannot target a symbolic link")
    try:
        validated_decision = RoutingDecision.model_validate_json(decision.model_dump_json())
    except ValidationError as error:
        raise ValueError("Routing decision failed canonical schema validation") from error
    explicit_triggers = tuple(
        code
        for code in validated_decision.trigger_codes
        if code not in {DEFAULT_TRIGGER, "repeated_unsuccessful_attempts"}
    )
    expected_decision = select_route(
        load_policy(),
        task_id=validated_decision.task_id,
        explicit_triggers=explicit_triggers,
        rationale_code=validated_decision.rationale_code,
        budget_limit=validated_decision.budget_limit,
        budget_unit=validated_decision.budget_unit,
        attempt_limit=validated_decision.attempt_limit,
        failed_attempts=validated_decision.failed_attempts,
        task_phase=validated_decision.task_phase,
        runtime_switch_supported=validated_decision.runtime_switch_supported,
        recorded_at=validated_decision.recorded_at,
    )
    if validated_decision != expected_decision:
        raise ValueError("Routing decision failed canonical semantic validation")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as evidence_file:
        evidence_file.write(validated_decision.model_dump_json() + "\n")
    path.chmod(0o600)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--trigger", action="append", choices=EXPLICIT_TRIGGER_CODES, default=[])
    parser.add_argument("--rationale-code", choices=RATIONALE_CODES, required=True)
    parser.add_argument("--budget-limit", required=True, type=int)
    parser.add_argument(
        "--budget-unit", choices=("tokens", "seconds", "cost_units"), default="tokens"
    )
    parser.add_argument("--attempt-limit", required=True, type=int)
    parser.add_argument("--failed-attempts", type=int, default=0)
    parser.add_argument("--task-phase", choices=("safe_task_start", "in_progress"), required=True)
    parser.add_argument("--runtime-switch-supported", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Select, append, and print one non-authorizing process-routing record."""

    arguments = _parser().parse_args(argv)
    try:
        decision = select_route(
            load_policy(),
            task_id=arguments.task_id,
            explicit_triggers=arguments.trigger,
            rationale_code=arguments.rationale_code,
            budget_limit=arguments.budget_limit,
            budget_unit=arguments.budget_unit,
            attempt_limit=arguments.attempt_limit,
            failed_attempts=arguments.failed_attempts,
            task_phase=arguments.task_phase,
            runtime_switch_supported=arguments.runtime_switch_supported,
        )
        append_decision(EVIDENCE_PATH, decision)
    except (OSError, ValueError, ValidationError) as error:
        print(f"model routing failed: {error}", file=sys.stderr)
        return 1
    print(json.dumps(decision.model_dump(mode="json"), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
