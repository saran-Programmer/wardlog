from typing import Literal

from langchain_core.messages import AIMessage, BaseMessage, SystemMessage
from pydantic import BaseModel

from ..constants import (
    IS_FOLLOWUP_MESSAGE,
    ROUTE_ACTIVITY_DETAILS,
    ROUTE_CHAT,
    ROUTE_EXTRACT,
    ROUTE_PATIENT,
    ROUTE_PATIENT_DETAILS,
)
from ..prompts.detector_prompt import DETECTOR_SYSTEM_PROMPT
from ..state import AssistantState
from .llm import get_llm

NODE_NAME = "detector"

class RouteDecision(BaseModel):
    route: Literal["extract", "patient", "patient_details", "activity_details", "chat"]


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
    }


def route_after_detector(state: AssistantState) -> str:
    route = state["route"]
    if route == ROUTE_EXTRACT:
        return ROUTE_EXTRACT
    if route == ROUTE_PATIENT:
        return ROUTE_PATIENT
    if route == ROUTE_PATIENT_DETAILS:
        return ROUTE_PATIENT_DETAILS
    if route == ROUTE_ACTIVITY_DETAILS:
        return ROUTE_ACTIVITY_DETAILS
    return ROUTE_CHAT
