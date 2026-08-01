from dotenv import load_dotenv

load_dotenv()

from langchain_core.messages import HumanMessage
from langgraph.types import Command

from db.connection import close_driver, verify_connection
from graph.build_graph import build_graph
from graph.constants import IS_FOLLOWUP_MESSAGE

# Sample doctor context for console testing — stands in for whatever will
# eventually populate `configurable` from the real request/session.
DOCTOR_CONFIG = {
    "configurable": {
        "id": "doc-1",
        "name": "Dr. Saran",
        "age": 23,
        "sex": "male",
        "tone": "warm",
        "rush": False,
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
        graph = build_graph()

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

            is_followup = messages[-1].additional_kwargs.get(IS_FOLLOWUP_MESSAGE, False)
            print(f"[is_followup_message: {is_followup}]")

            print(f"Assistant: {messages[-1].content}")
            print(end = "\n")
    finally:
        close_driver()


if __name__ == "__main__":
    main()
