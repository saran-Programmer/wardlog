from langchain_core.runnables import RunnableConfig

from db.report_saver import save_report

from ..config import DoctorContext
from ..state import AssistantState

NODE_NAME = "report_saver"


def report_saver_node(state: AssistantState, config: RunnableConfig):
    doctor = DoctorContext(
        **{
            k: v
            for k, v in config["configurable"].items()
            if k in DoctorContext.model_fields
        }
    )
    pending_report = state["pending_report"]
    file_url = state.get("pending_report_file_url")

    save_report(doctor.id, pending_report, file_url)

    return {
        "pending_report": None,
        "pending_report_file_url": None,
        "report_saved": pending_report,
    }
