"""
Vanna agent
"""

import os
import sys
from io import StringIO

import psycopg
from dotenv import load_dotenv
from vanna.openai import OpenAI_Chat
from vanna.pgvector import PG_VectorStore

from ..types import Provider, TextToSql

load_dotenv()


class Vanna(PG_VectorStore, OpenAI_Chat):
    def __init__(self, config=None):
        PG_VectorStore.__init__(self, config=config)
        OpenAI_Chat.__init__(self, config=config)


def get_vanna_client(conn: psycopg.Connection):
    vn = Vanna(
        config={
            "api_key": os.environ["OPENAI_API_KEY"],
            "connection_string": f"postgresql://{conn.info.user}:{conn.info.password}@{conn.info.host}:{conn.info.port}/{conn.info.dbname}",
            "model": "gpt-4o",
        }
    )
    vn.connect_to_postgres(
        host=conn.info.host,
        port=conn.info.port,
        dbname=conn.info.dbname,
        user=conn.info.user,
        password=conn.info.password,
    )
    return vn


async def setup(
    conn: psycopg.Connection,
    provider: Provider,
    model: str,
    vector_dimensions: int,
):
    vn = get_vanna_client(conn)
    df_information_schema = vn.run_sql("""
        SELECT
            *,
            col_description(('"' || table_schema || '"."' || table_name || '"')::regclass::oid, ordinal_position) AS column_comment
        FROM
            information_schema.columns
        WHERE
            table_schema = 'public'
        ORDER BY
            table_schema,
            table_name,
            ordinal_position;
    """)
    plan = vn.get_training_plan_generic(df_information_schema)
    vn.train(plan=plan)


def text_to_sql(
    conn: psycopg.Connection,
    inp: str,
    provider: Provider,
    model: str,
    entire_schema: bool,
    gold_tables: list[str],
) -> TextToSql:
    vn = get_vanna_client(conn)
    try:
        sys.stdout = StringIO()
        os.environ["TOKENIZERS_PARALLELISM"] = "false"
        query = vn.generate_sql(inp)
    finally:
        sys.stdout = sys.__stdout__

    return {"error": None, "messages": [], "query": query}
