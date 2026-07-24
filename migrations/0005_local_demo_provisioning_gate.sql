CREATE FUNCTION brain_security.provision_local_demo_scope(transition_request_id text)
RETURNS jsonb
LANGUAGE plpgsql
SET search_path = pg_catalog
AS $$
DECLARE
    authenticated_admin text := session_user;
    result_document jsonb;
BEGIN
    IF transition_request_id = '' OR length(transition_request_id) > 128 THEN
        RAISE EXCEPTION 'invalid provisioning transition identifier' USING ERRCODE = '22023';
    END IF;
    IF NOT EXISTS (
        SELECT 1 FROM pg_catalog.pg_roles
        WHERE rolname = authenticated_admin AND rolsuper
    ) THEN
        RAISE EXCEPTION 'local demo provisioning requires an authenticated database administrator'
            USING ERRCODE = '42501';
    END IF;

    INSERT INTO brain_catalog.brains (brain_id, display_name)
    VALUES ('brain-local-demo', 'Local Memory Demo')
    ON CONFLICT (brain_id) DO NOTHING;
    INSERT INTO brain_catalog.tenants (tenant_id, brain_id, display_name)
    VALUES ('tenant-local-demo', 'brain-local-demo', 'Local Demo Tenant')
    ON CONFLICT (tenant_id) DO NOTHING;
    INSERT INTO brain_catalog.areas (tenant_id, area_id, display_name)
    VALUES ('tenant-local-demo', 'area-local-demo', 'Local Demo Area')
    ON CONFLICT (tenant_id, area_id) DO NOTHING;
    INSERT INTO brain_catalog.projects (tenant_id, area_id, project_id, display_name)
    VALUES ('tenant-local-demo', 'area-local-demo', 'project-local-demo', 'Local Demo Project')
    ON CONFLICT (tenant_id, area_id, project_id) DO NOTHING;
    INSERT INTO brain_catalog.sessions (
        tenant_id, area_id, project_id, session_id, activity_state, activity_expires_at
    ) VALUES (
        'tenant-local-demo', 'area-local-demo', 'project-local-demo', 'session-local-demo',
        'active', statement_timestamp() + interval '1 hour'
    )
    ON CONFLICT (tenant_id, area_id, session_id) DO UPDATE
    SET activity_state = 'active', activity_expires_at = EXCLUDED.activity_expires_at;
    INSERT INTO brain_security.principals (principal_id, authenticated_subject)
    VALUES ('principal-local-demo', 'local://memory-demo')
    ON CONFLICT (principal_id) DO NOTHING;
    INSERT INTO brain_security.principal_scope_bindings (
        principal_id, tenant_id, area_id, can_ingest, can_read, can_dream
    ) VALUES (
        'principal-local-demo', 'tenant-local-demo', 'area-local-demo', true, true, false
    )
    ON CONFLICT (principal_id, tenant_id, area_id) DO UPDATE
    SET can_ingest = true, can_read = true, can_dream = false, valid_until = NULL;

    IF NOT EXISTS (
        SELECT 1 FROM brain_catalog.brains
        WHERE brain_id = 'brain-local-demo' AND display_name = 'Local Memory Demo'
    ) OR NOT EXISTS (
        SELECT 1 FROM brain_catalog.tenants
        WHERE tenant_id = 'tenant-local-demo' AND brain_id = 'brain-local-demo'
          AND display_name = 'Local Demo Tenant' AND status = 'active'
    ) OR NOT EXISTS (
        SELECT 1 FROM brain_catalog.areas
        WHERE tenant_id = 'tenant-local-demo' AND area_id = 'area-local-demo'
          AND display_name = 'Local Demo Area' AND status = 'active'
    ) OR NOT EXISTS (
        SELECT 1 FROM brain_catalog.projects
        WHERE tenant_id = 'tenant-local-demo' AND area_id = 'area-local-demo'
          AND project_id = 'project-local-demo' AND display_name = 'Local Demo Project'
          AND status = 'active'
    ) OR NOT EXISTS (
        SELECT 1 FROM brain_catalog.sessions
        WHERE tenant_id = 'tenant-local-demo' AND area_id = 'area-local-demo'
          AND project_id = 'project-local-demo' AND session_id = 'session-local-demo'
          AND activity_state = 'active' AND activity_expires_at > statement_timestamp()
    ) OR NOT EXISTS (
        SELECT 1 FROM brain_security.principals
        WHERE principal_id = 'principal-local-demo'
          AND authenticated_subject = 'local://memory-demo' AND status = 'active'
    ) OR NOT EXISTS (
        SELECT 1 FROM brain_security.principal_scope_bindings
        WHERE principal_id = 'principal-local-demo' AND tenant_id = 'tenant-local-demo'
          AND area_id = 'area-local-demo' AND can_ingest AND can_read AND NOT can_dream
          AND valid_until IS NULL
    ) THEN
        RAISE EXCEPTION 'local demo provisioning state conflicts with the fixed contract'
            USING ERRCODE = '55000';
    END IF;

    result_document := jsonb_build_object(
        'principal_id', 'principal-local-demo',
        'tenant_id', 'tenant-local-demo',
        'area_id', 'area-local-demo',
        'project_id', 'project-local-demo',
        'session_id', 'session-local-demo',
        'authenticated_admin', authenticated_admin
    );
    INSERT INTO memory_audit.events (
        tenant_id, area_id, event_type, principal_id, transition_request_id,
        subject_kind, subject_id, evidence
    ) VALUES (
        'tenant-local-demo', 'area-local-demo', 'local_demo_scope_provisioned',
        authenticated_admin, transition_request_id, 'principal_scope_binding',
        'principal-local-demo', result_document
    );
    RETURN result_document;
END;
$$;

ALTER FUNCTION brain_security.provision_local_demo_scope(text) OWNER TO neural_brain_owner;
REVOKE ALL ON FUNCTION brain_security.provision_local_demo_scope(text) FROM PUBLIC;
