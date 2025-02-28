import json
import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv

load_dotenv()


def get_psycopg_str(dbname: str = "postgres") -> str:
    return f"host={os.environ['POSTGRES_HOST']} dbname={dbname} user={os.environ['POSTGRES_USER']} password={os.environ['POSTGRES_PASSWORD']}"


root_directory = Path(__file__).resolve().parent.parent
datasets_dir = root_directory / "datasets"

failed = 0

datasets = sorted(os.listdir(datasets_dir))
for dataset in datasets:
    evals_path = datasets_dir / dataset / "evals"
    eval_paths = sorted(list(evals_path.iterdir()))
    connections = {}  # type: dict[str, psycopg.Connection]
    for eval_path in eval_paths:
        with (eval_path / "eval.json").open() as fp:
            inp = json.load(fp)
        if inp["database"] not in connections:
            connections[inp["database"]] = psycopg.connect(
                get_psycopg_str(f"{dataset}_{inp['database']}")
            )
        name = f"{dataset}_{inp['database']}/{eval_path.name}"
        error = ""
        try:
            with connections[inp["database"]].cursor() as cur:
                cur.execute(inp["query"])
                results = cur.fetchall()
                if len(results) == 0:
                    error = "No results"
                    print(f"  {name}: No results")
                    failed += 1
        except psycopg.DatabaseError as e:
            failed += 1
            error = f"Failed to execute query: {e}"
        finally:
            connections[inp["database"]].rollback()
        if error:
            print(f"  {name}: {error}")
            failed += 1
    for conn in connections.values():
        conn.close()

if failed > 0:
    raise SystemExit(f"Failed {failed} queries")
