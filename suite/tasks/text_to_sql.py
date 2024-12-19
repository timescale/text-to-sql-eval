import os

import polars as pl
import psycopg
import simplejson as json
from polars.testing import assert_frame_equal

from ..exceptions import AgentFnError, QueryExecutionError
from ..types import Provider


def compare(actual: pl.DataFrame, expected: pl.DataFrame, strict: bool) -> bool:
    actual_columns = set(actual.columns)
    expected_columns = set(expected.columns)
    if strict and actual_columns != expected_columns:
        return False
    elif not expected_columns.issubset(actual_columns):
        return False
    actual_new = actual.select(expected.columns)
    try:
        assert_frame_equal(
            actual_new, expected, check_column_order=False, check_row_order=False
        )
        return True
    except AssertionError:
        return False


def run(
    conn: psycopg.Connection,
    path: str,
    inp: str,
    agent_fn: callable,
    provider: Provider,
    model: str,
    strict: bool,
) -> bool:
    if os.path.exists(f"{path}/actual_query.sql"):
        os.unlink(f"{path}/actual_query.sql")
    if os.path.exists(f"{path}/actual_messages.txt"):
        os.unlink(f"{path}/actual_messages.txt")
    with open(f"{path}/eval.json", "r") as fp:
        gold_query = json.load(fp).get("query")
    try:
        result = agent_fn(conn, inp, provider, model)
        query = result["query"]
    except Exception as e:
        raise AgentFnError(e) from e
    with open(f"{path}/actual_query.sql", "w") as fp:
        fp.write(query)
    with open(f"{path}/actual_messages.txt", "w") as fp:
        for i in range(len(result["messages"])):
            if i > 0:
                fp.write("\n")
            message = result["messages"][i]
            fp.write(f"{message['role']}:\n{message['content']}")
    expected = pl.read_database(gold_query, conn)
    try:
        actual = pl.read_database(query, conn)
    except psycopg.DatabaseError as e:
        raise QueryExecutionError(e) from e
    return compare(actual, expected, strict)
