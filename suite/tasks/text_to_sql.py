import os
import time

import polars as pl
import psycopg
import simplejson as json
from polars.testing import assert_frame_equal
from sql_metadata import Parser

from ..agents import AgentFn
from ..exceptions import AgentFnError, GetExpectedError, QueryExecutionError
from ..types import Provider


def compare(actual: pl.DataFrame, expected: pl.DataFrame) -> bool:
    column_mappings = {}

    if len(actual.columns) < len(expected.columns):
        return False

    for e_col in expected.columns:
        e_values = expected[e_col]
        for a_col in actual.columns:
            # Check if the values match in the same order
            if e_values.equals(actual[a_col]):
                column_mappings[a_col] = e_col
                break

    actual_adjusted = actual.select(list(column_mappings.keys())).rename(
        column_mappings
    )
    try:
        assert_frame_equal(
            actual_adjusted, expected, check_column_order=False, check_row_order=False
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
    *args,
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
    start = time.time()
    try:
        result = await agent_fn(
            conn, inp, provider, model, entire_schema, gold_tables_list
        )
    except Exception as e:
        raise AgentFnError(e) from e
    duration = round(time.time() - start, 3)
    with open(f"{path}/actual_messages.txt", "w") as fp:
        for i in range(len(result["messages"])):
            if i > 0:
                fp.write("\n")
            message = result["messages"][i]
            if isinstance(message, str):
                fp.write(f"{message}")
            else:
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
    except psycopg.DatabaseError as e:
        raise QueryExecutionError(e) from e
    details = {
        "generated_query": query,
        "expected_query": gold_query,
        "duration": duration,
        "usage": result["usage"],
    }
    if gold_tables:
        details["gold_tables"] = gold_tables_list
    return {
        "status": "pass" if compare(actual, expected) else "fail",
        "details": details,
    }
