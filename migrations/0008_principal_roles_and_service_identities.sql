-- S1-01.1: versioned principal roles, scoped role bindings, and service identities.
-- Existing principal_scope_bindings remain the operation-capability boundary;
-- this catalog adds typed, revocable identity governance without widening it.

ALTER TABLE brain_security.principals
    ADD COLUMN principal_kind text NOT NULL DEFAULT 'human'
        CHECK (principal_kind IN ('human', 'service')),
    ADD COLUMN valid_from timestamptz NOT NULL DEFAULT transaction_timestamp(),
    ADD COLUMN valid_until timestamptz;

ALTER TABLE brain_security.principals
    ADD CONSTRAINT principals_validity_window_check
    CHECK (valid_until IS NULL OR valid_until > valid_from);

CREATE TABLE brain_security.roles (
    role_id text PRIMARY KEY,
    display_name text NOT NULL,
    status text NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'disabled', 'retired')),
    created_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
    CHECK (role_id <> '' AND length(role_id) <= 128),
    CHECK (display_name <> '' AND length(display_name) <= 256)
);

CREATE TABLE brain_security.principal_role_bindings (
    role_binding_id text PRIMARY KEY,
    principal_id text NOT NULL REFERENCES brain_security.principals (principal_id),
    role_id text NOT NULL REFERENCES brain_security.roles (role_id),
    tenant_id text NOT NULL,
    area_id text NOT NULL,
    project_id text,
    session_id text,
    status text NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'disabled', 'revoked', 'expired')),
    valid_from timestamptz NOT NULL DEFAULT transaction_timestamp(),
    valid_until timestamptz,
    created_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
    FOREIGN KEY (tenant_id, area_id)
        REFERENCES brain_catalog.areas (tenant_id, area_id),
    FOREIGN KEY (tenant_id, area_id, project_id)
        REFERENCES brain_catalog.projects (tenant_id, area_id, project_id),
    FOREIGN KEY (tenant_id, area_id, project_id, session_id)
        REFERENCES brain_catalog.sessions (tenant_id, area_id, project_id, session_id),
    CHECK (role_binding_id <> '' AND length(role_binding_id) <= 128),
    CHECK (valid_until IS NULL OR valid_until > valid_from),
    CHECK (session_id IS NULL OR project_id IS NOT NULL)
);

CREATE TABLE brain_security.service_identities (
    service_identity_id text PRIMARY KEY,
    principal_id text NOT NULL UNIQUE REFERENCES brain_security.principals (principal_id),
    runtime_component_id text NOT NULL UNIQUE,
    status text NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'disabled', 'retired')),
    valid_from timestamptz NOT NULL DEFAULT transaction_timestamp(),
    valid_until timestamptz,
    created_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
    CHECK (service_identity_id <> '' AND length(service_identity_id) <= 128),
    CHECK (runtime_component_id <> '' AND length(runtime_component_id) <= 128),
    CHECK (valid_until IS NULL OR valid_until > valid_from)
);

CREATE FUNCTION brain_security.assert_service_identity_principal_kind()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog
AS $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM brain_security.principals AS principal
        WHERE principal.principal_id = NEW.principal_id
          AND principal.principal_kind = 'service'
          AND principal.status = 'active'
          AND (principal.valid_until IS NULL OR principal.valid_until > statement_timestamp())
    ) THEN
        RAISE EXCEPTION 'service identity requires an active, valid service principal'
            USING ERRCODE = '42501';
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER service_identity_principal_kind_guard
BEFORE INSERT OR UPDATE OF principal_id ON brain_security.service_identities
FOR EACH ROW EXECUTE FUNCTION brain_security.assert_service_identity_principal_kind();

ALTER TABLE brain_security.roles OWNER TO neural_brain_owner;
ALTER TABLE brain_security.principal_role_bindings OWNER TO neural_brain_owner;
ALTER TABLE brain_security.service_identities OWNER TO neural_brain_owner;
ALTER FUNCTION brain_security.assert_service_identity_principal_kind() OWNER TO neural_brain_owner;
REVOKE ALL ON brain_security.roles, brain_security.principal_role_bindings,
    brain_security.service_identities FROM PUBLIC;
REVOKE ALL ON FUNCTION brain_security.assert_service_identity_principal_kind() FROM PUBLIC;
