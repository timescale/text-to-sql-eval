import json
import psycopg


def compare(actual, expected) -> bool:
    return set(actual) == set(expected)


def run(conn: psycopg.Connection, path: str, inp: str, agent_fn: callable) -> bool:
    with open(f"{path}/tables.json", "r") as fp:
        expected = json.load(fp)
    actual = agent_fn(conn, inp)
    with open(f"{path}/actual_get_tables.json", "w") as fp:
        json.dump(actual, fp)
    passing = compare(actual, expected)
    return passing
