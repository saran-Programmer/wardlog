from dotenv import load_dotenv

load_dotenv()

from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command

from db.graph_db import close_driver, verify_connection
from graph.constants import ROUTE_CHAT, ROUTE_EXTRACT
from graph.nodes.confirmation import NODE_NAME as CONFIRMATION_NODE
from graph.nodes.confirmation import confirmation_node
from graph.nodes.detector import NODE_NAME as DETECTOR_NODE
from graph.nodes.detector import detector_node, route_after_detector
from graph.nodes.activity_extractor import NODE_NAME as EXTRACTOR_NODE
from graph.nodes.activity_extractor import (
    activity_extractor_node,
    route_after_activity_extractor,
)
from graph.nodes.generator import NODE_NAME as GENERATOR_NODE
from graph.nodes.generator import generator_node
from graph.state import AssistantState

builder = StateGraph(AssistantState)
builder.add_node(DETECTOR_NODE, detector_node)
builder.add_node(EXTRACTOR_NODE, activity_extractor_node)
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
    route_after_activity_extractor,
    {"confirmation": CONFIRMATION_NODE, "generator": GENERATOR_NODE},
)
builder.add_edge(CONFIRMATION_NODE, GENERATOR_NODE)
builder.add_edge(GENERATOR_NODE, END)

# Explicitly allowlisted so checkpoint (de)serialization doesn't warn/block on
# our custom Activity model — see langgraph's LANGGRAPH_STRICT_MSGPACK gate.
CHECKPOINT_SERDE = JsonPlusSerializer(
    allowed_msgpack_modules=[("graph.models.activity", "Activity")]
)

# Sample doctor context for console testing — stands in for whatever will
# eventually populate `configurable` from the real request/session.
DOCTOR_CONFIG = {
    "configurable": {
        "id": "doc-1",
        "name": "Dr. Saran",
        "age": 23,
        "sex": "male",
        "tone": "funny",
        "rush": True,
        "assistant_name": "grok",
        "thread_id": "console-session",
    }
}

def prompt_for_decisions(payload):
    print("\nThe following activities need your confirmation:")
    decisions = []

    for item in payload:
        print(
            f"\n[{item['index']}] {item['type']} | "
            f"{item['start']} -> {item['end']} | "
            f"location={item['location']} | notes={item['notes']}"
        )
        choice = input("  accept / edit / reject? ").strip().lower()

        if choice == "reject":
            decisions.append({"index": item["index"], "decision": "reject"})
            continue

        if choice == "edit":
            fields = {}
            new_type = input("  new type (blank to keep): ").strip()
            new_start = input("  new start ISO datetime (blank to keep): ").strip()
            new_end = input("  new end ISO datetime (blank to keep): ").strip()
            new_location = input("  new location (blank to keep): ").strip()
            new_notes = input("  new notes (blank to keep): ").strip()

            if new_type:
                fields["type"] = new_type
            if new_start:
                fields["start"] = new_start
            if new_end:
                fields["end"] = new_end
            if new_location:
                fields["location"] = new_location
            if new_notes:
                fields["notes"] = new_notes

            decisions.append({"index": item["index"], "decision": "edit", "fields": fields})
            continue

        decisions.append({"index": item["index"], "decision": "accept"})

    return {"decisions": decisions}


def main():
    print("WardLog console — type 'exit' to quit.")
    messages = []

    verify_connection()
    try:
        graph = builder.compile(checkpointer=InMemorySaver(serde=CHECKPOINT_SERDE))

        while True:
            user_input = input("You: ").strip()
            if user_input.lower() in {"exit", "quit"}:
                break

            messages.append(HumanMessage(content=user_input))
            result = graph.invoke({"messages": messages}, config=DOCTOR_CONFIG)

            while "__interrupt__" in result:
                payload = result["__interrupt__"][0].value
                resume_value = prompt_for_decisions(payload)
                result = graph.invoke(Command(resume=resume_value), config=DOCTOR_CONFIG)

            messages = result["messages"]

            print(f"Assistant: {messages[-1].content}")
            print(end = "\n")
    finally:
        close_driver()


if __name__ == "__main__":
    main()
