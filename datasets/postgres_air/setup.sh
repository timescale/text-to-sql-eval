#!/usr/bin/env bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/databases/postgres_air.sql" ]; then
  exit 0
fi

mkdir -p "${SCRIPT_DIR}/databases"

curl -o /tmp/postgres_air_2024.sql.zip https://popsql-misc.s3.us-east-1.amazonaws.com/postgres_air_2024.sql.zip
unzip -d "${SCRIPT_DIR}/databases" /tmp/postgres_air_2024.sql.zip
mv "${SCRIPT_DIR}/databases/postgres_air_2024.sql" "${SCRIPT_DIR}/databases/postgres_air.sql"

pushd "$SCRIPT_DIR/../.." || exit 1
uv run python3 scripts/strip_postgres_dump.py "${SCRIPT_DIR}/databases/postgres_air.sql"
