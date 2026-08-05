from db.report_saver import save_report

from ..state import AssistantState

NODE_NAME = "report_saver"


def report_saver_node(state: AssistantState):
    pending_report = state["pending_report"]
    file_url = state.get("pending_report_file_url")

    save_report(pending_report, file_url)

    return {
        "pending_report": None,
        "pending_report_file_url": None,
        "report_saved": pending_report,
    }
