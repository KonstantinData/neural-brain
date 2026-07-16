CREATE TABLE memory_audit.events (
    tenant_id text NOT NULL,
    area_id text NOT NULL,
    audit_sequence bigint GENERATED ALWAYS AS IDENTITY,
    event_type text NOT NULL,
    principal_id text NOT NULL,
    transition_request_id text NOT NULL,
    subject_kind text NOT NULL,
    subject_id text NOT NULL,
    evidence jsonb NOT NULL,
    occurred_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
    PRIMARY KEY (tenant_id, area_id, audit_sequence),
    FOREIGN KEY (tenant_id, area_id)
        REFERENCES brain_catalog.areas (tenant_id, area_id),
    CHECK (jsonb_typeof(evidence) = 'object')
);

CREATE TABLE memory_core.observations (
    tenant_id text NOT NULL,
    area_id text NOT NULL,
    project_id text NOT NULL,
    observation_id text NOT NULL,
    session_id text NOT NULL,
    source_kind text NOT NULL,
    classification text NOT NULL
        CHECK (classification IN ('public', 'internal', 'confidential', 'restricted')),
    purpose text NOT NULL,
    payload jsonb NOT NULL,
    occurred_at timestamptz NOT NULL,
    received_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
    PRIMARY KEY (tenant_id, area_id, observation_id),
    FOREIGN KEY (tenant_id, area_id, project_id, session_id)
        REFERENCES brain_catalog.sessions (tenant_id, area_id, project_id, session_id),
    CHECK (observation_id <> '' AND length(observation_id) <= 128),
    CHECK (source_kind <> '' AND length(source_kind) <= 128),
    CHECK (purpose <> '' AND length(purpose) <= 256),
    CHECK (jsonb_typeof(payload) = 'object')
);

CREATE TABLE memory_core.working_contexts (
    tenant_id text NOT NULL,
    area_id text NOT NULL,
    project_id text NOT NULL,
    session_id text NOT NULL,
    slot_name text NOT NULL,
    current_version bigint NOT NULL CHECK (current_version > 0),
    current_value jsonb NOT NULL,
    updated_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
    PRIMARY KEY (tenant_id, area_id, project_id, session_id, slot_name),
    FOREIGN KEY (tenant_id, area_id, project_id, session_id)
        REFERENCES brain_catalog.sessions (tenant_id, area_id, project_id, session_id),
    CHECK (slot_name <> '' AND length(slot_name) <= 128),
    CHECK (jsonb_typeof(current_value) = 'object')
);

CREATE TABLE memory_core.working_context_versions (
    tenant_id text NOT NULL,
    area_id text NOT NULL,
    project_id text NOT NULL,
    session_id text NOT NULL,
    slot_name text NOT NULL,
    version bigint NOT NULL CHECK (version > 0),
    value jsonb NOT NULL,
    source_observation_id text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
    PRIMARY KEY (tenant_id, area_id, project_id, session_id, slot_name, version),
    FOREIGN KEY (tenant_id, area_id, project_id, session_id, slot_name)
        REFERENCES memory_core.working_contexts (
            tenant_id, area_id, project_id, session_id, slot_name
        ),
    FOREIGN KEY (tenant_id, area_id, source_observation_id)
        REFERENCES memory_core.observations (tenant_id, area_id, observation_id),
    CHECK (jsonb_typeof(value) = 'object')
);

CREATE TABLE memory_core.checkpoints (
    tenant_id text NOT NULL,
    area_id text NOT NULL,
    project_id text NOT NULL,
    checkpoint_id text NOT NULL,
    session_id text NOT NULL,
    working_memory_id text NOT NULL,
    snapshot jsonb NOT NULL,
    slot_count integer NOT NULL CHECK (slot_count >= 0),
    created_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
    PRIMARY KEY (tenant_id, area_id, checkpoint_id),
    FOREIGN KEY (tenant_id, area_id, project_id, session_id)
        REFERENCES brain_catalog.sessions (tenant_id, area_id, project_id, session_id),
    CHECK (checkpoint_id <> '' AND length(checkpoint_id) <= 128),
    CHECK (working_memory_id <> '' AND length(working_memory_id) <= 128),
    CHECK (jsonb_typeof(snapshot) = 'object')
);

CREATE TABLE memory_core.memory_candidates (
    tenant_id text NOT NULL,
    area_id text NOT NULL,
    candidate_id text NOT NULL,
    source_observation_id text NOT NULL,
    source_dreaming_run_id text,
    candidate_kind text NOT NULL,
    candidate_payload jsonb NOT NULL,
    state text NOT NULL DEFAULT 'inactive' CHECK (state = 'inactive'),
    created_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
    PRIMARY KEY (tenant_id, area_id, candidate_id),
    UNIQUE (tenant_id, area_id, source_observation_id, candidate_kind),
    FOREIGN KEY (tenant_id, area_id, source_observation_id)
        REFERENCES memory_core.observations (tenant_id, area_id, observation_id),
    CHECK (candidate_id <> '' AND length(candidate_id) <= 128),
    CHECK (candidate_kind <> '' AND length(candidate_kind) <= 128),
    CHECK (jsonb_typeof(candidate_payload) = 'object')
);

CREATE TABLE memory_core.transition_receipts (
    tenant_id text NOT NULL,
    area_id text NOT NULL,
    transition_request_id text NOT NULL,
    operation text NOT NULL,
    request_document jsonb NOT NULL,
    result_document jsonb NOT NULL,
    committed_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
    PRIMARY KEY (tenant_id, area_id, transition_request_id),
    FOREIGN KEY (tenant_id, area_id)
        REFERENCES brain_catalog.areas (tenant_id, area_id),
    CHECK (transition_request_id <> '' AND length(transition_request_id) <= 128),
    CHECK (jsonb_typeof(request_document) = 'object'),
    CHECK (jsonb_typeof(result_document) = 'object')
);

ALTER TABLE memory_audit.events OWNER TO neural_brain_owner;
ALTER TABLE memory_core.observations OWNER TO neural_brain_owner;
ALTER TABLE memory_core.working_contexts OWNER TO neural_brain_owner;
ALTER TABLE memory_core.working_context_versions OWNER TO neural_brain_owner;
ALTER TABLE memory_core.checkpoints OWNER TO neural_brain_owner;
ALTER TABLE memory_core.memory_candidates OWNER TO neural_brain_owner;
ALTER TABLE memory_core.transition_receipts OWNER TO neural_brain_owner;

CREATE FUNCTION memory_gate.reject_change()
RETURNS trigger
LANGUAGE plpgsql
SET search_path = pg_catalog
AS $$
BEGIN
    RAISE EXCEPTION '% is append-only', TG_TABLE_NAME USING ERRCODE = '55000';
END;
$$;

CREATE FUNCTION memory_gate.reject_scope_change()
RETURNS trigger
LANGUAGE plpgsql
SET search_path = pg_catalog
AS $$
BEGIN
    IF OLD.tenant_id IS DISTINCT FROM NEW.tenant_id
       OR OLD.area_id IS DISTINCT FROM NEW.area_id
       OR (to_jsonb(OLD) ->> 'project_id')
          IS DISTINCT FROM (to_jsonb(NEW) ->> 'project_id') THEN
        RAISE EXCEPTION 'persisted memory scope is immutable' USING ERRCODE = '55000';
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER audit_events_are_append_only
BEFORE UPDATE OR DELETE ON memory_audit.events
FOR EACH ROW EXECUTE FUNCTION memory_gate.reject_change();

CREATE TRIGGER observation_scope_is_immutable
BEFORE UPDATE ON memory_core.observations
FOR EACH ROW EXECUTE FUNCTION memory_gate.reject_scope_change();

CREATE TRIGGER working_context_scope_is_immutable
BEFORE UPDATE ON memory_core.working_contexts
FOR EACH ROW EXECUTE FUNCTION memory_gate.reject_scope_change();

CREATE TRIGGER checkpoint_scope_is_immutable
BEFORE UPDATE ON memory_core.checkpoints
FOR EACH ROW EXECUTE FUNCTION memory_gate.reject_scope_change();

CREATE TRIGGER candidate_scope_is_immutable
BEFORE UPDATE ON memory_core.memory_candidates
FOR EACH ROW EXECUTE FUNCTION memory_gate.reject_scope_change();

ALTER TABLE memory_audit.events ENABLE ROW LEVEL SECURITY;
ALTER TABLE memory_audit.events FORCE ROW LEVEL SECURITY;
ALTER TABLE memory_core.observations ENABLE ROW LEVEL SECURITY;
ALTER TABLE memory_core.observations FORCE ROW LEVEL SECURITY;
ALTER TABLE memory_core.working_contexts ENABLE ROW LEVEL SECURITY;
ALTER TABLE memory_core.working_contexts FORCE ROW LEVEL SECURITY;
ALTER TABLE memory_core.working_context_versions ENABLE ROW LEVEL SECURITY;
ALTER TABLE memory_core.working_context_versions FORCE ROW LEVEL SECURITY;
ALTER TABLE memory_core.checkpoints ENABLE ROW LEVEL SECURITY;
ALTER TABLE memory_core.checkpoints FORCE ROW LEVEL SECURITY;
ALTER TABLE memory_core.memory_candidates ENABLE ROW LEVEL SECURITY;
ALTER TABLE memory_core.memory_candidates FORCE ROW LEVEL SECURITY;
ALTER TABLE memory_core.transition_receipts ENABLE ROW LEVEL SECURITY;
ALTER TABLE memory_core.transition_receipts FORCE ROW LEVEL SECURITY;

CREATE POLICY audit_scope ON memory_audit.events
USING (
    tenant_id = NULLIF(pg_catalog.current_setting('neural_brain.tenant_id', true), '')
    AND area_id = NULLIF(pg_catalog.current_setting('neural_brain.area_id', true), '')
)
WITH CHECK (
    tenant_id = NULLIF(pg_catalog.current_setting('neural_brain.tenant_id', true), '')
    AND area_id = NULLIF(pg_catalog.current_setting('neural_brain.area_id', true), '')
);

CREATE POLICY observation_scope ON memory_core.observations
USING (
    tenant_id = NULLIF(pg_catalog.current_setting('neural_brain.tenant_id', true), '')
    AND area_id = NULLIF(pg_catalog.current_setting('neural_brain.area_id', true), '')
    AND project_id = NULLIF(pg_catalog.current_setting('neural_brain.project_id', true), '')
    AND session_id = NULLIF(pg_catalog.current_setting('neural_brain.session_id', true), '')
)
WITH CHECK (
    tenant_id = NULLIF(pg_catalog.current_setting('neural_brain.tenant_id', true), '')
    AND area_id = NULLIF(pg_catalog.current_setting('neural_brain.area_id', true), '')
    AND project_id = NULLIF(pg_catalog.current_setting('neural_brain.project_id', true), '')
    AND session_id = NULLIF(pg_catalog.current_setting('neural_brain.session_id', true), '')
);

CREATE POLICY working_context_scope ON memory_core.working_contexts
USING (
    tenant_id = NULLIF(pg_catalog.current_setting('neural_brain.tenant_id', true), '')
    AND area_id = NULLIF(pg_catalog.current_setting('neural_brain.area_id', true), '')
    AND project_id = NULLIF(pg_catalog.current_setting('neural_brain.project_id', true), '')
    AND session_id = NULLIF(pg_catalog.current_setting('neural_brain.session_id', true), '')
)
WITH CHECK (
    tenant_id = NULLIF(pg_catalog.current_setting('neural_brain.tenant_id', true), '')
    AND area_id = NULLIF(pg_catalog.current_setting('neural_brain.area_id', true), '')
    AND project_id = NULLIF(pg_catalog.current_setting('neural_brain.project_id', true), '')
    AND session_id = NULLIF(pg_catalog.current_setting('neural_brain.session_id', true), '')
);

CREATE POLICY working_version_scope ON memory_core.working_context_versions
USING (
    tenant_id = NULLIF(pg_catalog.current_setting('neural_brain.tenant_id', true), '')
    AND area_id = NULLIF(pg_catalog.current_setting('neural_brain.area_id', true), '')
    AND project_id = NULLIF(pg_catalog.current_setting('neural_brain.project_id', true), '')
    AND session_id = NULLIF(pg_catalog.current_setting('neural_brain.session_id', true), '')
)
WITH CHECK (
    tenant_id = NULLIF(pg_catalog.current_setting('neural_brain.tenant_id', true), '')
    AND area_id = NULLIF(pg_catalog.current_setting('neural_brain.area_id', true), '')
    AND project_id = NULLIF(pg_catalog.current_setting('neural_brain.project_id', true), '')
    AND session_id = NULLIF(pg_catalog.current_setting('neural_brain.session_id', true), '')
);

CREATE POLICY checkpoint_scope ON memory_core.checkpoints
USING (
    tenant_id = NULLIF(pg_catalog.current_setting('neural_brain.tenant_id', true), '')
    AND area_id = NULLIF(pg_catalog.current_setting('neural_brain.area_id', true), '')
    AND project_id = NULLIF(pg_catalog.current_setting('neural_brain.project_id', true), '')
    AND session_id = NULLIF(pg_catalog.current_setting('neural_brain.session_id', true), '')
)
WITH CHECK (
    tenant_id = NULLIF(pg_catalog.current_setting('neural_brain.tenant_id', true), '')
    AND area_id = NULLIF(pg_catalog.current_setting('neural_brain.area_id', true), '')
    AND project_id = NULLIF(pg_catalog.current_setting('neural_brain.project_id', true), '')
    AND session_id = NULLIF(pg_catalog.current_setting('neural_brain.session_id', true), '')
);

CREATE POLICY candidate_scope ON memory_core.memory_candidates
USING (
    tenant_id = NULLIF(pg_catalog.current_setting('neural_brain.tenant_id', true), '')
    AND area_id = NULLIF(pg_catalog.current_setting('neural_brain.area_id', true), '')
)
WITH CHECK (
    tenant_id = NULLIF(pg_catalog.current_setting('neural_brain.tenant_id', true), '')
    AND area_id = NULLIF(pg_catalog.current_setting('neural_brain.area_id', true), '')
);

CREATE POLICY receipt_scope ON memory_core.transition_receipts
USING (
    tenant_id = NULLIF(pg_catalog.current_setting('neural_brain.tenant_id', true), '')
    AND area_id = NULLIF(pg_catalog.current_setting('neural_brain.area_id', true), '')
)
WITH CHECK (
    tenant_id = NULLIF(pg_catalog.current_setting('neural_brain.tenant_id', true), '')
    AND area_id = NULLIF(pg_catalog.current_setting('neural_brain.area_id', true), '')
);

CREATE FUNCTION memory_gate.commit_memory_cycle(
    transition_request_id text,
    observation_id text,
    source_kind text,
    classification text,
    purpose text,
    observation_payload jsonb,
    occurred_at timestamptz,
    slot_name text,
    working_value jsonb,
    expected_working_version bigint,
    checkpoint_id text
)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog
AS $$
DECLARE
    context_principal text := brain_security.context_value('neural_brain.principal_id');
    context_tenant text := brain_security.context_value('neural_brain.tenant_id');
    context_area text := brain_security.context_value('neural_brain.area_id');
    context_project text := brain_security.context_value('neural_brain.project_id');
    context_session text := brain_security.context_value('neural_brain.session_id');
    request_document jsonb;
    existing_receipt memory_core.transition_receipts%ROWTYPE;
    existing_version bigint;
    next_version bigint;
    checkpoint_snapshot jsonb;
    result_document jsonb;
BEGIN
    PERFORM brain_security.assert_scope_authority('ingest');

    IF transition_request_id = '' OR observation_id = ''
       OR slot_name = '' OR checkpoint_id = '' THEN
        RAISE EXCEPTION 'memory identifiers must be non-empty' USING ERRCODE = '22023';
    END IF;
    IF expected_working_version < 0 THEN
        RAISE EXCEPTION 'expected working version cannot be negative' USING ERRCODE = '22023';
    END IF;
    IF jsonb_typeof(observation_payload) <> 'object'
       OR jsonb_typeof(working_value) <> 'object' THEN
        RAISE EXCEPTION 'memory payloads must be JSON objects' USING ERRCODE = '22023';
    END IF;

    request_document := jsonb_build_object(
        'observation_id', observation_id,
        'source_kind', source_kind,
        'classification', classification,
        'purpose', purpose,
        'observation_payload', observation_payload,
        'occurred_at', occurred_at,
        'slot_name', slot_name,
        'working_value', working_value,
        'expected_working_version', expected_working_version,
        'checkpoint_id', checkpoint_id
    );

    SELECT * INTO existing_receipt
    FROM memory_core.transition_receipts AS receipt
    WHERE receipt.tenant_id = context_tenant
      AND receipt.area_id = context_area
      AND receipt.transition_request_id = commit_memory_cycle.transition_request_id;

    IF FOUND THEN
        IF existing_receipt.operation <> 'commit_memory_cycle'
           OR existing_receipt.request_document <> request_document THEN
            RAISE EXCEPTION 'transition request replay does not match committed input'
                USING ERRCODE = '22000';
        END IF;
        RETURN existing_receipt.result_document;
    END IF;

    PERFORM 1
    FROM brain_catalog.sessions AS session
        WHERE session.tenant_id = context_tenant
          AND session.area_id = context_area
          AND session.project_id = context_project
          AND session.session_id = context_session
          AND session.activity_state = 'active'
          AND session.activity_expires_at > statement_timestamp();
    IF NOT FOUND THEN
        RAISE EXCEPTION 'session is not active in the trusted scope'
            USING ERRCODE = '55000';
    END IF;

    INSERT INTO memory_core.observations (
        tenant_id, area_id, project_id, observation_id, session_id, source_kind,
        classification, purpose, payload, occurred_at
    ) VALUES (
        context_tenant, context_area, context_project, observation_id, context_session, source_kind,
        classification, purpose, observation_payload, occurred_at
    );

    SELECT context.current_version INTO existing_version
    FROM memory_core.working_contexts AS context
    WHERE context.tenant_id = context_tenant
      AND context.area_id = context_area
      AND context.project_id = context_project
      AND context.session_id = context_session
      AND context.slot_name = commit_memory_cycle.slot_name
    FOR UPDATE;

    IF FOUND THEN
        IF existing_version <> expected_working_version THEN
            RAISE EXCEPTION 'stale working context version' USING ERRCODE = '40001';
        END IF;
        next_version := existing_version + 1;
        UPDATE memory_core.working_contexts AS context
        SET current_version = next_version,
            current_value = working_value,
            updated_at = transaction_timestamp()
        WHERE context.tenant_id = context_tenant
          AND context.area_id = context_area
          AND context.project_id = context_project
          AND context.session_id = context_session
          AND context.slot_name = commit_memory_cycle.slot_name;
    ELSE
        IF expected_working_version <> 0 THEN
            RAISE EXCEPTION 'stale working context version' USING ERRCODE = '40001';
        END IF;
        next_version := 1;
        INSERT INTO memory_core.working_contexts (
            tenant_id, area_id, project_id, session_id, slot_name,
            current_version, current_value
        ) VALUES (
            context_tenant, context_area, context_project, context_session, slot_name,
            next_version, working_value
        );
    END IF;

    INSERT INTO memory_core.working_context_versions (
        tenant_id, area_id, project_id, session_id, slot_name, version,
        value, source_observation_id
    ) VALUES (
        context_tenant, context_area, context_project, context_session, slot_name, next_version,
        working_value, observation_id
    );

    SELECT COALESCE(
        jsonb_object_agg(
            context.slot_name,
            jsonb_build_object('version', context.current_version, 'value', context.current_value)
            ORDER BY context.slot_name
        ),
        '{}'::jsonb
    ) INTO checkpoint_snapshot
    FROM memory_core.working_contexts AS context
    WHERE context.tenant_id = context_tenant
      AND context.area_id = context_area
      AND context.project_id = context_project
      AND context.session_id = context_session;

    INSERT INTO memory_core.checkpoints (
        tenant_id, area_id, project_id, checkpoint_id, session_id, working_memory_id,
        snapshot, slot_count
    ) VALUES (
        context_tenant, context_area, context_project, checkpoint_id, context_session, slot_name,
        checkpoint_snapshot,
        (SELECT count(*) FROM jsonb_object_keys(checkpoint_snapshot))
    );

    result_document := jsonb_build_object(
        'observation_id', observation_id,
        'session_id', context_session,
        'slot_name', slot_name,
        'working_version', next_version,
        'checkpoint_id', checkpoint_id,
        'checkpoint', checkpoint_snapshot
    );

    INSERT INTO memory_audit.events (
        tenant_id, area_id, event_type, principal_id, transition_request_id,
        subject_kind, subject_id, evidence
    ) VALUES (
        context_tenant, context_area, 'memory_cycle_committed', context_principal,
        transition_request_id, 'checkpoint', checkpoint_id,
        jsonb_build_object(
            'observation_id', observation_id,
            'session_id', context_session,
            'slot_name', slot_name,
            'working_version', next_version,
            'checkpoint_id', checkpoint_id
        )
    );

    INSERT INTO memory_core.transition_receipts (
        tenant_id, area_id, transition_request_id, operation,
        request_document, result_document
    ) VALUES (
        context_tenant, context_area, transition_request_id, 'commit_memory_cycle',
        request_document, result_document
    );

    RETURN result_document;
END;
$$;

CREATE FUNCTION memory_gate.read_checkpoint(checkpoint_id text)
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
        'checkpoint_id', checkpoint.checkpoint_id,
        'session_id', checkpoint.session_id,
        'working_memory_id', checkpoint.working_memory_id,
        'slot_count', checkpoint.slot_count,
        'snapshot', checkpoint.snapshot,
        'created_at', checkpoint.created_at
    ) INTO result_document
    FROM memory_core.checkpoints AS checkpoint
    WHERE checkpoint.tenant_id = context_tenant
      AND checkpoint.area_id = context_area
      AND checkpoint.project_id = context_project
      AND checkpoint.session_id = context_session
      AND checkpoint.checkpoint_id = read_checkpoint.checkpoint_id;

    IF result_document IS NULL THEN
        RAISE EXCEPTION 'checkpoint is unavailable in the trusted scope'
            USING ERRCODE = '02000';
    END IF;
    RETURN result_document;
END;
$$;

ALTER FUNCTION memory_gate.reject_change() OWNER TO neural_brain_owner;
ALTER FUNCTION memory_gate.reject_scope_change() OWNER TO neural_brain_owner;
ALTER FUNCTION memory_gate.commit_memory_cycle(
    text, text, text, text, text, jsonb, timestamptz, text, jsonb, bigint, text
) OWNER TO neural_brain_owner;
ALTER FUNCTION memory_gate.read_checkpoint(text) OWNER TO neural_brain_owner;

REVOKE ALL ON ALL TABLES IN SCHEMA memory_core, memory_audit FROM PUBLIC;
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA memory_gate FROM PUBLIC;
GRANT USAGE ON SCHEMA memory_core, memory_audit, memory_gate
TO neural_brain_gate, neural_brain_reader, neural_brain_dreamer;
GRANT EXECUTE ON FUNCTION memory_gate.commit_memory_cycle(
    text, text, text, text, text, jsonb, timestamptz, text, jsonb, bigint, text
) TO neural_brain_gate;
GRANT EXECUTE ON FUNCTION memory_gate.read_checkpoint(text)
TO neural_brain_reader, neural_brain_gate;
