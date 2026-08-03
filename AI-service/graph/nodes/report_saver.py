from db.report_saver import save_report

from ..state import AssistantState

NODE_NAME = "report_saver"


def report_saver_node(state: AssistantState):
    pending_report = state["pending_report"]

    save_report(pending_report)

    return {"pending_report": None, "report_saved": pending_report}
