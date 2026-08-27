from typing import Optional

from pydantic import BaseModel, Field

from .activity import Activity
from .patient_details import PatientSummary as PatientResult


class ConsultationResult(BaseModel):

    id: str
    patient: Optional[PatientResult] = None
    diagnoses: list[str] = Field(default_factory=list)
    drugs: list[str] = Field(default_factory=list)
    surgery_type: Optional[str] = None


class ActivityResult(BaseModel):

    activity: Activity
    consultations: list[ConsultationResult] = Field(default_factory=list)
