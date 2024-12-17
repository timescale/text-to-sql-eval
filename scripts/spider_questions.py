# Assumes that have downloaded the Spider dataset to the spider_data directory
# in the root of the repository. Takes all questions in dev.json and creates
# a directory for each question in the datasets/spider/evals directory with
# a JSON file that contains the database, question, and query.

import json
from pathlib import Path
import shutil

root_directory = Path(__file__).resolve().parent.parent
spider_data_directory = root_directory / "spider_data"
dataset_directory = root_directory / "datasets" / "spider"
databases_directory = dataset_directory / "databases"
evals_directory = dataset_directory / "evals"

if evals_directory.exists():
    shutil.rmtree(evals_directory)
evals_directory.mkdir()

all_questions = []
with (spider_data_directory / "dev.json").open() as f:
    all_questions = json.load(f)
with (spider_data_directory / "test.json").open() as f:
    all_questions.extend(json.load(f))
with (spider_data_directory / "train_others.json").open() as f:
    all_questions.extend(json.load(f))
with (spider_data_directory / "train_spider.json").open() as f:
    all_questions.extend(json.load(f))
questions = []
for question in all_questions:
    print(databases_directory / f"{question["db_id"]}.sql")
    if not (databases_directory / f"{question["db_id"]}.sql").exists():
        continue
    questions.append(question)
print(f"Loading {len(questions)}/{len(all_questions)} questions")
zfill = len(str(len(questions)))
for i in range(len(questions)):
    question = questions[i]
    eval_directory = evals_directory / str(i + 1).zfill(zfill)
    eval_directory.mkdir()
    with (eval_directory / "eval.json").open("w") as f:
        json.dump({
            "database": question["db_id"],
            "question": question["question"],
            "query": question["query"],
        }, f, indent=4)
