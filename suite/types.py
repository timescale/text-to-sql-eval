from typing import Any, Literal, TypedDict

Provider = Literal["anthropic", "ollama", "openai"]


class PromptMessage(TypedDict):
    role: Literal["system", "user"]
    content: str


class TextToSql(TypedDict):
    # TODO: improve typing and structure for pgai messages
    messages: list[PromptMessage | str]
    query: str


class EvalResult(TypedDict):
    status: Literal["pass", "fail", "error"]
    dataset: str
    database: str
    name: str
    question: str
    duration: float
    defaults: Any


class Results(TypedDict):
    passing: int
    total: int
    failed: list[str]
    failed_error_counts: dict[str, int]
    errored: list[str]
    evals: list[EvalResult]
