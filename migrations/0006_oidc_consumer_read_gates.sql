CREATE FUNCTION brain_security.resolve_authenticated_principal(authenticated_subject text)
RETURNS text
LANGUAGE plpgsql
SECURITY DEFINER
STABLE
SET search_path = pg_catalog
AS $$
DECLARE
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
      AND principal.status = 'active';

    IF resolved_principal_id IS NULL THEN
        RAISE EXCEPTION 'authenticated principal is unavailable'
            USING ERRCODE = '28000';
    END IF;

    RETURN resolved_principal_id;
END;
$$;

CREATE FUNCTION brain_security.provision_local_oidc_demo_subject()
RETURNS jsonb
LANGUAGE plpgsql
SET search_path = pg_catalog
AS $$
DECLARE
    authenticated_admin text := session_user;
    result_document jsonb;
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_catalog.pg_roles
        WHERE rolname = authenticated_admin AND rolsuper
    ) THEN
        RAISE EXCEPTION 'local OIDC demo provisioning requires an authenticated database administrator'
            USING ERRCODE = '42501';
    END IF;

    INSERT INTO brain_security.principals (principal_id, authenticated_subject)
    VALUES (
        'principal-local-oidc-demo',
        '["https://local.demo.invalid","operator-local-demo"]'
    ) ON CONFLICT (principal_id) DO NOTHING;
    INSERT INTO brain_security.principal_scope_bindings (
        principal_id, tenant_id, area_id, can_ingest, can_read, can_dream
    ) VALUES (
        'principal-local-oidc-demo', 'tenant-local-demo', 'area-local-demo', true, true, false
    ) ON CONFLICT (principal_id, tenant_id, area_id) DO UPDATE
    SET can_ingest = true, can_read = true, can_dream = false, valid_until = NULL;

    IF NOT EXISTS (
        SELECT 1 FROM brain_security.principals
        WHERE principal_id = 'principal-local-oidc-demo'
          AND authenticated_subject = '["https://local.demo.invalid","operator-local-demo"]'
          AND status = 'active'
    ) OR NOT EXISTS (
        SELECT 1 FROM brain_security.principal_scope_bindings
        WHERE principal_id = 'principal-local-oidc-demo'
          AND tenant_id = 'tenant-local-demo'
          AND area_id = 'area-local-demo'
          AND can_ingest AND can_read AND NOT can_dream AND valid_until IS NULL
    ) THEN
        RAISE EXCEPTION 'local OIDC demo principal state conflicts with the fixed contract'
            USING ERRCODE = '55000';
    END IF;

    result_document := jsonb_build_object(
        'principal_id', 'principal-local-oidc-demo',
        'issuer', 'https://local.demo.invalid',
        'subject', 'operator-local-demo',
        'authenticated_admin', authenticated_admin
    );
    INSERT INTO memory_audit.events (
        tenant_id, area_id, event_type, principal_id, transition_request_id,
        subject_kind, subject_id, evidence
    ) VALUES (
        'tenant-local-demo', 'area-local-demo', 'local_oidc_demo_principal_provisioned',
        authenticated_admin, 'local-oidc-demo-principal-v1', 'principal',
        'principal-local-oidc-demo', result_document
    ) ON CONFLICT DO NOTHING;
    RETURN result_document;
END;
$$;

CREATE FUNCTION memory_gate.read_observation(observation_id text)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
STABLE
SET search_path = pg_catalog
AS $$
DECLARE
    context_tenant text := brain_security.context_value('neural_brain.tenant_id');
    context_area text := brain_security.context_value('neural_brain.area_id');
    context_project text := brain_security.context_value('neural_brain.project_id');
    context_session text := brain_security.context_value('neural_brain.session_id');
    result_document jsonb;
BEGIN
    PERFORM brain_security.assert_scope_authority('read');
    SELECT jsonb_build_object(
        'observation_id', observation.observation_id,
        'source_kind', observation.source_kind,
        'source_ref', observation.payload ->> 'source_ref',
        'classification', observation.classification,
        'purpose', observation.purpose,
        'content', observation.payload ->> 'content',
        'occurred_at', observation.occurred_at
    ) INTO result_document
    FROM memory_core.observations AS observation
    WHERE observation.tenant_id = context_tenant
      AND observation.area_id = context_area
      AND observation.project_id = context_project
      AND observation.session_id = context_session
      AND observation.observation_id = read_observation.observation_id;

    IF result_document IS NULL THEN
        RAISE EXCEPTION 'observation is unavailable in the trusted scope'
            USING ERRCODE = '02000';
    END IF;
    RETURN result_document;
END;
$$;

CREATE FUNCTION memory_gate.read_working_memory(working_memory_id text)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
STABLE
SET search_path = pg_catalog
AS $$
DECLARE
    context_tenant text := brain_security.context_value('neural_brain.tenant_id');
    context_area text := brain_security.context_value('neural_brain.area_id');
    context_project text := brain_security.context_value('neural_brain.project_id');
    context_session text := brain_security.context_value('neural_brain.session_id');
    result_document jsonb;
BEGIN
    PERFORM brain_security.assert_scope_authority('read');
    SELECT jsonb_build_object(
        'working_memory_id', working_context.slot_name,
        'version', working_context.current_version,
        'value', working_context.current_value,
        'updated_at', working_context.updated_at
    ) INTO result_document
    FROM memory_core.working_contexts AS working_context
    WHERE working_context.tenant_id = context_tenant
      AND working_context.area_id = context_area
      AND working_context.project_id = context_project
      AND working_context.session_id = context_session
      AND working_context.slot_name = read_working_memory.working_memory_id;

    IF result_document IS NULL THEN
        RAISE EXCEPTION 'working memory is unavailable in the trusted scope'
            USING ERRCODE = '02000';
    END IF;
    RETURN result_document;
END;
$$;

ALTER FUNCTION brain_security.resolve_authenticated_principal(text) OWNER TO neural_brain_owner;
ALTER FUNCTION brain_security.provision_local_oidc_demo_subject() OWNER TO neural_brain_owner;
ALTER FUNCTION memory_gate.read_observation(text) OWNER TO neural_brain_owner;
ALTER FUNCTION memory_gate.read_working_memory(text) OWNER TO neural_brain_owner;

REVOKE ALL ON FUNCTION brain_security.resolve_authenticated_principal(text) FROM PUBLIC;
REVOKE ALL ON FUNCTION brain_security.provision_local_oidc_demo_subject() FROM PUBLIC;
REVOKE ALL ON FUNCTION memory_gate.read_observation(text) FROM PUBLIC;
REVOKE ALL ON FUNCTION memory_gate.read_working_memory(text) FROM PUBLIC;

GRANT EXECUTE ON FUNCTION brain_security.resolve_authenticated_principal(text)
TO neural_brain_reader, neural_brain_gate;
GRANT EXECUTE ON FUNCTION memory_gate.read_observation(text)
TO neural_brain_reader, neural_brain_gate;
GRANT EXECUTE ON FUNCTION memory_gate.read_working_memory(text)
TO neural_brain_reader, neural_brain_gate;
