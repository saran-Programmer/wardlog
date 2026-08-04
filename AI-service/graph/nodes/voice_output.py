from pathlib import Path
from uuid import uuid4

from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig

from ..config import DoctorContext
from ..state import AssistantState
from .llm import synthesize_speech

NODE_NAME = "voice_output"

AUDIO_OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "audio_output"


def voice_output_node(state: AssistantState, config: RunnableConfig):
    doctor = DoctorContext(
        **{
            k: v
            for k, v in config["configurable"].items()
            if k in DoctorContext.model_fields
        }
    )

    last_ai = next(
        (m for m in reversed(state["messages"]) if isinstance(m, AIMessage)), None
    )
    if last_ai is None:
        return {}

    AUDIO_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = str(AUDIO_OUTPUT_DIR / f"{uuid4()}.wav")

    try:
        synthesize_speech(last_ai.content, output_path)
    except Exception as exc:
        print(f"[voice_output] TTS failed for doctor {doctor.id}: {exc}")
        return {}

    return {"audio_path": output_path}
