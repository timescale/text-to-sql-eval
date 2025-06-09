import asyncio
import json
import os
import subprocess
import time
from pathlib import Path
from traceback import format_exc
from typing import Dict, Optional

import click
import psycopg
from dotenv import load_dotenv
from psycopg.sql import SQL, Identifier
from yaml import safe_load_all

from .agents import get_agent_fn, get_agent_setup_fn, get_agent_version
from .exceptions import GetExpectedError
from .tasks.get_tables import run as get_tables
from .tasks.text_to_sql import run as text_to_sql
from .types import Results
from .utils import (
    expand_embedding_model,
    expand_task_model,
    get_psycopg_str,
)

load_dotenv()

root_directory = Path(__file__).resolve().parent.parent
datasets_dir = root_directory / "datasets"
results_dir = root_directory / "results"


@click.group()
def cli():
    pass


@cli.command()
@click.option(
    "--filter", default=None, help="Comma separated list of datasets to include"
)
def generate_matrix(filter: Optional[str]) -> None:
    """
    Generates a matrix of all datasets and their databases for GitHub actions.

    When using the `--filter` option, for each entry, it will check if for each
    [dataset, database] pair, if there is a prefix match with an entry in the filter.
    For example, `--filter=s,bird` will include `spider` and `bird` datasets.
    """

    include = []

    for dataset in datasets_dir.iterdir():
        if not dataset.is_dir():
            continue
        if (dataset / "databases.json").exists():
            with (dataset / "databases.json").open("r") as fp:
                databases = json.load(fp)
            for db in databases:
                include.append({"dataset": dataset.name, "database": db})
            continue
        for database in (dataset / "databases").iterdir():
            if database.suffix != ".sql":
                continue
            if not database.is_file():
                continue
            db_name = database.name
            if ".part" in db_name and ".part000" not in db_name:
                continue
            if ".part000" in db_name:
                db_name = db_name[:-12]
            else:
                db_name = database.stem
            include.append({"dataset": dataset.name, "database": db_name})
    if filter is not None:
        filter_datasets = [x.strip() for x in filter.split(",")]
        filtered_include = []
        for entry in include:
            for dataset in filter_datasets:
                if f"{entry['dataset']}_{entry['database']}".startswith(dataset):
                    filtered_include.append(entry)
        include = filtered_include
    print(json.dumps({"include": include}))


@cli.command()
@click.option(
    "--dataset", default="all", help="Dataset to load [defaults to all datasets]"
)
@click.option(
    "--database", default="all", help="Database to load [defaults to all databases]"
)
def load(
    dataset: str,
    database: str,
) -> None:
    """
    Load the datasets into the database.
    """
    datasets = os.listdir(datasets_dir) if dataset == "all" else [dataset]
    print("Loading datasets...")
    for i in range(len(datasets)):
        if i > 0:
            print()
        dataset = datasets[i]
        print(f"  {dataset}")
        setup_sh = datasets_dir / dataset / "setup.sh"
        if setup_sh.exists():
            print("    Running setup.sh")
            subprocess.run(f"bash {str(setup_sh)}", shell=True, check=True)
        for entry in (datasets_dir / dataset / "databases").iterdir():
            if entry.suffix != ".sql":
                continue
            if ".part" in entry.name and ".part000" not in entry.name:
                continue
            name = entry.stem if ".part" not in entry.name else entry.name[:-12]
            if database != "all" and name != database:
                continue
            db_name = f"{dataset}_{name}"
            print(f"    {db_name}")
            with psycopg.connect(get_psycopg_str()) as root_db:
                root_db.autocommit = True
                print("      DROP DATABASE")
                root_db.execute(f"DROP DATABASE IF EXISTS {db_name}")
                print("      CREATE DATABASE")
                root_db.execute(f"CREATE DATABASE {db_name}")

            def load_sql_file(db_url, sql_file: Path) -> None:
                subprocess.run(["psql", "-q", db_url, "-f", str(sql_file)], check=True)

            db_url = get_psycopg_str(db_name)
            with psycopg.connect(db_url) as db:
                print("      Restoring dump")
                if ".part" not in entry.name:
                    load_sql_file(db_url, entry)
                else:
                    i = 0
                    while True:
                        sql_file = entry.parent / f"{name}.part{str(i).zfill(3)}.sql"
                        if not sql_file.exists():
                            break
                        load_sql_file(db_url, sql_file)
                        i += 1
                print("      Loading descriptions")
                with (datasets_dir / dataset / "databases" / f"{name}.yaml").open(
                    "r"
                ) as fp:
                    for doc in safe_load_all(fp):
                        if doc["type"] != "table":
                            continue
                        with db.cursor() as cur:
                            cur.execute(
                                SQL("COMMENT ON TABLE {}.{} IS {}").format(
                                    Identifier(doc["schema"]),
                                    Identifier(doc["name"]),
                                    doc["description"],
                                ),
                            )
                            for column in doc["columns"]:
                                cur.execute(
                                    SQL("COMMENT ON COLUMN {}.{}.{} IS {}").format(
                                        Identifier(doc["schema"]),
                                        Identifier(doc["name"]),
                                        Identifier(column["name"]),
                                        column["description"],
                                    ),
                                )


@cli.command()
@click.argument("agent")
@click.option(
    "--model",
    default="openai:text-embedding-3-small",
    help="Model to use for embedding",
)
@click.option("--dimensions", default=576, help="Number of dimensions for embeddings")
@click.option(
    "--dataset", default="all", help="Dataset to setup [default all datasets]"
)
@click.option("--database", default=None, help="Database to setup")
def setup(
    agent: str,
    model: Optional[str],
    dimensions: int,
    dataset: str,
    database: Optional[str],
) -> None:
    """
    Setup the agent
    """
    try:
        [provider, model] = expand_embedding_model(model).split(":", 1)
    except ValueError:
        raise ValueError(f"Invalid model: {model}") from None
    agent_setup_fn = get_agent_setup_fn(agent)
    print(f"Setting up agent {agent}...")
    datasets = sorted(os.listdir(datasets_dir) if dataset == "all" else [dataset])

    async def run():
        for i in range(len(datasets)):
            if i > 0:
                print()
            dataset = datasets[i]
            print(f"  Setting up {dataset}...")
            for entry in (datasets_dir / dataset / "databases").iterdir():
                if entry.suffix != ".sql":
                    continue
                if ".part" in entry.name and ".part000" not in entry.name:
                    continue
                name = entry.stem if ".part" not in entry.name else entry.name[:-12]
                if database and name != database:
                    continue
                db_name = f"{dataset}_{name}"
                print(f"    {db_name}", end="")
                with psycopg.connect(get_psycopg_str(db_name)) as db:
                    await agent_setup_fn(
                        db,
                        dataset,
                        provider,
                        model,
                        dimensions,
                    )
                print(" done")

    asyncio.run(run())


@cli.command()
@click.argument("agent")
@click.argument("task")
@click.option(
    "--model", default="openai:gpt-4.1-nano", help="Model to use for the task"
)
@click.option(
    "--dataset", default="all", help="Dataset to evaluate [default eval all datasets]"
)
@click.option("--database", default=None, help="Database to evaluate")
@click.option("--eval", default=None, help="Eval case to run")
@click.option("--fast", is_flag=True, default=False, help="Run 50 evals per dataset")
@click.option(
    "--entire-schema",
    is_flag=True,
    default=False,
    help="Agent should always use entire schema in LLM prompt",
)
@click.option(
    "--gold-tables",
    is_flag=True,
    default=False,
    help="Agent should only use gold tables in LLM prompt",
)
@click.option("--strict", is_flag=True, default=False, help="Use strict evaluation")
def eval(
    task: str,
    agent: str,
    model: str,
    dataset: str,
    database: Optional[str],
    eval: Optional[str],
    fast: bool,
    entire_schema: bool,
    gold_tables: bool,
    strict: bool,
) -> None:
    """
    Runs the eval suite for a given agent and task.

    The agent can be one of "baseline" or "pgai".
    The task can be one of "get_tables" or "text_to_sql".
    """
    try:
        [provider, model] = expand_task_model(model).split(":", 1)
    except ValueError:
        raise ValueError(f"Invalid model: {model}") from None
    if task not in ["get_tables", "text_to_sql"]:
        raise ValueError(f"Invalid task: {task}")
    datasets = sorted(os.listdir(datasets_dir) if dataset == "all" else [dataset])
    task_fn = get_tables if task == "get_tables" else text_to_sql
    agent_fn = get_agent_fn(agent, task)
    errored_evals = {}  # type: dict[str, list[str]]
    failed_evals = {}  # type: dict[str, list[str]]
    failed_error_counts = {}  # type: dict[str, dict[str, int]]
    eval_results = {}  # type: dict[str, Any]
    results: Dict[str, str | Dict[str, Results]] = {
        "task": task,
        "details": {
            "agent": {
                "name": agent,
                "version": get_agent_version(agent),
            },
            "provider": provider,
            "model": model,
            "fast": fast,
            "entire_schema": entire_schema,
            "gold_tables": gold_tables,
        },
        "results": {},
    }

    async def run():
        for i in range(len(datasets)):
            if i > 0:
                print()
            dataset = datasets[i]
            errored_evals[dataset] = []
            failed_evals[dataset] = []
            failed_error_counts[dataset] = {}
            eval_results[dataset] = []
            total_duration = 0
            usage = {
                "cached_tokens": 0,
                "cached_tokens_cost": 0.0,
                "request_tokens": 0,
                "request_tokens_cost": 0.0,
                "response_tokens": 0,
                "response_tokens_cost": 0.0,
            }
            passing = 0
            total = 0
            print(f"Evaluating {dataset}", end="")
            evals_path = datasets_dir / dataset / "evals"
            eval_paths = sorted(list(evals_path.iterdir()))
            evals_to_run = []
            for eval_path in eval_paths:
                if eval is not None and eval_path.name != eval:
                    continue
                with (eval_path / "eval.json").open() as fp:
                    inp = json.load(fp)
                if database and inp["database"] != database:
                    continue
                evals_to_run.append(eval_path)

            sample_size = 50
            if fast and len(evals_to_run) > sample_size:
                print(f" (sampling {sample_size} evals of {len(evals_to_run)})...")
                step = (len(evals_to_run) - 1) / (sample_size - 1)
                indices = [round(i * step) for i in range(sample_size)]
                evals_to_run = [evals_to_run[i] for i in indices]
            else:
                print(f" ({len(evals_to_run)} evals)...")

            for eval_path in evals_to_run:
                if eval is not None and eval_path.name != eval:
                    continue
                with (eval_path / "eval.json").open() as fp:
                    inp = json.load(fp)
                if database and inp["database"] != database:
                    continue
                print(f"  {eval_path.name}:", flush=True)
                total += 1
                with psycopg.connect(
                    get_psycopg_str(f"{dataset}_{inp['database']}")
                ) as db:
                    with db.cursor() as cur:
                        cur.execute("SET LOCAL statement_timeout = 120000;")

                    error_path = eval_path / "error.txt"
                    if error_path.exists():
                        error_path.unlink()
                    start = time.time()
                    try:
                        result = await task_fn(
                            db,
                            str(eval_path),
                            inp["question"],
                            agent_fn,
                            provider,
                            model,
                            entire_schema,
                            gold_tables,
                            strict,
                        )
                    except GetExpectedError:
                        total -= 1
                        continue
                    except Exception as e:
                        result = {
                            "status": "error",
                            "details": {
                                "exception_class": type(e).__name__,
                                "exception": str(e),
                                "exception_traceback": format_exc(),
                            },
                        }
                    duration = round(time.time() - start, 3)
                result["dataset"] = dataset
                result["database"] = inp["database"]
                result["name"] = eval_path.name
                result["question"] = inp["question"]
                if "duration" not in result:
                    result["duration"] = duration
                result["details"]["question"] = inp["question"]
                total_duration += result["duration"]
                if "usage" in result["details"]:
                    usage["cached_tokens"] += result["details"]["usage"][
                        "cached_tokens"
                    ]
                    usage["cached_tokens_cost"] += result["details"]["usage"][
                        "cached_tokens_cost"
                    ]
                    usage["request_tokens"] += result["details"]["usage"][
                        "request_tokens"
                    ]
                    usage["request_tokens_cost"] += result["details"]["usage"][
                        "request_tokens_cost"
                    ]
                    usage["response_tokens"] += result["details"]["usage"][
                        "response_tokens"
                    ]
                    usage["response_tokens_cost"] += result["details"]["usage"][
                        "response_tokens_cost"
                    ]
                to_print = f"    {result['status'].upper()}"
                print(to_print, end="", flush=True)
                if result["status"] == "error":
                    class_name = result["details"]["exception_class"]
                    if class_name not in failed_error_counts[dataset]:
                        failed_error_counts[dataset][class_name] = 0
                    failed_error_counts[dataset][class_name] += 1
                    print(
                        f" ({class_name}: {result['details']['exception']})",
                        end="",
                        flush=True,
                    )
                    with error_path.open("w") as fp:
                        fp.write(class_name + "\n\n")
                        fp.write(result["details"]["exception_traceback"] + "\n\n")
                        fp.write(result["details"]["exception"])
                print(flush=True)
                if result["status"] == "pass":
                    passing += 1
                elif result["status"] == "fail":
                    failed_evals[dataset].append(eval_path.name)
                else:
                    errored_evals[dataset].append(eval_path.name)
                eval_results[dataset].append(result)

            print(
                f"  {1 if total == 0 else round(passing/total, 2)} ({passing}/{total})"
            )
            if len(failed_evals[dataset]) > 0:
                print("Failed error type counts:")
                for error in sorted(failed_error_counts[dataset].keys()):
                    print(f"  {error}: {failed_error_counts[dataset][error]}")
                print(f"Failed evals:\n{sorted(failed_evals[dataset])}")
            if len(errored_evals[dataset]) > 0:
                print(f"Errored evals:\n{sorted(errored_evals[dataset])}")

            total_duration = round(total_duration, 3)

            print(f"  Total duration: {total_duration} seconds")
            print("  Usage:")
            print(f"    Request tokens: {usage['request_tokens']}")
            print(f"    Request tokens cost: ${usage['request_tokens_cost']:.8f}")
            print(f"    Cached tokens: {usage['cached_tokens']}")
            print(f"    Cached tokens cost: ${usage['cached_tokens_cost']:.8f}")
            print(f"    Response tokens: {usage['response_tokens']}")
            print(f"    Response tokens cost: ${usage['response_tokens_cost']:.8f}")

            results["results"][dataset] = {
                "passing": passing,
                "total": total,
                "total_duration": total_duration,
                "usage": usage,
                "failed": failed_evals[dataset],
                "failed_error_counts": failed_error_counts[dataset],
                "errored": errored_evals[dataset],
                "evals": eval_results[dataset],
            }

    asyncio.run(run())
    with (results_dir / "results.json").open("w") as fp:
        json.dump(
            results,
            fp,
        )


@cli.command()
def generate_report():
    combined_results = {}  # type: dict[str, Results]
    if not results_dir.exists() or not results_dir.is_dir():
        print("No results direcotry found. Please run the eval command first.")
        return

    for results_file in results_dir.iterdir():
        if not results_file.is_file() or not results_file.name.endswith(".json"):
            continue
        with results_file.open() as fp:
            try:
                results_obj = json.load(fp)
            except json.JSONDecodeError:
                print(f"Failed to decode {results_file.name}, contents:")
                print()
                print(fp.read())
                print()
                print("Skipping file...")
                continue
        results = results_obj["results"]
        for dataset, result in results.items():
            if dataset not in combined_results:
                combined_results[dataset] = {
                    "passing": 0,
                    "total": 0,
                    "total_duration": 0,
                    "usage": {
                        "cached_tokens": 0,
                        "cached_tokens_cost": 0.0,
                        "request_tokens": 0,
                        "request_tokens_cost": 0.0,
                        "response_tokens": 0,
                        "response_tokens_cost": 0.0,
                    },
                    "failed": [],
                    "failed_error_counts": {},
                    "errored": [],
                    "evals": [],
                }
            combined_results[dataset]["passing"] += result["passing"]
            combined_results[dataset]["total"] += result["total"]
            combined_results[dataset]["failed"] += result["failed"]
            combined_results[dataset]["total_duration"] += result["total_duration"]
            if "usage" in result:
                combined_results[dataset]["usage"]["cached_tokens"] += result["usage"][
                    "cached_tokens"
                ]
                combined_results[dataset]["usage"]["cached_tokens_cost"] += result[
                    "usage"
                ]["cached_tokens_cost"]
                combined_results[dataset]["usage"]["request_tokens"] += result["usage"][
                    "request_tokens"
                ]
                combined_results[dataset]["usage"]["request_tokens_cost"] += result[
                    "usage"
                ]["request_tokens_cost"]
                combined_results[dataset]["usage"]["response_tokens"] += result[
                    "usage"
                ]["response_tokens"]
                combined_results[dataset]["usage"]["response_tokens_cost"] += result[
                    "usage"
                ]["response_tokens_cost"]
            for error, count in result["failed_error_counts"].items():
                if error not in combined_results[dataset]["failed_error_counts"]:
                    combined_results[dataset]["failed_error_counts"][error] = 0
                combined_results[dataset]["failed_error_counts"][error] += count
            combined_results[dataset]["errored"] += result["errored"]
            combined_results[dataset]["evals"] += result["evals"]

    passing = 0
    total = 0
    for results in combined_results.values():
        passing += results["passing"]
        total += results["total"]
    print(f"Overall: {passing}/{total} ({round(passing/total, 2)})")
    print(
        f"  Total duration: {round(sum([x['total_duration'] for x in combined_results.values()]), 3)}"
    )
    print("  Usage:")
    print(
        f"    Request tokens: {sum([x['usage']['request_tokens'] for x in combined_results.values()])}"
    )
    print(
        f"    Request tokens cost: ${sum([x['usage']['request_tokens_cost'] for x in combined_results.values()]):.8f}"
    )
    print(
        f"    Cached tokens: {sum([x['usage']['cached_tokens'] for x in combined_results.values()])}"
    )
    print(
        f"    Cached tokens cost: ${sum([x['usage']['cached_tokens_cost'] for x in combined_results.values()]):.8f}"
    )
    print(
        f"    Response tokens: {sum([x['usage']['response_tokens'] for x in combined_results.values()])}"
    )
    print(
        f"    Response tokens cost: ${sum([x['usage']['response_tokens_cost'] for x in combined_results.values()]):.8f}"
    )
    print()

    i = 0
    for dataset in sorted(combined_results.keys()):
        if i > 0:
            print()
        results = combined_results[dataset]
        print(
            f"{dataset}: {results['passing']}/{results['total']} ({round(results['passing']/results['total'], 2)})"
        )
        print(f"  Total duration: {round(results['total_duration'], 3)}")
        print("  Usage:")
        print(f"    Request tokens: {results['usage']['request_tokens']}")
        print(
            f"    Request tokens cost: ${results['usage']['request_tokens_cost']:.8f}"
        )
        print(f"    Cached tokens: {results['usage']['cached_tokens']}")
        print(f"    Cached tokens cost: ${results['usage']['cached_tokens_cost']:.8f}")
        print(f"    Response tokens: {results['usage']['response_tokens']}")
        print(
            f"    Response tokens cost: ${results['usage']['response_tokens_cost']:.8f}"
        )
        if len(results["failed"]) > 0:
            print("  Failed error type counts:")
            for error in sorted(results["failed_error_counts"].keys()):
                print(f"    {error}: {results['failed_error_counts'][error]}")
            print(f"  Failed evals:\n    {sorted(results['failed'])}")

        if len(results["errored"]) > 0:
            print(f"  Errored evals:\n    {sorted(results['errored'])}")
        i += 1

    # save results if REPORT_POSTGRES_DSN is set
    if os.environ.get("REPORT_POSTGRES_DSN", ""):
        print("Saving results to database...", end="")
        try:
            with psycopg.connect(os.environ["REPORT_POSTGRES_DSN"]) as conn:
                with conn.cursor() as cursor:
                    scores = {}
                    for dataset in combined_results:
                        scores[dataset] = {
                            "passing": combined_results[dataset]["passing"],
                            "total": combined_results[dataset]["total"],
                        }
                    cursor.execute(
                        """
                        INSERT INTO runs (source, start_time, end_time, scores, task, details)
                        VALUES (%s, now(), now(), %s, %s, %s)
                        RETURNING id
                        """,
                        (
                            os.environ.get("SOURCE", "local"),
                            json.dumps(scores),
                            results_obj["task"],
                            json.dumps(results_obj["details"]),
                        ),
                    )
                    run_id = cursor.fetchone()[0]
                    for value in combined_results.values():
                        for eval in value["evals"]:
                            cursor.execute(
                                """
                                INSERT INTO evals (run_id, dataset, database, name, question, status, duration, details)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                                """,
                                (
                                    run_id,
                                    eval["dataset"],
                                    eval["database"],
                                    eval["name"],
                                    eval["question"],
                                    eval["status"],
                                    eval["duration"],
                                    json.dumps(eval["details"]),
                                ),
                            )
            print(" done")
        except BaseException as e:
            print(" ERROR")
            print("Failed to save results to database")
            print(f"Error: {e}")
            print(format_exc())
            print()
            return
