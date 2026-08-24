from langchain_core.runnables import RunnableConfig

from db.patient_search import search_patients

from ..config import DoctorContext
from ..state import AssistantState

NODE_NAME = "patient_resolver"


def patient_resolver_node(state: AssistantState, config: RunnableConfig):
    doctor = DoctorContext(
        **{
            k: v
            for k, v in config["configurable"].items()
            if k in DoctorContext.model_fields
        }
    )
    patient = state["consultation"].patient

    candidates = search_patients(doctor.id, patient)

    return {"patient_candidates": candidates}
