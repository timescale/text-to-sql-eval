from typing import Literal, TypedDict


class PromptMessage(TypedDict):
    role: Literal["system", "user"]
    content: str


class TextToSql(TypedDict):
    messages: list[PromptMessage]
    query: str
