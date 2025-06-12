import asyncio
import os
import random
from pathlib import Path

import pgai.semantic_catalog as sc
import psycopg
import pydantic_ai
from psycopg.sql import SQL, Identifier

from ..types import ContextMode, Provider, TextToSql
from ..utils import get_db_url_from_connection, get_git_info


def version() -> str:
    git_info = get_git_info(Path(__file__).parent.parent.parent.parent / "pgai")
    return f"{git_info.branch}-{git_info.commit}"


async def setup(
    conn: psycopg.Connection,
    catalog: str,
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
        / "catalogs"
        / catalog
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
    context_mode: ContextMode,
    gold_tables: list[str],
) -> TextToSql:
    db_url = get_db_url_from_connection(con)
    async with (
        await psycopg.AsyncConnection.connect(db_url) as target_con,
    ):
        catalog = await sc.from_name(target_con, "default")
        obj_ids = None
        sql_ids = None
        fact_ids = None
        if context_mode == "specific_ids":
            sql_ids = [x.id for x in await catalog.list_sql_examples(target_con)]
            fact_ids = [x.id for x in await catalog.list_facts(target_con)]
            async with target_con.cursor() as cur:
                await cur.execute(
                    SQL("""
                        SELECT id
                        FROM ai.{table}
                        WHERE objtype = 'table'
                        AND objnames[1] = %s
                        AND objnames[2] = ANY(%s);
                    """).format(
                        table=Identifier(f"semantic_catalog_obj_{catalog.id}"),
                    ),
                    ("public", gold_tables),
                )
                obj_ids = [x[0] for x in await cur.fetchall()]

        while True:
            try:
                response = await catalog.generate_sql(
                    target_con,
                    target_con,
                    f"{provider}:{model}",
                    inp,
                    context_mode=context_mode,
                    obj_ids=obj_ids,
                    sql_ids=sql_ids,
                    fact_ids=fact_ids,
                )
            except pydantic_ai.exceptions.ModelHTTPError as e:
                if e.status_code == 429:
                    if provider == "mistral":
                        wait = 5
                        # mistral has rate limit of 1 request per second
                        jitter = random.uniform(0, 4)
                    else:
                        wait = 60
                        # other models usually have an input limit of tokens per minute
                        jitter = random.uniform(-10, 10)
                    wait = round(wait - jitter, 2)
                    print(str(e), flush=True)
                    print(
                        f"    Rate limit hit, waiting for {wait} seconds...", flush=True
                    )
                    await asyncio.sleep(wait)
                    continue
                raise e
            break

    return {
        "error": None,
        "messages": [str(x) for x in response.messages],
        "query": response.sql_statement,
        "usage": {
            "cached_tokens": response.usage.details.get("cached_tokens", 0)
            if response.usage.details is not None
            else 0,
            "request_tokens": response.usage.request_tokens or 0,
            "response_tokens": response.usage.response_tokens or 0,
        },
    }
