#!/usr/bin/env bash
set -Eeuo pipefail

: "${NEURAL_BRAIN_SCOPE_DB:?missing scoped database name}"
: "${NEURAL_BRAIN_SCOPE_USER:?missing scoped database user}"
: "${NEURAL_BRAIN_SCOPE_PASSWORD:?missing scoped database password}"

psql --username "$POSTGRES_USER" --dbname postgres -v ON_ERROR_STOP=1 \
  -v scope_db="$NEURAL_BRAIN_SCOPE_DB" \
  -v scope_user="$NEURAL_BRAIN_SCOPE_USER" \
  -v scope_password="$NEURAL_BRAIN_SCOPE_PASSWORD" <<'SQL'
CREATE ROLE :"scope_user"
  LOGIN
  PASSWORD :'scope_password'
  NOSUPERUSER
  NOCREATEDB
  NOCREATEROLE
  NOINHERIT
  NOREPLICATION;

CREATE DATABASE :"scope_db" OWNER :"scope_user";
REVOKE ALL ON DATABASE :"scope_db" FROM PUBLIC;
GRANT CONNECT, TEMPORARY ON DATABASE :"scope_db" TO :"scope_user";
SQL

psql --username "$POSTGRES_USER" --dbname "$NEURAL_BRAIN_SCOPE_DB" -v ON_ERROR_STOP=1 \
  -v scope_user="$NEURAL_BRAIN_SCOPE_USER" <<'SQL'
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
GRANT USAGE, CREATE ON SCHEMA public TO :"scope_user";
SQL
