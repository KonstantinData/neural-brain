-- S1-06.1: issuer-bound Memory Core authority grants and immutable snapshots.
-- This catalog is evidence only. It does not change Memory Gate ownership or
-- release retrieval, disclosure, promotion, deletion, Goal, Action, or effects.

CREATE TABLE brain_security.memory_authority_grants (
    grant_id text PRIMARY KEY,
    issuer_id text NOT NULL REFERENCES brain_security.principals (principal_id),
    principal_id text NOT NULL REFERENCES brain_security.principals (principal_id),
    tenant_id text NOT NULL,
    area_id text NOT NULL,
    project_id text,
    session_id text,
    operation text NOT NULL CHECK (operation IN ('intake', 'retrieval', 'disclosure', 'promotion', 'correction', 'retention', 'deletion')),
    resource_pattern text NOT NULL,
    data_class text NOT NULL CHECK (data_class IN ('public', 'internal', 'confidential', 'restricted')),
    purpose text NOT NULL,
    environment text NOT NULL,
    status text NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'revoked', 'expired')),
    valid_from timestamptz NOT NULL DEFAULT transaction_timestamp(),
    valid_until timestamptz NOT NULL,
    created_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
    FOREIGN KEY (tenant_id, area_id) REFERENCES brain_catalog.areas (tenant_id, area_id),
    FOREIGN KEY (tenant_id, area_id, project_id) REFERENCES brain_catalog.projects (tenant_id, area_id, project_id),
    FOREIGN KEY (tenant_id, area_id, project_id, session_id) REFERENCES brain_catalog.sessions (tenant_id, area_id, project_id, session_id),
    CHECK (grant_id <> '' AND length(grant_id) <= 128),
    CHECK (issuer_id <> principal_id),
    CHECK (resource_pattern <> '' AND length(resource_pattern) <= 256),
    CHECK (purpose <> '' AND length(purpose) <= 128),
    CHECK (environment <> '' AND length(environment) <= 128),
    CHECK (valid_until > valid_from),
    CHECK (session_id IS NULL OR project_id IS NOT NULL)
);

CREATE TABLE brain_security.memory_authority_snapshots (
    snapshot_id text PRIMARY KEY,
    grant_id text NOT NULL REFERENCES brain_security.memory_authority_grants (grant_id),
    grant_digest char(64) NOT NULL CHECK (grant_digest ~ '^[0-9a-f]{64}$'),
    principal_id text NOT NULL REFERENCES brain_security.principals (principal_id),
    tenant_id text NOT NULL,
    area_id text NOT NULL,
    project_id text NOT NULL,
    session_id text NOT NULL,
    operation text NOT NULL CHECK (operation IN ('intake', 'retrieval', 'disclosure', 'promotion', 'correction', 'retention', 'deletion')),
    resource text NOT NULL,
    data_class text NOT NULL CHECK (data_class IN ('public', 'internal', 'confidential', 'restricted')),
    purpose text NOT NULL,
    environment text NOT NULL,
    captured_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
    valid_until timestamptz NOT NULL,
    FOREIGN KEY (tenant_id, area_id) REFERENCES brain_catalog.areas (tenant_id, area_id),
    FOREIGN KEY (tenant_id, area_id, project_id) REFERENCES brain_catalog.projects (tenant_id, area_id, project_id),
    FOREIGN KEY (tenant_id, area_id, project_id, session_id) REFERENCES brain_catalog.sessions (tenant_id, area_id, project_id, session_id),
    CHECK (snapshot_id <> '' AND length(snapshot_id) <= 128),
    CHECK (resource <> '' AND length(resource) <= 256),
    CHECK (purpose <> '' AND length(purpose) <= 128),
    CHECK (environment <> '' AND length(environment) <= 128),
    CHECK (valid_until > captured_at)
);

CREATE FUNCTION brain_security.reject_memory_authority_snapshot_change()
RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER SET search_path = pg_catalog AS $$
BEGIN
    RAISE EXCEPTION 'memory authority snapshots are immutable' USING ERRCODE = '55000';
END;
$$;

CREATE TRIGGER memory_authority_snapshot_is_immutable
BEFORE UPDATE OR DELETE ON brain_security.memory_authority_snapshots
FOR EACH ROW EXECUTE FUNCTION brain_security.reject_memory_authority_snapshot_change();

ALTER TABLE brain_security.memory_authority_grants OWNER TO neural_brain_owner;
ALTER TABLE brain_security.memory_authority_snapshots OWNER TO neural_brain_owner;
ALTER FUNCTION brain_security.reject_memory_authority_snapshot_change() OWNER TO neural_brain_owner;
REVOKE ALL ON brain_security.memory_authority_grants, brain_security.memory_authority_snapshots FROM PUBLIC;
REVOKE ALL ON FUNCTION brain_security.reject_memory_authority_snapshot_change() FROM PUBLIC;
