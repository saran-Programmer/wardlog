from langchain_groq import ChatGroq

MODEL = "llama-3.3-70b-versatile"

def get_llm(temperature: float = 0) -> ChatGroq:
    """Return a ChatGroq instance for the given temperature.

    The model name and any shared config live here in one place; each node
    picks the temperature it needs (e.g. 0 for deterministic routing, higher
    for more varied generation).
    """
    return ChatGroq(model=MODEL, temperature=temperature)
