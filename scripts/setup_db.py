import os

import psycopg
from dotenv import load_dotenv

load_dotenv()

with psycopg.connect(os.environ["REPORT_POSTGRES_DSN"]) as conn:
    with conn.cursor() as cur:
        cur.execute("DROP TABLE IF EXISTS evals")
        cur.execute("DROP TABLE IF EXISTS runs CASCADE")
        # once ai.version is implemented, add in pgai_version column
        cur.execute("""
            CREATE TABLE runs (
                id SERIAL PRIMARY KEY,
                source TEXT NOT NULL,
                start_time TIMESTAMP NOT NULL,
                end_time TIMESTAMP,
                task TEXT NOT NULL,
                scores JSON,
                details JSON
            )
        """)

        cur.execute("""
            CREATE TABLE evals (
                id SERIAL PRIMARY KEY,
                run_id INT REFERENCES runs(id),
                dataset text NOT NULL,
                database text NOT NULL,
                name text NOT NULL,
                question text NOT NULL,
                status text NOT NULL,
                duration NUMERIC NOT NULL,
                details JSON
            )
        """)

        conn.commit()

print("Database created.")
