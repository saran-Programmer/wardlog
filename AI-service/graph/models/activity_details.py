from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

from .activity import Activity
from .patient_details import PatientSummary


class ActivityConsultationSummary(BaseModel):
    patient: Optional[PatientSummary] = None
    diagnoses: list[str] = Field(default_factory=list)
    drugs: list[str] = Field(default_factory=list)
    surgery_type: Optional[str] = None


class ActivityDetails(BaseModel):
    activity: Activity
    consultations: list[ActivityConsultationSummary] = Field(default_factory=list)

    @classmethod
    def from_records(
        cls,
        activity_node: Any,
        consultations: list[Any],
    ) -> "ActivityDetails":
        return cls(
            activity=Activity(
                id=activity_node.get("id"),
                name=activity_node.get("name"),
                start=(
                    datetime.fromisoformat(activity_node["start"])
                    if activity_node.get("start")
                    else None
                ),
                end=(
                    datetime.fromisoformat(activity_node["end"])
                    if activity_node.get("end")
                    else None
                ),
                location=activity_node.get("location"),
                notes=activity_node.get("notes"),
            ),
            consultations=[
                ActivityConsultationSummary(
                    patient=(
                        PatientSummary(
                            name=c["patient_name"],
                            age=c["patient_age"],
                            sex=c["patient_sex"],
                        )
                        if c["patient_name"] is not None
                        else None
                    ),
                    diagnoses=c["diagnoses"],
                    drugs=c["drugs"],
                    surgery_type=c["surgery_type"],
                )
                for c in consultations
            ],
        )
