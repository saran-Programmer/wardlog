from typing import Annotated, NotRequired, Optional, TypedDict

from langgraph.graph.message import add_messages

from .models.activity import Activity
from .models.consultation import Consultation
from .models.patient_details import PatientDetails
from .models.report_extraction import ReportExtraction


class AssistantState(TypedDict):
    messages: Annotated[list, add_messages]
    route: str
    activities: list[Activity]
    activity_candidates: list[Activity]
    followup_messages: list[str]
    published_activities: list[Activity]
    rejected_activities: list[Activity]
    consultation: Optional[Consultation]
    return_to: Optional[str]
    resolved_activity_id: Optional[str]
    consultation_saved: NotRequired[Optional[Consultation]]
    document_rejection_reason: NotRequired[Optional[str]]
    pending_report: NotRequired[Optional[ReportExtraction]]
    report_saved: NotRequired[Optional[ReportExtraction]]
    patient_not_found: NotRequired[Optional[str]]
    patient_generated_content: NotRequired[Optional[str]]
    patient_details_data: NotRequired[Optional[PatientDetails]]
