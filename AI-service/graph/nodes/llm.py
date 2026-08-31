from functools import lru_cache

from groq import Groq
from langchain_groq import ChatGroq

TEXT_MODEL = "openai/gpt-oss-120b"
VISION_MODEL = "qwen/qwen3.6-27b"
TTS_MODEL = "canopylabs/orpheus-v1-english"
TTS_VOICE = "diana"
STT_MODEL = "whisper-large-v3"
SAFETY_MODEL = "openai/gpt-oss-safeguard-20b"
SCOPE_MODEL = "openai/gpt-oss-20b"
OUTPUT_GUARD_MODEL = "openai/gpt-oss-20b"

# Reused across calls — reads GROQ_API_KEY from env once at import time.
groq_client = Groq()

@lru_cache(maxsize=8)
def get_llm(temperature: float = 0) -> ChatGroq:
    """Return a ChatGroq instance for the given temperature.

    The model name and any shared config live here in one place; each node
    picks the temperature it needs (e.g. 0 for deterministic routing, higher
    for more varied generation).

    Cached per temperature — ChatGroq eagerly opens both a sync and an async
    httpx client on construction, so creating a fresh one per call leaks
    async clients that get closed later from a different event loop.
    """
    return ChatGroq(model=TEXT_MODEL, temperature=temperature, reasoning_effort=None)


@lru_cache(maxsize=8)
def get_safety_llm(temperature: float = 0) -> ChatGroq:
    """Return a ChatGroq instance for the input guardrail's safety check.

    gpt-oss-safeguard is a policy-following safety model — it's given a
    policy as its system input and classifies content against it.
    """
    return ChatGroq(model=SAFETY_MODEL, temperature=temperature, reasoning_effort=None)


@lru_cache(maxsize=8)
def get_scope_llm(temperature: float = 0) -> ChatGroq:
    """Return a ChatGroq instance for the input guardrail's scope check."""
    return ChatGroq(model=SCOPE_MODEL, temperature=temperature, reasoning_effort=None)


@lru_cache(maxsize=8)
def get_output_guard_llm(temperature: float = 0) -> ChatGroq:
    """Return a ChatGroq instance for the output guardrail's capability-scope check."""
    return ChatGroq(model=OUTPUT_GUARD_MODEL, temperature=temperature, reasoning_effort=None)


@lru_cache(maxsize=8)
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
