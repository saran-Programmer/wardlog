from groq import Groq
from langchain_groq import ChatGroq

TEXT_MODEL = "llama-3.3-70b-versatile"
VISION_MODEL = "qwen/qwen3.6-27b"
TTS_MODEL = "canopylabs/orpheus-v1-english"
TTS_VOICE = "diana"
STT_MODEL = "whisper-large-v3"

# Reused across calls — reads GROQ_API_KEY from env once at import time.
groq_client = Groq()

def get_llm(temperature: float = 0) -> ChatGroq:
    """Return a ChatGroq instance for the given temperature.

    The model name and any shared config live here in one place; each node
    picks the temperature it needs (e.g. 0 for deterministic routing, higher
    for more varied generation).
    """
    return ChatGroq(model=TEXT_MODEL, temperature=temperature)


def get_vision_llm(temperature: float = 0) -> ChatGroq:
    """Return a ChatGroq instance for multimodal (document/image) input.

    reasoning_effort="none" turns off the model's thinking mode — otherwise
    its hidden reasoning tokens eat into the completion budget before it
    ever emits the JSON output, truncating the response before it's valid.
    """
    return ChatGroq(
        model=VISION_MODEL,
        temperature=temperature,
        reasoning_effort="none",
        max_tokens=4096,
    )


# TODO: the audio is currently requested as uncompressed WAV, which is roughly 10x larger
# than it needs to be — and base64 adds another ~33% on top. Before this goes anywhere near
# real traffic, request a compressed format (e.g. mp3) from the TTS API instead of wav, and
# enable gzip on the API responses. Leaving it uncompressed for now.
def synthesize_speech(text: str) -> bytes:
    response = groq_client.audio.speech.create(
        model=TTS_MODEL,
        voice=TTS_VOICE,
        input=text,
        response_format="wav",
    )
    return response.read()


def transcribe_audio(file_bytes: bytes, filename: str) -> str:
    """Transcribe an audio recording to text via Groq Whisper.

    filename is passed alongside the bytes purely so Groq can infer the
    container format (webm/ogg/wav/etc) from its extension.
    """
    transcription = groq_client.audio.transcriptions.create(
        file=(filename, file_bytes),
        model=STT_MODEL,
    )
    return transcription.text.strip()
