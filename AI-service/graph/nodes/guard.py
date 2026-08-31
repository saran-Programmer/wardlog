import asyncio

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from pydantic import BaseModel

from ..constants import ROUTE_GENERATOR
from ..models.guard_verdict import GuardVerdict
from ..prompts.guard_prompts import SAFETY_POLICY, SCOPE_SYSTEM_PROMPT
from ..state import AssistantState
from .llm import get_safety_llm, get_scope_llm
from .report_extractor import route_entry

NODE_NAME = "guard"


class SafetyDecision(BaseModel):
    safe: bool
    reason: str


class ScopeDecision(BaseModel):
    in_scope: bool
    reason: str


async def _check_safety(latest_message: str) -> SafetyDecision:
    llm = get_safety_llm().with_structured_output(SafetyDecision)
    return await llm.ainvoke(
        [SystemMessage(content=SAFETY_POLICY), HumanMessage(content=latest_message)]
    )

async def _check_scope(messages: list[BaseMessage]) -> ScopeDecision:
    llm = get_scope_llm().with_structured_output(ScopeDecision)
    return await llm.ainvoke([SystemMessage(content=SCOPE_SYSTEM_PROMPT), *messages])


async def _run_checks(
    latest_message: str, messages: list[BaseMessage]
) -> tuple[SafetyDecision, ScopeDecision]:
    return await asyncio.gather(_check_safety(latest_message), _check_scope(messages))


def guard_node(state: AssistantState):
    messages = state["messages"]
    latest_message = messages[-1].content if messages else ""

    safety, scope = asyncio.run(_run_checks(latest_message, messages))

    if not safety.safe:
        guard = GuardVerdict(processable=False, category="disallowed", reason=safety.reason)
    elif not scope.in_scope:
        guard = GuardVerdict(processable=False, category="off_topic", reason=scope.reason)
    else:
        guard = GuardVerdict(processable=True, category="in_scope", reason=scope.reason)

    return {"guard": guard, "generation_attempts": 0, "output_guard": None}


def route_after_guard(state: AssistantState) -> str:
    guard = state.get("guard")
    if guard is not None and not guard.processable:
        return ROUTE_GENERATOR

    return route_entry(state)
