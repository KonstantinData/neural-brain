ALTER TABLE migration_validation_fixture.scoped_record
    ADD COLUMN aggregate_version bigint NOT NULL DEFAULT 1,
    ADD CONSTRAINT scoped_record_aggregate_version_positive CHECK (aggregate_version > 0);
