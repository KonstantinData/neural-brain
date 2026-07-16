"""Live PostgreSQL evidence for effect-free NB-1 checkpoint recovery."""

# ruff: noqa: SIM117

from datetime import UTC, datetime

import psycopg
import pytest
from psycopg.types.json import Jsonb

from neural_brain.cognition.errors import (
    CognitiveCheckpointUnavailableError,
    CognitiveRuntimeError,
    StaleCognitiveCheckpointError,
)
from neural_brain.cognition.models import (
    ActiveCognitiveModelEvidence,
    AttentionDecision,
    CognitiveTransitionEnvelope,
    InternalGoalProposal,
    InternalPlanProposal,
    MetacognitiveAssessment,
    RecordedObservation,
)
from neural_brain.memory.models import RuntimeContext
from neural_brain.postgres import PostgresCognitiveRepository

_DIGEST = "a" * 64
_PROVENANCE = {"model-v1": _DIGEST}


def _repository(database_dsn: str) -> PostgresCognitiveRepository:
    return PostgresCognitiveRepository(
        database_dsn,
        training_provenance_by_model=_PROVENANCE,
    )


def _context(*, area_b: bool = False) -> RuntimeContext:
    if area_b:
        return RuntimeContext(
            actor_id="principal-b",
            tenant_id="tenant-a",
            area_id="area-b",
            project_id="project-b",
            session_id="session-b",
        )
    return RuntimeContext(
        actor_id="principal-a",
        tenant_id="tenant-a",
        area_id="area-a",
        project_id="project-a",
        session_id="session-a",
    )


def _observation(suffix: str) -> RecordedObservation:
    return RecordedObservation(
        observation_id=f"observation-{suffix}",
        source_kind="recorded",
        provenance_ref=f"fixture-{suffix}",
        features=(0.25, -0.5),
        occurred_at=datetime(2026, 7, 16, 18, 0, tzinfo=UTC),
    )


def _transition(
    suffix: str,
    *,
    previous_version: int = 0,
    hidden_state: float = 0.125,
) -> CognitiveTransitionEnvelope:
    return CognitiveTransitionEnvelope(
        cycle_id=f"cycle-{suffix}",
        observation_id=f"observation-{suffix}",
        previous_checkpoint_version=previous_version,
        next_checkpoint_version=previous_version + 1,
        model_version="model-v1",
        hidden_state=(hidden_state,),
        attention=AttentionDecision(distribution=(0.75, 0.25), selected_feature_index=0),
        goal_proposal=InternalGoalProposal(
            goal_ref=f"goal-{suffix}",
            objective="maintain_positive_context",
            confidence=0.75,
        ),
        plan_proposal=InternalPlanProposal(plan_ref=f"plan-{suffix}", steps=("maintain_focus",)),
        metacognition=MetacognitiveAssessment(
            decision="continue",
            activation_ambiguity=0.25,
            reason="sufficient_context",
        ),
        active_model=ActiveCognitiveModelEvidence(
            manifest_digest=_DIGEST,
            parameter_digest=_DIGEST,
            training_artifact_digest=_DIGEST,
            code_digest=_DIGEST,
            contract_digest=_DIGEST,
            evaluation_spec_digest=_DIGEST,
        ),
    )


def _commit(
    repository: PostgresCognitiveRepository,
    suffix: str,
    *,
    previous_version: int = 0,
    hidden_state: float = 0.125,
) -> None:
    repository.commit_checkpoint(
        context=_context(),
        cycle_id=f"cycle-{suffix}",
        expected_version=previous_version,
        transition=_transition(
            suffix,
            previous_version=previous_version,
            hidden_state=hidden_state,
        ),
        observation=_observation(suffix),
    )


def _counts(database_dsn: str) -> tuple[int, int, int, int]:
    with psycopg.connect(database_dsn, autocommit=True) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT "
                "(SELECT count(*) FROM memory_core.checkpoints), "
                "(SELECT count(*) FROM memory_core.cognitive_transition_evidence), "
                "(SELECT count(*) FROM memory_core.transition_receipts), "
                "(SELECT count(*) FROM memory_audit.events)"
            )
            row = cursor.fetchone()
    assert row is not None
    return row


def test_trusted_training_provenance_must_match_active_model_before_connect() -> None:
    """Trusted runtime configuration cannot contradict committed model evidence."""
    repository = PostgresCognitiveRepository(
        "postgresql://connection-must-not-be-attempted",
        training_provenance_by_model={"model-v1": "b" * 64},
    )

    with pytest.raises(CognitiveRuntimeError, match="trusted training provenance"):
        repository.commit_checkpoint(
            context=_context(),
            cycle_id="cycle-provenance",
            expected_version=0,
            transition=_transition("provenance"),
            observation=_observation("provenance"),
        )


def test_commit_replay_restart_and_recovery_are_exact(database_dsn: str) -> None:
    """An exact replay is idempotent and a new adapter recovers the durable state."""
    repository = _repository(database_dsn)
    _commit(repository, "recover")
    first = repository.load_checkpoint(context=_context(), checkpoint_id="nb1:cycle-recover")

    _commit(repository, "recover")
    restarted = _repository(database_dsn)
    recovered = restarted.load_checkpoint(context=_context(), checkpoint_id="nb1:cycle-recover")

    assert recovered == first
    assert recovered.version == 1
    assert recovered.hidden_state == (0.125,)
    assert _counts(database_dsn) == (1, 1, 1, 2)


def test_changed_replay_and_stale_compare_and_set_are_denied(database_dsn: str) -> None:
    """The cycle receipt rejects changed input and the session slot enforces CAS."""
    repository = _repository(database_dsn)
    _commit(repository, "original")

    with pytest.raises(CognitiveRuntimeError):
        _commit(repository, "original", hidden_state=0.75)
    with pytest.raises(StaleCognitiveCheckpointError):
        _commit(repository, "stale")

    assert _counts(database_dsn) == (1, 1, 1, 2)


def test_missing_and_cross_scope_checkpoint_reads_fail_closed(database_dsn: str) -> None:
    """Missing and foreign-scope identifiers are indistinguishable to callers."""
    repository = _repository(database_dsn)
    _commit(repository, "scoped")

    with pytest.raises(CognitiveCheckpointUnavailableError):
        repository.load_checkpoint(context=_context(), checkpoint_id="nb1:missing")
    with pytest.raises(CognitiveCheckpointUnavailableError):
        repository.load_checkpoint(context=_context(area_b=True), checkpoint_id="nb1:cycle-scoped")


def test_corrupt_checkpoint_is_denied_during_recovery(database_dsn: str) -> None:
    """Checkpoint bytes that diverge from immutable evidence cannot be resumed."""
    repository = _repository(database_dsn)
    _commit(repository, "corrupt")

    with psycopg.connect(database_dsn, autocommit=True) as connection:
        with connection.transaction(), connection.cursor() as cursor:
            cursor.execute(
                "UPDATE memory_core.checkpoints SET snapshot = %s WHERE checkpoint_id = %s",
                (Jsonb({"corrupt": True}), "nb1:cycle-corrupt"),
            )

    with pytest.raises(CognitiveRuntimeError):
        _repository(database_dsn).load_checkpoint(
            context=_context(), checkpoint_id="nb1:cycle-corrupt"
        )


def test_audit_failure_rolls_back_the_complete_cognitive_transaction(
    database_dsn: str,
) -> None:
    """A failure after checkpoint creation exposes no partial cognitive state."""
    with psycopg.connect(database_dsn, autocommit=True) as connection:
        with connection.transaction(), connection.cursor() as cursor:
            cursor.execute(
                "CREATE FUNCTION memory_audit.fail_cognitive_audit() RETURNS trigger "
                "LANGUAGE plpgsql AS $$ BEGIN "
                "IF NEW.event_type = 'cognitive_cycle_committed' THEN "
                "RAISE EXCEPTION 'injected cognitive audit failure'; END IF; "
                "RETURN NEW; END; $$"
            )
            cursor.execute(
                "CREATE TRIGGER injected_cognitive_audit_failure "
                "BEFORE INSERT ON memory_audit.events FOR EACH ROW "
                "EXECUTE FUNCTION memory_audit.fail_cognitive_audit()"
            )

    try:
        with pytest.raises(CognitiveRuntimeError):
            _commit(_repository(database_dsn), "rollback")
        assert _counts(database_dsn) == (0, 0, 0, 0)
    finally:
        with psycopg.connect(database_dsn, autocommit=True) as connection:
            with connection.transaction(), connection.cursor() as cursor:
                cursor.execute(
                    "DROP TRIGGER injected_cognitive_audit_failure ON memory_audit.events"
                )
                cursor.execute("DROP FUNCTION memory_audit.fail_cognitive_audit()")
