-- S1-06.2: canonical request, context, and snapshot digests for immutable
-- Memory Core authority evidence.  This alters only the S1-06.1 evidence
-- record and does not integrate a grant with the Memory Transition Gate.

ALTER TABLE brain_security.memory_authority_snapshots
    ADD COLUMN context_digest char(64),
    ADD COLUMN request_digest char(64),
    ADD COLUMN snapshot_digest char(64);

-- 0009 is introduced immediately before this forward-only migration and has
-- no released snapshot rows.  Explicitly refuse an unexpected upgrade state
-- instead of inventing digests for evidence that cannot be reproduced.
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM brain_security.memory_authority_snapshots) THEN
        RAISE EXCEPTION
            'S1-06.2 requires canonical authority snapshot digests; existing rows require audited reconciliation';
    END IF;
END;
$$;

ALTER TABLE brain_security.memory_authority_snapshots
    ALTER COLUMN context_digest SET NOT NULL,
    ALTER COLUMN request_digest SET NOT NULL,
    ALTER COLUMN snapshot_digest SET NOT NULL,
    ADD CONSTRAINT memory_authority_snapshot_context_digest_format
        CHECK (context_digest ~ '^[0-9a-f]{64}$'),
    ADD CONSTRAINT memory_authority_snapshot_request_digest_format
        CHECK (request_digest ~ '^[0-9a-f]{64}$'),
    ADD CONSTRAINT memory_authority_snapshot_digest_format
        CHECK (snapshot_digest ~ '^[0-9a-f]{64}$'),
    ADD CONSTRAINT memory_authority_snapshot_digest_is_unique
        UNIQUE (snapshot_digest);

ALTER TABLE brain_security.memory_authority_snapshots OWNER TO neural_brain_owner;
REVOKE ALL ON brain_security.memory_authority_snapshots FROM PUBLIC;
