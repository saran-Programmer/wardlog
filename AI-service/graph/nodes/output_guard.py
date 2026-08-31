from langchain_core.messages import HumanMessage, RemoveMessage, SystemMessage

from ..constants import (
    MAX_GENERATION_RETRIES,
    ROUTE_END,
    ROUTE_GENERATOR,
    ROUTE_OUTPUT_FALLBACK,
)
from ..models.output_guard_verdict import OutputGuardVerdict
from ..prompts.output_guard_prompt import OUTPUT_GUARD_SYSTEM_PROMPT
from ..state import AssistantState
from .llm import get_output_guard_llm

NODE_NAME = "output_guard"


def output_guard_node(state: AssistantState):
    reply = state["messages"][-1]

    llm = get_output_guard_llm().with_structured_output(OutputGuardVerdict)
    verdict = llm.invoke(
        [
            SystemMessage(content=OUTPUT_GUARD_SYSTEM_PROMPT),
            HumanMessage(content=reply.content),
        ]
    )

    print("==========GUARD==========")
    print(verdict.passed)
    print("=========================")

    if verdict.passed:
        return {"output_guard": verdict}

    return {"output_guard": verdict, "messages": [RemoveMessage(id=reply.id)]}


def route_after_output_guard(state: AssistantState) -> str:
    verdict = state.get("output_guard")
    if verdict is None or verdict.passed:
        return ROUTE_END

    attempts = state.get("generation_attempts", 0)
    if attempts <= MAX_GENERATION_RETRIES:
        return ROUTE_GENERATOR
    return ROUTE_OUTPUT_FALLBACK
