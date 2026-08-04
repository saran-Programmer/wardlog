from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnableConfig

from ..config import DoctorContext
from ..constants import ROUTE_END, ROUTE_VOICE_OUTPUT
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
    system_prompt = GeneratorPrompt().build(doctor, state)

    llm = get_llm(temperature=0.5)
    reply = llm.invoke([SystemMessage(content=system_prompt), *state["messages"]])

    return {"messages": [reply]}


def route_after_generator(state: AssistantState, config: RunnableConfig) -> str:
    if config["configurable"].get("voice_output"):
        return ROUTE_VOICE_OUTPUT
    return ROUTE_END
