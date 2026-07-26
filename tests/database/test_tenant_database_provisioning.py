"""Live PostgreSQL evidence for the controlled Tenant database identity lifecycle."""

from __future__ import annotations

import hashlib
from collections.abc import Callable
from dataclasses import dataclass, field

import psycopg
import pytest
from psycopg import sql
from psycopg.conninfo import conninfo_to_dict, make_conninfo

from neural_brain.postgres.tenant_provisioning import (
    TenantDatabaseProvisioner,
    TenantProvisioningError,
    TenantProvisioningRequest,
    tenant_runtime_role_name,
)

_TENANT_PREFIX = "tenant-provisioned-"
_FIRST_PASSWORD = "Aa0!bcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
_SECOND_PASSWORD = "Zz9?ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz9876543210"


@dataclass
class _RevisionedSecretStore:
    fail_put: bool = False
    fail_after_put: bool = False
    fail_delete: bool = False
    credentials: dict[tuple[str, str, int], str] = field(default_factory=dict)
    deleted: list[tuple[str, str, int | None]] = field(default_factory=list)

    def put_database_credential(
        self, *, tenant_id: str, database_role: str, password: str, revision: int
    ) -> str:
        if self.fail_put:
            raise RuntimeError("injected secret-store failure")
        self.credentials[(tenant_id, database_role, revision)] = password
        if self.fail_after_put:
            raise RuntimeError("injected ambiguous secret-store timeout")
        return f"secret://tenant-database/{tenant_id}/{revision}"

    def delete_database_credential(
        self, *, tenant_id: str, database_role: str, revision: int | None = None
    ) -> None:
        if self.fail_delete:
            raise RuntimeError("injected secret-store cleanup failure")
        self.deleted.append((tenant_id, database_role, revision))
        if revision is None:
            keys = [key for key in self.credentials if key[:2] == (tenant_id, database_role)]
        else:
            keys = [(tenant_id, database_role, revision)]
        for key in keys:
            self.credentials.pop(key, None)


def _tenant_id(database_dsn: str) -> str:
    database_name = conninfo_to_dict(database_dsn).get("dbname")
    if not isinstance(database_name, str):
        raise RuntimeError("Disposable database DSN has no database name")
    return _TENANT_PREFIX + database_name.rsplit("_", maxsplit=1)[-1]


def _request(tenant_id: str) -> TenantProvisioningRequest:
    return TenantProvisioningRequest(
        tenant_id=tenant_id,
        brain_id="brain-neural",
        display_name="Provisioned Tenant",
    )


def _password_factory(*passwords: str) -> Callable[[], str]:
    remaining = iter(passwords)
    return lambda: next(remaining)


def _runtime_dsn(database_dsn: str, tenant_id: str, password: str) -> str:
    return make_conninfo(
        database_dsn,
        user=tenant_runtime_role_name(tenant_id),
        password=password,
        connect_timeout="2",
    )


def _cleanup_role(database_dsn: str, tenant_id: str) -> None:
    role_name = tenant_runtime_role_name(tenant_id)
    with (
        psycopg.connect(database_dsn, autocommit=True) as connection,
        connection.transaction(),
        connection.cursor() as cursor,
    ):
        cursor.execute(
            "SELECT 1 FROM pg_catalog.pg_roles WHERE rolname = %s",
            (role_name,),
        )
        if cursor.fetchone() is None:
            return
        cursor.execute(
            "DELETE FROM brain_security.tenant_runtime_identity_events WHERE tenant_id = %s",
            (tenant_id,),
        )
        cursor.execute(
            "DELETE FROM brain_security.tenant_runtime_identities WHERE tenant_id = %s",
            (tenant_id,),
        )
        database_name_row = cursor.execute("SELECT current_database()").fetchone()
        assert database_name_row is not None
        cursor.execute("SET LOCAL ROLE neural_brain_provisioner")
        cursor.execute(
            sql.SQL("REVOKE CONNECT ON DATABASE {} FROM {}").format(
                sql.Identifier(str(database_name_row[0])), sql.Identifier(role_name)
            )
        )
        cursor.execute(
            sql.SQL("REVOKE ALL PRIVILEGES ON SCHEMA brain_security FROM {}").format(
                sql.Identifier(role_name)
            )
        )
        cursor.execute(
            sql.SQL("REVOKE neural_brain_gate, neural_brain_reader FROM {}").format(
                sql.Identifier(role_name)
            )
        )
        cursor.execute("RESET ROLE")
        cursor.execute(sql.SQL("DROP OWNED BY {}").format(sql.Identifier(role_name)))
        cursor.execute(sql.SQL("DROP ROLE IF EXISTS {}").format(sql.Identifier(role_name)))


def test_provisioning_is_atomic_verified_and_idempotent(database_dsn: str) -> None:
    """One workflow creates exactly one least-privilege login, mapping, and secret revision."""

    password = _FIRST_PASSWORD
    tenant_id = _tenant_id(database_dsn)
    store = _RevisionedSecretStore()
    provisioner = TenantDatabaseProvisioner(
        database_dsn, store, password_factory=_password_factory(password)
    )
    try:
        first = provisioner.provision(_request(tenant_id))
        repeated = provisioner.provision(_request(tenant_id))

        assert first.verified is True
        assert first.credential_revision == 1
        assert first.secret_reference == f"secret://tenant-database/{tenant_id}/1"
        assert repeated.database_role == first.database_role
        assert repeated.credential_revision == 1
        assert repeated.secret_reference is None
        assert len(store.credentials) == 1
        with psycopg.connect(
            _runtime_dsn(database_dsn, tenant_id, password), autocommit=True
        ) as connection:
            assert connection.execute("SELECT brain_security.bound_tenant_id()").fetchone() == (
                tenant_id,
            )
    finally:
        _cleanup_role(database_dsn, tenant_id)


def test_secret_handoff_failure_rolls_back_catalog_role_and_mapping(database_dsn: str) -> None:
    """A partial provisioning failure leaves no Tenant login or protected mapping."""

    tenant_id = _tenant_id(database_dsn)
    role_name = tenant_runtime_role_name(tenant_id)
    provisioner = TenantDatabaseProvisioner(
        database_dsn,
        _RevisionedSecretStore(fail_put=True),
        password_factory=_password_factory(_FIRST_PASSWORD),
    )
    with pytest.raises(TenantProvisioningError, match="provisioning failed"):
        provisioner.provision(_request(tenant_id))

    with psycopg.connect(database_dsn, autocommit=True) as connection:
        assert connection.execute(
            "SELECT count(*) FROM brain_catalog.tenants WHERE tenant_id = %s", (tenant_id,)
        ).fetchone() == (0,)
        assert connection.execute(
            "SELECT count(*) FROM brain_security.tenant_runtime_identities WHERE tenant_id = %s",
            (tenant_id,),
        ).fetchone() == (0,)
        assert connection.execute(
            "SELECT count(*) FROM pg_catalog.pg_roles WHERE rolname = %s", (role_name,)
        ).fetchone() == (0,)


def test_ambiguous_secret_handoff_is_compensated_by_known_revision(database_dsn: str) -> None:
    """A timeout after a secret write still removes the known staged revision."""

    tenant_id = _tenant_id(database_dsn)
    role_name = tenant_runtime_role_name(tenant_id)
    store = _RevisionedSecretStore(fail_after_put=True)
    provisioner = TenantDatabaseProvisioner(
        database_dsn,
        store,
        password_factory=_password_factory(_FIRST_PASSWORD),
    )

    with pytest.raises(TenantProvisioningError, match="provisioning failed"):
        provisioner.provision(_request(tenant_id))

    assert store.credentials == {}
    assert store.deleted == [(tenant_id, role_name, 1)]
    with psycopg.connect(database_dsn, autocommit=True) as connection:
        assert connection.execute(
            "SELECT count(*) FROM brain_security.tenant_runtime_identities WHERE tenant_id = %s",
            (tenant_id,),
        ).fetchone() == (0,)
        assert connection.execute(
            "SELECT count(*) FROM pg_catalog.pg_roles WHERE rolname = %s", (role_name,)
        ).fetchone() == (0,)


def test_rotation_and_deprovisioning_revoke_old_and_live_sessions(database_dsn: str) -> None:
    """Rotation and deprovisioning kill live sessions and deny stale credentials."""

    first_password = _FIRST_PASSWORD
    second_password = _SECOND_PASSWORD
    tenant_id = _tenant_id(database_dsn)
    store = _RevisionedSecretStore()
    provisioner = TenantDatabaseProvisioner(
        database_dsn,
        store,
        password_factory=_password_factory(first_password, second_password),
    )
    old_connection: psycopg.Connection[tuple[object, ...]] | None = None
    rotated_connection: psycopg.Connection[tuple[object, ...]] | None = None
    try:
        provisioner.provision(_request(tenant_id))
        old_connection = psycopg.connect(
            _runtime_dsn(database_dsn, tenant_id, first_password), autocommit=True
        )
        rotated = provisioner.rotate(tenant_id=tenant_id)

        assert rotated.credential_revision == 2
        with pytest.raises(psycopg.Error):
            old_connection.execute("SELECT 1")
        with pytest.raises(psycopg.OperationalError):
            psycopg.connect(_runtime_dsn(database_dsn, tenant_id, first_password), autocommit=True)
        rotated_connection = psycopg.connect(
            _runtime_dsn(database_dsn, tenant_id, second_password), autocommit=True
        )
        assert rotated_connection.execute("SELECT brain_security.bound_tenant_id()").fetchone() == (
            tenant_id,
        )

        deprovisioned = provisioner.deprovision(tenant_id=tenant_id)
        assert deprovisioned.credential_revision == 3
        with pytest.raises(psycopg.Error):
            rotated_connection.execute("SELECT 1")
        with pytest.raises(psycopg.OperationalError):
            psycopg.connect(_runtime_dsn(database_dsn, tenant_id, second_password), autocommit=True)
        assert store.credentials == {}
    finally:
        if old_connection is not None:
            old_connection.close()
        if rotated_connection is not None:
            rotated_connection.close()
        _cleanup_role(database_dsn, tenant_id)


def test_failed_rotation_compensates_new_secret_revision(database_dsn: str) -> None:
    """A post-handoff database failure removes the staged secret and restores old access."""

    first_password = _FIRST_PASSWORD
    second_password = _SECOND_PASSWORD
    tenant_id = _tenant_id(database_dsn)
    store = _RevisionedSecretStore()
    provisioner = TenantDatabaseProvisioner(
        database_dsn,
        store,
        password_factory=_password_factory(first_password, second_password),
    )
    try:
        provisioner.provision(_request(tenant_id))
        with psycopg.connect(database_dsn, autocommit=True) as connection:
            connection.execute(
                "CREATE FUNCTION brain_security.fail_rotation_event() RETURNS trigger "
                "LANGUAGE plpgsql AS $$ BEGIN IF NEW.operation = 'rotated' THEN "
                "RAISE EXCEPTION 'injected rotation audit failure'; END IF; RETURN NEW; END; $$"
            )
            connection.execute(
                "CREATE TRIGGER injected_rotation_failure BEFORE INSERT ON "
                "brain_security.tenant_runtime_identity_events FOR EACH ROW "
                "EXECUTE FUNCTION brain_security.fail_rotation_event()"
            )
        try:
            with pytest.raises(TenantProvisioningError, match="rotation failed"):
                provisioner.rotate(tenant_id=tenant_id)
        finally:
            with psycopg.connect(database_dsn, autocommit=True) as connection:
                connection.execute(
                    "DROP TRIGGER injected_rotation_failure ON "
                    "brain_security.tenant_runtime_identity_events"
                )
                connection.execute("DROP FUNCTION brain_security.fail_rotation_event()")

        assert set(store.credentials) == {(tenant_id, tenant_runtime_role_name(tenant_id), 1)}
        assert store.deleted[-1] == (
            tenant_id,
            tenant_runtime_role_name(tenant_id),
            2,
        )
        with psycopg.connect(
            _runtime_dsn(database_dsn, tenant_id, first_password), autocommit=True
        ):
            pass
        with pytest.raises(psycopg.OperationalError):
            psycopg.connect(_runtime_dsn(database_dsn, tenant_id, second_password), autocommit=True)
    finally:
        _cleanup_role(database_dsn, tenant_id)


def test_weak_generated_password_is_rejected_before_any_state_change(database_dsn: str) -> None:
    """Provisioning owns password quality and fails before catalog, role, or secret changes."""

    tenant_id = _tenant_id(database_dsn)
    role_name = tenant_runtime_role_name(tenant_id)
    store = _RevisionedSecretStore()
    provisioner = TenantDatabaseProvisioner(
        database_dsn,
        store,
        password_factory=_password_factory("A" * 48),
    )

    with pytest.raises(TenantProvisioningError, match="insufficient entropy"):
        provisioner.provision(_request(tenant_id))

    assert store.credentials == {}
    with psycopg.connect(database_dsn, autocommit=True) as connection:
        assert connection.execute(
            "SELECT count(*) FROM brain_catalog.tenants WHERE tenant_id = %s", (tenant_id,)
        ).fetchone() == (0,)
        assert connection.execute(
            "SELECT count(*) FROM pg_catalog.pg_roles WHERE rolname = %s", (role_name,)
        ).fetchone() == (0,)


def test_provisioner_cannot_bypass_atomic_identity_lifecycle_functions(
    database_dsn: str,
) -> None:
    """The provisioner cannot directly remap identities or forge lifecycle evidence."""

    tenant_id = _tenant_id(database_dsn)
    provisioner = TenantDatabaseProvisioner(
        database_dsn,
        _RevisionedSecretStore(),
        password_factory=_password_factory(_FIRST_PASSWORD),
    )
    try:
        provisioner.provision(_request(tenant_id))
        statements = (
            (
                "UPDATE brain_security.tenant_runtime_identities "
                "SET tenant_id = 'forged-tenant' WHERE tenant_id = %s",
                (tenant_id,),
            ),
            (
                "INSERT INTO brain_security.tenant_runtime_identity_events "
                "(tenant_id, database_role, operation, credential_revision, "
                "authenticated_database_actor, evidence) "
                "VALUES (%s, 'forged-role', 'rotated', 99, session_user, '{}'::jsonb)",
                (tenant_id,),
            ),
            (
                "SELECT brain_security.register_tenant_runtime_identity("
                "'neural_brain_provisioner', %s, 'secret://forged')",
                (tenant_id,),
            ),
        )
        with psycopg.connect(database_dsn, autocommit=True) as connection:
            for statement, parameters in statements:
                with pytest.raises(psycopg.errors.InsufficientPrivilege), connection.transaction():
                    connection.execute("SET LOCAL ROLE neural_brain_provisioner")
                    connection.execute(statement, parameters)
            assert connection.execute(
                "SELECT count(*) FROM brain_security.tenant_runtime_identity_events "
                "WHERE tenant_id = %s",
                (tenant_id,),
            ).fetchone() == (1,)
    finally:
        _cleanup_role(database_dsn, tenant_id)


def test_secret_cleanup_failure_is_reported_as_reconciliation_required(
    database_dsn: str,
) -> None:
    """Failed compensation is explicit and never reported as a clean rollback."""

    tenant_id = _tenant_id(database_dsn)
    role_name = tenant_runtime_role_name(tenant_id)
    store = _RevisionedSecretStore(fail_delete=True)
    provisioner = TenantDatabaseProvisioner(
        database_dsn,
        store,
        password_factory=_password_factory(_FIRST_PASSWORD),
    )
    with psycopg.connect(database_dsn, autocommit=True) as connection:
        connection.execute(
            "CREATE FUNCTION brain_security.fail_provision_event() RETURNS trigger "
            "LANGUAGE plpgsql AS $$ BEGIN IF NEW.operation = 'provisioned' THEN "
            "RAISE EXCEPTION 'injected provision audit failure'; END IF; RETURN NEW; END; $$"
        )
        connection.execute(
            "CREATE TRIGGER injected_provision_failure BEFORE INSERT ON "
            "brain_security.tenant_runtime_identity_events FOR EACH ROW "
            "EXECUTE FUNCTION brain_security.fail_provision_event()"
        )
    try:
        with pytest.raises(TenantProvisioningError, match="cleanup requires reconciliation"):
            provisioner.provision(_request(tenant_id))
    finally:
        with psycopg.connect(database_dsn, autocommit=True) as connection:
            connection.execute(
                "DROP TRIGGER injected_provision_failure ON "
                "brain_security.tenant_runtime_identity_events"
            )
            connection.execute("DROP FUNCTION brain_security.fail_provision_event()")

    assert set(store.credentials) == {(tenant_id, role_name, 1)}
    with psycopg.connect(database_dsn, autocommit=True) as connection:
        assert connection.execute(
            "SELECT count(*) FROM brain_security.tenant_runtime_identities WHERE tenant_id = %s",
            (tenant_id,),
        ).fetchone() == (0,)
        assert connection.execute(
            "SELECT count(*) FROM pg_catalog.pg_roles WHERE rolname = %s", (role_name,)
        ).fetchone() == (0,)


def test_registration_gate_rejects_tenant_shaped_roles_with_unsafe_state(
    database_dsn: str,
) -> None:
    """A direct provisioner call cannot bind an administrative or object-owning login."""

    tenant_id = _tenant_id(database_dsn)
    digests = [
        hashlib.sha256(f"{tenant_id}:{variant}".encode()).hexdigest()[:24]
        for variant in ("admin", "owner")
    ]
    unsafe_roles = [f"neural_brain_tenant_{digest}_runtime" for digest in digests]
    owned_schema = f"unsafe_tenant_role_{digests[1]}"
    with psycopg.connect(database_dsn, autocommit=True) as connection:
        try:
            connection.execute(
                sql.SQL(
                    "CREATE ROLE {} LOGIN CREATEROLE NOINHERIT NOSUPERUSER "
                    "NOCREATEDB NOREPLICATION NOBYPASSRLS"
                ).format(sql.Identifier(unsafe_roles[0]))
            )
            connection.execute(
                sql.SQL(
                    "CREATE ROLE {} LOGIN NOCREATEROLE NOINHERIT NOSUPERUSER "
                    "NOCREATEDB NOREPLICATION NOBYPASSRLS"
                ).format(sql.Identifier(unsafe_roles[1]))
            )
            for role_name in unsafe_roles:
                connection.execute(
                    sql.SQL(
                        "GRANT neural_brain_gate, neural_brain_reader TO {} "
                        "WITH ADMIN FALSE, INHERIT FALSE, SET TRUE"
                    ).format(sql.Identifier(role_name))
                )
            connection.execute(
                sql.SQL("CREATE SCHEMA {} AUTHORIZATION {}").format(
                    sql.Identifier(owned_schema), sql.Identifier(unsafe_roles[1])
                )
            )

            for role_name in unsafe_roles:
                with pytest.raises(psycopg.errors.InsufficientPrivilege), connection.transaction():
                    connection.execute("SET LOCAL ROLE neural_brain_provisioner")
                    connection.execute(
                        "SELECT brain_security.register_tenant_runtime_identity(%s, %s, %s)",
                        (role_name, tenant_id, "secret://forged"),
                    )
        finally:
            connection.execute(
                sql.SQL("DROP SCHEMA IF EXISTS {} CASCADE").format(sql.Identifier(owned_schema))
            )
            for role_name in unsafe_roles:
                connection.execute(
                    sql.SQL("REVOKE neural_brain_gate, neural_brain_reader FROM {}").format(
                        sql.Identifier(role_name)
                    )
                )
                connection.execute(
                    sql.SQL("DROP ROLE IF EXISTS {}").format(sql.Identifier(role_name))
                )
