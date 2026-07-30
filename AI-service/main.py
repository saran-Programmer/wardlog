from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langgraph.graph import END, START, StateGraph

from graph.constants import ROUTE_CHAT, ROUTE_EXTRACT
from graph.nodes.confirmation import NODE_NAME as CONFIRMATION_NODE
from graph.nodes.confirmation import confirmation_node
from graph.nodes.detector import NODE_NAME as DETECTOR_NODE
from graph.nodes.detector import detector_node, route_after_detector
from graph.nodes.extractor import NODE_NAME as EXTRACTOR_NODE
from graph.nodes.extractor import extractor_node, route_after_extractor
from graph.nodes.generator import NODE_NAME as GENERATOR_NODE
from graph.nodes.generator import generator_node
from graph.state import AssistantState

load_dotenv()

builder = StateGraph(AssistantState)
builder.add_node(DETECTOR_NODE, detector_node)
builder.add_node(EXTRACTOR_NODE, extractor_node)
builder.add_node(CONFIRMATION_NODE, confirmation_node)
builder.add_node(GENERATOR_NODE, generator_node)

builder.add_edge(START, DETECTOR_NODE)
builder.add_conditional_edges(
    DETECTOR_NODE,
    route_after_detector,
    {ROUTE_EXTRACT: EXTRACTOR_NODE, ROUTE_CHAT: GENERATOR_NODE},
)
builder.add_conditional_edges(
    EXTRACTOR_NODE,
    route_after_extractor,
    {"confirmation": CONFIRMATION_NODE, "generator": GENERATOR_NODE},
)
builder.add_edge(CONFIRMATION_NODE, GENERATOR_NODE)
builder.add_edge(GENERATOR_NODE, END)

graph = builder.compile()

# Sample doctor context for console testing — stands in for whatever will
# eventually populate `configurable` from the real request/session.
DOCTOR_CONFIG = {
    "configurable": {
        "id": "doc-1",
        "name": "Dr. Saran",
        "age": 23,
        "sex": "male",
        "tone": "funny",
        "rush": False,
        "assistant_name": "grok",
    }
}

def main():
    print("WardLog console — type 'exit' to quit.")
    messages = []

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            break

        messages.append(HumanMessage(content=user_input))
        result = graph.invoke({"messages": messages}, config=DOCTOR_CONFIG)
        messages = result["messages"]

        print(f"Assistant: {messages[-1].content}")
        print(end = "\n")


if __name__ == "__main__":
    main()
