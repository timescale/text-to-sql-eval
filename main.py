import json
import os

import psycopg

from baseline import run


def compare(actual, expected) -> bool:
    if "columns" not in actual or "data" not in actual:
        return False
    if actual["columns"] != expected["columns"]:
        return False
    if len(actual["data"]) != len(expected["data"]):
        return False
    for i in range(len(actual["data"])):
        if list(actual["data"][i]) != expected["data"][i]:
            return False
    return True


def evaluate(db: str, input: str, expected) -> bool:
    with psycopg.connect(f"host=127.0.0.1 dbname={db} user=postgres password=postgres") as conn:
        query = run(db, input)
        with conn.cursor() as cur:
            cur.execute(query)
            result = cur.fetchall()
            actual = {
                "columns": [desc[0] for desc in cur.description],
                "data": result
            }
    passing = compare(actual, expected)
    if not passing:
        print(f"    Query: {query}")
    return passing

def main():
    datasets = os.listdir("datasets")
    for dataset in datasets:
        passing = 0
        total = 0
        print(f"Evaluating {dataset}...")
        for eval in os.scandir(f"datasets/{dataset}/eval"):
            total += 1
            inp = open(f"{eval.path}/input.txt", "r").read()
            with open(f"{eval.path}/expected.json", "r") as fp:
                expected = json.load(fp)
            print(f"  {eval.name}:")
            result = evaluate(dataset, inp, expected)
            print(f"    {'PASS' if result else 'FAIL'}")
            if result:
                passing += 1
        print(f"  {round(passing/total, 2)}")


if __name__ == "__main__":
    main()
