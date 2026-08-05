import base64
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

    try:
        audio_bytes = synthesize_speech(last_ai.content)
    except Exception as exc:
        print(f"[voice_output] TTS failed for doctor {doctor.id}: {exc}")
        return {}

    # --- TEMPORARY: local audio dump, for development listening only. ---
    # The real output path is the base64 audio returned in the API response above.
    # DELETE this whole block (and the audio_output/ folder) when it is no longer needed.
    try:
        AUDIO_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        output_path = AUDIO_OUTPUT_DIR / f"{uuid4()}.wav"
        output_path.write_bytes(audio_bytes)
    except Exception as exc:
        print(f"[voice_output] local audio dump failed for doctor {doctor.id}: {exc}")
    # --- END TEMPORARY ---

    encoded = base64.b64encode(audio_bytes).decode("ascii")
    return {"audio_base64": encoded}
