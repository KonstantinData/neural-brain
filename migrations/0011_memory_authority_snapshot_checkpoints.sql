-- S1-06.3: preserve the trusted checkpoint identifier inside immutable
-- authority evidence so a policy decision cannot be reused for another
-- Memory Core checkpoint.  This is evidence only; it does not call or widen
-- the Memory Transition Gate.

ALTER TABLE brain_security.memory_authority_snapshots
    ADD COLUMN checkpoint_id text;

-- Existing rows were created before checkpoint binding existed.  Refuse an
-- unreconciled upgrade rather than fabricating a trusted checkpoint reference.
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM brain_security.memory_authority_snapshots) THEN
        RAISE EXCEPTION
            'S1-06.3 requires checkpoint-bound authority evidence; existing rows require audited reconciliation';
    END IF;
END;
$$;

ALTER TABLE brain_security.memory_authority_snapshots
    ALTER COLUMN checkpoint_id SET NOT NULL,
    ADD CONSTRAINT memory_authority_snapshot_checkpoint_id_nonempty
        CHECK (checkpoint_id <> '' AND length(checkpoint_id) <= 128);

ALTER TABLE brain_security.memory_authority_snapshots OWNER TO neural_brain_owner;
REVOKE ALL ON brain_security.memory_authority_snapshots FROM PUBLIC;
