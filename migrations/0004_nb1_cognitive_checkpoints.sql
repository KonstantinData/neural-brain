CREATE TABLE memory_core.cognitive_transition_evidence (
    tenant_id text NOT NULL,
    area_id text NOT NULL,
    project_id text NOT NULL,
    session_id text NOT NULL,
    cycle_id text NOT NULL,
    checkpoint_id text NOT NULL,
    checkpoint_version bigint NOT NULL CHECK (checkpoint_version > 0),
    observation_id text NOT NULL,
    model_version text NOT NULL,
    transition_envelope jsonb NOT NULL,
    audit_evidence jsonb NOT NULL,
    created_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
    PRIMARY KEY (tenant_id, area_id, cycle_id),
    UNIQUE (tenant_id, area_id, checkpoint_id),
    FOREIGN KEY (tenant_id, area_id, checkpoint_id)
        REFERENCES memory_core.checkpoints (tenant_id, area_id, checkpoint_id),
    CHECK (cycle_id <> '' AND length(cycle_id) <= 128),
    CHECK (checkpoint_id <> '' AND length(checkpoint_id) <= 128),
    CHECK (observation_id <> '' AND length(observation_id) <= 128),
    CHECK (model_version <> '' AND length(model_version) <= 128),
    CHECK (jsonb_typeof(transition_envelope) = 'object'),
    CHECK (jsonb_typeof(audit_evidence) = 'object')
);

ALTER TABLE memory_core.cognitive_transition_evidence OWNER TO neural_brain_owner;

CREATE TRIGGER cognitive_transition_evidence_is_append_only
BEFORE UPDATE OR DELETE ON memory_core.cognitive_transition_evidence
FOR EACH ROW EXECUTE FUNCTION memory_gate.reject_change();

ALTER TABLE memory_core.cognitive_transition_evidence ENABLE ROW LEVEL SECURITY;
ALTER TABLE memory_core.cognitive_transition_evidence FORCE ROW LEVEL SECURITY;

CREATE POLICY cognitive_transition_evidence_scope
ON memory_core.cognitive_transition_evidence
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

CREATE FUNCTION memory_gate.commit_cognitive_cycle(
    cycle_id text,
    observation_id text,
    source_kind text,
    provenance_ref text,
    observation_features jsonb,
    occurred_at timestamptz,
    expected_checkpoint_version bigint,
    checkpoint_id text,
    transition_envelope jsonb,
    training_provenance_ref text
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
    slot_name text := 'nb1-cognition:' || context_session;
    memory_result jsonb;
    audit_document jsonb;
    existing_evidence memory_core.cognitive_transition_evidence%ROWTYPE;
    next_version bigint;
BEGIN
    PERFORM brain_security.assert_scope_authority('ingest');

    IF cycle_id = '' OR observation_id = '' OR provenance_ref = '' OR checkpoint_id = ''
       OR training_provenance_ref = '' THEN
        RAISE EXCEPTION 'cognitive identifiers must be non-empty' USING ERRCODE = '22023';
    END IF;
    IF jsonb_typeof(observation_features) <> 'array'
       OR jsonb_array_length(observation_features) <> 2
       OR jsonb_typeof(transition_envelope) <> 'object' THEN
        RAISE EXCEPTION 'cognitive payload is invalid' USING ERRCODE = '22023';
    END IF;
    IF transition_envelope ->> 'cycle_id' IS DISTINCT FROM cycle_id
       OR transition_envelope ->> 'observation_id' IS DISTINCT FROM observation_id
       OR transition_envelope -> 'active_model' ->> 'training_artifact_digest'
          IS DISTINCT FROM training_provenance_ref
       OR (transition_envelope ->> 'previous_checkpoint_version')::bigint
          IS DISTINCT FROM expected_checkpoint_version
       OR (transition_envelope ->> 'next_checkpoint_version')::bigint
          IS DISTINCT FROM expected_checkpoint_version + 1 THEN
        RAISE EXCEPTION 'cognitive transition identity or version is inconsistent'
            USING ERRCODE = '22023';
    END IF;

    memory_result := memory_gate.commit_memory_cycle(
        cycle_id,
        observation_id,
        source_kind,
        'internal',
        'NB-1 effect-free cognitive workspace transition',
        jsonb_build_object(
            'source_ref', provenance_ref,
            'content', jsonb_build_object('features', observation_features)::text
        ),
        occurred_at,
        slot_name,
        jsonb_build_object(
            'entries', jsonb_build_array(jsonb_build_object(
                'entry_id', 'nb1-cognitive-workspace-state',
                'source_observation_id', observation_id,
                'content', transition_envelope::text
            ))
        ),
        expected_checkpoint_version,
        checkpoint_id
    );
    next_version := (memory_result ->> 'working_version')::bigint;

    audit_document := jsonb_build_object(
        'cycle_id', cycle_id,
        'model_version', transition_envelope ->> 'model_version',
        'training_provenance_ref', training_provenance_ref,
        'observation_id', observation_id,
        'previous_checkpoint_version', expected_checkpoint_version,
        'committed_checkpoint_version', next_version,
        'active_model', transition_envelope -> 'active_model',
        'external_effects_occurred', false,
        'active_model_mutated', false,
        'audit_committed', true
    );

    SELECT * INTO existing_evidence
    FROM memory_core.cognitive_transition_evidence AS evidence
    WHERE evidence.tenant_id = context_tenant
      AND evidence.area_id = context_area
      AND evidence.cycle_id = commit_cognitive_cycle.cycle_id;

    IF FOUND THEN
        IF existing_evidence.project_id <> context_project
           OR existing_evidence.session_id <> context_session
           OR existing_evidence.checkpoint_id <> checkpoint_id
           OR existing_evidence.checkpoint_version <> next_version
           OR existing_evidence.transition_envelope <> transition_envelope
           OR existing_evidence.audit_evidence <> audit_document THEN
            RAISE EXCEPTION 'cognitive cycle replay does not match committed evidence'
                USING ERRCODE = '22000';
        END IF;
        RETURN memory_result || jsonb_build_object(
            'transition_envelope', existing_evidence.transition_envelope,
            'audit_evidence', existing_evidence.audit_evidence
        );
    END IF;

    INSERT INTO memory_core.cognitive_transition_evidence (
        tenant_id, area_id, project_id, session_id, cycle_id, checkpoint_id,
        checkpoint_version, observation_id, model_version, transition_envelope,
        audit_evidence
    ) VALUES (
        context_tenant, context_area, context_project, context_session, cycle_id, checkpoint_id,
        next_version, observation_id, transition_envelope ->> 'model_version',
        transition_envelope, audit_document
    );

    INSERT INTO memory_audit.events (
        tenant_id, area_id, event_type, principal_id, transition_request_id,
        subject_kind, subject_id, evidence
    ) VALUES (
        context_tenant, context_area, 'cognitive_cycle_committed', context_principal,
        cycle_id, 'cognitive_checkpoint', checkpoint_id, audit_document
    );

    RETURN memory_result || jsonb_build_object(
        'transition_envelope', transition_envelope,
        'audit_evidence', audit_document
    );
END;
$$;

CREATE FUNCTION memory_gate.read_cognitive_checkpoint(checkpoint_id text)
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
    checkpoint_document jsonb;
    evidence memory_core.cognitive_transition_evidence%ROWTYPE;
    slot_name text;
    entries jsonb;
    persisted_transition jsonb;
BEGIN
    PERFORM brain_security.assert_scope_authority('read');
    checkpoint_document := memory_gate.read_checkpoint(checkpoint_id);

    SELECT * INTO evidence
    FROM memory_core.cognitive_transition_evidence AS item
    WHERE item.tenant_id = context_tenant
      AND item.area_id = context_area
      AND item.project_id = context_project
      AND item.session_id = context_session
      AND item.checkpoint_id = read_cognitive_checkpoint.checkpoint_id;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'cognitive checkpoint evidence is unavailable in the trusted scope'
            USING ERRCODE = '02000';
    END IF;

    slot_name := checkpoint_document ->> 'working_memory_id';
    entries := checkpoint_document -> 'snapshot' -> slot_name -> 'value' -> 'entries';
    IF jsonb_typeof(entries) IS DISTINCT FROM 'array'
       OR jsonb_array_length(entries) <> 1
       OR entries -> 0 ->> 'entry_id' IS DISTINCT FROM 'nb1-cognitive-workspace-state'
       OR entries -> 0 ->> 'source_observation_id' IS DISTINCT FROM evidence.observation_id THEN
        RAISE EXCEPTION 'cognitive checkpoint snapshot is missing or corrupt'
            USING ERRCODE = '22000';
    END IF;
    BEGIN
        persisted_transition := (entries -> 0 ->> 'content')::jsonb;
    EXCEPTION WHEN invalid_text_representation THEN
        RAISE EXCEPTION 'cognitive checkpoint transition is corrupt' USING ERRCODE = '22000';
    END;
    IF persisted_transition <> evidence.transition_envelope
       OR (checkpoint_document -> 'snapshot' -> slot_name ->> 'version')::bigint
          <> evidence.checkpoint_version THEN
        RAISE EXCEPTION 'cognitive checkpoint does not match committed evidence'
            USING ERRCODE = '22000';
    END IF;

    RETURN jsonb_build_object(
        'checkpoint_id', checkpoint_id,
        'checkpoint_version', evidence.checkpoint_version,
        'transition_envelope', evidence.transition_envelope,
        'audit_evidence', evidence.audit_evidence
    );
END;
$$;

ALTER FUNCTION memory_gate.commit_cognitive_cycle(
    text, text, text, text, jsonb, timestamptz, bigint, text, jsonb, text
) OWNER TO neural_brain_owner;
ALTER FUNCTION memory_gate.read_cognitive_checkpoint(text) OWNER TO neural_brain_owner;

REVOKE ALL ON TABLE memory_core.cognitive_transition_evidence FROM PUBLIC;
REVOKE ALL ON FUNCTION memory_gate.commit_cognitive_cycle(
    text, text, text, text, jsonb, timestamptz, bigint, text, jsonb, text
) FROM PUBLIC;
REVOKE ALL ON FUNCTION memory_gate.read_cognitive_checkpoint(text) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION memory_gate.commit_cognitive_cycle(
    text, text, text, text, jsonb, timestamptz, bigint, text, jsonb, text
) TO neural_brain_gate;
GRANT EXECUTE ON FUNCTION memory_gate.read_cognitive_checkpoint(text)
TO neural_brain_reader, neural_brain_gate;
