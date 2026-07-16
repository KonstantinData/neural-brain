CREATE TABLE memory_core.dreaming_runs (
    tenant_id text NOT NULL,
    area_id text NOT NULL,
    dreaming_run_id text NOT NULL,
    requested_reason text NOT NULL,
    status text NOT NULL CHECK (status IN ('completed', 'skipped')),
    skip_reason text,
    active_work_signals jsonb NOT NULL,
    snapshot_manifest jsonb,
    candidate_count integer NOT NULL DEFAULT 0 CHECK (candidate_count >= 0),
    validation_result text NOT NULL CHECK (validation_result IN ('passed', 'not_run')),
    active_pointer_updated boolean NOT NULL DEFAULT false CHECK (NOT active_pointer_updated),
    report jsonb NOT NULL,
    created_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
    PRIMARY KEY (tenant_id, area_id, dreaming_run_id),
    FOREIGN KEY (tenant_id, area_id)
        REFERENCES brain_catalog.areas (tenant_id, area_id),
    CHECK (dreaming_run_id <> '' AND length(dreaming_run_id) <= 128),
    CHECK (requested_reason <> '' AND length(requested_reason) <= 256),
    CHECK (jsonb_typeof(active_work_signals) = 'object'),
    CHECK (snapshot_manifest IS NULL OR jsonb_typeof(snapshot_manifest) = 'object'),
    CHECK (jsonb_typeof(report) = 'object'),
    CHECK (
        (status = 'completed' AND skip_reason IS NULL AND snapshot_manifest IS NOT NULL
            AND validation_result = 'passed')
        OR (status = 'skipped' AND skip_reason IS NOT NULL AND snapshot_manifest IS NULL
            AND validation_result = 'not_run')
    )
);

ALTER TABLE memory_core.dreaming_runs OWNER TO neural_brain_owner;

ALTER TABLE memory_core.memory_candidates
ADD CONSTRAINT memory_candidate_dreaming_run_fk
FOREIGN KEY (tenant_id, area_id, source_dreaming_run_id)
REFERENCES memory_core.dreaming_runs (tenant_id, area_id, dreaming_run_id)
DEFERRABLE INITIALLY DEFERRED;

CREATE TRIGGER dreaming_run_scope_is_immutable
BEFORE UPDATE ON memory_core.dreaming_runs
FOR EACH ROW EXECUTE FUNCTION memory_gate.reject_scope_change();

ALTER TABLE memory_core.dreaming_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE memory_core.dreaming_runs FORCE ROW LEVEL SECURITY;

CREATE POLICY dreaming_run_scope ON memory_core.dreaming_runs
USING (
    tenant_id = NULLIF(pg_catalog.current_setting('neural_brain.tenant_id', true), '')
    AND area_id = NULLIF(pg_catalog.current_setting('neural_brain.area_id', true), '')
)
WITH CHECK (
    tenant_id = NULLIF(pg_catalog.current_setting('neural_brain.tenant_id', true), '')
    AND area_id = NULLIF(pg_catalog.current_setting('neural_brain.area_id', true), '')
);

CREATE FUNCTION memory_gate.run_dreaming_dry_run(
    dreaming_run_id text,
    requested_reason text
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
    existing_run memory_core.dreaming_runs%ROWTYPE;
    active_count integer;
    stale_count integer;
    observation_manifest jsonb;
    working_manifest jsonb;
    snapshot_manifest jsonb;
    active_signals jsonb;
    candidate_count integer := 0;
    candidate_manifest jsonb := '[]'::jsonb;
    report_document jsonb;
BEGIN
    PERFORM brain_security.assert_scope_authority('dream');

    IF dreaming_run_id = '' OR requested_reason = '' THEN
        RAISE EXCEPTION 'Dreaming identifiers and reason must be non-empty'
            USING ERRCODE = '22023';
    END IF;

    SELECT * INTO existing_run
    FROM memory_core.dreaming_runs AS run
    WHERE run.tenant_id = context_tenant
      AND run.area_id = context_area
      AND run.dreaming_run_id = run_dreaming_dry_run.dreaming_run_id;

    IF FOUND THEN
        IF existing_run.requested_reason <> requested_reason THEN
            RAISE EXCEPTION 'Dreaming run replay does not match committed input'
                USING ERRCODE = '22000';
        END IF;
        RETURN existing_run.report;
    END IF;

    IF NOT pg_try_advisory_xact_lock(
        hashtextextended(context_tenant || ':' || context_area, 17417)
    ) THEN
        active_signals := jsonb_build_object('lock_available', false);
        report_document := jsonb_build_object(
            'status', 'skipped',
            'skip_reason', 'lock_unavailable',
            'active_work_signals', active_signals,
            'candidate_count', 0,
            'candidates', candidate_manifest,
            'validation_result', 'not_run',
            'active_pointer_updated', false
        );
        INSERT INTO memory_core.dreaming_runs (
            tenant_id, area_id, dreaming_run_id, requested_reason, status, skip_reason,
            active_work_signals, candidate_count, validation_result, report
        ) VALUES (
            context_tenant, context_area, dreaming_run_id, requested_reason, 'skipped',
            'lock_unavailable', active_signals, 0, 'not_run', report_document
        );
        INSERT INTO memory_audit.events (
            tenant_id, area_id, event_type, principal_id, transition_request_id,
            subject_kind, subject_id, evidence
        ) VALUES (
            context_tenant, context_area, 'dreaming_skipped', context_principal,
            dreaming_run_id, 'dreaming_run', dreaming_run_id,
            jsonb_build_object(
                'skip_reason', 'lock_unavailable',
                'active_work_signals', active_signals,
                'active_pointer_updated', false
            )
        );
        RETURN report_document;
    END IF;

    SELECT
        count(*) FILTER (
            WHERE session.activity_state = 'active'
              AND session.activity_expires_at > statement_timestamp()
        ),
        count(*) FILTER (
            WHERE session.activity_state = 'reconciling'
               OR (
                    session.activity_state = 'active'
                    AND session.activity_expires_at <= statement_timestamp()
               )
        )
    INTO active_count, stale_count
    FROM brain_catalog.sessions AS session
    WHERE session.tenant_id = context_tenant
      AND session.area_id = context_area;

    active_signals := jsonb_build_object(
        'lock_available', true,
        'active_session_count', active_count,
        'reconciliation_required_count', stale_count
    );

    IF stale_count > 0 OR active_count > 0 THEN
        report_document := jsonb_build_object(
            'status', 'skipped',
            'skip_reason', CASE
                WHEN stale_count > 0 THEN 'reconciliation_required'
                ELSE 'active_work'
            END,
            'active_work_signals', active_signals,
            'candidate_count', 0,
            'candidates', candidate_manifest,
            'validation_result', 'not_run',
            'active_pointer_updated', false
        );
        INSERT INTO memory_core.dreaming_runs (
            tenant_id, area_id, dreaming_run_id, requested_reason, status, skip_reason,
            active_work_signals, candidate_count, validation_result, report
        ) VALUES (
            context_tenant, context_area, dreaming_run_id, requested_reason, 'skipped',
            report_document ->> 'skip_reason', active_signals, 0, 'not_run', report_document
        );
        INSERT INTO memory_audit.events (
            tenant_id, area_id, event_type, principal_id, transition_request_id,
            subject_kind, subject_id, evidence
        ) VALUES (
            context_tenant, context_area, 'dreaming_skipped', context_principal,
            dreaming_run_id, 'dreaming_run', dreaming_run_id,
            jsonb_build_object(
                'skip_reason', report_document ->> 'skip_reason',
                'active_work_signals', active_signals,
                'active_pointer_updated', false
            )
        );
        RETURN report_document;
    END IF;

    SELECT COALESCE(
        jsonb_agg(
            jsonb_build_object(
                'observation_id', observation.observation_id,
                'project_id', observation.project_id,
                'session_id', observation.session_id,
                'received_at', observation.received_at
            ) ORDER BY observation.observation_id
        ),
        '[]'::jsonb
    ) INTO observation_manifest
    FROM memory_core.observations AS observation
    WHERE observation.tenant_id = context_tenant
      AND observation.area_id = context_area;

    SELECT COALESCE(
        jsonb_agg(
            jsonb_build_object(
                'project_id', context.project_id,
                'session_id', context.session_id,
                'slot_name', context.slot_name,
                'version', context.current_version
            ) ORDER BY context.project_id, context.session_id, context.slot_name
        ),
        '[]'::jsonb
    ) INTO working_manifest
    FROM memory_core.working_contexts AS context
    WHERE context.tenant_id = context_tenant
      AND context.area_id = context_area;

    snapshot_manifest := jsonb_build_object(
        'observations', observation_manifest,
        'working_context_versions', working_manifest
    );

    INSERT INTO memory_core.memory_candidates (
        tenant_id, area_id, candidate_id, source_observation_id,
        source_dreaming_run_id, candidate_kind, candidate_payload
    )
    SELECT
        context_tenant,
        context_area,
        observation.observation_id,
        observation.observation_id,
        dreaming_run_id,
        'observation_review',
        jsonb_build_object(
            'source_observation_id', observation.observation_id,
            'reason', 'stage1_deterministic_review'
        )
    FROM memory_core.observations AS observation
    WHERE observation.tenant_id = context_tenant
      AND observation.area_id = context_area
    ON CONFLICT (tenant_id, area_id, source_observation_id, candidate_kind) DO NOTHING;
    GET DIAGNOSTICS candidate_count = ROW_COUNT;

    SELECT COALESCE(
        jsonb_agg(
            jsonb_build_object(
                'candidate_id', candidate.candidate_id,
                'source_observation_id', candidate.source_observation_id,
                'candidate_kind', candidate.candidate_kind,
                'state', candidate.state,
                'retrievable', false
            ) ORDER BY candidate.candidate_id
        ),
        '[]'::jsonb
    ) INTO candidate_manifest
    FROM memory_core.memory_candidates AS candidate
    WHERE candidate.tenant_id = context_tenant
      AND candidate.area_id = context_area
      AND candidate.source_dreaming_run_id = dreaming_run_id;

    report_document := jsonb_build_object(
        'status', 'completed',
        'skip_reason', NULL,
        'active_work_signals', active_signals,
        'snapshot_manifest', snapshot_manifest,
        'candidate_count', candidate_count,
        'candidates', candidate_manifest,
        'validation_result', 'passed',
        'active_pointer_updated', false
    );

    INSERT INTO memory_core.dreaming_runs (
        tenant_id, area_id, dreaming_run_id, requested_reason, status,
        active_work_signals, snapshot_manifest, candidate_count,
        validation_result, report
    ) VALUES (
        context_tenant, context_area, dreaming_run_id, requested_reason, 'completed',
        active_signals, snapshot_manifest, candidate_count, 'passed', report_document
    );

    INSERT INTO memory_audit.events (
        tenant_id, area_id, event_type, principal_id, transition_request_id,
        subject_kind, subject_id, evidence
    ) VALUES (
        context_tenant, context_area, 'dreaming_dry_run_completed', context_principal,
        dreaming_run_id, 'dreaming_run', dreaming_run_id,
        jsonb_build_object(
            'candidate_count', candidate_count,
            'validation_result', 'passed',
            'active_pointer_updated', false
        )
    );

    RETURN report_document;
END;
$$;

ALTER FUNCTION memory_gate.run_dreaming_dry_run(text, text) OWNER TO neural_brain_owner;
REVOKE ALL ON FUNCTION memory_gate.run_dreaming_dry_run(text, text) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION memory_gate.run_dreaming_dry_run(text, text)
TO neural_brain_dreamer;
