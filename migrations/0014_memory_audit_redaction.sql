-- S1-03.7: redact audit payloads before the canonical hash-chain appends them.
--
-- Audit rows retain immutable actor, Tenant/Area scope, decision and result
-- evidence.  They do not retain observation content, credentials, secrets, or
-- a second copy of deletable protected payloads.  This migration applies only
-- to future rows; existing immutable evidence is never rewritten.

CREATE FUNCTION memory_audit.contains_sensitive_evidence_field(raw_value jsonb)
RETURNS boolean
LANGUAGE plpgsql
SET search_path = pg_catalog
AS $$
DECLARE
    entry record;
BEGIN
    IF jsonb_typeof(raw_value) = 'object' THEN
        FOR entry IN SELECT key, value FROM jsonb_each(raw_value)
        LOOP
            IF entry.key ~* '(secret|password|token|credential|authorization|cookie|raw|content|payload|prompt)'
               OR memory_audit.contains_sensitive_evidence_field(entry.value) THEN
                RETURN true;
            END IF;
        END LOOP;
    ELSIF jsonb_typeof(raw_value) = 'array' THEN
        FOR entry IN SELECT value FROM jsonb_array_elements(raw_value)
        LOOP
            IF memory_audit.contains_sensitive_evidence_field(entry.value) THEN
                RETURN true;
            END IF;
        END LOOP;
    END IF;
    RETURN false;
END;
$$;

CREATE FUNCTION memory_audit.reject_sensitive_evidence(raw_evidence jsonb)
RETURNS void
LANGUAGE plpgsql
SET search_path = pg_catalog
AS $$
BEGIN
    IF jsonb_typeof(raw_evidence) IS DISTINCT FROM 'object' THEN
        RAISE EXCEPTION 'audit evidence must be an object' USING ERRCODE = '22023';
    END IF;

    IF memory_audit.contains_sensitive_evidence_field(raw_evidence) THEN
        RAISE EXCEPTION 'audit evidence contains a prohibited sensitive payload field'
            USING ERRCODE = '22023';
    END IF;
END;
$$;

CREATE FUNCTION memory_audit.redact_event_evidence()
RETURNS trigger
LANGUAGE plpgsql
SET search_path = pg_catalog
AS $$
DECLARE
    result_state text;
    policy_state text := 'not_implemented';
BEGIN
    PERFORM memory_audit.reject_sensitive_evidence(NEW.evidence);

    IF NEW.event_type NOT IN (
        'memory_cycle_committed',
        'cognitive_cycle_committed',
        'local_demo_scope_provisioned',
        'local_oidc_demo_principal_provisioned'
    ) THEN
        RAISE EXCEPTION 'audit event type has no approved redaction contract'
            USING ERRCODE = '22023';
    END IF;

    IF NEW.event_type IN ('memory_cycle_committed', 'cognitive_cycle_committed') THEN
        result_state := 'committed';
    ELSE
        result_state := 'provisioned';
    END IF;

    -- The current MS-1 gates have an authority check but no Policy Decision
    -- runtime.  Record that absence explicitly instead of forging approval or
    -- policy evidence.  The actor and immutable scope remain typed columns,
    -- not content duplicated from the incoming JSON document.
    NEW.evidence := jsonb_build_object(
        'audit_schema_version', 's1-03-7-v1',
        'policy', jsonb_build_object('state', policy_state),
        'decision', NEW.event_type,
        'result', result_state,
        'evidence_references', jsonb_build_array(
            jsonb_build_object('kind', 'transition_request', 'reference_id', NEW.transition_request_id),
            jsonb_build_object('kind', NEW.subject_kind, 'reference_id', NEW.subject_id)
        )
    );
    RETURN NEW;
END;
$$;

CREATE TRIGGER audit_a_redaction_before_hash_chain
BEFORE INSERT ON memory_audit.events
FOR EACH ROW EXECUTE FUNCTION memory_audit.redact_event_evidence();

CREATE FUNCTION memory_gate.read_redacted_memory_audit_event(audit_sequence bigint)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
STABLE
SET search_path = pg_catalog
AS $$
DECLARE
    context_tenant text := brain_security.context_value('neural_brain.tenant_id');
    context_area text := brain_security.context_value('neural_brain.area_id');
    audit_document jsonb;
BEGIN
    PERFORM brain_security.assert_scope_authority('read');
    SELECT jsonb_build_object(
        'tenant_id', event.tenant_id,
        'area_id', event.area_id,
        'audit_sequence', event.audit_sequence,
        'event_type', event.event_type,
        'principal_id', event.principal_id,
        'transition_request_id', event.transition_request_id,
        'subject_kind', event.subject_kind,
        'subject_id', event.subject_id,
        'evidence', event.evidence,
        'occurred_at', event.occurred_at,
        'previous_event_hash', event.previous_event_hash,
        'event_hash', event.event_hash
    ) INTO audit_document
    FROM memory_audit.events AS event
    WHERE event.tenant_id = context_tenant
      AND event.area_id = context_area
      AND event.audit_sequence = read_redacted_memory_audit_event.audit_sequence;
    IF audit_document IS NULL THEN
        RAISE EXCEPTION 'redacted audit event is unavailable in the trusted scope'
            USING ERRCODE = '02000';
    END IF;
    RETURN audit_document;
END;
$$;

ALTER FUNCTION memory_audit.contains_sensitive_evidence_field(jsonb) OWNER TO neural_brain_owner;
ALTER FUNCTION memory_audit.reject_sensitive_evidence(jsonb) OWNER TO neural_brain_owner;
ALTER FUNCTION memory_audit.redact_event_evidence() OWNER TO neural_brain_owner;
ALTER FUNCTION memory_gate.read_redacted_memory_audit_event(bigint) OWNER TO neural_brain_owner;
REVOKE ALL ON FUNCTION memory_audit.contains_sensitive_evidence_field(jsonb) FROM PUBLIC;
REVOKE ALL ON FUNCTION memory_audit.reject_sensitive_evidence(jsonb) FROM PUBLIC;
REVOKE ALL ON FUNCTION memory_audit.redact_event_evidence() FROM PUBLIC;
REVOKE ALL ON FUNCTION memory_gate.read_redacted_memory_audit_event(bigint) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION memory_gate.read_redacted_memory_audit_event(bigint)
TO neural_brain_gate, neural_brain_reader;
