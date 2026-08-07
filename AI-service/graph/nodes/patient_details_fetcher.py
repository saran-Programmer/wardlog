from typing import Optional

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

from db.normalize import strip_honorifics
from db.patient_fetcher import find_patient_details

from ..config import DoctorContext
from ..constants import ROUTE_GENERATOR, ROUTE_PATIENT_DETAILS_GENERATOR
from ..state import AssistantState
from .llm import get_llm

NODE_NAME = "patient_details_fetcher"

PATIENT_NAME_QUERY_PROMPT = (
    "Extract the name of the patient the doctor is asking about from their "
    "latest message. Leave it null if no specific patient is named."
)

class PatientNameQuery(BaseModel):
    patient_name: Optional[str] = Field(
        default=None,
        description=(
            "the name of the patient the doctor is asking about, or null if "
            "no specific patient is named."
        ),
    )


def patient_details_fetcher_node(state: AssistantState, config: RunnableConfig):
    doctor = DoctorContext(
        **{
            k: v
            for k, v in config["configurable"].items()
            if k in DoctorContext.model_fields
        }
    )
    messages = state["messages"]
    last = messages[-1] if messages else None
    doctor_message = last.content if last is not None else ""

    result = (
        get_llm()
        .with_structured_output(PatientNameQuery)
        .invoke(
            [
                SystemMessage(content=PATIENT_NAME_QUERY_PROMPT),
                HumanMessage(content=doctor_message),
            ]
        )
    )

    if not result.patient_name:
        return {"patient_not_found": ""}

    patient_name = strip_honorifics(result.patient_name)
    patient_data = find_patient_details(doctor.id, patient_name)

    if patient_data is None:
        return {"patient_not_found": patient_name}

    return {"patient_details_data": patient_data}


def route_after_patient_details_fetcher(state: AssistantState) -> str:
    if state.get("patient_not_found") is not None:
        return ROUTE_GENERATOR
    return ROUTE_PATIENT_DETAILS_GENERATOR
