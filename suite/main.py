import json
import os
from pathlib import Path
from traceback import format_exc
from typing import Optional

import click
import psycopg
from dotenv import load_dotenv

from .agents import get_agent_fn
from .exceptions import GetExpectedError
from .tasks.get_tables import run as get_tables
from .tasks.text_to_sql import run as text_to_sql
from .types import Results
from .utils import (
    get_default_embedding_model,
    get_default_model,
    get_psycopg_str,
    setup_pgai_config,
    validate_embedding_provider,
    validate_provider,
)

load_dotenv()

root_directory = Path(__file__).resolve().parent.parent
datasets_dir = root_directory / "datasets"


@click.group()
def cli():
    pass


@cli.command()
@click.argument("stage")
@click.argument("provider")
@click.argument("model", required=False)
def get_model(stage: str, provider: str, model: Optional[str]) -> None:
    """
    Given a provider, returns the default model for it if no model was provided.
    """
    if stage not in ["eval", "load"]:
        raise ValueError(f"Invalid stage: {stage}")
    if model is None:
        fn = get_default_model if stage == "eval" else get_default_embedding_model
        model = fn(provider)
    print(model)


@cli.command()
def generate_matrix() -> None:
    """
    Generates a matrix of all datasets and their databases for GitHub actions.
    """

    include = []

    for dataset in datasets_dir.iterdir():
        if not dataset.is_dir():
            continue
        for database in (dataset / "databases").iterdir():
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
    print(json.dumps({"include": include}))


@cli.command()
@click.option(
    "--provider",
    default="ollama",
    help="Provider to use for embeddings [default ollama]",
)
@click.option("--model", default=None, help="Model to use for embeddings")
@click.option("--dimensions", default=576, help="Number of dimensions for embeddings")
@click.option(
    "--dataset", default="all", help="Dataset to load [defaults to all datasets]"
)
@click.option(
    "--database", default="all", help="Database to load [defaults to all databases]"
)
@click.option(
    "--no-comments",
    is_flag=True,
    default=False,
    help="Do not use obj comments for embeddings",
)
def load(
    provider: str,
    model: Optional[str],
    dimensions: int,
    dataset: str,
    database: str,
    no_comments: bool,
) -> None:
    """
    Load the datasets into the database.
    """
    validate_embedding_provider(provider)
    if model is None:
        model = get_default_embedding_model(provider)
    datasets = os.listdir(datasets_dir) if dataset == "all" else [dataset]
    with psycopg.connect(get_psycopg_str()) as root_db:
        with root_db.cursor() as cur:
            cur.execute("SELECT * FROM pg_available_extensions WHERE name = 'ai'")
            pgai = len(cur.fetchall()) > 0
    print(f"pgai: {pgai}")
    print("Loading datasets...")
    for i in range(len(datasets)):
        if i > 0:
            print()
        dataset = datasets[i]
        print(f"  {dataset}")
        for entry in (datasets_dir / dataset / "databases").iterdir():
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
            with psycopg.connect(get_psycopg_str(db_name)) as db:
                print("      Restoring dump")
                if ".part" not in entry.name:
                    with entry.open() as fp:
                        db.execute(fp.read())
                else:
                    i = 0
                    while True:
                        sql_file = entry.parent / f"{name}.part{str(i).zfill(3)}.sql"
                        if not sql_file.exists():
                            break
                        db.execute(sql_file.read_text())
                        i += 1
                if pgai:
                    print("      Initializing pgai")
                    with db.cursor() as cur:
                        setup_pgai_config(cur)
                        cur.execute(
                            "select set_config('ai.enable_feature_flag_text_to_sql', 'true', false)"
                        )
                        cur.execute("CREATE EXTENSION ai CASCADE")
                        cur.execute("select ai.grant_ai_usage('postgres', true)")
                        cur.execute(
                            f"""
                            select ai.create_semantic_catalog(
                                embedding=>ai.embedding_{provider}(
                                    %s,
                                    %s
                                )
                            )
                            """,
                            (
                                model,
                                dimensions,
                            ),
                        )
                        db.commit()
                        cur.execute(
                            """
                            SELECT table_name
                            FROM information_schema.tables
                            WHERE table_schema = 'public'
                            AND table_type = 'BASE TABLE';
                            """
                        )
                        tables = []
                        for row in cur.fetchall():
                            tables.append(row[0])
                        cur.execute(
                            """
                            SELECT
                                table_schema,
                                table_name,
                                column_name,
                                col_description(('"' || table_schema || '"."' || table_name || '"')::regclass::oid, ordinal_position) AS column_comment
                            FROM
                                information_schema.columns
                            WHERE
                                table_schema = 'public'
                            ORDER BY
                                table_schema,
                                table_name,
                                ordinal_position;
                            """
                        )
                        columns = []
                        for row in cur.fetchall():
                            columns.append(row)
                        for table in tables:
                            cur.execute(
                                f"select ai.set_description('{table}', '{table}');"
                            )
                        for column in columns:
                            cur.execute(
                                "select ai.set_column_description(%s, %s, %s);",
                                (
                                    column[1],
                                    column[2],
                                    column[3]
                                    if column[3] and not no_comments
                                    else f"{column[1]}.{column[2]}",
                                ),
                            )
                        db.commit()
                        extra_args = ""
                        params = [model,]
                        if provider == "openai":
                            extra_args = ", dimensions => %s"
                            params.append(dimensions)
                        cur.execute(
                            f"""
                            insert into ai.semantic_catalog_obj_1_store(embedding_uuid, objtype, objnames, objargs, chunk_seq, chunk, embedding)
                            select
                                gen_random_uuid(),
                                objtype,
                                objnames,
                                objargs,
                                0,
                                description,
                                ai.{provider}_embed(%s, description{extra_args})
                            from ai.semantic_catalog_obj
                            """,
                            params,
                        )
                        cur.execute("delete from ai._vectorizer_q_1")


@cli.command()
@click.argument("agent")
@click.argument("task")
@click.option(
    "--provider",
    default="anthropic",
    help="Provider to use for the task [default anthropic]",
)
@click.option("--model", default=None, help="Model to use for task")
@click.option(
    "--dataset", default="all", help="Dataset to evaluate [default eval all datasets]"
)
@click.option("--database", default=None, help="Database to evaluate")
@click.option("--eval", default=None, help="Eval case to run")
@click.option("--strict", is_flag=True, default=False, help="Use strict evaluation")
def eval(
    task: str,
    agent: str,
    provider: str,
    model: Optional[str],
    dataset: str,
    database: Optional[str],
    eval: Optional[str],
    strict: bool,
) -> None:
    """
    Runs the eval suite for a given agent and task.

    The agent can be one of "baseline" or "pgai".
    The task can be one of "get_tables" or "text_to_sql".
    """
    validate_provider(provider)
    if model is None:
        model = get_default_model(provider)
    if task not in ["get_tables", "text_to_sql"]:
        raise ValueError(f"Invalid task: {task}")
    datasets = sorted(os.listdir(datasets_dir) if dataset == "all" else [dataset])
    task_fn = get_tables if task == "get_tables" else text_to_sql
    agent_fn = get_agent_fn(agent, task)
    errored_evals = {}  # type: dict[str, list[str]]
    failed_evals = {}  # type: dict[str, list[str]]
    failed_error_counts = {}  # type: dict[str, dict[str, int]]
    results = {}  # type: dict[str, Results]
    for i in range(len(datasets)):
        if i > 0:
            print()
        dataset = datasets[i]
        errored_evals[dataset] = []
        failed_evals[dataset] = []
        failed_error_counts[dataset] = {}
        passing = 0
        total = 0
        print(f"Evaluating {dataset}...")
        evals_path = datasets_dir / dataset / "evals"
        eval_paths = sorted(list(evals_path.iterdir()))

        def run_eval(eval_path: Path, dataset: str, inp: dict):
            nonlocal errored_evals, failed_evals, passing, total
            with psycopg.connect(get_psycopg_str(f"{dataset}_{inp['database']}")) as db:
                error_path = eval_path / "error.txt"
                if error_path.exists():
                    error_path.unlink()
                exc = None
                traceback = None
                try:
                    result = task_fn(
                        db,
                        str(eval_path),
                        inp["question"],
                        agent_fn,
                        provider,
                        model,
                        strict,
                    )
                except GetExpectedError as e:
                    result = None
                    exc = e
                    traceback = format_exc()
                except Exception as e:
                    result = False
                    exc = e
                    traceback = format_exc()
                to_print = "    "
                if result is True:
                    to_print += "PASS"
                elif result is False:
                    to_print += "FAIL"
                else:
                    to_print += "EXPECTED ERROR"
                    total -= 1
                print(to_print, end="")
                if exc:
                    class_name = type(exc).__name__
                    if class_name not in failed_error_counts[dataset]:
                        failed_error_counts[dataset][class_name] = 0
                    failed_error_counts[dataset][class_name] += 1
                    print(f" ({class_name})", end="")
                    with error_path.open("w") as fp:
                        fp.write(class_name + "\n\n")
                        fp.write(traceback + "\n\n")
                        fp.write(str(exc))
                print()
                if result is True:
                    passing += 1
                elif result is False:
                    failed_evals[dataset].append(eval_path.name)
                else:
                    errored_evals[dataset].append(eval_path.name)

        for eval_path in eval_paths:
            if eval is not None and eval_path.name != eval:
                continue
            with (eval_path / "eval.json").open() as fp:
                inp = json.load(fp)
            if database and inp["database"] != database:
                continue
            print(f"  {eval_path.name}:")
            total += 1
            run_eval(eval_path, dataset, inp)

        print(f"  {1 if total == 0 else round(passing/total, 2)} ({passing}/{total})")
        if len(failed_evals[dataset]) > 0:
            print("Failed error type counts:")
            for error in sorted(failed_error_counts[dataset].keys()):
                print(f"  {error}: {failed_error_counts[dataset][error]}")
            print(f"Failed evals:\n{sorted(failed_evals[dataset])}")
        if len(errored_evals[dataset]) > 0:
            print(f"Errored evals:\n{sorted(errored_evals[dataset])}")

        results[dataset] = {
            "passing": passing,
            "total": total,
            "failed": failed_evals[dataset],
            "failed_error_counts": failed_error_counts[dataset],
            "errored": errored_evals[dataset],
        }

    with (root_directory / "results.json").open("w") as fp:
        json.dump(
            results,
            fp,
        )


@cli.command()
def generate_report():
    results_dir = root_directory / "results"
    combined_results = {}  # type: dict[str, Results]
    if not results_dir.exists() or not results_dir.is_dir():
        print("No results direcotry found. Please run the eval command first.")
        return
    for results_file in results_dir.iterdir():
        if not results_file.is_file() or not results_file.name.endswith(".json"):
            continue
        with results_file.open() as fp:
            try:
                results = json.load(fp)
            except json.JSONDecodeError:
                print(f"Failed to decode {results_file.name}, contents:")
                print()
                print(fp.read())
                print()
                print("Skipping file...")
                continue
        for dataset, result in results.items():
            if dataset not in combined_results:
                combined_results[dataset] = {
                    "passing": 0,
                    "total": 0,
                    "failed": [],
                    "failed_error_counts": {},
                    "errored": [],
                }
            combined_results[dataset]["passing"] += result["passing"]
            combined_results[dataset]["total"] += result["total"]
            combined_results[dataset]["failed"] += result["failed"]
            for error, count in result["failed_error_counts"].items():
                if error not in combined_results[dataset]["failed_error_counts"]:
                    combined_results[dataset]["failed_error_counts"][error] = 0
                combined_results[dataset]["failed_error_counts"][error] += count
            combined_results[dataset]["errored"] += result["errored"]

    passing = 0
    total = 0
    for results in combined_results.values():
        passing += results["passing"]
        total += results["total"]
    print(f"Overall: {passing}/{total} ({round(passing/total, 2)})")
    print()

    i = 0
    for dataset in sorted(combined_results.keys()):
        if i > 0:
            print()
        results = combined_results[dataset]
        print(
            f"{dataset}: {results['passing']}/{results['total']} ({round(results['passing']/results['total'], 2)})"
        )
        if len(results["failed"]) > 0:
            print("  Failed error type counts:")
            for error in sorted(results["failed_error_counts"].keys()):
                print(f"    {error}: {results['failed_error_counts'][error]}")
            print(f"  Failed evals:\n    {sorted(results['failed'])}")

        if len(results["errored"]) > 0:
            print(f"  Errored evals:\n    {sorted(results['errored'])}")
        i += 1
