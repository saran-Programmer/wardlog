from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnableConfig

from ..prompts.answer_prompt import AnswerPrompt
from ..state import AssistantState
from .describe import describe_activity, describe_patient
from .details_common import build_doctor_context
from .llm import get_llm

NODE_NAME = "answer_synthesizer"


def _build_context(state: AssistantState) -> str:
    activities = state.get("fetched_activities") or []
    patients = state.get("fetched_patients") or []

    lines = [describe_activity(a) for a in activities]
    lines += [describe_patient(p) for p in patients]
    return "\n\n".join(lines)


def answer_synthesizer_node(state: AssistantState, config: RunnableConfig):
    """Reason over the data fetched by data_query into a substantive, factual
    answer to the doctor's question. Hands off to the generator afterward,
    which applies tone/voice only — this node owns the cleaning + answering.
    """
    doctor = build_doctor_context(config)
    context = _build_context(state)

    system_prompt = AnswerPrompt().build(doctor, context)
    response = get_llm(temperature=0.2).invoke(
        [SystemMessage(content=system_prompt), *state["messages"]]
    )

    print("==============anwser==============")
    print(response.content)
    print("==================================")

    return {"activity_generated_content": response.content}
