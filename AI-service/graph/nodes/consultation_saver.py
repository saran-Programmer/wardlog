from uuid import UUID

from langchain_core.runnables import RunnableConfig

from db.consultation_saver import save_consultation
from messaging.kafka_producer import publish_patient

from ..config import DoctorContext
from ..state import AssistantState

NODE_NAME = "consultation_saver"


def consultation_saver_node(state: AssistantState, config: RunnableConfig):
    doctor = DoctorContext(
        **{
            k: v
            for k, v in config["configurable"].items()
            if k in DoctorContext.model_fields
        }
    )
    resolved_activity_id = state["resolved_activity_id"]
    consultation = state["consultation"]

    save_consultation(doctor.id, resolved_activity_id, consultation)

    patient = consultation.patient
    publish_patient(
        activityId=UUID(resolved_activity_id),
        name=patient.name,
        age=patient.age,
        sex=patient.sex,
        diagnosis=consultation.diagnoses,
        drugs=consultation.drugs,
    )

    return {"consultation_saved": consultation}
