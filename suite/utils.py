import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from psycopg import Connection

load_dotenv()


def get_db_url_from_connection(conn: Connection, dbname: Optional[str] = None) -> str:
    """
    Get the database URL from a psycopg connection object.
    """
    return f"postgres://{conn.info.user}:{conn.info.password}@{conn.info.host}:{conn.info.port}/{dbname or conn.info.dbname}"


def get_psycopg_str(dbname: str = "postgres") -> str:
    return f"{os.environ['POSTGRES_DSN']}/{dbname}"


OPENAI_EMBEDDING_MODELS = [
    "text-embedding-ada-002",
    "text-embedding-3-large",
    "text-embedding-3-small",
]

OLLAMA_EMBEDDING_MODELS = [
    "smollm",
    "smollm:135m",
    "smollm:360m",
    "smollm:1.7b",
    "smollm2",
    "smollm2:135m",
    "smollm2:360m",
    "smollm2:1.7b",
]


def expand_embedding_model(model: str) -> str:
    if model in OLLAMA_EMBEDDING_MODELS:
        model = f"ollama:{model}"
    elif model in OPENAI_EMBEDDING_MODELS:
        model = f"openai:{model}"
    elif model.startswith("nomic-ai/"):
        model = f"sentence_transformers:{model}"
    return model


ANTHROPIC_TASK_MODELS = [
    "claude-3-7-sonnet",
    "claude-3-7-sonnet-latest",
    "claude-3-5-haiku",
    "claude-3-5-haiku-latest",
    "claude-3-5-sonnet",
    "claude-3-5-sonnet-latest",
    "claude-3-opus-latest",
]

MISTRAL_TASK_MODELS = [
    "codestral-latest",
    "mistral-large-latest",
    "mistral-moderation-latest",
    "mistral-small-latest",
]

OPENAI_TASK_MODELS = [
    "gpt-4.1",
    "gpt-4.1-mini",
    "gpt-4.1-nano",
    "o3",
    "o3-mini" "o4-mini",
]


def expand_task_model(model: str) -> str:
    if model in ANTHROPIC_TASK_MODELS:
        model = f"anthropic:{model}"
    elif model in MISTRAL_TASK_MODELS:
        model = f"mistral:{model}"
    elif model in OPENAI_TASK_MODELS:
        model = f"openai:{model}"
    return model


@dataclass
class GitInfo:
    branch: str
    commit: str


def get_git_info(path: Path) -> GitInfo:
    """
    Get the git information from a given path.

    Returns:
        A dictionary containing the branch and commit information.
    """
    git_info = GitInfo(branch="??", commit="??")
    git_dir = path / ".git"
    with (git_dir / "HEAD").open("r") as f:
        head = f.read().strip()
    if head.startswith("ref:"):
        ref = head.split(" ")[1]
        with (git_dir / ref).open("r") as f:
            commit = f.read().strip()
        branch = ref.split("/", 2)[2]
    else:
        commit = head
        branch = "??"

    git_info.branch = branch
    git_info.commit = commit

    return git_info


def get_catalog(con: Connection) -> str:
    with con.cursor() as cur:
        cur.execute("SELECT value FROM text2sql.config WHERE name = 'catalog'")
        row = cur.fetchone()
        return row[0]
