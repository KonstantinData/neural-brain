"""Tenant-bound synchronous PostgreSQL connection-pool resolution."""

from __future__ import annotations

from collections import OrderedDict
from collections.abc import Iterator
from contextlib import AbstractContextManager, contextmanager, suppress
from dataclasses import dataclass, field
from threading import RLock
from typing import Protocol

import psycopg
from psycopg.conninfo import conninfo_to_dict
from psycopg_pool import ConnectionPool

_BOUND_IDENTITY_QUERY = "SELECT * FROM brain_security.bound_database_identity()"
_MAX_IDENTIFIER_LENGTH = 256


class TenantPoolError(RuntimeError):
    """Base error for fail-closed tenant database pool resolution."""


class TenantPoolConfigurationError(TenantPoolError):
    """Trusted tenant database configuration is invalid or inconsistent."""


class TenantPoolUnavailableError(TenantPoolError):
    """A tenant-specific pool or credential is unavailable."""


class TenantDatabaseIdentityError(TenantPoolError):
    """The acquired database connection is not bound to the requested tenant."""


class TenantPoolClosedError(TenantPoolError):
    """The tenant pool resolver has already been closed."""


@dataclass(frozen=True, slots=True)
class TenantDatabaseEndpoint:
    """Secret-backed database endpoint for one immutable tenant pool generation.

    ``credential_revision`` must change whenever the credential or endpoint changes.
    The connection string is intentionally excluded from representation and identity.
    """

    tenant_id: str
    endpoint_id: str
    credential_revision: str
    conninfo: str = field(repr=False, compare=False, hash=False)
    database_name: str = field(init=False)

    def __post_init__(self) -> None:
        for label, value in (
            ("tenant_id", self.tenant_id),
            ("endpoint_id", self.endpoint_id),
            ("credential_revision", self.credential_revision),
        ):
            if not value or value.strip() != value or len(value) > _MAX_IDENTIFIER_LENGTH:
                raise TenantPoolConfigurationError(f"{label} is invalid")
        if not self.conninfo or not self.conninfo.strip():
            raise TenantPoolConfigurationError("tenant database credential is unavailable")
        try:
            database_name = conninfo_to_dict(self.conninfo).get("dbname")
        except psycopg.Error:
            raise TenantPoolConfigurationError("tenant database endpoint is invalid") from None
        if (
            not isinstance(database_name, str)
            or not database_name
            or database_name.strip() != database_name
            or len(database_name) > _MAX_IDENTIFIER_LENGTH
        ):
            raise TenantPoolConfigurationError("tenant database name is unavailable")
        object.__setattr__(self, "database_name", database_name)

    @property
    def pool_key(self) -> tuple[str, str, str]:
        """Return the non-secret identity of this tenant pool generation."""
        return (self.tenant_id, self.endpoint_id, self.credential_revision)


class SecretProvider(Protocol):
    """Resolve operator-controlled database configuration for exactly one tenant."""

    def get_database_endpoint(self, tenant_id: str) -> TenantDatabaseEndpoint:
        """Return the current endpoint generation or fail closed."""
        ...


class _ResultCursor(Protocol):
    def fetchone(self) -> tuple[object, ...] | None:
        """Return one result row."""
        ...


class TenantPoolConnection(Protocol):
    """Minimum synchronous connection surface exposed by a pool lease."""

    def execute(self, query: str) -> _ResultCursor:
        """Execute a database-identity verification query."""
        ...


class TenantConnectionPool(Protocol):
    """Minimum synchronous ``psycopg_pool.ConnectionPool`` surface used here."""

    def connection(self) -> AbstractContextManager[TenantPoolConnection]:
        """Lease a connection and return it through pool-managed cleanup."""
        ...

    def close(self) -> None:
        """Close the pool and all managed resources."""
        ...


class _ResettableConnection(Protocol):
    autocommit: bool

    def rollback(self) -> None: ...

    def execute(self, query: str) -> object: ...


class TenantPoolFactory(Protocol):
    """Create one pool from a secret-bearing endpoint."""

    def __call__(self, endpoint: TenantDatabaseEndpoint, *, max_size: int) -> TenantConnectionPool:
        """Create a closed-world tenant pool without a shared fallback."""
        ...


def _discard_session_state(
    connection: _ResettableConnection,
) -> None:
    """Remove transaction, role, GUC, prepared, and temporary session state."""
    if not connection.autocommit:
        connection.rollback()
        connection.autocommit = True
    connection.execute("DISCARD ALL")


class _PsycopgTenantPool:
    def __init__(self, endpoint: TenantDatabaseEndpoint, max_size: int) -> None:
        self._pool: ConnectionPool[psycopg.Connection[tuple[object, ...]]] = ConnectionPool(
            conninfo=endpoint.conninfo,
            min_size=0,
            max_size=max_size,
            open=True,
            kwargs={"autocommit": True, "prepare_threshold": None},
            reset=_discard_session_state,
        )

    @contextmanager
    def connection(self) -> Iterator[TenantPoolConnection]:
        with self._pool.connection() as connection:
            yield connection

    def close(self) -> None:
        self._pool.close()


def _default_pool_factory(
    endpoint: TenantDatabaseEndpoint, *, max_size: int
) -> TenantConnectionPool:
    """Create a tenant pool with bounded capacity and deterministic reset."""
    try:
        pool = _PsycopgTenantPool(endpoint, max_size)
    except TypeError, ValueError, OSError:
        raise TenantPoolUnavailableError("tenant database pool could not be created") from None
    return pool


@dataclass(slots=True)
class _PoolEntry:
    endpoint: TenantDatabaseEndpoint
    pool: TenantConnectionPool


class TenantPoolResolver:
    """Resolve bounded, tenant-specific pools with no cross-tenant fallback."""

    def __init__(
        self,
        *,
        secret_provider: SecretProvider,
        max_cached_pools: int = 32,
        pool_max_size: int = 10,
        pool_factory: TenantPoolFactory | None = None,
    ) -> None:
        if max_cached_pools < 1:
            raise ValueError("max_cached_pools must be positive")
        if pool_max_size < 1:
            raise ValueError("pool_max_size must be positive")
        self._secret_provider = secret_provider
        self._max_cached_pools = max_cached_pools
        self._pool_max_size = pool_max_size
        self._pool_factory = pool_factory or _default_pool_factory
        self._entries: OrderedDict[tuple[str, str, str], _PoolEntry] = OrderedDict()
        self._lock = RLock()
        self._closed = False

    @property
    def cached_pool_count(self) -> int:
        """Return the current bounded cache size without exposing credentials."""
        with self._lock:
            return len(self._entries)

    @contextmanager
    def connection(self, tenant_id: str) -> Iterator[TenantPoolConnection]:
        """Lease and verify a connection bound to ``tenant_id`` before yielding it."""
        entry = self._resolve_entry(tenant_id)
        lease = entry.pool.connection()
        consumer_error: Exception | None = None
        try:
            with lease as connection:
                self._verify_bound_identity(connection, entry.endpoint)
                try:
                    yield connection
                except Exception as error:
                    consumer_error = error
                    raise
        except TenantDatabaseIdentityError:
            self.evict_tenant(tenant_id)
            raise
        except TenantPoolError:
            self.evict_tenant(tenant_id)
            raise
        except Exception as error:
            if error is consumer_error:
                raise
            self.evict_tenant(tenant_id)
            raise TenantPoolUnavailableError("tenant database connection is unavailable") from None

    @contextmanager
    def psycopg_connection(
        self, tenant_id: str
    ) -> Iterator[psycopg.Connection[tuple[object, ...]]]:
        """Lease one verified concrete psycopg connection for repository adapters."""
        with self.connection(tenant_id) as connection:
            if not isinstance(connection, psycopg.Connection):
                raise TenantPoolUnavailableError(
                    "tenant database pool returned an incompatible connection"
                )
            yield connection

    def evict_tenant(self, tenant_id: str) -> int:
        """Close and remove every cached generation for one tenant."""
        _validate_requested_tenant(tenant_id)
        with self._lock:
            entries = self._pop_tenant_entries(tenant_id)
        self._close_entries(entries)
        return len(entries)

    def rotate_tenant(self, tenant_id: str) -> int:
        """Evict one tenant so its next acquisition must load the latest secret."""
        return self.evict_tenant(tenant_id)

    def close(self) -> None:
        """Permanently close all tenant pools and reject later acquisitions."""
        with self._lock:
            if self._closed:
                return
            self._closed = True
            entries = list(self._entries.values())
            self._entries.clear()
        self._close_entries(entries)

    def _resolve_entry(self, tenant_id: str) -> _PoolEntry:
        _validate_requested_tenant(tenant_id)
        with self._lock:
            if self._closed:
                raise TenantPoolClosedError("tenant pool resolver is closed")
            endpoint = self._load_endpoint(tenant_id)
            key = endpoint.pool_key
            existing = self._entries.get(key)
            if existing is not None:
                if existing.endpoint.conninfo != endpoint.conninfo:
                    raise TenantPoolConfigurationError(
                        "credential revision was reused with different secret material"
                    )
                self._entries.move_to_end(key)
                return existing

            stale_entries = self._pop_tenant_entries(tenant_id)
            try:
                pool = self._pool_factory(endpoint, max_size=self._pool_max_size)
            except TenantPoolError:
                self._restore_entries(stale_entries)
                raise
            except Exception:
                self._restore_entries(stale_entries)
                raise TenantPoolUnavailableError(
                    "tenant database pool could not be created"
                ) from None

            entry = _PoolEntry(endpoint=endpoint, pool=pool)
            self._entries[key] = entry
            evicted_entries: list[_PoolEntry] = []
            while len(self._entries) > self._max_cached_pools:
                _, evicted = self._entries.popitem(last=False)
                evicted_entries.append(evicted)

        try:
            self._close_entries([*stale_entries, *evicted_entries])
        except TenantPoolUnavailableError:
            with self._lock:
                self._entries.pop(key, None)
            with suppress(Exception):
                pool.close()
            raise
        return entry

    def _load_endpoint(self, tenant_id: str) -> TenantDatabaseEndpoint:
        try:
            endpoint = self._secret_provider.get_database_endpoint(tenant_id)
        except TenantPoolError:
            raise
        except Exception:
            raise TenantPoolUnavailableError("tenant database credential is unavailable") from None
        if endpoint.tenant_id != tenant_id:
            raise TenantPoolConfigurationError(
                "tenant database credential belongs to a different tenant"
            )
        return endpoint

    def _pop_tenant_entries(self, tenant_id: str) -> list[_PoolEntry]:
        keys = [key for key in self._entries if key[0] == tenant_id]
        return [self._entries.pop(key) for key in keys]

    def _restore_entries(self, entries: list[_PoolEntry]) -> None:
        for entry in entries:
            self._entries[entry.endpoint.pool_key] = entry

    @staticmethod
    def _close_entries(entries: list[_PoolEntry]) -> None:
        failed = False
        for entry in entries:
            try:
                entry.pool.close()
            except Exception:
                failed = True
        if failed:
            raise TenantPoolUnavailableError("tenant database pool cleanup failed")

    @staticmethod
    def _verify_bound_identity(
        connection: TenantPoolConnection, endpoint: TenantDatabaseEndpoint
    ) -> None:
        try:
            row = connection.execute(_BOUND_IDENTITY_QUERY).fetchone()
        except Exception:
            raise TenantDatabaseIdentityError(
                "database tenant identity could not be verified"
            ) from None
        expected = (
            endpoint.tenant_id,
            endpoint.database_name,
            endpoint.credential_revision,
        )
        if row is None or len(row) != 3 or row != expected:
            raise TenantDatabaseIdentityError(
                "database identity does not match the requested tenant generation"
            )


def _validate_requested_tenant(tenant_id: str) -> None:
    if (
        not isinstance(tenant_id, str)
        or not tenant_id
        or tenant_id.strip() != tenant_id
        or len(tenant_id) > _MAX_IDENTIFIER_LENGTH
    ):
        raise TenantPoolConfigurationError("requested tenant_id is invalid")


__all__ = [
    "SecretProvider",
    "TenantConnectionPool",
    "TenantDatabaseEndpoint",
    "TenantDatabaseIdentityError",
    "TenantPoolClosedError",
    "TenantPoolConfigurationError",
    "TenantPoolConnection",
    "TenantPoolError",
    "TenantPoolFactory",
    "TenantPoolResolver",
    "TenantPoolUnavailableError",
]
