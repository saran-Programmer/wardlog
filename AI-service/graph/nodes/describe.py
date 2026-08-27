from typing import Optional

from ..models.activity_query_result import ActivityResult
from ..models.patient_history import PatientHistory
from .details_common import ACTIVITY_LABELS, format_datetime
from .details_common import describe_activity as _describe_activity_fields


def describe_activity(result: ActivityResult) -> str:
    """Human-readable, id/score-free description of one fetched activity and
    its consultations (patient name/age/sex, diagnoses, drugs, surgery_type)."""
    activity = result.activity
    return _describe_activity_fields(
        activity.name,
        activity.start,
        activity.end,
        activity.location,
        activity.notes,
        result.consultations,
    )


def describe_patient(entry: dict) -> str:
    """Human-readable, id/score-free description of one fetched patient and
    their history.

    `entry` is one result from query_patients_tool:
    {"patient": PatientSummary, "match_score": float, "match_breakdown": dict,
    "history": Optional[PatientHistory]}. match_score/match_breakdown are
    internal ranking data and are never surfaced here.
    """
    patient = entry["patient"]
    details = []
    if patient.age is not None:
        details.append(f"{patient.age} years old")
    if patient.sex:
        details.append(patient.sex)

    header = patient.name or "Unnamed patient"
    if details:
        header += f" ({', '.join(details)})"

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
            if r.notes:
                lines.append(f"    Notes: {r.notes}")

    return "\n".join(lines)
