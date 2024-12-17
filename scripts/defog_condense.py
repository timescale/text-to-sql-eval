# Given the defog-data repo (https://github.com/defog-ai/defog-data) checked out
# in the parent directory, then this script will go through each SQL file,
# load it into a PostgreSQL database, add comments, and then dump it back out
# to our datasets/spider/databases directory.

import json
import os
from pathlib import Path
import psycopg
import subprocess

os.environ["PGPASSWORD"] = "postgres"
root_directory = Path(__file__).resolve().parent.parent
defog_data_dir = str(root_directory / "defog-data/defog_data")

for entry in os.scandir(defog_data_dir):
    if entry.is_file():
        continue
    dataset = entry.name
    with open(f"{defog_data_dir}/{dataset}/{dataset}.json") as f:
        data = json.load(f)
    subprocess.check_call(["psql", "-h", "localhost", "-U", "postgres", "-d", "postgres", "-c", f"DROP DATABASE IF EXISTS spider_{dataset}"])
    subprocess.check_call(["psql", "-h", "localhost", "-U", "postgres", "-d", "postgres", "-c", f"CREATE DATABASE spider_{dataset}"])
    subprocess.check_call(["psql", "-h", "localhost", "-U", "postgres", "-d", f"spider_{dataset}", "-f", f"{defog_data_dir}/{dataset}/{dataset}.sql"])
    with psycopg.connect(f"dbname=spider_{dataset} host=localhost user=postgres password=postgres") as conn:
        for table in data["table_metadata"]:
            for column in data["table_metadata"][table]:
              with conn.cursor() as cur:
                  cur.execute(f"COMMENT ON COLUMN {table}.{column['column_name']} IS '{column['column_description'].replace("'", "''")}'")
    subprocess.run(
        ["pg_dump", "-h", "localhost", "-U", "postgres", "--inserts", "--no-owner", "--no-publications", "-f", f"{str(root_directory)}/datasets/spider/databases/{dataset}-raw.sql", f"spider_{dataset}"],
    )
    with open(f"datasets/spider/databases/{dataset}-raw.sql", "r") as inp, open(f"{str(root_directory)}/datasets/spider/databases/{dataset}.sql", "w") as out:
        to_write = []
        for line in inp:
            if line.startswith("SELECT"):
                continue
            if line.startswith("SET"):
                continue
            if line.startswith("--"):
                continue
            to_write.append(line)
        while to_write and to_write[0].strip() == '':
            to_write.pop(0)
        while to_write and to_write[-1].strip() == '':
            to_write.pop()
        for i in range(len(to_write)):
            if i > 0 and to_write[i - 1].strip() == '' and to_write[i].strip() == '':
                continue
            out.write(to_write[i])
        out.write("\n")
    os.unlink(f"{str(root_directory)}/datasets/spider/databases/{dataset}-raw.sql")



