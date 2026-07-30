from typing import Literal

from langchain_core.messages import SystemMessage
from pydantic import BaseModel

from ..prompts.detector_prompt import DETECTOR_SYSTEM_PROMPT
from ..state import AssistantState
from .llm import llm

NODE_NAME = "DETECTOR"

class RouteDecision(BaseModel):
    route: Literal["extract", "chat"]


def detector_node(state: AssistantState):

    messages = [SystemMessage(content=DETECTOR_SYSTEM_PROMPT), *state["messages"]]
    decision = llm.with_structured_output(RouteDecision).invoke(messages)

    return {"route": decision.route}


def route_after_detector(state: AssistantState) -> str:
    return "extract" if state["route"] == "extract" else "chat"
