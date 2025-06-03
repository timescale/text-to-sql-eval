from typing import Awaitable, Callable

from psycopg import Connection

from ..types import Provider, TextToSql
from .baseline import (
    get_tables as baseline_get_tables,
)
from .baseline import (
    text_to_sql as baseline_text_to_sql,
)
from .baseline import (
    version as baseline_version,
)
from .pgai import (
    setup as pgai_setup,
)
from .pgai import (
    text_to_sql as pgai_text_to_sql,
)
from .pgai import (
    version as pgai_version,
)
from .vn import (
    setup as vanna_setup,
)
from .vn import (
    text_to_sql as vanna_text_to_sql,
)
from .vn import (
    version as vanna_version,
)

AgentFn = Callable[
    [Connection, str, Provider, str, bool, list[str]], Awaitable[TextToSql]
]


def get_agent_fn(agent: str, task: str) -> AgentFn:
    if task not in ["get_tables", "text_to_sql"]:
        raise ValueError(f"Invalid task: {task}")
    if agent == "baseline":
        agent_fn = (
            baseline_text_to_sql if task == "text_to_sql" else baseline_get_tables
        )
    elif agent == "pgai":
        if task != "text_to_sql":
            raise ValueError(f"Invalid task for pgai: {task}")
        agent_fn = pgai_text_to_sql
    elif agent == "vanna" or agent == "vn":
        if task != "text_to_sql":
            raise ValueError(f"Invalid task for vanna: {task}")
        agent_fn = vanna_text_to_sql
    else:
        raise ValueError(f"Invalid agent: {agent}")
    return agent_fn


def get_agent_setup_fn(
    agent: str,
) -> Callable[[Connection, Provider, str, int], Awaitable[None]]:
    if agent == "pgai":
        return pgai_setup
    if agent == "vanna" or agent == "vn":
        return vanna_setup
    else:
        raise ValueError(f"Invalid agent: {agent}")


def get_agent_version(agent: str) -> str:
    if agent == "baseline":
        return baseline_version()
    elif agent == "pgai":
        return pgai_version()
    elif agent == "vanna" or agent == "vn":
        return vanna_version()
    else:
        raise ValueError(f"Invalid agent: {agent}")
