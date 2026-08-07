from langchain_core.runnables import RunnableConfig

from db.activity_detail_fetcher import find_activity_details

from ..config import DoctorContext
from ..constants import (
    ROUTE_ACTIVITY_DETAILS_GENERATOR,
    ROUTE_ACTIVITY_LOOKUP,
    ROUTE_ACTIVITY_RESOLVER,
    ROUTE_GENERATOR,
)
from ..state import AssistantState
from .activity_disambiguation import resolve_candidates

NODE_NAME = "activity_lookup"


def activity_lookup_node(state: AssistantState, config: RunnableConfig):
    resolved_activity_id = state.get("resolved_activity_id")

    if resolved_activity_id is None and "activity_candidates" not in state:
        return {"return_to": NODE_NAME}

    if resolved_activity_id is None:
        n = len(state["activity_candidates"])
        result = resolve_candidates(state, NODE_NAME)
        if n == 0:
            result["activity_not_found"] = True
        return result

    doctor = DoctorContext(
        **{
            k: v
            for k, v in config["configurable"].items()
            if k in DoctorContext.model_fields
        }
    )
    data = find_activity_details(doctor.id, resolved_activity_id)
    if data is None:
        return {"activity_not_found": True}

    return {"activity_details_data": data}


def route_after_activity_lookup(state: AssistantState) -> str:
    resolved_activity_id = state.get("resolved_activity_id")

    if resolved_activity_id is None:
        if "activity_candidates" not in state:
            return ROUTE_ACTIVITY_RESOLVER
        if state.get("return_to") == NODE_NAME:
            return ROUTE_ACTIVITY_RESOLVER
        return ROUTE_GENERATOR

    if state.get("activity_details_data") is not None:
        return ROUTE_ACTIVITY_DETAILS_GENERATOR

    if state.get("activity_not_found"):
        return ROUTE_GENERATOR

    return ROUTE_ACTIVITY_LOOKUP
