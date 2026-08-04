from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnableConfig

from ..models.patient_details import PatientDetails
from ..prompts.patient_details_prompt import PatientDetailsPrompt
from ..state import AssistantState
from .details_common import build_doctor_context, describe_activity
from .llm import get_llm

NODE_NAME = "patient_details_generator"


def _render_patient_data(data: PatientDetails) -> str:
    patient = data.patient
    header = f"Patient: {patient.name}"
    details = []
    if patient.age is not None:
        details.append(f"{patient.age} years old")
    if patient.sex:
        details.append(patient.sex)
    if details:
        header += f" ({', '.join(details)})"

    lines = [header]

    if data.consultations:
        lines.append("\nConsultations:")
        for c in data.consultations:
            lines.append(
                "- "
                + describe_activity(
                    c.activity_name,
                    c.activity_start,
                    c.activity_end,
                    c.activity_location,
                )
            )
            if c.diagnoses:
                lines.append(f"  Diagnoses: {', '.join(c.diagnoses)}")
            if c.drugs:
                lines.append(f"  Drugs: {', '.join(c.drugs)}")
            if c.surgery_type:
                lines.append(f"  Surgery type: {c.surgery_type}")
    else:
        lines.append("\nConsultations: none recorded.")

    if data.reports:
        lines.append("\nReports:")
        for r in data.reports:
            entry = f"- {r.report_type or 'report'}"
            if r.report_date:
                entry += f" ({r.report_date.isoformat()})"
            lines.append(entry)
            if r.findings:
                lines.append(f"  Findings: {r.findings}")
            if r.notes:
                lines.append(f"  Doctor notes: {r.notes}")
    else:
        lines.append("\nReports: none recorded.")

    return "\n".join(lines)


def patient_details_generator_node(state: AssistantState, config: RunnableConfig):
    doctor = build_doctor_context(config)
    patient_data = state["patient_details_data"]
    rendered = _render_patient_data(patient_data)
    system_prompt = PatientDetailsPrompt().build(doctor, rendered)

    response = get_llm(temperature=0.3).invoke(
        [SystemMessage(content=system_prompt), *state["messages"]]
    )

    return {"patient_generated_content": response.content}
