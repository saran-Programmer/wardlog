from datetime import datetime
from typing import Any, Optional, Sequence

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
    consultations: Optional[Sequence[Any]] = None,
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

    if not consultations:
        return description

    lines = [description, "  Patients seen:"]
    for c in consultations:
        if c.patient and c.patient.name:
            header = c.patient.name
            details = []
            if c.patient.age is not None:
                details.append(f"{c.patient.age} years old")
            if c.patient.sex:
                details.append(c.patient.sex)
            if details:
                header += f" ({', '.join(details)})"
        else:
            header = "Unnamed patient"
        lines.append(f"  - {header}")
        if c.diagnoses:
            lines.append(f"    Diagnoses: {', '.join(c.diagnoses)}")
        if c.drugs:
            lines.append(f"    Drugs: {', '.join(c.drugs)}")
        if c.surgery_type:
            lines.append(f"    Surgery type: {c.surgery_type}")

    return "\n".join(lines)


def build_doctor_context(config: RunnableConfig) -> DoctorContext:
    return DoctorContext(
        **{
            k: v
            for k, v in config["configurable"].items()
            if k in DoctorContext.model_fields
        }
    )
