from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnableConfig

from ..config import DoctorContext
from ..models.activity import Activity, ActivityList, check_incomplete
from ..prompts.extractor_prompt import ExtractorPrompt
from ..state import AssistantState
from .llm import get_llm

NODE_NAME = "ACTIVITY_EXTRACT"


def build_followup_messages(activity: Activity) -> list[str]:
    """Return one follow-up question per missing required field."""
    label = activity.name or "activity"
    messages = []

    if activity.name is None:
        messages.append(
            "What type of activity was this — a surgery block, clinic "
            "block, on-call shift, or onsite on-call shift?"
        )
    if activity.start is None:
        messages.append(f"What time did the {label} start?")
    if activity.end is None:
        messages.append(f"What time did the {label} end?")

    return messages


def extractor_node(state: AssistantState, config: RunnableConfig):
    doctor = DoctorContext(
        **{
            k: v
            for k, v in config["configurable"].items()
            if k in DoctorContext.model_fields
        }
    )
    system_prompt = ExtractorPrompt().build(doctor)

    result = (
        get_llm(temperature=0)
        .with_structured_output(ActivityList)
        .invoke([SystemMessage(content=system_prompt), *state["messages"]])
    )

    followup_messages = []

    print("==============EXTRACTOR===================")
    
    for activity in result.activities:

        print(activity, end="\n")

        if check_incomplete(activity):
            followup_messages.extend(build_followup_messages(activity))

    print("=========================================")

    return {"activities": result.activities, "followup_messages": followup_messages}


def route_after_extractor(state: AssistantState) -> str:
    activities = state["activities"]
    followup_messages = state["followup_messages"]

    if activities and not followup_messages:
        return "confirmation"

    return "generator"
