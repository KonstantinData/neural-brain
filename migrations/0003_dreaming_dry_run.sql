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
BEGIN
    RAISE EXCEPTION
        'Dreaming is unavailable: persistent lease, immutable snapshot, and independent validation are not implemented'
        USING ERRCODE = '55000';
END;
$$;

ALTER FUNCTION memory_gate.run_dreaming_dry_run(text, text) OWNER TO neural_brain_owner;
REVOKE ALL ON FUNCTION memory_gate.run_dreaming_dry_run(text, text) FROM PUBLIC;
REVOKE ALL ON FUNCTION memory_gate.run_dreaming_dry_run(text, text)
FROM neural_brain_dreamer;
