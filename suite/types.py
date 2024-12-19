from typing import Literal, TypedDict

Provider = Literal["anthropic", "ollama", "openai"]


class PromptMessage(TypedDict):
    role: Literal["system", "user"]
    content: str


class TextToSql(TypedDict):
    messages: list[PromptMessage]
    query: str
