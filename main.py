import json
import os
from pathlib import Path
import subprocess

from dotenv import load_dotenv
import click
import psycopg
from tasks.get_tables import run as get_tables
from tasks.text_to_sql import run as text_to_sql

from baseline import text_to_sql as baseline_text_to_sql
from baseline import get_tables as baseline_get_tables
from pgai import get_tables as pgai_get_tables

load_dotenv()

root_directory = Path(__file__).resolve().parent

env = os.environ.copy()
env["PGPASSWORD"] = os.environ["POSTGRES_PASSWORD"]
OLLAMA_HOST = "http://ollama:11434"

@click.group()
def cli():
    pass


@cli.command()
@click.option("--dataset", default="all", help="Dataset to evaluate")
@click.option("--pgai", is_flag=True, default=False, help="Use PGAI")
def load(dataset, pgai):
    datasets = os.listdir("datasets") if dataset == "all" else [dataset]
    for dataset in datasets:
        for entry in Path(f"datasets/{dataset}/databases").iterdir():
            db_name = f"{dataset}_{entry.stem}"
            subprocess.run(
                ["psql", "-h", os.environ["POSTGRES_HOST"], "-U", os.environ["POSTGRES_USER"], "-d", "postgres", "-c", f"DROP DATABASE IF EXISTS {dataset}_{entry.stem}"],
                env=env,
            )
            subprocess.run(
                ["psql", "-h", os.environ["POSTGRES_HOST"], "-U", os.environ["POSTGRES_USER"], "-d", "postgres", "-c", f"CREATE DATABASE {dataset}_{entry.stem}"],
                env=env,
            )
            if pgai:
                with psycopg.connect(
                    f"host=127.0.0.1 dbname={db_name} user=postgres password=postgres"
                ) as db:
                    with db.cursor() as cur:
                        cur.execute("select set_config('ai.enable_feature_flag_text_to_sql', 'true', false)")
                        cur.execute("CREATE EXTENSION ai CASCADE")
            subprocess.run(
                ["psql", "-h", os.environ["POSTGRES_HOST"], "-U", os.environ["POSTGRES_USER"], "-d", db_name, "-f", str(entry)],
                env=env,
            )
            if pgai:
                with psycopg.connect(
                    f"host=127.0.0.1 dbname={db_name} user=postgres password=postgres"
                ) as db:
                    with db.cursor() as cur:
                        cur.execute("select set_config('ai.enable_feature_flag_text_to_sql', 'true', false)")
                        cur.execute("select ai.grant_ai_usage('postgres', true)")
                        cur.execute(
                            """
                            select ai.initialize_semantic_catalog
                                ( embedding=>ai.embedding_ollama
                                    ( 'smollm:135m'
                                    , 576
                                    , base_url=>%s
                                    )
                                )
                            """,
                            (OLLAMA_HOST,),
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
                            cur.execute(f"select ai.set_description('{table}', '{table}');")
                        for column in columns:
                            cur.execute(f"select ai.set_column_description('{column[1]}', '{column[2]}', '{column[1]}.{column[2]}');")
                        db.commit()
                        cur.execute(
                            """
                            insert into ai.semantic_catalog_obj_1_store(embedding_uuid, objtype, objnames, objargs, chunk_seq, chunk, embedding)
                            select
                            gen_random_uuid()
                            , objtype, objnames, objargs
                            , 0
                            , description
                            , ai.ollama_embed('smollm:135m', description, host=>%s)
                            from ai.semantic_catalog_obj
                            """,
                            (OLLAMA_HOST,),
                        )
                        cur.execute("delete from ai._vectorizer_q_1")



@cli.command()
@click.argument("task")
@click.argument("agent")
@click.option("--dataset", default="all", help="Dataset to evaluate")
@click.option("--strict", is_flag=True, default=False, help="Use strict evaluation")
def eval(task, agent, dataset, strict):
    if task not in ["get_tables", "text_to_sql"]:
        raise ValueError(f"Invalid task: {task}")
    if agent not in ["pgai", "baseline"]:
        raise ValueError(f"Invalid agent: {agent}")
    datasets = sorted(os.listdir("datasets") if dataset == "all" else [dataset])
    task_fn = get_tables if task == "get_tables" else text_to_sql
    if agent == "pgai":
        if task == "get_tables":
            agent_fn = pgai_get_tables
        else:
            raise NotImplementedError
    elif agent == "baseline":
        agent_fn = (
            baseline_text_to_sql if task == "text_to_sql" else baseline_get_tables
        )
    for dataset in datasets:
        passing = 0
        total = 0
        print(f"Evaluating {dataset}...")
        evals_path = Path(root_directory, "datasets", dataset, "evals")
        eval_paths = sorted(list(evals_path.iterdir()))
        for eval_path in eval_paths:
            total += 1
            print(f"  {os.path.basename(eval_path)}:")
            with (eval_path / "eval.json").open() as fp:
                inp = json.load(fp)
            with psycopg.connect(
                f"host=127.0.0.1 dbname={dataset}_{inp["database"]} user=postgres password=postgres"
            ) as db:
                result = task_fn(db, str(eval_path), inp["question"], agent_fn, strict)
                # result = evaluate(dataset, inp, expected)
                print(f"    {'PASS' if result else 'FAIL'}")
                if result:
                    passing += 1
        print(f"  {round(passing/total, 2)}")


if __name__ == "__main__":
    cli()
