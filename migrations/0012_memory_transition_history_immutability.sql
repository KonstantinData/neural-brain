-- S1-03.4: make the completed MS-1 Memory Core transition record immutable.
--
-- A committed transition receipt is the terminal representation of a Memory
-- Transition Gate operation.  It is intentionally not a general lifecycle
-- state machine: candidate promotion, quarantine, deletion, Goals, and
-- Actions remain outside this MS-1 migration.  Corrections require a new,
-- separately authorized transition and audit record; they never rewrite the
-- prior receipt, checkpoint, or working-context version.

CREATE FUNCTION memory_gate.reject_memory_transition_history_change()
RETURNS trigger
LANGUAGE plpgsql
SET search_path = pg_catalog
AS $$
BEGIN
    RAISE EXCEPTION 'memory transition history is immutable; committed transitions are terminal'
        USING ERRCODE = '55000';
END;
$$;

CREATE TRIGGER working_context_versions_are_immutable
BEFORE UPDATE OR DELETE ON memory_core.working_context_versions
FOR EACH ROW EXECUTE FUNCTION memory_gate.reject_memory_transition_history_change();

CREATE TRIGGER checkpoints_are_immutable
BEFORE UPDATE OR DELETE ON memory_core.checkpoints
FOR EACH ROW EXECUTE FUNCTION memory_gate.reject_memory_transition_history_change();

CREATE TRIGGER transition_receipts_are_immutable
BEFORE UPDATE OR DELETE ON memory_core.transition_receipts
FOR EACH ROW EXECUTE FUNCTION memory_gate.reject_memory_transition_history_change();

ALTER FUNCTION memory_gate.reject_memory_transition_history_change() OWNER TO neural_brain_owner;
REVOKE ALL ON FUNCTION memory_gate.reject_memory_transition_history_change() FROM PUBLIC;
