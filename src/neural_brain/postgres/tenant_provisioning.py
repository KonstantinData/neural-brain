"""Controlled lifecycle for one PostgreSQL runtime identity per Tenant."""

from __future__ import annotations

import hashlib
import secrets
from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol

import psycopg
from psycopg import sql


class TenantSecretStore(Protocol):
    """External secret custody used by the provisioning control path."""

    def put_database_credential(
        self, *, tenant_id: str, database_role: str, password: str, revision: int
    ) -> str:
        """Store a credential and return a non-secret reference."""
        ...

    def delete_database_credential(
        self, *, tenant_id: str, database_role: str, revision: int | None = None
    ) -> None:
        """Delete one staged revision or every credential for a deprovisioned Tenant."""
        ...


@dataclass(frozen=True, slots=True)
class TenantProvisioningRequest:
    """Trusted administrative inputs for an atomic Tenant identity provision."""

    tenant_id: str
    brain_id: str
    display_name: str


@dataclass(frozen=True, slots=True)
class TenantIdentityEvidence:
    """Secret-free, revision-safe lifecycle evidence."""

    tenant_id: str
    database_role: str
    credential_revision: int
    operation: str
    secret_reference: str | None
    verified: bool


class TenantProvisioningError(RuntimeError):
    """Raised when the controlled Tenant identity lifecycle fails closed."""


def tenant_runtime_role_name(tenant_id: str) -> str:
    """Derive a stable, non-identifying PostgreSQL role name from a Tenant ID."""

    _validate_identifier(tenant_id, "tenant_id")
    digest = hashlib.sha256(tenant_id.encode("utf-8")).hexdigest()[:24]
    return f"neural_brain_tenant_{digest}_runtime"


def generate_database_password() -> str:
    """Generate a high-entropy credential without persisting or logging it."""

    return secrets.token_urlsafe(48)


class TenantDatabaseProvisioner:
    """Run Tenant login lifecycle operations through one audited admin transaction."""

    def __init__(
        self,
        admin_dsn: str,
        secret_store: TenantSecretStore,
        *,
        password_factory: Callable[[], str] = generate_database_password,
    ) -> None:
        self._admin_dsn = admin_dsn
        self._secret_store = secret_store
        self._password_factory = password_factory

    def provision(self, request: TenantProvisioningRequest) -> TenantIdentityEvidence:
        """Provision catalog, login, mapping, memberships, secret, and verification."""

        _validate_identifier(request.tenant_id, "tenant_id")
        _validate_identifier(request.brain_id, "brain_id")
        if not request.display_name or len(request.display_name) > 256:
            raise TenantProvisioningError("Tenant display name is invalid")
        role_name = tenant_runtime_role_name(request.tenant_id)
        secret_reference: str | None = None
        secret_put_attempted = False
        role_created = False
        connection = psycopg.connect(self._admin_dsn)
        try:
            with connection.cursor() as cursor:
                self._require_administrative_actor(cursor)
                cursor.execute(
                    "SELECT pg_catalog.pg_advisory_xact_lock(pg_catalog.hashtextextended(%s, 0))",
                    (f"neural-brain-tenant:{request.tenant_id}",),
                )
                existing = self._identity_row(cursor, request.tenant_id)
                if existing is not None:
                    existing_role, status, revision = existing
                    if existing_role != role_name or status != "active":
                        raise TenantProvisioningError(
                            "Existing Tenant identity conflicts with the provisioning request"
                        )
                    self._verify_identity(cursor, request.tenant_id, role_name)
                    connection.rollback()
                    return TenantIdentityEvidence(
                        tenant_id=request.tenant_id,
                        database_role=role_name,
                        credential_revision=revision,
                        operation="provisioned",
                        secret_reference=None,
                        verified=True,
                    )

                cursor.execute(
                    "SELECT 1 FROM brain_catalog.brains WHERE brain_id = %s",
                    (request.brain_id,),
                )
                if cursor.fetchone() is None:
                    raise TenantProvisioningError("Requested Brain does not exist")
                cursor.execute(
                    "INSERT INTO brain_catalog.tenants (tenant_id, brain_id, display_name) "
                    "VALUES (%s, %s, %s) ON CONFLICT (tenant_id) DO NOTHING",
                    (request.tenant_id, request.brain_id, request.display_name),
                )
                cursor.execute(
                    "SELECT brain_id, display_name, status FROM brain_catalog.tenants "
                    "WHERE tenant_id = %s",
                    (request.tenant_id,),
                )
                if cursor.fetchone() != (request.brain_id, request.display_name, "active"):
                    raise TenantProvisioningError(
                        "Existing Tenant catalog entry conflicts with the request"
                    )
                password = self._new_password()
                cursor.execute(
                    sql.SQL(
                        "CREATE ROLE {} LOGIN PASSWORD {} NOSUPERUSER NOCREATEDB "
                        "NOCREATEROLE NOINHERIT NOREPLICATION NOBYPASSRLS"
                    ).format(sql.Identifier(role_name), sql.Literal(password))
                )
                role_created = True
                cursor.execute(
                    sql.SQL(
                        "GRANT neural_brain_gate, neural_brain_reader TO {} "
                        "WITH ADMIN FALSE, INHERIT FALSE, SET TRUE"
                    ).format(sql.Identifier(role_name))
                )
                cursor.execute("SELECT current_database()")
                database_row = cursor.fetchone()
                if database_row is None or not isinstance(database_row[0], str):
                    raise TenantProvisioningError("Current database identity is unavailable")
                cursor.execute(
                    sql.SQL("REVOKE ALL ON DATABASE {} FROM {}").format(
                        sql.Identifier(database_row[0]), sql.Identifier(role_name)
                    )
                )
                cursor.execute(
                    sql.SQL("GRANT CONNECT ON DATABASE {} TO {}").format(
                        sql.Identifier(database_row[0]), sql.Identifier(role_name)
                    )
                )
                cursor.execute(
                    sql.SQL("GRANT USAGE ON SCHEMA brain_security TO {}").format(
                        sql.Identifier(role_name)
                    )
                )
                secret_put_attempted = True
                secret_reference = self._secret_store.put_database_credential(
                    tenant_id=request.tenant_id,
                    database_role=role_name,
                    password=password,
                    revision=1,
                )
                if not secret_reference:
                    raise TenantProvisioningError("Secret store returned no reference")
                cursor.execute(
                    "SELECT brain_security.register_tenant_runtime_identity(%s, %s, %s)",
                    (role_name, request.tenant_id, secret_reference),
                )
                if cursor.fetchone() != (1,):
                    raise TenantProvisioningError(
                        "Tenant runtime identity registration returned invalid evidence"
                    )
                self._verify_identity(cursor, request.tenant_id, role_name)
            connection.commit()
        except Exception as error:
            connection.rollback()
            if role_created:
                try:
                    self._drop_failed_role(connection, role_name)
                except Exception as cleanup_error:
                    if self._role_exists(role_name):
                        raise TenantProvisioningError(
                            "Tenant provisioning cleanup requires reconciliation"
                        ) from cleanup_error
            if secret_put_attempted:
                try:
                    self._secret_store.delete_database_credential(
                        tenant_id=request.tenant_id,
                        database_role=role_name,
                        revision=1,
                    )
                except Exception as cleanup_error:
                    raise TenantProvisioningError(
                        "Tenant provisioning secret cleanup requires reconciliation"
                    ) from cleanup_error
            if isinstance(error, TenantProvisioningError):
                raise
            raise TenantProvisioningError("Tenant database provisioning failed") from error
        finally:
            connection.close()
        return TenantIdentityEvidence(
            tenant_id=request.tenant_id,
            database_role=role_name,
            credential_revision=1,
            operation="provisioned",
            secret_reference=secret_reference,
            verified=True,
        )

    def rotate(self, *, tenant_id: str) -> TenantIdentityEvidence:
        """Rotate one Tenant credential without creating a shared fallback."""

        _validate_identifier(tenant_id, "tenant_id")
        role_name = tenant_runtime_role_name(tenant_id)
        secret_reference: str | None = None
        secret_put_attempted = False
        connection = psycopg.connect(self._admin_dsn)
        try:
            with connection.cursor() as cursor:
                self._require_administrative_actor(cursor)
                cursor.execute(
                    "SELECT pg_catalog.pg_advisory_xact_lock(pg_catalog.hashtextextended(%s, 0))",
                    (f"neural-brain-tenant:{tenant_id}",),
                )
                existing = self._identity_row(cursor, tenant_id)
                if existing is None or existing[0] != role_name or existing[1] != "active":
                    raise TenantProvisioningError("Tenant database identity is unavailable")
                revision = existing[2] + 1
                password = self._new_password()
                cursor.execute(
                    sql.SQL("ALTER ROLE {} LOGIN PASSWORD {}").format(
                        sql.Identifier(role_name), sql.Literal(password)
                    )
                )
                self._terminate_role_sessions(cursor, role_name)
                self._verify_identity(cursor, tenant_id, role_name)
                secret_put_attempted = True
                secret_reference = self._secret_store.put_database_credential(
                    tenant_id=tenant_id,
                    database_role=role_name,
                    password=password,
                    revision=revision,
                )
                if not secret_reference:
                    raise TenantProvisioningError("Secret store returned no reference")
                cursor.execute(
                    "SELECT brain_security.rotate_tenant_runtime_identity(%s, %s, %s, %s)",
                    (role_name, tenant_id, existing[2], secret_reference),
                )
                if cursor.fetchone() != (revision,):
                    raise TenantProvisioningError(
                        "Tenant credential rotation returned invalid evidence"
                    )
            connection.commit()
        except Exception as error:
            connection.rollback()
            if secret_put_attempted:
                try:
                    self._secret_store.delete_database_credential(
                        tenant_id=tenant_id,
                        database_role=role_name,
                        revision=revision,
                    )
                except Exception as cleanup_error:
                    raise TenantProvisioningError(
                        "Tenant rotation secret cleanup requires reconciliation"
                    ) from cleanup_error
            if isinstance(error, TenantProvisioningError):
                raise
            raise TenantProvisioningError("Tenant credential rotation failed") from error
        finally:
            connection.close()
        return TenantIdentityEvidence(
            tenant_id=tenant_id,
            database_role=role_name,
            credential_revision=revision,
            operation="rotated",
            secret_reference=secret_reference,
            verified=True,
        )

    def _new_password(self) -> str:
        try:
            password = self._password_factory()
        except Exception:
            raise TenantProvisioningError("Tenant database password generation failed") from None
        if not isinstance(password, str) or len(password) < 48 or len(set(password)) < 16:
            raise TenantProvisioningError(
                "Tenant database password generator returned insufficient entropy"
            )
        return password

    def deprovision(self, *, tenant_id: str) -> TenantIdentityEvidence:
        """Revoke the mapping, login, memberships, and externally stored credential."""

        _validate_identifier(tenant_id, "tenant_id")
        role_name = tenant_runtime_role_name(tenant_id)
        connection = psycopg.connect(self._admin_dsn)
        try:
            with connection.cursor() as cursor:
                self._require_administrative_actor(cursor)
                cursor.execute(
                    "SELECT pg_catalog.pg_advisory_xact_lock(pg_catalog.hashtextextended(%s, 0))",
                    (f"neural-brain-tenant:{tenant_id}",),
                )
                existing = self._identity_row(cursor, tenant_id)
                if existing is None or existing[0] != role_name:
                    raise TenantProvisioningError("Tenant database identity is unavailable")
                revision = existing[2] + 1
                cursor.execute(sql.SQL("ALTER ROLE {} NOLOGIN").format(sql.Identifier(role_name)))
                self._terminate_role_sessions(cursor, role_name)
                cursor.execute(
                    sql.SQL("REVOKE neural_brain_gate, neural_brain_reader FROM {}").format(
                        sql.Identifier(role_name)
                    )
                )
                cursor.execute("SELECT current_database()")
                database_row = cursor.fetchone()
                if database_row is None or not isinstance(database_row[0], str):
                    raise TenantProvisioningError("Current database identity is unavailable")
                cursor.execute(
                    sql.SQL("REVOKE CONNECT ON DATABASE {} FROM {}").format(
                        sql.Identifier(database_row[0]), sql.Identifier(role_name)
                    )
                )
                cursor.execute(
                    sql.SQL("REVOKE USAGE ON SCHEMA brain_security FROM {}").format(
                        sql.Identifier(role_name)
                    )
                )
                cursor.execute(
                    "SELECT brain_security.deprovision_tenant_runtime_identity(%s, %s, %s)",
                    (role_name, tenant_id, existing[2]),
                )
                if cursor.fetchone() != (revision,):
                    raise TenantProvisioningError("Tenant deprovisioning returned invalid evidence")
            connection.commit()
        except Exception as error:
            connection.rollback()
            if isinstance(error, TenantProvisioningError):
                raise
            raise TenantProvisioningError("Tenant deprovisioning failed") from error
        finally:
            connection.close()
        try:
            self._secret_store.delete_database_credential(
                tenant_id=tenant_id, database_role=role_name, revision=None
            )
        except Exception as error:
            raise TenantProvisioningError(
                "Tenant access is revoked but secret deletion requires reconciliation"
            ) from error
        return TenantIdentityEvidence(
            tenant_id=tenant_id,
            database_role=role_name,
            credential_revision=revision,
            operation="deprovisioned",
            secret_reference=None,
            verified=True,
        )

    @staticmethod
    def _require_administrative_actor(cursor: psycopg.Cursor[tuple[object, ...]]) -> None:
        cursor.execute(
            "SELECT rolsuper OR pg_catalog.pg_has_role("
            "session_user, 'neural_brain_provisioner', 'MEMBER') "
            "FROM pg_catalog.pg_roles WHERE rolname = session_user"
        )
        row = cursor.fetchone()
        if row != (True,):
            raise TenantProvisioningError(
                "Tenant provisioning requires an authenticated database administrator"
            )
        cursor.execute("SET LOCAL ROLE neural_brain_provisioner")

    @staticmethod
    def _identity_row(
        cursor: psycopg.Cursor[tuple[object, ...]], tenant_id: str
    ) -> tuple[str, str, int] | None:
        cursor.execute(
            "SELECT database_role::text, status, credential_revision "
            "FROM brain_security.tenant_runtime_identities WHERE tenant_id = %s",
            (tenant_id,),
        )
        row = cursor.fetchone()
        if row is None:
            return None
        revision = row[2]
        if not isinstance(revision, int) or isinstance(revision, bool):
            raise TenantProvisioningError("Tenant credential revision is invalid")
        return str(row[0]), str(row[1]), revision

    @staticmethod
    def _verify_identity(
        cursor: psycopg.Cursor[tuple[object, ...]], tenant_id: str, role_name: str
    ) -> None:
        cursor.execute(
            "SELECT rolcanlogin, rolsuper, rolcreatedb, rolcreaterole, rolinherit, "
            "rolreplication, rolbypassrls FROM pg_catalog.pg_roles WHERE rolname = %s",
            (role_name,),
        )
        if cursor.fetchone() != (True, False, False, False, False, False, False):
            raise TenantProvisioningError("Tenant runtime role attributes are unsafe")
        cursor.execute(
            "SELECT granted.rolname, membership.admin_option, membership.inherit_option, "
            "membership.set_option FROM pg_catalog.pg_auth_members AS membership "
            "JOIN pg_catalog.pg_roles AS granted ON granted.oid = membership.roleid "
            "JOIN pg_catalog.pg_roles AS member ON member.oid = membership.member "
            "WHERE member.rolname = %s ORDER BY granted.rolname",
            (role_name,),
        )
        if cursor.fetchall() != [
            ("neural_brain_gate", False, False, True),
            ("neural_brain_reader", False, False, True),
        ]:
            raise TenantProvisioningError("Tenant runtime role memberships are unsafe")
        cursor.execute(
            "SELECT tenant_id, status FROM brain_security.tenant_runtime_identities "
            "WHERE database_role = %s",
            (role_name,),
        )
        if cursor.fetchone() != (tenant_id, "active"):
            raise TenantProvisioningError("Tenant runtime identity mapping is invalid")
        cursor.execute(
            "SELECT EXISTS ("
            "SELECT 1 FROM pg_catalog.pg_class WHERE relowner = ("
            "SELECT oid FROM pg_catalog.pg_roles WHERE rolname = %s))",
            (role_name,),
        )
        if cursor.fetchone() != (False,):
            raise TenantProvisioningError("Tenant runtime role owns database relations")

    @staticmethod
    def _terminate_role_sessions(
        cursor: psycopg.Cursor[tuple[object, ...]], role_name: str
    ) -> None:
        cursor.execute(
            "SELECT pg_catalog.pg_terminate_backend(activity.pid) "
            "FROM pg_catalog.pg_stat_activity AS activity "
            "WHERE activity.usename = %s AND activity.pid <> pg_catalog.pg_backend_pid()",
            (role_name,),
        )
        if any(row != (True,) for row in cursor.fetchall()):
            raise TenantProvisioningError("Tenant runtime sessions could not be terminated")

    @staticmethod
    def _drop_failed_role(
        connection: psycopg.Connection[tuple[object, ...]], role_name: str
    ) -> None:
        with connection.cursor() as cursor:
            database_name_row = cursor.execute("SELECT current_database()").fetchone()
            if database_name_row is None:
                raise TenantProvisioningError("Current database identity is unavailable")
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
            cursor.execute(sql.SQL("DROP ROLE {}").format(sql.Identifier(role_name)))
        connection.commit()

    def _role_exists(self, role_name: str) -> bool:
        with psycopg.connect(self._admin_dsn, autocommit=True) as connection:
            row = connection.execute(
                "SELECT EXISTS (SELECT 1 FROM pg_catalog.pg_roles WHERE rolname = %s)",
                (role_name,),
            ).fetchone()
        return row == (True,)


def _validate_identifier(value: str, label: str) -> None:
    if not value or len(value) > 128:
        raise TenantProvisioningError(f"{label} is invalid")
