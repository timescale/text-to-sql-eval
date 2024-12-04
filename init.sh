#!/usr/bin/env sh

export PGPASSWORD=postgres

psql -U postgres -d postgres -f /datasets/world/data/data.sql
