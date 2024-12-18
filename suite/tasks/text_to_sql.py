import os
import psycopg
import simplejson as json

from ..exceptions import AgentFnError, QueryExecutionError


def compare(actual, expected) -> bool:
    if "columns" not in actual or "data" not in actual:
        return False
    if actual["columns"] != expected["columns"]:
        return False
    if len(actual["data"]) != len(expected["data"]):
        return False
    for i in range(len(actual["data"])):
        if list(actual["data"][i]) != list(expected["data"][i]):
            return False
    return True


def run(
    conn: psycopg.Connection, path: str, inp: str, agent_fn: callable, strict: bool
) -> bool:
    if os.path.exists(f"{path}/actual_query.sql"):
        os.unlink(f"{path}/actual_query.sql")
    with open(f"{path}/eval.json", "r") as fp:
        gold_query = json.load(fp).get("query")
    try:
        result = agent_fn(conn, inp)
        query = result["query"]
    except Exception as e:
        raise AgentFnError(e)
    with open(f"{path}/actual_query.sql", "w") as fp:
        fp.write(query)
    with conn.cursor() as cur:
        cur.execute(gold_query)
        result = cur.fetchall()
        expected = {"columns": [desc[0] for desc in cur.description], "data": result}
    try:
        with conn.cursor() as cur:
            cur.execute(query)
            result = cur.fetchall()
            actual = {"columns": [desc[0] for desc in cur.description], "data": result}
    except psycopg.DatabaseError as e:
        raise QueryExecutionError(e)
    return compare(actual, expected)
