import os

import polars as pl
import psycopg
import simplejson as json
from polars.testing import assert_frame_equal
from sql_metadata import Parser

from ..agents import AgentFn
from ..exceptions import AgentFnError, GetExpectedError, QueryExecutionError
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


async def run(
    conn: psycopg.Connection,
    path: str,
    inp: str,
    agent_fn: AgentFn,
    provider: Provider,
    model: str,
    entire_schema: bool,
    gold_tables: bool,
    strict: bool,
) -> bool:
    if os.path.exists(f"{path}/actual_query.sql"):
        os.unlink(f"{path}/actual_query.sql")
    if os.path.exists(f"{path}/actual_messages.txt"):
        os.unlink(f"{path}/actual_messages.txt")
    with open(f"{path}/eval.json", "r") as fp:
        gold_query = json.load(fp).get("query")
    gold_tables_list = []
    if gold_tables:
        parser = Parser(gold_query)
        gold_tables_list = [table.lower() for table in parser.tables]
    try:
        result = await agent_fn(
            conn, inp, provider, model, entire_schema, gold_tables_list
        )
    except Exception as e:
        raise AgentFnError(e) from e
    with open(f"{path}/actual_messages.txt", "w") as fp:
        for i in range(len(result["messages"])):
            if i > 0:
                fp.write("\n")
            message = result["messages"][i]
            fp.write(f"{message['role']}:\n{message['content']}")
    if "error" in result and result["error"] is not None:
        raise (
            result["error"]
            if isinstance(result["error"], Exception)
            else AgentFnError(str(result["error"]))
        )
    query = result["query"]
    with open(f"{path}/actual_query.sql", "w") as fp:
        fp.write(query)
    try:
        expected = pl.read_database(gold_query, conn)
    except psycopg.DatabaseError as e:
        raise GetExpectedError(e) from e
    try:
        actual = pl.read_database(query, conn)
        parser = Parser(query)
        if len(parser.columns_aliases) > 0:
            actual = actual.rename(parser.columns_aliases)
    except psycopg.DatabaseError as e:
        raise QueryExecutionError(e) from e
    details = {
        "generated_query": query,
        "expected_query": gold_query,
    }
    if gold_tables:
        details["gold_tables"] = gold_tables_list
    return {
        "status": "pass" if compare(actual, expected, strict) else "fail",
        "details": details,
    }
