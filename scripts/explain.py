from pathlib import Path
import json
from typing import Generator, Any

import psycopg
from psycopg.types.json import Jsonb, Json
from psycopg.errors import Diagnostic


class Eval:
    def __init__(self, dataset: str, directory: Path, database: str, question: str, query: str):
        self.dataset = dataset
        self.directory = directory
        self.question = question
        self.query = query
        self.database = database
        self.error: None | dict[str, Any] = None
        self.query_plan: None | dict[str, Any] = None
        self.actuals: None | list[dict[str, Any]] = None

    @property
    def name(self) -> str:
        return self.directory.name


def diagnostic_to_dict(diagnostic: Diagnostic) -> dict[str, Any]:
    return {
        "severity": diagnostic.severity,
        "severity_nonlocalized": diagnostic.severity_nonlocalized,
        "sqlstate": diagnostic.sqlstate,
        "message_primary": diagnostic.message_primary,
        "message_detail": diagnostic.message_detail,
        "message_hint": diagnostic.message_hint,
        "statement_position": diagnostic.statement_position,
        "internal_position": diagnostic.internal_position,
        "internal_query": diagnostic.internal_query,
        "context": diagnostic.context,
        "schema_name": diagnostic.schema_name,
        "table_name": diagnostic.table_name,
        "column_name": diagnostic.column_name,
        "datatype_name": diagnostic.datatype_name,
        "constraint_name": diagnostic.constraint_name,
        "source_file": diagnostic.source_file,
        "source_line": diagnostic.source_line,
        "source_function": diagnostic.source_function,
    }


def diagnostic_to_text(diagnostic: Diagnostic) -> str:
    d = diagnostic_to_dict(diagnostic)
    lines = []
    for k, v in d.items():
        if v is None:
            continue
        lines.append(f"{k}: {v}")
    return "\n".join(lines)


def evals(dataset: str) -> Generator[Eval, None, None]:
    dataset_dir = Path(__file__).parent.parent.resolve().joinpath("datasets", dataset)
    dirs = [p for p in dataset_dir.joinpath("evals").iterdir() if p.is_dir()]
    dirs.sort()
    for d in dirs:
        j = d.joinpath("eval.json")
        if not j.exists():
            continue
        yield Eval(dataset=dataset, directory=d, **(json.loads(j.read_text())))


def db_url(dataset: str, database: str) -> str:
    return f"postgres://postgres@localhost:5432/{dataset}_{database}"


def create_table(conn: psycopg.Connection) -> None:
    with conn.cursor() as cur:
        cur.execute("""
            create table eval
            ( id bigint not null primary key generated always as identity 
            , dataset text not null
            , database text not null
            , name text not null
            , question text not null
            , query text not null
            , query_plan jsonb
            , error jsonb
            , actuals json
            )
        """)
    conn.commit()


def check_golden_queries(dataset: str) -> None:
    with psycopg.connect("postgres://postgres@localhost:5432/eval") as con1:
        create_table(con1)
        for e in evals(dataset):
            with psycopg.connect(db_url(dataset, e.database)) as con2:
                with con2.cursor() as cur2:
                    try:
                        cur2.execute(f"explain (analyze, verbose, format json) {e.query}")
                        query_plan = cur2.fetchone()[0]
                        e.query_plan = query_plan
                        e.directory.joinpath("expected_plan.json").write_text(json.dumps(query_plan, indent=2))
                    except psycopg.Error as err:
                        e.error = diagnostic_to_dict(err.diag)
                        e.directory.joinpath("expected_error.txt").write_text(diagnostic_to_text(err.diag))
                    else:
                        cur2.execute(f"select json_agg(to_json(x)) from ({e.query}) x")
                        e.actuals = cur2.fetchone()[0]
                with con1.cursor() as cur1:
                    cur1.execute("""
                        insert into eval (dataset, database, name, question, query, query_plan, error, actuals)
                        values ( %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        e.dataset,
                        e.database,
                        e.name,
                        e.question,
                        e.query,
                        None if e.query_plan is None else Jsonb(e.query_plan),
                        None if e.error is None else Jsonb(e.error),
                        None if e.actuals is None else Json(e.actuals),
                    ))
                con1.commit()
            print(e.name)


def clean(dataset: str) -> None:
    for e in evals(dataset):
        f = e.directory.joinpath("expected_error.txt")
        if f.exists():
            print(f"{f}")
            f.unlink()


if __name__ == "__main__":
    dataset = "spider"
    check_golden_queries(dataset)

