from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnableConfig

from db.normalize import strip_honorifics

from ..config import DoctorContext
from ..models.consultation import Consultation
from ..prompts.consultation_extractor_prompt import ConsultationExtractorPrompt
from ..state import AssistantState
from .llm import get_llm

NODE_NAME = "consultation_extractor"


def consultation_extractor_node(state: AssistantState, config: RunnableConfig):
    doctor = DoctorContext(
        **{
            k: v
            for k, v in config["configurable"].items()
            if k in DoctorContext.model_fields
        }
    )
    system_prompt = ConsultationExtractorPrompt().build(doctor)

    result = (
        get_llm(temperature=0)
        .with_structured_output(Consultation)
        .invoke([SystemMessage(content=system_prompt), *state["messages"]])
    )

    if result.patient.name:
        cleaned_patient = result.patient.model_copy(
            update={"name": strip_honorifics(result.patient.name)}
        )
        result = result.model_copy(update={"patient": cleaned_patient})

    return {"consultation": result}
