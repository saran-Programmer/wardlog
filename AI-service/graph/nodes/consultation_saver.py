from db.consultation_saver import save_consultation

from ..state import AssistantState

NODE_NAME = "consultation_saver"


def consultation_saver_node(state: AssistantState):
    resolved_activity_id = state["resolved_activity_id"]
    consultation = state["consultation"]

    save_consultation(resolved_activity_id, consultation)

    return {"consultation_saved": consultation}
