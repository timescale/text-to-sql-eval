import os
from pathlib import Path

import pgai.semantic_catalog as sc
import psycopg
from psycopg.sql import Identifier, SQL

from ..types import Provider, TextToSql
from ..utils import get_db_url_from_connection


async def setup(
    conn: psycopg.Connection,
    dataset: str,
    provider: Provider,
    model: str,
    vector_dimensions: int,
):
    import pgai
    from pgai.semantic_catalog import create
    from pgai.semantic_catalog.vectorizer import embedding_config_from_dict

    db_url = get_db_url_from_connection(conn)

    pgai.install(db_url, strict=False)

    api_key = None
    base_url = None

    if provider == "ollama":
        implementation = "ollama"
        base_url = os.environ["OLLAMA_HOST"]
    elif provider == "openai":
        implementation = "openai"
        api_key = os.environ["OPENAI_API_KEY"]
    else:
        implementation = "sentence_transformers"

    config = embedding_config_from_dict(
        {
            "implementation": implementation,
            "model": model,
            "dimensions": vector_dimensions,
            "api_key": api_key,
            "base_url": base_url,
        }
    )

    database = conn.info.dbname.replace(f"{dataset}_", "")

    yaml_file = (
        Path(__file__).parent.parent.parent
        / "datasets"
        / dataset
        / "databases"
        / f"{database}.yaml"
    )

    async with (
        await psycopg.AsyncConnection.connect(db_url) as tcon,
    ):
        sc = await create(tcon, "default", embedding_name=None, embedding_config=config)
        with yaml_file.open("r") as f:
            await sc.import_catalog(tcon, tcon, f, None)


async def text_to_sql(
    con: psycopg.Connection,
    inp: str,
    provider: Provider,
    model: str,
    *args,
) -> TextToSql:
    db_url = get_db_url_from_connection(con)
    async with (
        await psycopg.AsyncConnection.connect(db_url) as target_con,
    ):
        catalog = await sc.from_name(catalog_con, "default")
        # generate sql
        response = await catalog.generate_sql(
            target_con,
            target_con,
            f"{provider}:{model}",
            inp,
        )

    return {
        "error": None,
        "messages": [str(x) for x in response.messages],
        "query": response.sql_statement,
        "usage": {
            "cached_tokens": response.usage.details["cached_tokens"] or 0
            if response.usage.details is not None
            else 0,
            "request_tokens": response.usage.request_tokens or 0,
            "response_tokens": response.usage.response_tokens or 0,
        },
    }
