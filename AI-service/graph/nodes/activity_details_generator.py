from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnableConfig

from ..models.activity_details import ActivityDetails
from ..prompts.activity_details_prompt import ActivityDetailsPrompt
from ..state import AssistantState
from .details_common import build_doctor_context, describe_activity
from .llm import get_llm

NODE_NAME = "activity_details_generator"


def _render_activity_data(data: ActivityDetails) -> str:
    activity = data.activity
    lines = [
        describe_activity(
            activity.name, activity.start, activity.end, activity.location, activity.notes
        )
    ]

    if data.consultations:
        lines.append("\nPatients seen:")
        for c in data.consultations:
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
            lines.append(f"- {header}")
            if c.diagnoses:
                lines.append(f"  Diagnoses: {', '.join(c.diagnoses)}")
            if c.drugs:
                lines.append(f"  Drugs: {', '.join(c.drugs)}")
            if c.surgery_type:
                lines.append(f"  Surgery type: {c.surgery_type}")
    else:
        lines.append("\nPatients seen: none recorded.")

    return "\n".join(lines)


def activity_details_generator_node(state: AssistantState, config: RunnableConfig):
    doctor = build_doctor_context(config)
    activity_data = state["activity_details_data"]
    rendered = _render_activity_data(activity_data)
    system_prompt = ActivityDetailsPrompt().build(doctor, rendered)

    response = get_llm(temperature=0.3).invoke(
        [SystemMessage(content=system_prompt), *state["messages"]]
    )

    return {"activity_generated_content": response.content}
