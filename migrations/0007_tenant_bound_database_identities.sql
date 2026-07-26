CREATE TABLE brain_security.tenant_runtime_identities (
    database_role name PRIMARY KEY,
    tenant_id text NOT NULL UNIQUE REFERENCES brain_catalog.tenants (tenant_id),
    status text NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'revoked')),
    credential_revision bigint NOT NULL DEFAULT 1 CHECK (credential_revision > 0),
    created_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
    updated_at timestamptz NOT NULL DEFAULT transaction_timestamp()
);

ALTER TABLE brain_security.tenant_runtime_identities OWNER TO neural_brain_owner;
REVOKE ALL ON brain_security.tenant_runtime_identities FROM PUBLIC;

CREATE TABLE brain_security.tenant_runtime_identity_events (
    event_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tenant_id text NOT NULL,
    database_role name NOT NULL,
    operation text NOT NULL CHECK (
        operation IN ('provisioned', 'rotated', 'revoked', 'deprovisioned')
    ),
    credential_revision bigint NOT NULL CHECK (credential_revision > 0),
    authenticated_database_actor name NOT NULL,
    evidence jsonb NOT NULL,
    occurred_at timestamptz NOT NULL DEFAULT transaction_timestamp()
);

ALTER TABLE brain_security.tenant_runtime_identity_events OWNER TO neural_brain_owner;
REVOKE ALL ON brain_security.tenant_runtime_identity_events FROM PUBLIC;

CREATE FUNCTION brain_security.bound_database_identity()
RETURNS TABLE (
    tenant_id text,
    database_name text,
    credential_revision text
)
LANGUAGE plpgsql
SECURITY DEFINER
STABLE
SET search_path = pg_catalog
AS $$
BEGIN
    RETURN QUERY
    SELECT
        identity.tenant_id,
        pg_catalog.current_database()::text,
        identity.credential_revision::text
    FROM brain_security.tenant_runtime_identities AS identity
    WHERE identity.database_role = session_user
      AND identity.status = 'active';

    IF NOT FOUND THEN
        RAISE EXCEPTION 'database login has no active tenant binding'
            USING ERRCODE = '28000';
    END IF;
END;
$$;

CREATE FUNCTION brain_security.bound_tenant_id()
RETURNS text
LANGUAGE sql
SECURITY DEFINER
STABLE
SET search_path = pg_catalog
AS $$
    SELECT identity.tenant_id
    FROM brain_security.bound_database_identity() AS identity;
$$;

CREATE FUNCTION brain_security.assert_tenant_context()
RETURNS text
LANGUAGE plpgsql
SECURITY DEFINER
STABLE
SET search_path = pg_catalog
AS $$
DECLARE
    database_tenant text := brain_security.bound_tenant_id();
    requested_tenant text := brain_security.context_value('neural_brain.tenant_id');
BEGIN
    IF requested_tenant <> database_tenant THEN
        RAISE EXCEPTION 'trusted Tenant context does not match the database login identity'
            USING ERRCODE = '42501';
    END IF;
    RETURN database_tenant;
END;
$$;

CREATE OR REPLACE FUNCTION brain_security.assert_scope_authority(required_operation text)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog
AS $$
DECLARE
    context_principal text := brain_security.context_value('neural_brain.principal_id');
    context_tenant text := brain_security.assert_tenant_context();
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

CREATE OR REPLACE FUNCTION brain_security.resolve_authenticated_principal(
    authenticated_subject text
)
RETURNS text
LANGUAGE plpgsql
SECURITY DEFINER
STABLE
SET search_path = pg_catalog
AS $$
DECLARE
    database_tenant text := brain_security.bound_tenant_id();
    resolved_principal_id text;
BEGIN
    IF authenticated_subject IS NULL
       OR authenticated_subject = ''
       OR length(authenticated_subject) > 512 THEN
        RAISE EXCEPTION 'authenticated subject is invalid'
            USING ERRCODE = '28000';
    END IF;

    SELECT principal.principal_id INTO resolved_principal_id
    FROM brain_security.principals AS principal
    WHERE principal.authenticated_subject = resolve_authenticated_principal.authenticated_subject
      AND principal.status = 'active'
      AND EXISTS (
          SELECT 1
          FROM brain_security.principal_scope_bindings AS binding
          WHERE binding.principal_id = principal.principal_id
            AND binding.tenant_id = database_tenant
            AND (binding.valid_until IS NULL OR binding.valid_until > statement_timestamp())
      );

    IF resolved_principal_id IS NULL THEN
        RAISE EXCEPTION 'authenticated principal is unavailable for database Tenant'
            USING ERRCODE = '28000';
    END IF;

    RETURN resolved_principal_id;
END;
$$;

ALTER FUNCTION brain_security.bound_database_identity() OWNER TO neural_brain_owner;
ALTER FUNCTION brain_security.bound_tenant_id() OWNER TO neural_brain_owner;
ALTER FUNCTION brain_security.assert_tenant_context() OWNER TO neural_brain_owner;
ALTER FUNCTION brain_security.assert_scope_authority(text) OWNER TO neural_brain_owner;
ALTER FUNCTION brain_security.resolve_authenticated_principal(text) OWNER TO neural_brain_owner;

REVOKE ALL ON FUNCTION brain_security.bound_database_identity() FROM PUBLIC;
REVOKE ALL ON FUNCTION brain_security.bound_tenant_id() FROM PUBLIC;
REVOKE ALL ON FUNCTION brain_security.assert_tenant_context() FROM PUBLIC;
REVOKE ALL ON FUNCTION brain_security.assert_scope_authority(text) FROM PUBLIC;
REVOKE ALL ON FUNCTION brain_security.resolve_authenticated_principal(text) FROM PUBLIC;

GRANT EXECUTE ON FUNCTION brain_security.bound_database_identity() TO PUBLIC;
GRANT EXECUTE ON FUNCTION brain_security.bound_tenant_id() TO PUBLIC;
GRANT EXECUTE ON FUNCTION brain_security.assert_tenant_context()
TO neural_brain_gate, neural_brain_reader, neural_brain_dreamer;
GRANT EXECUTE ON FUNCTION brain_security.assert_scope_authority(text)
TO neural_brain_gate, neural_brain_reader, neural_brain_dreamer;
GRANT EXECUTE ON FUNCTION brain_security.resolve_authenticated_principal(text)
TO neural_brain_reader, neural_brain_gate;

DROP POLICY tenant_scope_select ON brain_catalog.tenants;
CREATE POLICY tenant_scope_select ON brain_catalog.tenants
FOR SELECT
USING (
    tenant_id = brain_security.bound_tenant_id()
    AND tenant_id = NULLIF(pg_catalog.current_setting('neural_brain.tenant_id', true), '')
);

DROP POLICY area_scope_select ON brain_catalog.areas;
CREATE POLICY area_scope_select ON brain_catalog.areas
FOR SELECT
USING (
    tenant_id = brain_security.bound_tenant_id()
    AND tenant_id = NULLIF(pg_catalog.current_setting('neural_brain.tenant_id', true), '')
    AND area_id = NULLIF(pg_catalog.current_setting('neural_brain.area_id', true), '')
);

DROP POLICY project_scope_select ON brain_catalog.projects;
CREATE POLICY project_scope_select ON brain_catalog.projects
FOR SELECT
USING (
    tenant_id = brain_security.bound_tenant_id()
    AND tenant_id = NULLIF(pg_catalog.current_setting('neural_brain.tenant_id', true), '')
    AND area_id = NULLIF(pg_catalog.current_setting('neural_brain.area_id', true), '')
);

DROP POLICY session_scope_select ON brain_catalog.sessions;
CREATE POLICY session_scope_select ON brain_catalog.sessions
FOR SELECT
USING (
    tenant_id = brain_security.bound_tenant_id()
    AND tenant_id = NULLIF(pg_catalog.current_setting('neural_brain.tenant_id', true), '')
    AND area_id = NULLIF(pg_catalog.current_setting('neural_brain.area_id', true), '')
);

DROP POLICY audit_scope ON memory_audit.events;
CREATE POLICY audit_scope ON memory_audit.events
USING (
    tenant_id = brain_security.bound_tenant_id()
    AND tenant_id = NULLIF(pg_catalog.current_setting('neural_brain.tenant_id', true), '')
    AND area_id = NULLIF(pg_catalog.current_setting('neural_brain.area_id', true), '')
)
WITH CHECK (
    tenant_id = brain_security.bound_tenant_id()
    AND tenant_id = NULLIF(pg_catalog.current_setting('neural_brain.tenant_id', true), '')
    AND area_id = NULLIF(pg_catalog.current_setting('neural_brain.area_id', true), '')
);

DROP POLICY observation_scope ON memory_core.observations;
CREATE POLICY observation_scope ON memory_core.observations
USING (
    tenant_id = brain_security.bound_tenant_id()
    AND tenant_id = NULLIF(pg_catalog.current_setting('neural_brain.tenant_id', true), '')
    AND area_id = NULLIF(pg_catalog.current_setting('neural_brain.area_id', true), '')
    AND project_id = NULLIF(pg_catalog.current_setting('neural_brain.project_id', true), '')
    AND session_id = NULLIF(pg_catalog.current_setting('neural_brain.session_id', true), '')
)
WITH CHECK (
    tenant_id = brain_security.bound_tenant_id()
    AND tenant_id = NULLIF(pg_catalog.current_setting('neural_brain.tenant_id', true), '')
    AND area_id = NULLIF(pg_catalog.current_setting('neural_brain.area_id', true), '')
    AND project_id = NULLIF(pg_catalog.current_setting('neural_brain.project_id', true), '')
    AND session_id = NULLIF(pg_catalog.current_setting('neural_brain.session_id', true), '')
);

DROP POLICY working_context_scope ON memory_core.working_contexts;
CREATE POLICY working_context_scope ON memory_core.working_contexts
USING (
    tenant_id = brain_security.bound_tenant_id()
    AND tenant_id = NULLIF(pg_catalog.current_setting('neural_brain.tenant_id', true), '')
    AND area_id = NULLIF(pg_catalog.current_setting('neural_brain.area_id', true), '')
    AND project_id = NULLIF(pg_catalog.current_setting('neural_brain.project_id', true), '')
    AND session_id = NULLIF(pg_catalog.current_setting('neural_brain.session_id', true), '')
)
WITH CHECK (
    tenant_id = brain_security.bound_tenant_id()
    AND tenant_id = NULLIF(pg_catalog.current_setting('neural_brain.tenant_id', true), '')
    AND area_id = NULLIF(pg_catalog.current_setting('neural_brain.area_id', true), '')
    AND project_id = NULLIF(pg_catalog.current_setting('neural_brain.project_id', true), '')
    AND session_id = NULLIF(pg_catalog.current_setting('neural_brain.session_id', true), '')
);

DROP POLICY working_version_scope ON memory_core.working_context_versions;
CREATE POLICY working_version_scope ON memory_core.working_context_versions
USING (
    tenant_id = brain_security.bound_tenant_id()
    AND tenant_id = NULLIF(pg_catalog.current_setting('neural_brain.tenant_id', true), '')
    AND area_id = NULLIF(pg_catalog.current_setting('neural_brain.area_id', true), '')
    AND project_id = NULLIF(pg_catalog.current_setting('neural_brain.project_id', true), '')
    AND session_id = NULLIF(pg_catalog.current_setting('neural_brain.session_id', true), '')
)
WITH CHECK (
    tenant_id = brain_security.bound_tenant_id()
    AND tenant_id = NULLIF(pg_catalog.current_setting('neural_brain.tenant_id', true), '')
    AND area_id = NULLIF(pg_catalog.current_setting('neural_brain.area_id', true), '')
    AND project_id = NULLIF(pg_catalog.current_setting('neural_brain.project_id', true), '')
    AND session_id = NULLIF(pg_catalog.current_setting('neural_brain.session_id', true), '')
);

DROP POLICY checkpoint_scope ON memory_core.checkpoints;
CREATE POLICY checkpoint_scope ON memory_core.checkpoints
USING (
    tenant_id = brain_security.bound_tenant_id()
    AND tenant_id = NULLIF(pg_catalog.current_setting('neural_brain.tenant_id', true), '')
    AND area_id = NULLIF(pg_catalog.current_setting('neural_brain.area_id', true), '')
    AND project_id = NULLIF(pg_catalog.current_setting('neural_brain.project_id', true), '')
    AND session_id = NULLIF(pg_catalog.current_setting('neural_brain.session_id', true), '')
)
WITH CHECK (
    tenant_id = brain_security.bound_tenant_id()
    AND tenant_id = NULLIF(pg_catalog.current_setting('neural_brain.tenant_id', true), '')
    AND area_id = NULLIF(pg_catalog.current_setting('neural_brain.area_id', true), '')
    AND project_id = NULLIF(pg_catalog.current_setting('neural_brain.project_id', true), '')
    AND session_id = NULLIF(pg_catalog.current_setting('neural_brain.session_id', true), '')
);

DROP POLICY candidate_scope ON memory_core.memory_candidates;
CREATE POLICY candidate_scope ON memory_core.memory_candidates
USING (
    tenant_id = brain_security.bound_tenant_id()
    AND tenant_id = NULLIF(pg_catalog.current_setting('neural_brain.tenant_id', true), '')
    AND area_id = NULLIF(pg_catalog.current_setting('neural_brain.area_id', true), '')
)
WITH CHECK (
    tenant_id = brain_security.bound_tenant_id()
    AND tenant_id = NULLIF(pg_catalog.current_setting('neural_brain.tenant_id', true), '')
    AND area_id = NULLIF(pg_catalog.current_setting('neural_brain.area_id', true), '')
);

DROP POLICY receipt_scope ON memory_core.transition_receipts;
CREATE POLICY receipt_scope ON memory_core.transition_receipts
USING (
    tenant_id = brain_security.bound_tenant_id()
    AND tenant_id = NULLIF(pg_catalog.current_setting('neural_brain.tenant_id', true), '')
    AND area_id = NULLIF(pg_catalog.current_setting('neural_brain.area_id', true), '')
)
WITH CHECK (
    tenant_id = brain_security.bound_tenant_id()
    AND tenant_id = NULLIF(pg_catalog.current_setting('neural_brain.tenant_id', true), '')
    AND area_id = NULLIF(pg_catalog.current_setting('neural_brain.area_id', true), '')
);

DROP POLICY dreaming_run_scope ON memory_core.dreaming_runs;
CREATE POLICY dreaming_run_scope ON memory_core.dreaming_runs
USING (
    tenant_id = brain_security.bound_tenant_id()
    AND tenant_id = NULLIF(pg_catalog.current_setting('neural_brain.tenant_id', true), '')
    AND area_id = NULLIF(pg_catalog.current_setting('neural_brain.area_id', true), '')
)
WITH CHECK (
    tenant_id = brain_security.bound_tenant_id()
    AND tenant_id = NULLIF(pg_catalog.current_setting('neural_brain.tenant_id', true), '')
    AND area_id = NULLIF(pg_catalog.current_setting('neural_brain.area_id', true), '')
);

DROP POLICY cognitive_transition_evidence_scope
ON memory_core.cognitive_transition_evidence;
CREATE POLICY cognitive_transition_evidence_scope
ON memory_core.cognitive_transition_evidence
USING (
    tenant_id = brain_security.bound_tenant_id()
    AND tenant_id = NULLIF(pg_catalog.current_setting('neural_brain.tenant_id', true), '')
    AND area_id = NULLIF(pg_catalog.current_setting('neural_brain.area_id', true), '')
    AND project_id = NULLIF(pg_catalog.current_setting('neural_brain.project_id', true), '')
    AND session_id = NULLIF(pg_catalog.current_setting('neural_brain.session_id', true), '')
)
WITH CHECK (
    tenant_id = brain_security.bound_tenant_id()
    AND tenant_id = NULLIF(pg_catalog.current_setting('neural_brain.tenant_id', true), '')
    AND area_id = NULLIF(pg_catalog.current_setting('neural_brain.area_id', true), '')
    AND project_id = NULLIF(pg_catalog.current_setting('neural_brain.project_id', true), '')
    AND session_id = NULLIF(pg_catalog.current_setting('neural_brain.session_id', true), '')
);

CREATE POLICY tenant_provisioner_manage ON brain_catalog.tenants
FOR ALL
TO neural_brain_provisioner
USING (true)
WITH CHECK (true);

CREATE FUNCTION brain_security.assert_provisionable_tenant_runtime_role(
    requested_database_role name
)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
STABLE
SET search_path = pg_catalog
AS $$
DECLARE
    requested_role_oid oid;
    granted_roles text[];
BEGIN
    IF requested_database_role = session_user
       OR requested_database_role::text !~ '^neural_brain_tenant_[0-9a-f]{24}_runtime$' THEN
        RAISE EXCEPTION 'Tenant runtime role identity is invalid'
            USING ERRCODE = '42501';
    END IF;

    SELECT role.oid INTO requested_role_oid
    FROM pg_catalog.pg_roles AS role
    WHERE role.rolname = requested_database_role
      AND role.rolcanlogin
      AND NOT role.rolsuper
      AND NOT role.rolcreatedb
      AND NOT role.rolcreaterole
      AND NOT role.rolinherit
      AND NOT role.rolreplication
      AND NOT role.rolbypassrls;
    IF requested_role_oid IS NULL THEN
        RAISE EXCEPTION 'Tenant runtime role attributes are unsafe'
            USING ERRCODE = '42501';
    END IF;

    SELECT COALESCE(
        pg_catalog.array_agg(granted.rolname::text ORDER BY granted.rolname),
        ARRAY[]::text[]
    ) INTO granted_roles
    FROM pg_catalog.pg_auth_members AS membership
    JOIN pg_catalog.pg_roles AS granted ON granted.oid = membership.roleid
    WHERE membership.member = requested_role_oid
      AND NOT membership.admin_option
      AND NOT membership.inherit_option
      AND membership.set_option;
    IF granted_roles <> ARRAY['neural_brain_gate', 'neural_brain_reader']::text[]
       OR EXISTS (
            SELECT 1
            FROM pg_catalog.pg_auth_members AS membership
            WHERE membership.member = requested_role_oid
              AND (
                    membership.admin_option
                    OR membership.inherit_option
                    OR NOT membership.set_option
              )
       ) THEN
        RAISE EXCEPTION 'Tenant runtime role memberships are unsafe'
            USING ERRCODE = '42501';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM pg_catalog.pg_shdepend AS dependency
        WHERE dependency.refclassid = 'pg_catalog.pg_authid'::pg_catalog.regclass
          AND dependency.refobjid = requested_role_oid
          AND dependency.deptype = 'o'
    ) THEN
        RAISE EXCEPTION 'Tenant runtime role owns database objects'
            USING ERRCODE = '42501';
    END IF;
END;
$$;

CREATE FUNCTION brain_security.register_tenant_runtime_identity(
    requested_database_role name,
    requested_tenant_id text,
    requested_secret_reference text
)
RETURNS bigint
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog
AS $$
BEGIN
    PERFORM brain_security.assert_provisionable_tenant_runtime_role(
        requested_database_role
    );
    IF requested_secret_reference IS NULL
       OR requested_secret_reference = ''
       OR length(requested_secret_reference) > 1024 THEN
        RAISE EXCEPTION 'Tenant secret reference is invalid'
            USING ERRCODE = '22023';
    END IF;

    INSERT INTO brain_security.tenant_runtime_identities (
        database_role,
        tenant_id,
        status,
        credential_revision
    ) VALUES (
        requested_database_role,
        requested_tenant_id,
        'active',
        1
    );
    INSERT INTO brain_security.tenant_runtime_identity_events (
        tenant_id,
        database_role,
        operation,
        credential_revision,
        authenticated_database_actor,
        evidence
    ) VALUES (
        requested_tenant_id,
        requested_database_role,
        'provisioned',
        1,
        session_user,
        pg_catalog.jsonb_build_object(
            'verified', true,
            'secret_reference', requested_secret_reference
        )
    );
    RETURN 1;
END;
$$;

CREATE FUNCTION brain_security.rotate_tenant_runtime_identity(
    requested_database_role name,
    requested_tenant_id text,
    expected_revision bigint,
    requested_secret_reference text
)
RETURNS bigint
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog
AS $$
DECLARE
    next_revision bigint := expected_revision + 1;
BEGIN
    IF requested_secret_reference IS NULL
       OR requested_secret_reference = ''
       OR length(requested_secret_reference) > 1024 THEN
        RAISE EXCEPTION 'Tenant secret reference is invalid'
            USING ERRCODE = '22023';
    END IF;
    UPDATE brain_security.tenant_runtime_identities
    SET credential_revision = next_revision,
        updated_at = transaction_timestamp()
    WHERE database_role = requested_database_role
      AND tenant_id = requested_tenant_id
      AND status = 'active'
      AND credential_revision = expected_revision;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Tenant identity revision is stale or unavailable'
            USING ERRCODE = '40001';
    END IF;
    INSERT INTO brain_security.tenant_runtime_identity_events (
        tenant_id,
        database_role,
        operation,
        credential_revision,
        authenticated_database_actor,
        evidence
    ) VALUES (
        requested_tenant_id,
        requested_database_role,
        'rotated',
        next_revision,
        session_user,
        pg_catalog.jsonb_build_object(
            'verified', true,
            'secret_reference', requested_secret_reference
        )
    );
    RETURN next_revision;
END;
$$;

CREATE FUNCTION brain_security.deprovision_tenant_runtime_identity(
    requested_database_role name,
    requested_tenant_id text,
    expected_revision bigint
)
RETURNS bigint
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog
AS $$
DECLARE
    next_revision bigint := expected_revision + 1;
BEGIN
    UPDATE brain_security.tenant_runtime_identities
    SET status = 'revoked',
        credential_revision = next_revision,
        updated_at = transaction_timestamp()
    WHERE database_role = requested_database_role
      AND tenant_id = requested_tenant_id
      AND status = 'active'
      AND credential_revision = expected_revision;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Tenant identity revision is stale or unavailable'
            USING ERRCODE = '40001';
    END IF;
    INSERT INTO brain_security.tenant_runtime_identity_events (
        tenant_id,
        database_role,
        operation,
        credential_revision,
        authenticated_database_actor,
        evidence
    ) VALUES (
        requested_tenant_id,
        requested_database_role,
        'deprovisioned',
        next_revision,
        session_user,
        pg_catalog.jsonb_build_object('verified', true)
    );
    RETURN next_revision;
END;
$$;

ALTER FUNCTION brain_security.assert_provisionable_tenant_runtime_role(name)
OWNER TO neural_brain_owner;
ALTER FUNCTION brain_security.register_tenant_runtime_identity(name, text, text)
OWNER TO neural_brain_owner;
ALTER FUNCTION brain_security.rotate_tenant_runtime_identity(name, text, bigint, text)
OWNER TO neural_brain_owner;
ALTER FUNCTION brain_security.deprovision_tenant_runtime_identity(name, text, bigint)
OWNER TO neural_brain_owner;
REVOKE ALL ON FUNCTION
    brain_security.assert_provisionable_tenant_runtime_role(name)
FROM PUBLIC;
REVOKE ALL ON FUNCTION
    brain_security.register_tenant_runtime_identity(name, text, text)
FROM PUBLIC;
REVOKE ALL ON FUNCTION
    brain_security.rotate_tenant_runtime_identity(name, text, bigint, text)
FROM PUBLIC;
REVOKE ALL ON FUNCTION
    brain_security.deprovision_tenant_runtime_identity(name, text, bigint)
FROM PUBLIC;
GRANT EXECUTE ON FUNCTION
    brain_security.register_tenant_runtime_identity(name, text, text)
TO neural_brain_provisioner;
GRANT EXECUTE ON FUNCTION
    brain_security.rotate_tenant_runtime_identity(name, text, bigint, text)
TO neural_brain_provisioner;
GRANT EXECUTE ON FUNCTION
    brain_security.deprovision_tenant_runtime_identity(name, text, bigint)
TO neural_brain_provisioner;

GRANT USAGE ON SCHEMA brain_catalog TO neural_brain_provisioner;
GRANT USAGE ON SCHEMA brain_security TO neural_brain_provisioner WITH GRANT OPTION;
GRANT SELECT ON brain_catalog.brains TO neural_brain_provisioner;
GRANT SELECT, INSERT ON brain_catalog.tenants TO neural_brain_provisioner;
GRANT SELECT ON brain_security.tenant_runtime_identities TO neural_brain_provisioner;

REVOKE CREATE ON SCHEMA public FROM PUBLIC;

DO $$
BEGIN
    EXECUTE pg_catalog.format(
        'GRANT CONNECT ON DATABASE %I TO neural_brain_provisioner WITH GRANT OPTION',
        pg_catalog.current_database()
    );
END;
$$;
