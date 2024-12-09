import psycopg
import simplejson as json


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


def run(conn: psycopg.Connection, path: str, inp: str, agent_fn: callable) -> bool:
    with open(f"{path}/expected.json", "r") as fp:
        expected = json.load(fp)
    query = agent_fn(conn, inp)
    with conn.cursor() as cur:
        cur.execute(query)
        result = cur.fetchall()
        actual = {"columns": [desc[0] for desc in cur.description], "data": result}
    with open(f"{path}/actual_text_to_sql.json", "w") as fp:
        json.dump(actual, fp)
    with open(f"{path}/actual_query.sql", "w") as fp:
        fp.write(query)
    passing = compare(actual, expected)
    if not passing:
        print(f"    Query: {query}")
    return passing
