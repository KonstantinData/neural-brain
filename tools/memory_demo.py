"""Run one secret-free, authenticated local Memory Core round-trip."""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import psycopg
from psycopg.conninfo import make_conninfo

from neural_brain.memory import (
    CheckpointRequest,
    MemoryKernelError,
    MemoryService,
    ObservationRequest,
    RuntimeContext,
    WorkingMemoryEntryRequest,
    WorkingMemoryRequest,
)
from neural_brain.postgres import PostgresMemoryRepository
from tools.install_memory_core import (
    DEMO_AREA_ID,
    DEMO_PRINCIPAL_ID,
    DEMO_PROJECT_ID,
    DEMO_SESSION_ID,
    DEMO_TENANT_ID,
    install_local_memory_core,
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ENVIRONMENT_FILE = ROOT / ".local" / "dev.env"
REQUIRED_ENVIRONMENT_NAMES = (
    "NEURAL_BRAIN_POSTGRES_ADMIN_USER",
    "NEURAL_BRAIN_POSTGRES_ADMIN_PASSWORD",
    "NEURAL_BRAIN_DEV_DB",
    "NEURAL_BRAIN_DEV_USER",
    "NEURAL_BRAIN_DEV_PASSWORD",
    "NEURAL_BRAIN_DEV_PORT",
)


@dataclass(frozen=True, slots=True)
class FixedLocalContextProvider:
    """Return fixed trusted context that cannot be overridden by demo input."""

    def current_context(self) -> RuntimeContext:
        """Return the provisioned local demo principal and immutable scope."""

        return RuntimeContext(
            actor_id=DEMO_PRINCIPAL_ID,
            tenant_id=DEMO_TENANT_ID,
            area_id=DEMO_AREA_ID,
            project_id=DEMO_PROJECT_ID,
            session_id=DEMO_SESSION_ID,
        )


def read_local_environment(path: Path) -> dict[str, str]:
    """Read the owner-protected local environment without logging any value."""

    environment: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        name, separator, value = line.partition("=")
        if not separator or not name or not value or name in environment:
            raise ValueError("The generated local environment is malformed")
        environment[name] = value
    missing = [name for name in REQUIRED_ENVIRONMENT_NAMES if name not in environment]
    if missing:
        raise ValueError("The generated local environment is incomplete")
    return environment


def _connection_dsn(environment: dict[str, str], *, administrative: bool) -> str:
    user_suffix = "POSTGRES_ADMIN_USER" if administrative else "DEV_USER"
    password_suffix = "POSTGRES_ADMIN_PASSWORD" if administrative else "DEV_PASSWORD"
    return make_conninfo(
        host="127.0.0.1",
        port=environment["NEURAL_BRAIN_DEV_PORT"],
        dbname=environment["NEURAL_BRAIN_DEV_DB"],
        user=environment[f"NEURAL_BRAIN_{user_suffix}"],
        password=environment[f"NEURAL_BRAIN_{password_suffix}"],
        connect_timeout="5",
        application_name="neural-brain-memory-demo",
    )


def run_memory_demo(admin_dsn: str, runtime_dsn: str, runtime_role: str) -> dict[str, object]:
    """Install the local slice, commit one cycle, and read its checkpoint back."""

    migration_count = install_local_memory_core(admin_dsn, runtime_role, ROOT / "migrations")
    run_id = uuid.uuid4().hex
    observation = ObservationRequest(
        observation_id=f"observation-{run_id}",
        source_kind="operator_demo",
        source_ref=f"local-demo-{run_id}",
        classification="internal",
        purpose="local_memory_core_verification",
        content="Local Memory Core round-trip",
        occurred_at=datetime.now(UTC),
    )
    working_memory = WorkingMemoryRequest(
        working_memory_id=f"working-{run_id}",
        expected_version=0,
        entries=(
            WorkingMemoryEntryRequest(
                entry_id=f"entry-{run_id}",
                source_observation_id=observation.observation_id,
                content=observation.content,
            ),
        ),
    )
    checkpoint_request = CheckpointRequest(checkpoint_id=f"checkpoint-{run_id}")
    service = MemoryService(
        context_provider=FixedLocalContextProvider(),
        repository=PostgresMemoryRepository(runtime_dsn),
    )
    result = service.record_observation_and_checkpoint(
        transition_request_id=f"transition-{run_id}",
        observation=observation,
        working_memory=working_memory,
        checkpoint=checkpoint_request,
    )
    checkpoint = service.read_checkpoint(checkpoint_request)
    if checkpoint != result.checkpoint:
        raise RuntimeError("Checkpoint readback did not match the committed memory cycle")
    return {
        "status": "passed",
        "migrations": migration_count,
        "observation_id": result.observation.observation_id,
        "working_memory_id": result.working_memory.working_memory_id,
        "working_memory_version": result.working_memory.version,
        "checkpoint_id": result.checkpoint.checkpoint_id,
        "audit_committed": result.audit_committed,
        "checkpoint_readback": True,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--environment-file",
        type=Path,
        default=DEFAULT_ENVIRONMENT_FILE,
        help="Owner-protected local environment generated by tools/dev.ps1",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the demo without exposing connection strings or credentials."""

    arguments = _parser().parse_args(argv)
    try:
        environment = read_local_environment(arguments.environment_file)
        result = run_memory_demo(
            _connection_dsn(environment, administrative=True),
            _connection_dsn(environment, administrative=False),
            environment["NEURAL_BRAIN_DEV_USER"],
        )
    except (OSError, ValueError, RuntimeError, psycopg.Error, MemoryKernelError) as error:
        print(f"memory demo failed: {type(error).__name__}", file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
