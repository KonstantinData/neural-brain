"""Run one secret-free, authenticated local Memory Core round-trip."""

from __future__ import annotations

import argparse
import base64
import json
import sys
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import psycopg
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from psycopg.conninfo import make_conninfo

from neural_brain.consumer import (
    OidcAuthenticationError,
    OidcJwtAuthenticator,
    OidcJwtConfiguration,
    OidcMemoryCoreConsumer,
)
from neural_brain.memory import (
    CheckpointRequest,
    MemoryKernelError,
    ObservationRequest,
    RuntimeContext,
    WorkingMemoryEntryRequest,
    WorkingMemoryRequest,
)
from neural_brain.postgres import PostgresMemoryRepository, PostgresOidcPrincipalResolver
from tools.install_memory_core import (
    DEMO_AREA_ID,
    DEMO_OIDC_ISSUER,
    DEMO_OIDC_SUBJECT,
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
LOCAL_OIDC_AUDIENCE = "neural-brain-local-demo"


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


def _base64url(value: bytes) -> str:
    """Encode public JWT material without storing or printing private key bytes."""

    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _local_oidc_token(
    private_key: rsa.RSAPrivateKey, occurred_at: datetime
) -> tuple[str, dict[str, object]]:
    """Create one in-memory RS256 token and public JWK set for the local demonstration."""

    public_numbers = private_key.public_key().public_numbers()
    modulus_size = (public_numbers.n.bit_length() + 7) // 8
    jwks: dict[str, object] = {
        "keys": [
            {
                "kid": "local-demo-rs256-v1",
                "kty": "RSA",
                "alg": "RS256",
                "use": "sig",
                "n": _base64url(public_numbers.n.to_bytes(modulus_size, "big")),
                "e": _base64url(public_numbers.e.to_bytes(3, "big")),
            }
        ]
    }
    header = {"alg": "RS256", "kid": "local-demo-rs256-v1", "typ": "JWT"}
    claims = {
        "iss": DEMO_OIDC_ISSUER,
        "aud": [LOCAL_OIDC_AUDIENCE],
        "sub": DEMO_OIDC_SUBJECT,
        "exp": int(occurred_at.timestamp()) + 300,
        "nbf": int(occurred_at.timestamp()) - 1,
        "neural_brain_scope": {
            "tenant_id": DEMO_TENANT_ID,
            "area_id": DEMO_AREA_ID,
            "project_id": DEMO_PROJECT_ID,
            "session_id": DEMO_SESSION_ID,
        },
    }
    encoded_header = _base64url(json.dumps(header, sort_keys=True, separators=(",", ":")).encode())
    encoded_claims = _base64url(json.dumps(claims, sort_keys=True, separators=(",", ":")).encode())
    signing_input = f"{encoded_header}.{encoded_claims}".encode("ascii")
    signature = private_key.sign(signing_input, padding.PKCS1v15(), hashes.SHA256())
    return f"{encoded_header}.{encoded_claims}.{_base64url(signature)}", jwks


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
    occurred_at = datetime.now(UTC)
    observation = ObservationRequest(
        observation_id=f"observation-{run_id}",
        source_kind="operator_demo",
        source_ref=f"local-demo-{run_id}",
        classification="internal",
        purpose="local_memory_core_verification",
        content="Local Memory Core round-trip",
        occurred_at=occurred_at,
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
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    token, jwks = _local_oidc_token(private_key, occurred_at)
    consumer = OidcMemoryCoreConsumer(
        authenticator=OidcJwtAuthenticator(
            configuration=OidcJwtConfiguration(
                issuer=DEMO_OIDC_ISSUER, audience=LOCAL_OIDC_AUDIENCE
            ),
            jwks=jwks,
            principal_resolver=PostgresOidcPrincipalResolver(runtime_dsn),
        ),
        repository=PostgresMemoryRepository(runtime_dsn),
    )
    result = consumer.record_observation_and_checkpoint(
        **{"bearer_token": token},
        transition_request_id=f"transition-{run_id}",
        observation=observation,
        working_memory=working_memory,
        checkpoint=checkpoint_request,
    )
    checkpoint = consumer.read_checkpoint(
        **{"bearer_token": token}, checkpoint_id=checkpoint_request.checkpoint_id
    )
    observation_readback = consumer.read_observation(
        **{"bearer_token": token}, observation_id=observation.observation_id
    )
    working_memory_readback = consumer.read_working_memory(
        **{"bearer_token": token}, working_memory_id=working_memory.working_memory_id
    )
    if checkpoint != result.checkpoint:
        raise RuntimeError("Checkpoint readback did not match the committed memory cycle")
    if (
        observation_readback != result.observation
        or working_memory_readback != result.working_memory
    ):
        raise RuntimeError("OIDC scoped readback did not match the committed memory cycle")
    return {
        "status": "passed",
        "migrations": migration_count,
        "observation_id": result.observation.observation_id,
        "working_memory_id": result.working_memory.working_memory_id,
        "working_memory_version": result.working_memory.version,
        "checkpoint_id": result.checkpoint.checkpoint_id,
        "audit_committed": result.audit_committed,
        "authentication": "oidc_rs256_local_demo",
        "observation_readback": True,
        "working_memory_readback": True,
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


def _operator_error_code(error: Exception) -> str:
    """Map an expected boundary failure to its stable, secret-free operator code."""

    if isinstance(error, (MemoryKernelError, OidcAuthenticationError)):
        return error.code
    return MemoryKernelError.code


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
        print(
            json.dumps({"code": _operator_error_code(error), "status": "failed"}, sort_keys=True),
            file=sys.stderr,
        )
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
