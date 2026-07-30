from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnableConfig

from ..config import DoctorContext
from ..prompts.generator_prompt import GeneratorPrompt
from ..state import AssistantState
from .llm import get_llm

NODE_NAME = "GENERATOR"


def generator_node(state: AssistantState, config: RunnableConfig):
    doctor = DoctorContext(
        **{
            k: v
            for k, v in config["configurable"].items()
            if k in DoctorContext.model_fields
        }
    )
    system_prompt = GeneratorPrompt().build(doctor)

    llm = get_llm(temperature=0.5)
    reply = llm.invoke([SystemMessage(content=system_prompt), *state["messages"]])

    return {"messages": [reply]}
