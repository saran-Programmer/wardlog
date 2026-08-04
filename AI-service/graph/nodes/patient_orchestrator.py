from langchain_core.runnables import RunnableConfig

from ..constants import (
    ROUTE_ACTIVITY_RESOLVER,
    ROUTE_CONSULTATION_SAVER,
    ROUTE_GENERATOR,
    ROUTE_PATIENT_EXTRACTOR,
)
from ..state import AssistantState
from .activity_disambiguation import resolve_candidates

NODE_NAME = "patient_orchestrator"


def patient_orchestrator_node(state: AssistantState, config: RunnableConfig):
    resolved_activity_id = state.get("resolved_activity_id")

    if resolved_activity_id is None and "activity_candidates" not in state:
        return {"return_to": NODE_NAME}

    if resolved_activity_id is None:
        return resolve_candidates(state, NODE_NAME)

    return {}


def route_after_orchestrator(state: AssistantState) -> str:
    resolved_activity_id = state.get("resolved_activity_id")

    if resolved_activity_id is None:
        if "activity_candidates" not in state:
            return ROUTE_ACTIVITY_RESOLVER
        if state.get("return_to") == NODE_NAME:
            return ROUTE_ACTIVITY_RESOLVER
        return ROUTE_GENERATOR

    if state.get("consultation") is None:
        return ROUTE_PATIENT_EXTRACTOR

    return ROUTE_CONSULTATION_SAVER
