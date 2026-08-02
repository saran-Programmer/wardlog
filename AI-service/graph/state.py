from typing import Annotated, NotRequired, Optional, TypedDict

from langgraph.graph.message import add_messages

from .models.activity import Activity
from .models.consultation import Consultation


class AssistantState(TypedDict):
    messages: Annotated[list, add_messages]
    route: str
    activities: list[Activity]
    activity_candidates: list[Activity]
    followup_messages: list[str]
    published_activities: list[Activity]
    rejected_activities: list[Activity]
    consultation: Optional[Consultation]
    return_to: Optional[str]
    resolved_activity_id: Optional[str]
    consultation_saved: NotRequired[Optional[Consultation]]
