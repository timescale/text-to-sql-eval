from .baseline import (
    get_tables as baseline_get_tables,
)
from .baseline import (
    text_to_sql as baseline_text_to_sql,
)
from .pgai import get_tables as pgai_get_tables
from .pgai import text_to_sql as pgai_text_to_sql

from .vn import setup as vanna_setup
from .vn import text_to_sql as vanna_text_to_sql

def get_agent_fn(agent: str, task: str) -> callable:
    if task not in ["get_tables", "text_to_sql"]:
        raise ValueError(f"Invalid task: {task}")
    if agent == "pgai":
        agent_fn = pgai_text_to_sql if task == "text_to_sql" else pgai_get_tables
    elif agent == "baseline":
        agent_fn = (
            baseline_text_to_sql if task == "text_to_sql" else baseline_get_tables
        )
    elif agent == "vanna":
        if task != "text_to_sql":
            raise ValueError(f"Invalid task for vanna: {task}")
        agent_fn = vanna_text_to_sql
    else:
        raise ValueError(f"Invalid agent: {agent}")
    return agent_fn


def get_agent_setup_fn(agent: str) -> callable:
    if agent == "vanna":
        return vanna_setup
    else:
        raise ValueError(f"Invalid agent: {agent}")
