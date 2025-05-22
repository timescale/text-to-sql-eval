import json
import os
from pathlib import Path
import time

import psycopg
from dotenv import load_dotenv

load_dotenv()


def get_psycopg_str(dbname: str = "postgres") -> str:
    return f"{os.environ['POSTGRES_DSN']}/{dbname}"


root_directory = Path(__file__).resolve().parent.parent
datasets_dir = root_directory / "datasets"

failed = 0

stats = {}

datasets = sorted(os.listdir(datasets_dir))
for dataset in datasets:
    evals_path = datasets_dir / dataset / "evals"
    print(f"Validating {dataset}...")
    stats[dataset] = {
        "total": 0,
        "avg_time": 0,
        "max_time": 0,
        "min_time": 0,
    }
    times = []
    eval_paths = sorted(list(evals_path.iterdir()))
    connections = {}  # type: dict[str, psycopg.Connection]
    for eval_path in eval_paths:
        stats[dataset]["total"] += 1
        with (eval_path / "eval.json").open() as fp:
            inp = json.load(fp)
        if inp["database"] not in connections:
            connections[inp["database"]] = psycopg.connect(
                get_psycopg_str(f"{dataset}_{inp['database']}")
            )
        name = f"{dataset}_{inp['database']}/{eval_path.name}"
        error = ""
        start_time = time.time()
        try:
            with connections[inp["database"]].cursor() as cur:
                cur.execute(inp["query"])
                results = cur.fetchall()
                if len(results) == 0:
                    error = "No results"
        except psycopg.DatabaseError as e:
            error = f"Failed to execute query: {e}"
        finally:
            connections[inp["database"]].rollback()
        times.append(time.time() - start_time)
        if error:
            print(f"  {name}: {error}")
            failed += 1
    for conn in connections.values():
        conn.close()
    stats[dataset]["avg_time"] = round(sum(times) / len(times), 5)
    stats[dataset]["max_time"] = round(max(times), 5)
    stats[dataset]["min_time"] = round(min(times), 5)
    print("Stats:")
    print(f"  {dataset}: {stats[dataset]['total']} queries")
    print(f"  {dataset}: {stats[dataset]['avg_time']} avg time")
    print(f"  {dataset}: {stats[dataset]['max_time']} max time")
    print(f"  {dataset}: {stats[dataset]['min_time']} min time")
    print()

print("Total queries:", sum([s["total"] for s in stats.values()]))
print("Avg time:", sum([s["avg_time"] for s in stats.values()]) / len(stats))
print("Max time:", max([s["max_time"] for s in stats.values()]))
print("Min time:", min([s["min_time"] for s in stats.values()]))

if failed > 0:
    raise SystemExit(f"Failed {failed} queries")
