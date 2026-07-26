"""Unit evidence for tenant-specific database pool resolution."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import override

import pytest
from psycopg_pool import PoolTimeout

from neural_brain.postgres.tenant_pool import (
    SecretProvider,
    TenantDatabaseEndpoint,
    TenantDatabaseIdentityError,
    TenantPoolClosedError,
    TenantPoolConfigurationError,
    TenantPoolResolver,
    TenantPoolUnavailableError,
    _discard_session_state,
)


class _FakeCursor:
    def __init__(self, row: tuple[object, ...] | None) -> None:
        self._row = row

    def fetchone(self) -> tuple[object, ...] | None:
        return self._row


class _FakeConnection:
    def __init__(
        self,
        bound_tenant_id: str | None,
        database_name: str = "brain_tenant-a",
        credential_revision: str = "revision-1",
    ) -> None:
        self.bound_tenant_id = bound_tenant_id
        self.database_name = database_name
        self.credential_revision = credential_revision
        self.queries: list[str] = []

    def execute(self, query: str) -> _FakeCursor:
        self.queries.append(query)
        row = (
            None
            if self.bound_tenant_id is None
            else (self.bound_tenant_id, self.database_name, self.credential_revision)
        )
        return _FakeCursor(row)


class _FakePool:
    def __init__(self, endpoint: TenantDatabaseEndpoint) -> None:
        self.endpoint = endpoint
        self.connection_value = _FakeConnection(
            endpoint.tenant_id,
            endpoint.database_name,
            endpoint.credential_revision,
        )
        self.closed = False
        self.active_leases = 0
        self.returned_leases = 0
        self.fail_enter = False
        self.fail_exit = False

    @contextmanager
    def connection(self) -> Iterator[_FakeConnection]:
        if self.fail_enter:
            raise PoolTimeout("injected capacity exhaustion")
        self.active_leases += 1
        try:
            yield self.connection_value
        finally:
            self.active_leases -= 1
            self.returned_leases += 1
            if self.fail_exit:
                raise RuntimeError("injected reset failure")

    def close(self) -> None:
        self.closed = True


class _FakePoolFactory:
    def __init__(self) -> None:
        self.created: list[_FakePool] = []
        self.max_sizes: list[int] = []
        self.fail = False

    def __call__(self, endpoint: TenantDatabaseEndpoint, *, max_size: int) -> _FakePool:
        if self.fail:
            raise RuntimeError("injected pool creation failure")
        pool = _FakePool(endpoint)
        self.created.append(pool)
        self.max_sizes.append(max_size)
        return pool


class _FakeSecretProvider:
    def __init__(self, endpoints: dict[str, TenantDatabaseEndpoint]) -> None:
        self.endpoints = endpoints
        self.requests: list[str] = []
        self.fail = False

    def get_database_endpoint(self, tenant_id: str) -> TenantDatabaseEndpoint:
        self.requests.append(tenant_id)
        if self.fail:
            raise RuntimeError("injected secret provider failure")
        return self.endpoints[tenant_id]


class _UnavailableSecretProvider:
    def __init__(self, state: str) -> None:
        self._state = state

    def get_database_endpoint(self, tenant_id: str) -> TenantDatabaseEndpoint:
        raise TenantPoolUnavailableError(f"tenant database credential is {self._state}")


def _endpoint(
    tenant_id: str,
    *,
    endpoint_id: str | None = None,
    revision: str = "revision-1",
    host: str = "db.internal",
) -> TenantDatabaseEndpoint:
    return TenantDatabaseEndpoint(
        tenant_id=tenant_id,
        endpoint_id=endpoint_id or f"endpoint-{tenant_id}",
        credential_revision=revision,
        conninfo=f"host={host} dbname=brain_{tenant_id} user={tenant_id} password=top-secret",
    )


def _resolver(
    provider: SecretProvider,
    factory: _FakePoolFactory,
    *,
    max_cached_pools: int = 4,
) -> TenantPoolResolver:
    return TenantPoolResolver(
        secret_provider=provider,
        pool_factory=factory,
        max_cached_pools=max_cached_pools,
        pool_max_size=7,
    )


def test_endpoint_never_represents_secret_material() -> None:
    endpoint = _endpoint("tenant-a")

    assert "top-secret" not in repr(endpoint)
    assert "top-secret" not in str(endpoint)
    assert endpoint.pool_key == ("tenant-a", "endpoint-tenant-a", "revision-1")
    assert endpoint.database_name == "brain_tenant-a"


def test_same_tenant_endpoint_and_revision_reuses_exactly_one_pool() -> None:
    provider = _FakeSecretProvider({"tenant-a": _endpoint("tenant-a")})
    factory = _FakePoolFactory()
    resolver = _resolver(provider, factory)

    with resolver.connection("tenant-a") as first:
        assert first is factory.created[0].connection_value
    with resolver.connection("tenant-a") as second:
        assert second is first

    assert len(factory.created) == 1
    assert factory.max_sizes == [7]
    assert resolver.cached_pool_count == 1
    assert factory.created[0].connection_value.queries == [
        "SELECT * FROM brain_security.bound_database_identity()",
        "SELECT * FROM brain_security.bound_database_identity()",
    ]


def test_tenants_with_different_hosts_and_databases_get_distinct_pools() -> None:
    provider = _FakeSecretProvider(
        {
            "tenant-a": _endpoint("tenant-a", host="host-a.internal"),
            "tenant-b": _endpoint("tenant-b", host="host-b.internal"),
        }
    )
    factory = _FakePoolFactory()
    resolver = _resolver(provider, factory)

    with resolver.connection("tenant-a"):
        pass
    with resolver.connection("tenant-b"):
        pass

    assert len(factory.created) == 2
    assert "host-a.internal" in factory.created[0].endpoint.conninfo
    assert "host-b.internal" in factory.created[1].endpoint.conninfo
    assert resolver.cached_pool_count == 2


def test_missing_secret_fails_closed_without_cached_or_shared_fallback() -> None:
    provider = _FakeSecretProvider({})
    factory = _FakePoolFactory()
    resolver = _resolver(provider, factory)

    with (
        pytest.raises(TenantPoolUnavailableError, match="credential is unavailable"),
        resolver.connection("tenant-missing"),
    ):
        pass

    assert factory.created == []
    assert resolver.cached_pool_count == 0


@pytest.mark.parametrize("state", ["expired", "revoked"])
def test_expired_or_revoked_secret_fails_closed_without_fallback(state: str) -> None:
    factory = _FakePoolFactory()
    resolver = _resolver(_UnavailableSecretProvider(state), factory)

    with pytest.raises(TenantPoolUnavailableError, match=state), resolver.connection("tenant-a"):
        pass

    assert factory.created == []
    assert resolver.cached_pool_count == 0


def test_secret_for_another_tenant_is_rejected_before_pool_creation() -> None:
    provider = _FakeSecretProvider({"tenant-a": _endpoint("tenant-b")})
    factory = _FakePoolFactory()
    resolver = _resolver(provider, factory)

    with (
        pytest.raises(TenantPoolConfigurationError, match="different tenant"),
        resolver.connection("tenant-a"),
    ):
        pass

    assert factory.created == []


def test_database_identity_mismatch_is_denied_and_lease_is_returned() -> None:
    provider = _FakeSecretProvider({"tenant-a": _endpoint("tenant-a")})
    factory = _FakePoolFactory()
    resolver = _resolver(provider, factory)
    with resolver.connection("tenant-a"):
        pass
    pool = factory.created[0]
    pool.connection_value.bound_tenant_id = "tenant-b"

    with (
        pytest.raises(TenantDatabaseIdentityError, match="does not match"),
        resolver.connection("tenant-a"),
    ):
        pass

    assert pool.active_leases == 0
    assert pool.returned_leases == 2
    assert pool.closed is True
    assert resolver.cached_pool_count == 0


@pytest.mark.parametrize("field", ["database_name", "credential_revision"])
def test_database_target_or_revision_mismatch_is_denied(field: str) -> None:
    provider = _FakeSecretProvider({"tenant-a": _endpoint("tenant-a")})
    factory = _FakePoolFactory()
    resolver = _resolver(provider, factory)
    with resolver.connection("tenant-a"):
        pass
    pool = factory.created[0]
    setattr(pool.connection_value, field, "unexpected")

    with (
        pytest.raises(TenantDatabaseIdentityError, match="does not match"),
        resolver.connection("tenant-a"),
    ):
        pass

    assert pool.closed is True
    assert resolver.cached_pool_count == 0


def test_consumer_failure_still_returns_connection_to_pool_cleanup() -> None:
    provider = _FakeSecretProvider({"tenant-a": _endpoint("tenant-a")})
    factory = _FakePoolFactory()
    resolver = _resolver(provider, factory)

    with pytest.raises(RuntimeError, match="consumer failed"), resolver.connection("tenant-a"):
        raise RuntimeError("consumer failed")

    assert factory.created[0].active_leases == 0
    assert factory.created[0].returned_leases == 1


def test_pool_capacity_exhaustion_fails_closed_and_evicts_generation() -> None:
    provider = _FakeSecretProvider({"tenant-a": _endpoint("tenant-a")})
    factory = _FakePoolFactory()
    resolver = _resolver(provider, factory)
    with resolver.connection("tenant-a"):
        pass
    pool = factory.created[0]
    pool.fail_enter = True

    with (
        pytest.raises(TenantPoolUnavailableError, match="connection is unavailable"),
        resolver.connection("tenant-a"),
    ):
        pass

    assert pool.closed is True
    assert resolver.cached_pool_count == 0


def test_pool_reset_failure_fails_closed_and_evicts_generation() -> None:
    provider = _FakeSecretProvider({"tenant-a": _endpoint("tenant-a")})
    factory = _FakePoolFactory()
    resolver = _resolver(provider, factory)
    with resolver.connection("tenant-a"):
        pass
    pool = factory.created[0]
    pool.fail_exit = True

    with (
        pytest.raises(TenantPoolUnavailableError, match="connection is unavailable"),
        resolver.connection("tenant-a"),
    ):
        pass

    assert pool.returned_leases == 2
    assert pool.closed is True
    assert resolver.cached_pool_count == 0


def test_new_credential_revision_closes_old_pool_and_uses_new_generation() -> None:
    provider = _FakeSecretProvider({"tenant-a": _endpoint("tenant-a")})
    factory = _FakePoolFactory()
    resolver = _resolver(provider, factory)
    with resolver.connection("tenant-a"):
        pass
    old_pool = factory.created[0]
    provider.endpoints["tenant-a"] = _endpoint("tenant-a", revision="revision-2")

    with resolver.connection("tenant-a"):
        pass

    assert old_pool.closed is True
    assert len(factory.created) == 2
    assert resolver.cached_pool_count == 1


def test_cached_pool_is_not_used_when_secret_refresh_fails() -> None:
    provider = _FakeSecretProvider({"tenant-a": _endpoint("tenant-a")})
    factory = _FakePoolFactory()
    resolver = _resolver(provider, factory)
    with resolver.connection("tenant-a"):
        pass
    cached_pool = factory.created[0]
    provider.fail = True

    with (
        pytest.raises(TenantPoolUnavailableError, match="credential is unavailable"),
        resolver.connection("tenant-a"),
    ):
        pass

    assert cached_pool.returned_leases == 1


def test_pool_creation_failure_never_falls_back_to_stale_generation() -> None:
    provider = _FakeSecretProvider({"tenant-a": _endpoint("tenant-a")})
    factory = _FakePoolFactory()
    resolver = _resolver(provider, factory)
    with resolver.connection("tenant-a"):
        pass
    stale_pool = factory.created[0]
    provider.endpoints["tenant-a"] = _endpoint("tenant-a", revision="revision-2")
    factory.fail = True

    with (
        pytest.raises(TenantPoolUnavailableError, match="could not be created"),
        resolver.connection("tenant-a"),
    ):
        pass

    assert stale_pool.returned_leases == 1
    assert stale_pool.closed is False
    assert resolver.cached_pool_count == 1


def test_reused_revision_with_changed_secret_fails_closed() -> None:
    provider = _FakeSecretProvider({"tenant-a": _endpoint("tenant-a")})
    factory = _FakePoolFactory()
    resolver = _resolver(provider, factory)
    with resolver.connection("tenant-a"):
        pass
    provider.endpoints["tenant-a"] = _endpoint("tenant-a", host="unexpected.internal")

    with (
        pytest.raises(TenantPoolConfigurationError, match="revision was reused"),
        resolver.connection("tenant-a"),
    ):
        pass

    assert len(factory.created) == 1


def test_bounded_lru_closes_least_recently_used_tenant_pool() -> None:
    provider = _FakeSecretProvider(
        {tenant: _endpoint(tenant) for tenant in ("tenant-a", "tenant-b", "tenant-c")}
    )
    factory = _FakePoolFactory()
    resolver = _resolver(provider, factory, max_cached_pools=2)
    with resolver.connection("tenant-a"):
        pass
    with resolver.connection("tenant-b"):
        pass
    with resolver.connection("tenant-a"):
        pass
    with resolver.connection("tenant-c"):
        pass

    assert factory.created[0].closed is False
    assert factory.created[1].closed is True
    assert factory.created[2].closed is False
    assert resolver.cached_pool_count == 2


def test_tenant_eviction_rotation_and_close_do_not_affect_other_tenants() -> None:
    provider = _FakeSecretProvider(
        {tenant: _endpoint(tenant) for tenant in ("tenant-a", "tenant-b")}
    )
    factory = _FakePoolFactory()
    resolver = _resolver(provider, factory)
    with resolver.connection("tenant-a"):
        pass
    with resolver.connection("tenant-b"):
        pass

    assert resolver.rotate_tenant("tenant-a") == 1
    assert factory.created[0].closed is True
    assert factory.created[1].closed is False
    assert resolver.cached_pool_count == 1

    resolver.close()
    assert factory.created[1].closed is True
    assert resolver.cached_pool_count == 0
    with pytest.raises(TenantPoolClosedError), resolver.connection("tenant-b"):
        pass


class _WrongShapeConnection(_FakeConnection):
    @override
    def execute(self, query: str) -> _FakeCursor:
        self.queries.append(query)
        return _FakeCursor(("tenant-a", "unexpected"))


def test_missing_or_malformed_database_identity_result_fails_closed() -> None:
    for connection in (_FakeConnection(None), _WrongShapeConnection("tenant-a")):
        provider = _FakeSecretProvider({"tenant-a": _endpoint("tenant-a")})
        factory = _FakePoolFactory()
        resolver = _resolver(provider, factory)
        with resolver.connection("tenant-a"):
            pass
        factory.created[0].connection_value = connection

        with pytest.raises(TenantDatabaseIdentityError), resolver.connection("tenant-a"):
            pass


def test_invalid_tenant_and_pool_bounds_are_rejected() -> None:
    provider = _FakeSecretProvider({})
    factory = _FakePoolFactory()
    with pytest.raises(ValueError, match="max_cached_pools"):
        TenantPoolResolver(secret_provider=provider, pool_factory=factory, max_cached_pools=0)
    with pytest.raises(ValueError, match="pool_max_size"):
        TenantPoolResolver(secret_provider=provider, pool_factory=factory, pool_max_size=0)
    resolver = _resolver(provider, factory)
    with (
        pytest.raises(TenantPoolConfigurationError, match="tenant_id"),
        resolver.connection(" tenant-a"),
    ):
        pass


class _ResetFailureConnection:
    def __init__(self) -> None:
        self.autocommit = False
        self.rolled_back = False

    def rollback(self) -> None:
        self.rolled_back = True

    def execute(self, query: str) -> None:
        assert query == "DISCARD ALL"
        raise RuntimeError("injected reset failure")


def test_session_reset_failure_is_not_suppressed() -> None:
    """A connection whose session state cannot be discarded must fail pool reset."""

    connection = _ResetFailureConnection()
    with pytest.raises(RuntimeError, match="reset failure"):
        _discard_session_state(connection)
    assert connection.rolled_back is True
    assert connection.autocommit is True
