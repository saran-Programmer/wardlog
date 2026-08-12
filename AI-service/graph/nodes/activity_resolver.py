from datetime import datetime, time, timedelta
from typing import Optional

from langchain_core.messages import BaseMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.types import Command

from db.activity_fetcher import find_activities

from ..config import DoctorContext
from ..models.activity import Activity
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


def resolve_activity_references(doctor: DoctorContext, messages: list[BaseMessage]) -> list[Activity]:
    """Extract a date/time/type reference from the conversation and return every
    matching activity. Shared by the graph-node resolver below (which disambiguates
    down to one activity for the patient/consultation flow) and by
    activity_details_generator_node (which wants every match, not just one)."""
    system_prompt = ActivityResolverPrompt().build(doctor)

    ref = (
        get_llm()
        .with_structured_output(ActivityReference)
        .invoke([SystemMessage(content=system_prompt), *messages])
    )

    lower, upper = _build_window(ref)
    return find_activities(doctor.id, ref.activity_type, lower, upper)


def activity_resolver_node(state: AssistantState, config: RunnableConfig):
    doctor = DoctorContext(
        **{
            k: v
            for k, v in config["configurable"].items()
            if k in DoctorContext.model_fields
        }
    )
    activities = resolve_activity_references(doctor, state["messages"])
    return Command(goto=state["return_to"], update={"activity_candidates": activities})