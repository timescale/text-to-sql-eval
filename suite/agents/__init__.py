from .baseline import (
    get_tables as baseline_get_tables,
)
from .baseline import (
    text_to_sql as baseline_text_to_sql,
)
from .pgai import get_tables as pgai_get_tables
from .pgai import text_to_sql as pgai_text_to_sql


def get_agent_fn(agent: str, task: str) -> callable:
    if task not in ["get_tables", "text_to_sql"]:
        raise ValueError(f"Invalid task: {task}")
    if agent not in ["pgai", "baseline"]:
        raise ValueError(f"Invalid agent: {agent}")
    if agent == "pgai":
        agent_fn = pgai_text_to_sql if task == "text_to_sql" else pgai_get_tables
    elif agent == "baseline":
        agent_fn = (
            baseline_text_to_sql if task == "text_to_sql" else baseline_get_tables
        )
    return agent_fn
