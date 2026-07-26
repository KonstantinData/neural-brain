-- S1-03.8: bounded, authenticated reconstruction view over redacted audit evidence.
--
-- This is a read Gate only. It reconstructs the MS-1 transition timeline from
-- redacted, hash-chained evidence without reading protected Memory Core payloads.

CREATE FUNCTION memory_gate.read_scoped_memory_audit_timeline(
    after_audit_sequence bigint DEFAULT 0,
    maximum_events integer DEFAULT 100
)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog
AS $$
DECLARE
    context_tenant text := brain_security.context_value('neural_brain.tenant_id');
    context_area text := brain_security.context_value('neural_brain.area_id');
    timeline_entries jsonb;
BEGIN
    PERFORM brain_security.assert_scope_authority('read');

    IF after_audit_sequence < 0 THEN
        RAISE EXCEPTION 'audit timeline cursor must be non-negative' USING ERRCODE = '22023';
    END IF;
    IF maximum_events < 1 OR maximum_events > 100 THEN
        RAISE EXCEPTION 'audit timeline maximum_events must be between 1 and 100'
            USING ERRCODE = '22023';
    END IF;

    -- Reconstruction is evidence only while the complete authenticated scope
    -- retains a valid canonical chain. The verifier fails closed on tampering.
    PERFORM memory_gate.verify_memory_audit_chain();

    SELECT COALESCE(
        jsonb_agg(
            jsonb_build_object(
                'audit_sequence', event.audit_sequence,
                'occurred_at', event.occurred_at,
                'principal_id', event.principal_id,
                'transition_request_id', event.transition_request_id,
                'subject', jsonb_build_object(
                    'kind', event.subject_kind,
                    'reference_id', event.subject_id
                ),
                'decision', event.evidence ->> 'decision',
                'result', event.evidence ->> 'result',
                'policy', event.evidence -> 'policy',
                'provenance_references', event.evidence -> 'evidence_references',
                'previous_event_hash', event.previous_event_hash,
                'event_hash', event.event_hash
            ) ORDER BY event.audit_sequence
        ),
        '[]'::jsonb
    ) INTO timeline_entries
    FROM (
        SELECT *
        FROM memory_audit.events AS scoped_event
        WHERE scoped_event.tenant_id = context_tenant
          AND scoped_event.area_id = context_area
          AND scoped_event.audit_sequence > after_audit_sequence
        ORDER BY scoped_event.audit_sequence
        LIMIT maximum_events
    ) AS event;

    RETURN jsonb_build_object(
        'timeline_schema_version', 's1-03-8-v1',
        'tenant_id', context_tenant,
        'area_id', context_area,
        'integrity', jsonb_build_object('audit_hash_chain', 'verified'),
        'entries', timeline_entries
    );
END;
$$;

ALTER FUNCTION memory_gate.read_scoped_memory_audit_timeline(bigint, integer)
    OWNER TO neural_brain_owner;
REVOKE ALL ON FUNCTION memory_gate.read_scoped_memory_audit_timeline(bigint, integer)
    FROM PUBLIC;
GRANT EXECUTE ON FUNCTION memory_gate.read_scoped_memory_audit_timeline(bigint, integer)
TO neural_brain_gate, neural_brain_reader;
