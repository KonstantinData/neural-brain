CREATE SCHEMA migration_validation_fixture;

CREATE TABLE migration_validation_fixture.scoped_record (
    tenant_id text NOT NULL,
    area_id text NOT NULL,
    record_id bigint GENERATED ALWAYS AS IDENTITY,
    payload text NOT NULL,
    CONSTRAINT scoped_record_pk PRIMARY KEY (tenant_id, area_id, record_id)
);
