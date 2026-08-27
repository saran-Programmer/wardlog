import json
import logging
from typing import Optional

from langchain_core.messages import SystemMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool

from db.activity_query import query_activities
from db.patient_history_fetcher import get_patient_history
from db.patient_query import query_patients

from ..models.activity_query_result import ActivityResult
from ..models.patient_history import PatientHistory
from ..prompts.data_query_prompt import DataQueryPrompt
from ..state import AssistantState
from .details_common import ACTIVITY_LABELS, build_doctor_context, describe_activity, format_datetime
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
    def query_activities_tool(
        filters: list[dict], include: Optional[list[str]] = None
    ) -> list[ActivityResult]:
        """Look up the doctor's logged Activity records via structured filters.

        filters: a list of filter objects, each shaped
        {"field": ..., "operator": ..., "value": ...}, AND-ed together. See the
        system prompt for the allowed fields, operators, and value shapes. An
        empty list returns every logged activity.

        include: optional list of related data to fetch alongside each
        matched activity. See the system prompt for the allowed values. Omit
        or leave empty to fetch activities only.
        """
        return query_activities(doctor_id, filters, include)

    return query_activities_tool


def _build_query_patients_tool(doctor_id: str):
    """Build a query_patients tool scoped to one doctor.

    Built fresh per node invocation so doctor_id is captured per-request via
    closure rather than exposed as a tool argument the LLM can set — the LLM
    only ever sees/supplies name/age/sex.
    """

    @tool
    def query_patients_tool(
        name: Optional[str] = None,
        age: Optional[int] = None,
        sex: Optional[str] = None,
    ) -> list[dict]:
        """Look up the doctor's Patient records by optional name/age/sex.

        name: fuzzy-matched against patient names.
        age: soft boost toward patients within a few years of this age.
        sex: soft boost toward patients of this sex ("male" or "female").
        All three are optional and can be combined; omit any filter you don't
        have information for. Omitting all three returns a broad set of the
        doctor's patients.
        """
        candidates = query_patients(doctor_id, name=name, age=age, sex=sex)

        for candidate in candidates:
            patient_id = candidate["patient"].id
            candidate["history"] = (
                get_patient_history(doctor_id, patient_id) if patient_id else None
            )

        return candidates

    return query_patients_tool


def _describe_patient(entry: dict) -> str:
    patient = entry["patient"]
    details = []
    if patient.age is not None:
        details.append(f"{patient.age} years old")
    if patient.sex:
        details.append(patient.sex)

    header = patient.name or "Unnamed patient"
    if details:
        header += f" ({', '.join(details)})"
    header += f" — match score {entry['match_score']}"

    history: Optional[PatientHistory] = entry.get("history")
    if history is None:
        return header

    lines = [header]

    if history.consultations:
        lines.append("  Visit history:")
        for c in history.consultations:
            visit = c.visit
            label = ACTIVITY_LABELS.get(visit.name, visit.name or "visit") if visit else "visit"
            when = format_datetime(visit.start) if visit and visit.start else "unknown date"
            lines.append(f"  - {label} on {when}")
            if c.diagnoses:
                lines.append(f"    Diagnoses: {', '.join(c.diagnoses)}")
            if c.drugs:
                lines.append(f"    Drugs: {', '.join(c.drugs)}")
            if c.surgery_type:
                lines.append(f"    Surgery type: {c.surgery_type}")

    if history.reports:
        lines.append("  Reports:")
        for r in history.reports:
            report_line = f"  - {r.report_type or 'report'}"
            if r.report_date:
                report_line += f" ({r.report_date})"
            lines.append(report_line)
            if r.findings:
                lines.append(f"    Findings: {r.findings}")

    return "\n".join(lines)


def data_query_node(state: AssistantState, config: RunnableConfig):
    doctor = build_doctor_context(config)
    activity_tool = _build_query_activities_tool(doctor.id)
    patient_tool = _build_query_patients_tool(doctor.id)

    system_prompt = DataQueryPrompt().build(doctor)
    messages = [SystemMessage(content=system_prompt), *state["messages"]]

    llm = get_llm().bind_tools([activity_tool, patient_tool])

    fetched_activities: list[ActivityResult] = []
    fetched_patients: list[dict] = []

    for _ in range(MAX_TOOL_ITERATIONS):
        response = llm.invoke(messages)
        messages.append(response)

        if not response.tool_calls:
            break

        for call in response.tool_calls:
            if call["name"] == "query_patients_tool":
                args = call["args"]
                try:
                    patients = patient_tool.invoke(args)
                except ValueError as exc:
                    logger.warning(
                        "data_query invalid patient query: doctor_id=%s args=%s error=%s",
                        doctor.id, args, exc,
                    )
                    messages.append(
                        ToolMessage(content=f"Error: {exc}", tool_call_id=call["id"])
                    )
                    continue

                fetched_patients.extend(patients)
                logger.info(
                    "data_query fetched patients: doctor_id=%s args=%s -> %s",
                    doctor.id, args, patients,
                )
                messages.append(
                    ToolMessage(
                        content=json.dumps(
                            [
                                {
                                    "patient": p["patient"].model_dump(mode="json"),
                                    "match_score": p["match_score"],
                                    "history": (
                                        p["history"].model_dump(mode="json")
                                        if p["history"] is not None
                                        else None
                                    ),
                                }
                                for p in patients
                            ]
                        ),
                        tool_call_id=call["id"],
                    )
                )
                continue

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

    if not fetched_activities and not fetched_patients:
        return {"activity_not_found": True}

    content_lines = [
        f"- {describe_activity(a.activity.name, a.activity.start, a.activity.end, a.activity.location, a.activity.notes, a.consultations)}"
        for a in fetched_activities
    ]
    content_lines += [f"- {_describe_patient(p)}" for p in fetched_patients]

    return {"activity_generated_content": "\n".join(content_lines)}
