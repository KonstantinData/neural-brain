CREATE SCHEMA brain_catalog AUTHORIZATION neural_brain_owner;
CREATE SCHEMA brain_security AUTHORIZATION neural_brain_owner;
CREATE SCHEMA memory_core AUTHORIZATION neural_brain_owner;
CREATE SCHEMA memory_audit AUTHORIZATION neural_brain_owner;
CREATE SCHEMA memory_gate AUTHORIZATION neural_brain_owner;

REVOKE ALL ON SCHEMA brain_catalog, brain_security, memory_core, memory_audit, memory_gate
FROM PUBLIC;

CREATE TABLE brain_catalog.brains (
    brain_id text PRIMARY KEY,
    display_name text NOT NULL,
    singleton_key boolean NOT NULL DEFAULT true CHECK (singleton_key),
    created_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
    UNIQUE (singleton_key),
    CHECK (brain_id <> '' AND length(brain_id) <= 128)
);

CREATE TABLE brain_catalog.tenants (
    tenant_id text PRIMARY KEY,
    brain_id text NOT NULL REFERENCES brain_catalog.brains (brain_id),
    display_name text NOT NULL,
    status text NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'suspended', 'retired')),
    created_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
    CHECK (tenant_id <> '' AND length(tenant_id) <= 128)
);

CREATE TABLE brain_catalog.areas (
    tenant_id text NOT NULL,
    area_id text NOT NULL,
    display_name text NOT NULL,
    status text NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'suspended', 'retired')),
    created_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
    PRIMARY KEY (tenant_id, area_id),
    FOREIGN KEY (tenant_id) REFERENCES brain_catalog.tenants (tenant_id),
    CHECK (area_id <> '' AND length(area_id) <= 128)
);

CREATE TABLE brain_catalog.projects (
    tenant_id text NOT NULL,
    area_id text NOT NULL,
    project_id text NOT NULL,
    display_name text NOT NULL,
    status text NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'suspended', 'retired')),
    created_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
    PRIMARY KEY (tenant_id, area_id, project_id),
    FOREIGN KEY (tenant_id, area_id)
        REFERENCES brain_catalog.areas (tenant_id, area_id),
    CHECK (project_id <> '' AND length(project_id) <= 128)
);

CREATE TABLE brain_catalog.sessions (
    tenant_id text NOT NULL,
    area_id text NOT NULL,
    session_id text NOT NULL,
    project_id text NOT NULL,
    activity_state text NOT NULL DEFAULT 'inactive'
        CHECK (activity_state IN ('active', 'inactive', 'reconciling')),
    activity_expires_at timestamptz,
    created_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
    PRIMARY KEY (tenant_id, area_id, session_id),
    UNIQUE (tenant_id, area_id, project_id, session_id),
    FOREIGN KEY (tenant_id, area_id)
        REFERENCES brain_catalog.areas (tenant_id, area_id),
    FOREIGN KEY (tenant_id, area_id, project_id)
        REFERENCES brain_catalog.projects (tenant_id, area_id, project_id),
    CHECK (session_id <> '' AND length(session_id) <= 128),
    CHECK (
        (activity_state = 'inactive' AND activity_expires_at IS NULL)
        OR (activity_state IN ('active', 'reconciling') AND activity_expires_at IS NOT NULL)
    )
);

ALTER TABLE brain_catalog.brains OWNER TO neural_brain_owner;
ALTER TABLE brain_catalog.tenants OWNER TO neural_brain_owner;
ALTER TABLE brain_catalog.areas OWNER TO neural_brain_owner;
ALTER TABLE brain_catalog.projects OWNER TO neural_brain_owner;
ALTER TABLE brain_catalog.sessions OWNER TO neural_brain_owner;

CREATE TABLE brain_security.principals (
    principal_id text PRIMARY KEY,
    authenticated_subject text NOT NULL UNIQUE,
    status text NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'disabled', 'retired')),
    created_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
    CHECK (principal_id <> '' AND length(principal_id) <= 128),
    CHECK (authenticated_subject <> '' AND length(authenticated_subject) <= 512)
);

CREATE TABLE brain_security.principal_scope_bindings (
    principal_id text NOT NULL REFERENCES brain_security.principals (principal_id),
    tenant_id text NOT NULL,
    area_id text NOT NULL,
    can_ingest boolean NOT NULL DEFAULT false,
    can_read boolean NOT NULL DEFAULT false,
    can_dream boolean NOT NULL DEFAULT false,
    valid_until timestamptz,
    created_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
    PRIMARY KEY (principal_id, tenant_id, area_id),
    FOREIGN KEY (tenant_id, area_id)
        REFERENCES brain_catalog.areas (tenant_id, area_id),
    CHECK (can_ingest OR can_read OR can_dream)
);

ALTER TABLE brain_security.principals OWNER TO neural_brain_owner;
ALTER TABLE brain_security.principal_scope_bindings OWNER TO neural_brain_owner;

ALTER TABLE brain_catalog.tenants ENABLE ROW LEVEL SECURITY;
ALTER TABLE brain_catalog.tenants FORCE ROW LEVEL SECURITY;
ALTER TABLE brain_catalog.areas ENABLE ROW LEVEL SECURITY;
ALTER TABLE brain_catalog.areas FORCE ROW LEVEL SECURITY;
ALTER TABLE brain_catalog.projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE brain_catalog.projects FORCE ROW LEVEL SECURITY;
ALTER TABLE brain_catalog.sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE brain_catalog.sessions FORCE ROW LEVEL SECURITY;

CREATE FUNCTION brain_security.context_value(setting_name text)
RETURNS text
LANGUAGE plpgsql
STABLE
SET search_path = pg_catalog
AS $$
DECLARE
    value text;
BEGIN
    value := NULLIF(pg_catalog.current_setting(setting_name, true), '');
    IF value IS NULL THEN
        RAISE EXCEPTION 'trusted runtime context is missing %', setting_name
            USING ERRCODE = '28000';
    END IF;
    RETURN value;
END;
$$;

CREATE FUNCTION brain_security.assert_scope_authority(required_operation text)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog
AS $$
DECLARE
    context_principal text := brain_security.context_value('neural_brain.principal_id');
    context_tenant text := brain_security.context_value('neural_brain.tenant_id');
    context_area text := brain_security.context_value('neural_brain.area_id');
BEGIN
    IF required_operation NOT IN ('ingest', 'read', 'dream') THEN
        RAISE EXCEPTION 'unknown memory operation'
            USING ERRCODE = '42501';
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM brain_security.principals AS principal
        JOIN brain_security.principal_scope_bindings AS binding
          ON binding.principal_id = principal.principal_id
        JOIN brain_catalog.areas AS area
          ON area.tenant_id = binding.tenant_id
         AND area.area_id = binding.area_id
        JOIN brain_catalog.tenants AS tenant
          ON tenant.tenant_id = binding.tenant_id
        WHERE principal.principal_id = context_principal
          AND binding.tenant_id = context_tenant
          AND binding.area_id = context_area
          AND principal.status = 'active'
          AND tenant.status = 'active'
          AND area.status = 'active'
          AND (binding.valid_until IS NULL OR binding.valid_until > statement_timestamp())
          AND CASE required_operation
                WHEN 'ingest' THEN binding.can_ingest
                WHEN 'read' THEN binding.can_read
                WHEN 'dream' THEN binding.can_dream
                ELSE false
              END
    ) THEN
        RAISE EXCEPTION 'principal has no valid authority for the trusted scope and operation'
            USING ERRCODE = '42501';
    END IF;
END;
$$;

ALTER FUNCTION brain_security.context_value(text) OWNER TO neural_brain_owner;
ALTER FUNCTION brain_security.assert_scope_authority(text) OWNER TO neural_brain_owner;
REVOKE ALL ON FUNCTION brain_security.context_value(text) FROM PUBLIC;
REVOKE ALL ON FUNCTION brain_security.assert_scope_authority(text) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION brain_security.assert_scope_authority(text)
TO neural_brain_gate, neural_brain_reader, neural_brain_dreamer;

CREATE POLICY tenant_scope_select ON brain_catalog.tenants
FOR SELECT
USING (tenant_id = NULLIF(pg_catalog.current_setting('neural_brain.tenant_id', true), ''));

CREATE POLICY area_scope_select ON brain_catalog.areas
FOR SELECT
USING (
    tenant_id = NULLIF(pg_catalog.current_setting('neural_brain.tenant_id', true), '')
    AND area_id = NULLIF(pg_catalog.current_setting('neural_brain.area_id', true), '')
);

CREATE POLICY project_scope_select ON brain_catalog.projects
FOR SELECT
USING (
    tenant_id = NULLIF(pg_catalog.current_setting('neural_brain.tenant_id', true), '')
    AND area_id = NULLIF(pg_catalog.current_setting('neural_brain.area_id', true), '')
);

CREATE POLICY session_scope_select ON brain_catalog.sessions
FOR SELECT
USING (
    tenant_id = NULLIF(pg_catalog.current_setting('neural_brain.tenant_id', true), '')
    AND area_id = NULLIF(pg_catalog.current_setting('neural_brain.area_id', true), '')
);

GRANT USAGE ON SCHEMA brain_catalog, brain_security
TO neural_brain_gate, neural_brain_reader, neural_brain_dreamer;
GRANT SELECT ON brain_catalog.tenants, brain_catalog.areas, brain_catalog.projects,
    brain_catalog.sessions
TO neural_brain_gate, neural_brain_reader, neural_brain_dreamer;

REVOKE ALL ON ALL TABLES IN SCHEMA brain_security FROM PUBLIC;
REVOKE ALL ON ALL TABLES IN SCHEMA brain_catalog FROM PUBLIC;
