from typing import Annotated, TypedDict

from langgraph.graph.message import add_messages

from .models.activity import Activity


class AssistantState(TypedDict):
    messages: Annotated[list, add_messages]
    route: str
    activities: list[Activity]
    followup_messages: list[str]
    published_activities: list[Activity]
    rejected_activities: list[Activity]
