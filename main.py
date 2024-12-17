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

load_dotenv()

root_directory = Path(__file__).resolve().parent

env = os.environ.copy()
env["PGPASSWORD"] = os.environ["POSTGRES_PASSWORD"]

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
            subprocess.run(
                ["psql", "-h", os.environ["POSTGRES_HOST"], "-U", os.environ["POSTGRES_USER"], "-d", "postgres", "-c", f"DROP DATABASE IF EXISTS {dataset}_{entry.stem}"],
                env=env,
            )
            subprocess.run(
                ["psql", "-h", os.environ["POSTGRES_HOST"], "-U", os.environ["POSTGRES_USER"], "-d", "postgres", "-c", f"CREATE DATABASE {dataset}_{entry.stem}"],
                env=env,
            )
            if pgai:
                subprocess.run(
                    ["psql", "-h", os.environ["POSTGRES_HOST"], "-U", os.environ["POSTGRES_USER"], "-d", f"{dataset}_{entry.stem}", "-c", "select set_config('ai.enable_feature_flag_text_to_sql', 'true', false)"],
                    env=env,
                )
                subprocess.run(
                    ["psql", "-h", os.environ["POSTGRES_HOST"], "-U", os.environ["POSTGRES_USER"], "-d", f"{dataset}_{entry.stem}", "-c", "CREATE EXTENSION ai CASCADE"],
                    env=env,
                )
            subprocess.run(
                ["psql", "-h", os.environ["POSTGRES_HOST"], "-U", os.environ["POSTGRES_USER"], "-d", f"{dataset}_{entry.stem}", "-f", str(entry)],
                env=env,
            )


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
