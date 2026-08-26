import json
import logging

from langchain_core.messages import SystemMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool

from db.activity_query import query_activities

from ..models.activity import Activity
from ..prompts.data_query_prompt import DataQueryPrompt
from ..state import AssistantState
from .details_common import build_doctor_context, describe_activity
from .llm import get_llm

NODE_NAME = "data_query"

logger = logging.getLogger(__name__)

MAX_TOOL_ITERATIONS = 10


def _build_query_activities_tool(doctor_id: str):
    """Build a query_activities tool scoped to one doctor.

    Built fresh per node invocation so doctor_id is captured per-request via
    closure rather than exposed as a tool argument the LLM can set — the LLM
    only ever sees/supplies `filters`.
    """

    @tool
    def query_activities_tool(filters: list[dict]) -> list[Activity]:
        """Look up the doctor's logged Activity records via structured filters.

        filters: a list of filter objects, each shaped
        {"field": ..., "operator": ..., "value": ...}, AND-ed together. See the
        system prompt for the allowed fields, operators, and value shapes. An
        empty list returns every logged activity.
        """
        return query_activities(doctor_id, filters)

    return query_activities_tool


def data_query_node(state: AssistantState, config: RunnableConfig):
    doctor = build_doctor_context(config)
    activity_tool = _build_query_activities_tool(doctor.id)

    system_prompt = DataQueryPrompt().build(doctor)
    messages = [SystemMessage(content=system_prompt), *state["messages"]]

    llm = get_llm().bind_tools([activity_tool])

    fetched_activities: list[Activity] = []

    for _ in range(MAX_TOOL_ITERATIONS):
        response = llm.invoke(messages)
        messages.append(response)

        if not response.tool_calls:
            break

        for call in response.tool_calls:
            filters = call["args"].get("filters", [])
            try:

                print(call["args"])

                activities = activity_tool.invoke(call["args"])
            except ValueError as exc:
                logger.warning(
                    "data_query invalid filters: doctor_id=%s filters=%s error=%s",
                    doctor.id, filters, exc,
                )
                messages.append(
                    ToolMessage(content=f"Error: {exc}", tool_call_id=call["id"])
                )
                continue

            fetched_activities.extend(activities)
            logger.info(
                "data_query fetched activities: doctor_id=%s filters=%s -> %s",
                doctor.id, filters, activities,
            )
            messages.append(
                ToolMessage(
                    content=json.dumps(
                        [a.model_dump(mode="json") for a in activities]
                    ),
                    tool_call_id=call["id"],
                )
            )
    else:
        logger.warning(
            "data_query hit the %d-iteration tool-call cap: doctor_id=%s",
            MAX_TOOL_ITERATIONS, doctor.id,
        )

    if not fetched_activities:
        return {"activity_not_found": True}

    content = "\n".join(
        f"- {describe_activity(a.name, a.start, a.end, a.location, a.notes)}"
        for a in fetched_activities
    )

    return {"activity_generated_content": content}
