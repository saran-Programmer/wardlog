from typing import Literal

from langchain_core.messages import AIMessage, BaseMessage, SystemMessage
from pydantic import BaseModel

from ..constants import (
    IS_FOLLOWUP_MESSAGE,
    ROUTE_CHAT,
    ROUTE_DATA_QUERY,
    ROUTE_EXTRACT,
    ROUTE_PATIENT,
)
from ..prompts.detector_prompt import DETECTOR_SYSTEM_PROMPT
from ..state import AssistantState
from .llm import get_llm

NODE_NAME = "detector"

class RouteDecision(BaseModel):
    route: Literal["extract", "patient", "data_query", "chat"]


def get_current_exchange(messages: list[BaseMessage]) -> list[BaseMessage]:
    collected: list[BaseMessage] = []

    for message in reversed(messages):
        if isinstance(message, AIMessage) and not message.additional_kwargs.get(
            IS_FOLLOWUP_MESSAGE
        ):
            break
        collected.append(message)

    collected.reverse()
    return collected


def detector_node(state: AssistantState):
    exchange = get_current_exchange(state["messages"])
    messages = [SystemMessage(content=DETECTOR_SYSTEM_PROMPT), *exchange]
    decision = get_llm().with_structured_output(RouteDecision).invoke(messages)

    print("==========================")
    print(decision.route)
    print("==========================")

    return {
        "route": decision.route,
        "activities": [],
        "followup_messages": [],
        "published_activities": [],
        "rejected_activities": [],
        "blocked_activities": [],
        "consultation_saved": None,
        "document_rejection_reason": None,
        "report_saved": None,
        "patient_not_found": None,
        "patient_generated_content": None,
        "patient_details_data": None,
        "activity_not_found": None,
        "activity_generated_content": None,
        "fetched_activities": [],
        "fetched_patients": [],
    }


def route_after_detector(state: AssistantState) -> str:
    route = state["route"]
    if route == ROUTE_EXTRACT:
        return ROUTE_EXTRACT
    if route == ROUTE_PATIENT:
        return ROUTE_PATIENT
    if route == ROUTE_DATA_QUERY:
        return ROUTE_DATA_QUERY
    return ROUTE_CHAT
