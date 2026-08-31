from langchain_core.messages import AIMessage

from ..state import AssistantState

NODE_NAME = "output_fallback"

FALLBACK_MESSAGE = (
    "Sorry, I can't give you a good answer to that right now. I can help you "
    "log activities, save or look up patients and consultations, and "
    "extract, save, or fetch reports — what would you like to do?"
)


def output_fallback_node(state: AssistantState):
    return {"messages": [AIMessage(content=FALLBACK_MESSAGE)]}
