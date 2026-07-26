-- S1-03.5: canonical, append-only integrity chain for MS-1 audit evidence.
--
-- This migration deliberately starts only on an empty audit ledger.  It must
-- never fabricate chain values for existing evidence; any populated upgrade
-- requires an independently authorized, audited reconciliation procedure.

CREATE EXTENSION IF NOT EXISTS pgcrypto;

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM memory_audit.events) THEN
        RAISE EXCEPTION
            'S1-03.5 requires audited reconciliation before hashing existing audit evidence'
            USING ERRCODE = '55000';
    END IF;
END;
$$;

ALTER TABLE memory_audit.events
    ADD COLUMN previous_event_hash text NOT NULL
        CHECK (previous_event_hash ~ '^[0-9a-f]{64}$'),
    ADD COLUMN event_hash text NOT NULL
        CHECK (event_hash ~ '^[0-9a-f]{64}$');

CREATE TABLE memory_audit.chain_heads (
    tenant_id text NOT NULL,
    area_id text NOT NULL,
    event_count bigint NOT NULL CHECK (event_count > 0),
    last_audit_sequence bigint NOT NULL CHECK (last_audit_sequence > 0),
    head_hash text NOT NULL CHECK (head_hash ~ '^[0-9a-f]{64}$'),
    updated_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
    PRIMARY KEY (tenant_id, area_id),
    FOREIGN KEY (tenant_id, area_id)
        REFERENCES brain_catalog.areas (tenant_id, area_id)
);

ALTER TABLE memory_audit.chain_heads OWNER TO neural_brain_owner;
ALTER TABLE memory_audit.chain_heads ENABLE ROW LEVEL SECURITY;
ALTER TABLE memory_audit.chain_heads FORCE ROW LEVEL SECURITY;

CREATE POLICY audit_chain_head_scope ON memory_audit.chain_heads
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

CREATE FUNCTION memory_audit.canonical_event_hash(
    tenant_id text,
    area_id text,
    audit_sequence bigint,
    event_type text,
    principal_id text,
    transition_request_id text,
    subject_kind text,
    subject_id text,
    evidence jsonb,
    occurred_at timestamptz,
    previous_event_hash text
)
RETURNS text
LANGUAGE sql
SET search_path = pg_catalog
AS $$
    SELECT encode(
        public.digest(
            convert_to(
                jsonb_build_object(
                    'area_id', area_id,
                    'audit_sequence', audit_sequence,
                    'event_type', event_type,
                    'evidence', evidence,
                    'occurred_at', to_char(
                        occurred_at AT TIME ZONE 'UTC',
                        'YYYY-MM-DD"T"HH24:MI:SS.US"Z"'
                    ),
                    'previous_event_hash', previous_event_hash,
                    'principal_id', principal_id,
                    'subject_id', subject_id,
                    'subject_kind', subject_kind,
                    'tenant_id', tenant_id,
                    'transition_request_id', transition_request_id
                )::text,
                'UTF8'
            ),
            'sha256'
        ),
        'hex'
    );
$$;

CREATE FUNCTION memory_audit.append_event_hash()
RETURNS trigger
LANGUAGE plpgsql
SET search_path = pg_catalog
AS $$
DECLARE
    previous_hash text := repeat('0', 64);
    prior_head memory_audit.chain_heads%ROWTYPE;
BEGIN
    IF NEW.previous_event_hash IS NOT NULL OR NEW.event_hash IS NOT NULL THEN
        RAISE EXCEPTION 'audit hash fields are owned by the append-only audit chain'
            USING ERRCODE = '55000';
    END IF;

    PERFORM pg_advisory_xact_lock(
        hashtextextended(NEW.tenant_id || chr(0) || NEW.area_id, 0)
    );
    SELECT * INTO prior_head
    FROM memory_audit.chain_heads AS head
    WHERE head.tenant_id = NEW.tenant_id
      AND head.area_id = NEW.area_id
    FOR UPDATE;

    IF FOUND THEN
        IF NEW.audit_sequence <= prior_head.last_audit_sequence THEN
            RAISE EXCEPTION 'audit sequence is not strictly increasing for the scoped chain'
                USING ERRCODE = '55000';
        END IF;
        previous_hash := prior_head.head_hash;
    END IF;

    NEW.previous_event_hash := previous_hash;
    NEW.event_hash := memory_audit.canonical_event_hash(
        NEW.tenant_id, NEW.area_id, NEW.audit_sequence, NEW.event_type,
        NEW.principal_id, NEW.transition_request_id, NEW.subject_kind,
        NEW.subject_id, NEW.evidence, NEW.occurred_at, previous_hash
    );

    INSERT INTO memory_audit.chain_heads (
        tenant_id, area_id, event_count, last_audit_sequence, head_hash
    ) VALUES (
        NEW.tenant_id, NEW.area_id, 1, NEW.audit_sequence, NEW.event_hash
    ) ON CONFLICT (tenant_id, area_id) DO UPDATE
    SET event_count = memory_audit.chain_heads.event_count + 1,
        last_audit_sequence = EXCLUDED.last_audit_sequence,
        head_hash = EXCLUDED.head_hash,
        updated_at = transaction_timestamp();
    RETURN NEW;
END;
$$;

CREATE TRIGGER audit_events_are_hash_chained
BEFORE INSERT ON memory_audit.events
FOR EACH ROW EXECUTE FUNCTION memory_audit.append_event_hash();

CREATE FUNCTION memory_gate.verify_memory_audit_chain()
RETURNS boolean
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog
AS $$
DECLARE
    context_tenant text := brain_security.context_value('neural_brain.tenant_id');
    context_area text := brain_security.context_value('neural_brain.area_id');
    expected_previous_hash text := repeat('0', 64);
    expected_hash text;
    observed_count bigint := 0;
    observed_last_sequence bigint := 0;
    scoped_head memory_audit.chain_heads%ROWTYPE;
    audit_event memory_audit.events%ROWTYPE;
BEGIN
    PERFORM brain_security.assert_scope_authority('read');

    FOR audit_event IN
        SELECT *
        FROM memory_audit.events AS event
        WHERE event.tenant_id = context_tenant
          AND event.area_id = context_area
        ORDER BY event.audit_sequence
    LOOP
        IF audit_event.previous_event_hash <> expected_previous_hash THEN
            RAISE EXCEPTION 'audit hash chain previous-hash mismatch at audit sequence %',
                audit_event.audit_sequence USING ERRCODE = '55000';
        END IF;
        expected_hash := memory_audit.canonical_event_hash(
            audit_event.tenant_id, audit_event.area_id, audit_event.audit_sequence,
            audit_event.event_type, audit_event.principal_id,
            audit_event.transition_request_id, audit_event.subject_kind,
            audit_event.subject_id, audit_event.evidence, audit_event.occurred_at,
            expected_previous_hash
        );
        IF audit_event.event_hash <> expected_hash THEN
            RAISE EXCEPTION 'audit hash chain event-hash mismatch at audit sequence %',
                audit_event.audit_sequence USING ERRCODE = '55000';
        END IF;
        expected_previous_hash := audit_event.event_hash;
        observed_count := observed_count + 1;
        observed_last_sequence := audit_event.audit_sequence;
    END LOOP;

    SELECT * INTO scoped_head
    FROM memory_audit.chain_heads AS head
    WHERE head.tenant_id = context_tenant
      AND head.area_id = context_area;

    IF observed_count = 0 THEN
        IF FOUND THEN
            RAISE EXCEPTION 'audit hash chain head exists without scoped events'
                USING ERRCODE = '55000';
        END IF;
        RETURN true;
    END IF;
    IF NOT FOUND
       OR scoped_head.event_count <> observed_count
       OR scoped_head.last_audit_sequence <> observed_last_sequence
       OR scoped_head.head_hash <> expected_previous_hash THEN
        RAISE EXCEPTION 'audit hash chain head mismatch' USING ERRCODE = '55000';
    END IF;
    RETURN true;
END;
$$;

ALTER FUNCTION memory_audit.canonical_event_hash(
    text, text, bigint, text, text, text, text, text, jsonb, timestamptz, text
) OWNER TO neural_brain_owner;
ALTER FUNCTION memory_audit.append_event_hash() OWNER TO neural_brain_owner;
ALTER FUNCTION memory_gate.verify_memory_audit_chain() OWNER TO neural_brain_owner;
REVOKE ALL ON FUNCTION memory_audit.canonical_event_hash(
    text, text, bigint, text, text, text, text, text, jsonb, timestamptz, text
) FROM PUBLIC;
REVOKE ALL ON FUNCTION memory_audit.append_event_hash() FROM PUBLIC;
REVOKE ALL ON FUNCTION memory_gate.verify_memory_audit_chain() FROM PUBLIC;
GRANT EXECUTE ON FUNCTION memory_gate.verify_memory_audit_chain()
TO neural_brain_gate, neural_brain_reader;
REVOKE ALL ON memory_audit.chain_heads FROM PUBLIC;
