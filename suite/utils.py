import os
from typing import Optional

from dotenv import load_dotenv
from psycopg import Connection, Cursor

load_dotenv()


def get_db_url_from_connection(conn: Connection, dbname: Optional[str] = None) -> str:
    """
    Get the database URL from a psycopg connection object.
    """
    return f"postgres://{conn.info.user}:{conn.info.password}@{conn.info.host}:{conn.info.port}/{dbname or conn.info.dbname}"


def get_psycopg_str(dbname: str = "postgres") -> str:
    return f"{os.environ['POSTGRES_DSN']}/{dbname}"


def validate_embedding_provider(provider: str) -> bool:
    if provider not in ["ollama", "openai"]:
        raise ValueError(f"Invalid provider: {provider}")


def get_default_embedding_model(provider: str) -> str:
    models = {
        "ollama": "smollm:135m",
        "openai": "text-embedding-3-small",
        "sentence_transformers": "nomic-ai/nomic-embed-text-v1.5",
    }
    if provider not in models:
        raise ValueError(f"Invalid provider: {provider}")
    return models[provider]


def validate_provider(provider: str) -> bool:
    if provider not in ["anthropic", "ollama", "openai"]:
        raise ValueError(f"Invalid provider: {provider}")


def get_default_model(provider: str) -> str:
    models = {
        "anthropic": "claude-3-5-haiku-latest",
        "ollama": "smollm:135m",
        "openai": "gpt-4.1-mini",
    }
    if provider not in models:
        raise ValueError(f"Invalid provider: {provider}")
    return models[provider]


def setup_pgai_config(cur: Cursor) -> None:
    cur.execute(
        "select set_config('ai.enable_feature_flag_text_to_sql', 'true', false)"
    )
    value = os.environ.get("ANTHROPIC_API_KEY", None)
    if value is not None:
        cur.execute(
            "select set_config('ai.anthropic_api_key', %s, false) is not null",
            (value,),
        )
    value = os.environ.get("OLLAMA_HOST", None)
    if value is not None:
        cur.execute(
            "select set_config('ai.ollama_host', %s, false) is not null",
            (value,),
        )
    value = os.environ.get("OPENAI_API_KEY", None)
    if value is not None:
        cur.execute(
            "select set_config('ai.openai_api_key', %s, false) is not null",
            (value,),
        )
