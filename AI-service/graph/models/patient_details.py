from datetime import date, datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class PatientSummary(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    sex: Optional[str] = None


class ConsultationSummary(BaseModel):
    diagnoses: list[str] = Field(default_factory=list)
    drugs: list[str] = Field(default_factory=list)
    surgery_type: Optional[str] = None
    activity_name: Optional[str] = None
    activity_start: Optional[datetime] = None
    activity_end: Optional[datetime] = None
    activity_location: Optional[str] = None


class ReportSummary(BaseModel):
    report_type: Optional[str] = None
    report_date: Optional[date] = None
    findings: Optional[str] = None
    notes: Optional[str] = None


class PatientDetails(BaseModel):
    patient: PatientSummary
    consultations: list[ConsultationSummary] = Field(default_factory=list)
    reports: list[ReportSummary] = Field(default_factory=list)

    @classmethod
    def from_records(
        cls,
        patient_node: Any,
        consultations: list[Any],
        reports: list[Any],
    ) -> "PatientDetails":
        return cls(
            patient=PatientSummary(
                name=patient_node.get("name"),
                age=patient_node.get("age"),
                sex=patient_node.get("sex"),
            ),
            consultations=[
                ConsultationSummary(
                    diagnoses=c["diagnoses"],
                    drugs=c["drugs"],
                    surgery_type=c["surgery_type"],
                    activity_name=c["activity_name"],
                    activity_start=(
                        datetime.fromisoformat(c["activity_start"])
                        if c["activity_start"]
                        else None
                    ),
                    activity_end=(
                        datetime.fromisoformat(c["activity_end"])
                        if c["activity_end"]
                        else None
                    ),
                    activity_location=c["activity_location"],
                )
                for c in consultations
            ],
            reports=[
                ReportSummary(
                    report_type=r["report_type"],
                    report_date=(
                        date.fromisoformat(r["report_date"])
                        if r["report_date"]
                        else None
                    ),
                    findings=r["findings"],
                    notes=r["notes"],
                )
                for r in reports
            ],
        )
