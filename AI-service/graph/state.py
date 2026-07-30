from typing import Annotated, TypedDict

from langgraph.graph.message import add_messages


class AssistantState(TypedDict):
    messages: Annotated[list, add_messages]
    route: str
