import os

import psycopg
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

from .types import TextToSql

load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


class SQLQuery(BaseModel):
    query: str


class Tables(BaseModel):
    tables: list[str]


def get_tables(conn: psycopg.Connection, inp: str) -> list[str]:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
        )
        tables = cur.fetchall()
        tables = [table[0] for table in tables]
    chat = client.beta.chat.completions.parse(
        messages=[
            {
                "role": "system",
                "content": "You are an AI assistant that can pick out the most relevant SQL tables that would help answer a given question.",
            },
            {
                "role": "system",
                "content": f"Here are the tables in the database:\n\n{'\n'.join(tables)}",
            },
            {
                "role": "user",
                "content": f"Which tables would you use to answer the following question:\n\n{inp}",
            },
        ],
        model="gpt-4o-mini",
        n=1,
        response_format=Tables,
    )
    return chat.choices[0].message.parsed.tables


def text_to_sql(conn: psycopg.Connection, inp: str) -> TextToSql:
    tables = get_tables(conn, inp)
    table_ddl = []
    for table in tables:
        with conn.cursor() as cur:
            cur.execute(
                """
SELECT
'CREATE TABLE ' || relname || E'\n(\n' ||
array_to_string(
    array_agg(
        '    ' || column_name || ' ' ||  type || ' '|| not_null ||
        CASE
            WHEN comment IS NOT NULL THEN ' -- ' || comment
            ELSE ''
        END
    ),
    E',\n'
) || E'\n);\n'
from
(
    SELECT
        c.relname,
        a.attname AS column_name,
        pg_catalog.format_type(a.atttypid, a.atttypmod) as type,
        CASE
            WHEN a.attnotnull
            THEN 'NOT NULL'
            ELSE 'NULL'
        END AS not_null,
        d.description AS comment
    FROM pg_class c
    JOIN pg_attribute a ON a.attrelid = c.oid
    LEFT JOIN pg_description d ON d.objoid = c.oid AND d.objsubid = a.attnum
    JOIN pg_type t ON a.atttypid = t.oid
    WHERE
        c.relname = %s
        AND a.attnum > 0
    ORDER BY a.attnum
) as tabledefinition
group by relname;
""",
                [table],
            )
            table_ddl.append(cur.fetchone()[0])

    messages = [
        {
            "role": "system",
            "content": "You are a genius at generating SQL from natural language.",
        },
        {
            "role": "system",
            "content": f"Here are some tables that might help you answer the question:\n\n{'\n'.join(table_ddl)}",
        },
        {
            "role": "user",
            "content": f"Generate a SQL query for PostgreSQL that answers the following question:\n\n{inp}",
        },
    ]
    chat = client.beta.chat.completions.parse(
        messages=messages,
        model="gpt-4o-mini",
        n=1,
        response_format=SQLQuery,
        temperature=0,
    )
    return {"messages": messages, "query": chat.choices[0].message.parsed.query}
