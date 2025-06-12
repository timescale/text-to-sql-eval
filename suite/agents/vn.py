"""
Vanna agent
"""

import os
import sys
from io import StringIO
from pathlib import Path
from tomllib import load as load_toml
from typing import Union

import psycopg
from dotenv import load_dotenv
from vanna.anthropic import Anthropic_Chat
from vanna.openai import OpenAI_Chat
from vanna.pgvector import PG_VectorStore

from ..types import Provider, TextToSql
from ..utils import get_db_url_from_connection

load_dotenv()


def version() -> str:
    with Path(__file__).parent.parent.parent.joinpath("uv.lock").open("r") as f:
        lockfile = load_toml(f)
    return next((obj for obj in lockfile["package"] if obj["name"] == "vanna"), None)[
        "version"
    ]


class AnthropicVanna(PG_VectorStore, Anthropic_Chat):
    def __init__(self, config=None):
        PG_VectorStore.__init__(self, config=config)
        Anthropic_Chat.__init__(self, config=config)


class OpenAIVanna(PG_VectorStore, OpenAI_Chat):
    def __init__(self, config=None):
        PG_VectorStore.__init__(self, config=config)
        OpenAI_Chat.__init__(self, config={**config, "temperature": 1})


VannaType = Union[OpenAIVanna, AnthropicVanna]


def get_vanna_client(
    conn: psycopg.Connection, provider: Provider = "openai", model="o4-mini"
) -> VannaType:
    if provider == "anthropic":
        vn = AnthropicVanna(
            config={
                "api_key": os.environ["ANTHROPIC_API_KEY"],
                "connection_string": get_db_url_from_connection(conn).replace(
                    "postgres://", "postgresql://"
                ),
                "model": model,
            }
        )
    elif provider == "openai":
        vn = OpenAIVanna(
            config={
                "api_key": os.environ["OPENAI_API_KEY"],
                "connection_string": get_db_url_from_connection(conn).replace(
                    "postgres://", "postgresql://"
                ),
                "model": model,
            }
        )
    else:
        raise ValueError(f"Invalid provider: {provider}")
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
    catalog: str,
    dataset: str,
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


async def text_to_sql(
    conn: psycopg.Connection,
    inp: str,
    provider: Provider,
    model: str,
    entire_schema: bool,
    gold_tables: list[str],
) -> TextToSql:
    vn = get_vanna_client(conn, provider, model)
    try:
        sys.stdout = StringIO()
        os.environ["TOKENIZERS_PARALLELISM"] = "false"
        query = vn.generate_sql(inp, allow_llm_to_see_data=True)
    finally:
        sys.stdout = sys.__stdout__

    return {"error": None, "messages": [], "query": query}
