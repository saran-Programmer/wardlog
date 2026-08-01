from datetime import datetime, time, timedelta
from typing import Optional

from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.types import Command

from db.activity_fetcher import find_activities

from ..config import DoctorContext
from ..models.activity_reference import ActivityReference
from ..prompts.activity_resolver_prompt import ActivityResolverPrompt
from ..state import AssistantState
from .llm import get_llm

NODE_NAME = "activity_resolver"


def _parse_time(value: Optional[str]) -> Optional[time]:
    if not value:
        return None

    for fmt in ("%H:%M:%S", "%H:%M"):
        try:
            return datetime.strptime(value, fmt).time()
        except ValueError:
            continue

    return None


def _build_window(ref: ActivityReference):

    start_time = _parse_time(ref.start_time)
    end_time = _parse_time(ref.end_time)

    lower = None
    if ref.start_date is not None:
        lower = datetime.combine(ref.start_date, start_time or time(0, 0))

    upper = None
    if ref.end_date is not None:
        if end_time is not None:
            upper = datetime.combine(ref.end_date, end_time)
        else:
            # no end time -> through the end of end_date, i.e. start of next day
            upper = datetime.combine(ref.end_date + timedelta(days=1), time(0, 0))

    return lower, upper


def activity_resolver_node(state: AssistantState, config: RunnableConfig):
    doctor = DoctorContext(
        **{
            k: v
            for k, v in config["configurable"].items()
            if k in DoctorContext.model_fields
        }
    )
    system_prompt = ActivityResolverPrompt().build(doctor)

    ref = (
        get_llm()
        .with_structured_output(ActivityReference)
        .invoke([SystemMessage(content=system_prompt), *state["messages"]])
    )

    lower, upper = _build_window(ref)
    activity_type = ref.activity_type

    activities = find_activities(doctor.id, activity_type, lower, upper)

    return Command(goto=state["return_to"], update={"activity_candidates": activities})