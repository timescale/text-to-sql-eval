"""
Given the BIRD mini dataset at ../bird_minidev, this:
1. Loads the SQL file from MINIDEV_POSTGRESQL/BIRD_dev.sql into a database
2. Add comments to each column based on MINIDEV/dev_databases/*/database_description/*.csv
3. Splits the tables into their own respective databases based on bird_minidev/dev_tables.json
4. Separates out MINIDEV/mini_dev_postgresql.json into individual eval files
"""

import csv
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

import psycopg
from dotenv import load_dotenv

load_dotenv()

skip_load = False
for arg in sys.argv:
    if arg == "--skip-load":
        skip_load = True


def get_psycopg_str(dbname: str = "postgres") -> str:
    return f"{os.environ['PGAI_POSTGRES_DSN']}/{dbname}"


current_directory = Path(__file__).parent
dataset_dir = current_directory / ".." / "datasets" / "bird"
shutil.rmtree(dataset_dir)
(dataset_dir / "databases").mkdir(parents=True)
(dataset_dir / "evals").mkdir()

bird_dir = Path(current_directory, "..", "bird_minidev")

pg_uri = urlparse(os.environ["PGAI_POSTGRES_DSN"])

if not skip_load:
    with (bird_dir / "MINIDEV" / "dev_tables.json").open() as fp:
        dev_tables = json.load(fp)

    with psycopg.connect(get_psycopg_str()) as conn:
        conn.autocommit = True
        conn.execute("DROP DATABASE IF EXISTS bird_minidev")
        conn.execute("CREATE DATABASE bird_minidev")

        base_args = [
            "-h",
            pg_uri.hostname,
            "-U",
            pg_uri.username,
            "-d",
            "bird_minidev",
        ]

        env = os.environ.copy()
        env["PGPASSWORD"] = pg_uri.password

        cmd = [
            "psql",
            *base_args,
            "-f",
            str(bird_dir / "MINIDEV_postgresql" / "BIRD_dev.sql"),
        ]
        subprocess.run(cmd, check=True, env=env)

    with psycopg.connect(get_psycopg_str("bird_minidev")) as conn:
        conn.autocommit = True
        for db_dir in (bird_dir / "MINIDEV" / "dev_databases").iterdir():
            for csv_file in (db_dir / "database_description").iterdir():
                with csv_file.open("r", encoding="latin-1") as fp:
                    reader = csv.reader(fp)
                    next(reader)
                    for row in reader:
                        column_name = row[0].strip()
                        description = row[2].strip()
                        extra = row[4].strip()

                    table_name = csv_file.stem.lower()
                    comment = f"{description}."
                    if extra:
                        comment += f" {extra}."
                    comment = comment.replace("'", "''")
                    try:
                        conn.execute(
                            f'COMMENT ON COLUMN "{table_name}"."{column_name}" IS \'{comment}\''
                        )
                    except:
                        try:
                            conn.execute(
                                f'COMMENT ON COLUMN "{table_name}"."{column_name.lower()}" IS \'{comment}\''
                            )
                        except:
                            pass

for obj in dev_tables:
    cmd = [
        "pg_dump",
        *base_args,
        "--inserts",
        "--no-owner",
        "--no-publications",
    ]
    for table in obj["table_names"]:
        cmd.extend(["-t", table])
    output_file = dataset_dir / "databases" / f"{obj["db_id"]}.sql"
    cmd.extend(["-f", str(output_file)])
    subprocess.run(cmd, check=True, env=env)

    subprocess.run(
        [
            "uv",
            "run",
            "scripts/strip_postgres_dump.py",
            str(output_file),
        ],
        cwd=str(current_directory.parent),
    )

    subprocess.run(
        [
            "uv",
            "run",
            "scripts/split_file.py",
            str(output_file),
        ],
        cwd=str(current_directory.parent),
    )


question_file = bird_dir / "MINIDEV" / "mini_dev_postgresql.json"

evals_dir = dataset_dir / "evals"
with question_file.open("r") as fp:
    questions = json.load(fp)  # type: list[dict[str, str]]
    zfill = len(str(len(questions)))
    cnt = 1
    for question in questions:
        name = str(cnt).zfill(zfill)
        (evals_dir / name).mkdir()

        obj = {
            "database": question["db_id"],
            "question": f"{question["question"]}\n{question.get('evidence', '')}",
            "query": question["SQL"],
        }

        with (evals_dir / name / "eval.json").open("w") as fp:
            json.dump(obj, fp, indent=2)
        cnt += 1
