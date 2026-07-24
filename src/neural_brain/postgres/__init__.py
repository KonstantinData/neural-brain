"""Synchronous PostgreSQL adapters for protected Neural Brain gates."""

from neural_brain.postgres.cognitive_repository import PostgresCognitiveRepository
from neural_brain.postgres.memory_repository import PostgresMemoryRepository
from neural_brain.postgres.oidc_principal_resolver import PostgresOidcPrincipalResolver

__all__ = [
    "PostgresCognitiveRepository",
    "PostgresMemoryRepository",
    "PostgresOidcPrincipalResolver",
]
