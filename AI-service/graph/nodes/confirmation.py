from ..state import AssistantState

NODE_NAME = "confirmation"


def confirmation_node(state: AssistantState):
    print(state["activities"])
    return {}
