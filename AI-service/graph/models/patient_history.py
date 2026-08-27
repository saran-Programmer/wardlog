from datetime import date, datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

from .activity import Activity
from .patient_details import PatientSummary


class ConsultationVisit(BaseModel):
    id: Optional[str] = None
    diagnoses: list[str] = Field(default_factory=list)
    drugs: list[str] = Field(default_factory=list)
    surgery_type: Optional[str] = None
    visit: Optional[Activity] = None


class ReportResult(BaseModel):
    report_type: Optional[str] = None
    report_date: Optional[date] = None
    findings: Optional[str] = None
    notes: Optional[str] = None
    file_url: Optional[str] = None


class PatientHistory(BaseModel):
    patient: PatientSummary
    consultations: list[ConsultationVisit] = Field(default_factory=list)
    reports: list[ReportResult] = Field(default_factory=list)

    @classmethod
    def from_records(
        cls,
        patient_node: Any,
        consultations: list[Any],
        reports: list[Any],
    ) -> "PatientHistory":
        return cls(
            patient=PatientSummary(
                id=patient_node.get("id"),
                name=patient_node.get("name"),
                age=patient_node.get("age"),
                sex=patient_node.get("sex"),
            ),
            consultations=[
                ConsultationVisit(
                    id=c["consultation_id"],
                    diagnoses=c["diagnoses"],
                    drugs=c["drugs"],
                    surgery_type=c["surgery_type"],
                    visit=_to_activity(c["activity"]),
                )
                for c in consultations
            ],
            reports=[
                ReportResult(
                    report_type=r["report_type"],
                    report_date=(
                        date.fromisoformat(r["report_date"]) if r["report_date"] else None
                    ),
                    findings=r["findings"],
                    notes=r["notes"],
                    file_url=r["file_url"],
                )
                for r in reports
            ],
        )


def _to_activity(node: Any) -> Optional[Activity]:
    if node is None:
        return None
    return Activity(
        id=node.get("id"),
        name=node.get("name"),
        start=datetime.fromisoformat(node["start"]) if node.get("start") else None,
        end=datetime.fromisoformat(node["end"]) if node.get("end") else None,
        location=node.get("location"),
        notes=node.get("notes"),
    )
