from langchain_groq import ChatGroq

TEXT_MODEL = "llama-3.3-70b-versatile"
VISION_MODEL = "qwen/qwen3.6-27b"

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
