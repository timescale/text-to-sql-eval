import os

from dotenv import load_dotenv
import psycopg

from .types import TextToSql

load_dotenv()


def get_tables(conn: psycopg.Connection, inp: str) -> list[str]:
    with conn.cursor() as cur:
        cur.execute(
            "select set_config('ai.enable_feature_flag_text_to_sql', 'true', false)"
        )
        cur.execute(
            f"select * from ai.find_relevant_obj('{inp}', objtypes=>array['table column']);"
        )
        objs = cur.fetchall()
    return list(set([row[1][1] for row in objs]))


def text_to_sql(conn: psycopg.Connection, inp: str) -> TextToSql:
    with conn.cursor() as cur:
        cur.execute(
            "select set_config('ai.enable_feature_flag_text_to_sql', 'true', false)"
        )
        cur.execute(
            "select set_config('ai.openai_api_key', %s, false) is not null",
            (os.environ["OPENAI_API_KEY"],),
        )
        cur.execute(
            """
            select ai._text_to_sql_prompt(%s)
            """,
            (inp,),
        )
        prompt = cur.fetchone()[0]
        cur.execute(
            """
            select ai.text_to_sql(
                %s,
                ai.text_to_sql_openai('gpt-4o-mini')
            )
            """,
            (inp,),
        )
        query = cur.fetchone()[0]
    return {
        "messages": [
            {
                "role": "system",
                "content": """
                    You are an expert database developer and DBA specializing in PostgreSQL.
                    You will be provided with context about a database model and a question to be answered.
                    You respond with nothing but a SQL statement that addresses the question posed.
                    You should not wrap the SQL statement in markdown.
                    The SQL statement must be valid syntax for PostgreSQL.
                    SQL features and functions that are built-in to PostgreSQL may be used.
                """.strip(),
            },
            {"role": "user", "content": prompt},
        ],
        "query": query,
    }
