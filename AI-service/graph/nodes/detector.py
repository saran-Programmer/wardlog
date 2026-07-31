from typing import Literal

from langchain_core.messages import AIMessage, BaseMessage, SystemMessage
from pydantic import BaseModel

from ..constants import IS_FOLLOWUP_MESSAGE, ROUTE_CHAT, ROUTE_EXTRACT
from ..prompts.detector_prompt import DETECTOR_SYSTEM_PROMPT
from ..state import AssistantState
from .llm import get_llm

NODE_NAME = "detector"

class RouteDecision(BaseModel):
    route: Literal["extract", "patient", "chat"]


def get_current_exchange(messages: list[BaseMessage]) -> list[BaseMessage]:
    """Return only the messages belonging to the current exchange.

    Walk backwards from the latest message. An AI message flagged as a
    follow-up means the request before it is still in progress, so the walk
    continues through it. The walk STOPS at the first AI message that is NOT a
    follow-up — that reply closed an earlier request, and everything before it
    is unrelated history.

    This keeps the detector from re-routing on activities/topics mentioned in
    earlier, already-closed exchanges.
    """
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

    print("=============================")
    print(decision.route)
    print("=============================")

    return {
        "route": decision.route,
        "activities": [],
        "followup_messages": [],
        "published_activities": [],
        "rejected_activities": [],
    }


def route_after_detector(state: AssistantState) -> str:
    route = state["route"]
    if route == ROUTE_EXTRACT:
        return ROUTE_EXTRACT
    if route == "patient":
        return "patient"
    return ROUTE_CHAT
