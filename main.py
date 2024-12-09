import os

from dotenv import load_dotenv
import click
import psycopg
from tasks.get_tables import run as get_tables
from tasks.text_to_sql import run as text_to_sql

from baseline import text_to_sql as baseline_text_to_sql
from baseline import get_tables as baseline_get_tables

load_dotenv()


@click.command()
@click.option("--dataset", default="all", help="Dataset to evaluate")
@click.argument("task")
@click.argument("agent")
def main(dataset, task, agent):
    if task not in ["get_tables", "text_to_sql"]:
        raise ValueError(f"Invalid task: {task}")
    if agent not in ["pgai", "baseline"]:
        raise ValueError(f"Invalid agent: {agent}")
    datasets = os.listdir("datasets") if dataset == "all" else [dataset]
    task_fn = get_tables if task == "get_tables" else text_to_sql
    if agent == "pgai":
        raise NotImplementedError
    elif agent == "baseline":
        agent_fn = (
            baseline_text_to_sql if task == "text_to_sql" else baseline_get_tables
        )
    for dataset in datasets:
        with psycopg.connect(
            f"host=127.0.0.1 dbname={dataset} user=postgres password=postgres"
        ) as db:
            passing = 0
            total = 0
            print(f"Evaluating {dataset}...")
            for eval in os.scandir(f"datasets/{dataset}/eval"):
                total += 1
                with open(f"{eval.path}/input.txt", "r") as fp:
                    inp = fp.read().strip()
                print(f"  {eval.name}:")
                result = task_fn(db, eval.path, inp, agent_fn)
                # result = evaluate(dataset, inp, expected)
                print(f"    {'PASS' if result else 'FAIL'}")
                if result:
                    passing += 1
            print(f"  {round(passing/total, 2)}")


if __name__ == "__main__":
    main()
