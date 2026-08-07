from uuid import UUID

from db.consultation_saver import save_consultation
from messaging.kafka_producer import publish_patient

from ..state import AssistantState

NODE_NAME = "consultation_saver"


def consultation_saver_node(state: AssistantState):
    resolved_activity_id = state["resolved_activity_id"]
    consultation = state["consultation"]

    save_consultation(resolved_activity_id, consultation)

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
