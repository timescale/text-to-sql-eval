"""
Given a dataset name as sys.argv[1], then we remove any eval.json files that
reference a database that does not exist. This is useful if we end up having to
delete a database for whatever reason in a dataset.
"""

from pathlib import Path
import json
import shutil
import sys

root_directory = Path(__file__).resolve().parent.parent
dataset_directory = root_directory / "datasets" / sys.argv[1]

if not dataset_directory.exists():
    print(f"Dataset {sys.argv[1]} does not exist.")
    sys.exit(1)

evals_directory = dataset_directory / "evals"
databases_directory = dataset_directory / "databases"

for eval_directory in evals_directory.iterdir():
    with (eval_directory / "eval.json").open() as f:
        eval_data = json.load(f)
    db_file = databases_directory / f"{eval_data['database']}.sql"
    if not db_file.exists():
        shutil.rmtree(eval_directory)
