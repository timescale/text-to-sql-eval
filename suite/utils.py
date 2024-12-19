import os

from dotenv import load_dotenv
from psycopg import Cursor

from .types import Provider

load_dotenv()


def get_psycopg_str(dbname: str = "postgres") -> str:
    return f"host={os.environ['POSTGRES_HOST']} dbname={dbname} user={os.environ['POSTGRES_USER']} password={os.environ['POSTGRES_PASSWORD']}"


def validate_embedding_provider(provider: str) -> bool:
    if provider not in ["ollama", "openai"]:
        raise ValueError(f"Invalid provider: {provider}")


def get_default_embedding_model(provider: str) -> str:
    models = {
        "ollama": "smollm:135m",
        "openai": "text-embedding-3-small",
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
        "openai": "gpt-4o-mini",
    }
    if provider not in models:
        raise ValueError(f"Invalid provider: {provider}")
    return models[provider]


def setup_pgai_config(cur: Cursor, provider: Provider) -> None:
    cur.execute(
        "select set_config('ai.enable_feature_flag_text_to_sql', 'true', false)"
    )
    if provider == "anthropic":
        cur.execute(
            "select set_config('ai.anthropic_api_key', %s, false) is not null",
            (os.environ["ANTHROPIC_API_KEY"],),
        )
    elif provider == "ollama":
        cur.execute(
            "select set_config('ai.ollama_host', %s, false) is not null",
            (os.environ["OLLAMA_HOST"],),
        )
    elif provider == "openai":
        cur.execute(
            "select set_config('ai.openai_api_key', %s, false) is not null",
            (os.environ["OPENAI_API_KEY"],),
        )
