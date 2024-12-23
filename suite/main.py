import json
import os
from pathlib import Path
from typing import Optional

import click
import psycopg
from dotenv import load_dotenv

from .agents import get_agent_fn
from .tasks.get_tables import run as get_tables
from .tasks.text_to_sql import run as text_to_sql
from .utils import (
    get_default_embedding_model,
    get_default_model,
    get_psycopg_str,
    setup_pgai_config,
    validate_embedding_provider,
    validate_provider,
)

root_directory = Path(__file__).resolve().parent.parent
load_dotenv()


@click.group()
def cli():
    pass


@cli.command()
@click.option("--provider", default="openai", help="Provider to use for embeddings [default openai]")
@click.option("--model", default=None, help="Model to use for embeddings")
@click.option("--dataset", default="all", help="Dataset to load [defaults to all datasets]")
@click.option("--no-comments", is_flag=True, default=False, help="Do not use obj comments for embeddings")
def load(provider: str, model: Optional[str], dataset: str, no_comments: bool) -> None:
    """
    Load the datasets into the database.
    """
    validate_embedding_provider(provider)
    if model is None:
        model = get_default_embedding_model(provider)
    datasets = os.listdir("datasets") if dataset == "all" else [dataset]
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
        for entry in (root_directory / "datasets" / dataset / "databases").iterdir():
            db_name = f"{dataset}_{entry.stem}"
            print(f"    {db_name}")
            with psycopg.connect(get_psycopg_str()) as root_db:
                root_db.autocommit = True
                print("      DROP DATABASE")
                root_db.execute(f"DROP DATABASE IF EXISTS {db_name}")
                print("      CREATE DATABASE")
                root_db.execute(f"CREATE DATABASE {db_name}")
            with psycopg.connect(get_psycopg_str(db_name)) as db:
                print("      Restoring dump")
                with entry.open() as fp:
                    db.execute(fp.read())
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
                            select ai.initialize_semantic_catalog(
                                embedding=>ai.embedding_{provider}(
                                    %s,
                                    576
                                )
                            )
                            """,
                            (model,),
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
                                ai.{provider}_embed(%s, description)
                            from ai.semantic_catalog_obj
                            """,
                            (model,),
                        )
                        cur.execute("delete from ai._vectorizer_q_1")


@cli.command()
@click.argument("agent")
@click.argument("task")
@click.option("--provider", default="openai", help="Provider to use for the task [default openai]")
@click.option("--model", default=None, help="Model to use for task")
@click.option("--dataset", default="all", help="Dataset to evaluate [default eval all datasets]")
@click.option("--database", default=None, help="Database to evaluate")
@click.option("--strict", is_flag=True, default=False, help="Use strict evaluation")
def eval(
    task: str,
    agent: str,
    provider: str,
    model: Optional[str],
    dataset: str,
    database: Optional[str],
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
    datasets = sorted(os.listdir("datasets") if dataset == "all" else [dataset])
    task_fn = get_tables if task == "get_tables" else text_to_sql
    agent_fn = get_agent_fn(agent, task)
    failed_evals = {}
    for i in range(len(datasets)):
        if i > 0:
            print()
        dataset = datasets[i]
        failed_evals[dataset] = []
        passing = 0
        total = 0
        print(f"Evaluating {dataset}...")
        evals_path = root_directory / "datasets" / dataset / "evals"
        eval_paths = sorted(list(evals_path.iterdir()))
        for eval_path in eval_paths:
            with (eval_path / "eval.json").open() as fp:
                inp = json.load(fp)
            if database and inp["database"] != database:
                continue
            total += 1
            print(f"  {eval_path.name}:")
            with psycopg.connect(get_psycopg_str(f"{dataset}_{inp['database']}")) as db:
                error_path = eval_path / "error.txt"
                if error_path.exists():
                    error_path.unlink()
                exc = None
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
                except Exception as e:
                    result = False
                    exc = e
                print(f"    {'PASS' if result else 'FAIL'}", end="")
                if exc:
                    print(f" ({type(exc).__name__})", end="")
                    with error_path.open("w") as fp:
                        fp.write(type(exc).__name__ + "\n\n")
                        fp.write(str(exc))
                print()
                if result:
                    passing += 1
                else:
                    failed_evals[dataset].append(eval_path.name)
        print(f"  {round(passing/total, 2)} ({passing}/{total})")
        if len(failed_evals[dataset]) > 0:
            print(f"Failed evals:\n{failed_evals[dataset]}")
