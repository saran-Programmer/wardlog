from datetime import datetime
from typing import Optional

from langchain_core.runnables import RunnableConfig

from ..config import DoctorContext

ACTIVITY_LABELS = {
    "surgeryblock": "surgery block",
    "clinicblock": "clinic block",
    "oncall": "on-call",
    "onsiteoncall": "on-site on-call",
}


def format_datetime(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M")


def describe_activity(
    activity_name: Optional[str],
    start: Optional[datetime],
    end: Optional[datetime],
    location: Optional[str],
    notes: Optional[str] = None,
) -> str:
    label = ACTIVITY_LABELS.get(activity_name, activity_name or "activity")
    if start and end:
        when = f"{format_datetime(start)} to {format_datetime(end)}"
    elif start:
        when = f"starting {format_datetime(start)}"
    elif end:
        when = f"ending {format_datetime(end)}"
    else:
        when = "no time recorded"

    description = f"{label}, {when}"
    if location:
        description += f", at {location}"
    if notes:
        description += f" (notes: {notes})"
    return description


def build_doctor_context(config: RunnableConfig) -> DoctorContext:
    return DoctorContext(
        **{
            k: v
            for k, v in config["configurable"].items()
            if k in DoctorContext.model_fields
        }
    )
