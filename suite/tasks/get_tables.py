import json
import os

import psycopg
from sql_metadata import Parser

from ..exceptions import AgentFnError
from ..types import Provider


def compare(actual, expected, strict: bool) -> bool:
    return (
        set(actual) == set(expected) if strict else set(expected).issubset(set(actual))
    )


def run(
    conn: psycopg.Connection,
    path: str,
    inp: str,
    agent_fn: callable,
    provider: Provider,
    model: str,
    strict: bool,
) -> bool:
    if os.path.exists(f"{path}/actual_get_tables.json"):
        os.unlink(f"{path}/actual_get_tables.json")
    with open(f"{path}/eval.json", "r") as fp:
        query = json.load(fp).get("query")
    try:
        parser = Parser(query)
    except Exception as e:
        raise AgentFnError(e) from e
    # normalize table names as query uses mix of uppercase/lowercase to reference them
    expected = list(set([table.lower() for table in parser.tables]))
    actual = agent_fn(conn, inp, provider, model)
    with open(f"{path}/actual_get_tables.json", "w") as fp:
        json.dump(actual, fp)
    return compare(actual, expected, strict)
