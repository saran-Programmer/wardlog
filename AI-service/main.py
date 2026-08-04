import re
from uuid import uuid4

from dotenv import load_dotenv

load_dotenv()

from db.connection import close_driver, verify_connection
from db.postgres import create_tables
from graph.config import DoctorContext
from graph.constants import CHOICE_QUERY
from service.conversation_service import resume, send_message, start_conversation

# Dev-only CLI input format: `file (path/to/report.pdf): message text`.
FILE_INPUT_PATTERN = re.compile(r"^file\s*\((?P<path>[^)]+)\)\s*:\s*(?P<message>.*)$")


def parse_doctor_input(raw: str) -> tuple[str | None, str]:
    """Parse the dev console's `file (path): message` input format.

    Returns (file_path, message) — file_path is None for ordinary input.
    """
    match = FILE_INPUT_PATTERN.match(raw)
    if not match:
        return None, raw

    path = match.group("path").strip()
    if len(path) >= 2 and path[0] == path[-1] and path[0] in "\"'":
        path = path[1:-1]

    return path, match.group("message").strip()


# Sample doctor context for console testing — stands in for whatever will
# eventually populate the request/session in the FastAPI layer.
DOCTOR = DoctorContext(
    id="doc-2",
    name="Dr. Purushothaman",
    age=49,
    sex="male",
    tone="warm",
    rush=False,
    assistant_name="grok",
    voice_output=True,
)


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


def prompt_for_activity_choice(payload):
    options = payload["options"]
    allow_query = payload.get("allow_query", False)

    print("\nMultiple matching activities were found:")
    for option in options:
        print(
            f"\n[{option['index']}] {option['type']} | "
            f"{option['start']} -> {option['end']} | "
            f"location={option['location']} | notes={option['notes']}"
        )

    prompt = "  pick an index"
    if allow_query:
        prompt += " (or type a question to narrow it down)"
    prompt += ": "

    choice = input(prompt).strip()

    if allow_query and not choice.isdigit():
        return {"choice": CHOICE_QUERY, "text": choice}

    selected = options[int(choice)]
    return {"choice": selected["id"]}


def render_interrupt(payload):
    if isinstance(payload, dict) and "options" in payload:
        return prompt_for_activity_choice(payload)
    return prompt_for_decisions(payload)


def main():
    print("WardLog console — type 'exit' to quit.")

    create_tables()
    verify_connection()
    try:
        conversation_id = start_conversation(DOCTOR.id)

        while True:
            user_input = input("You: ").strip()
            if user_input.lower() in {"exit", "quit"}:
                break

            file_path, doctor_message = parse_doctor_input(user_input)
            result = send_message(conversation_id, DOCTOR, doctor_message, file_path)

            while result["status"] == "interrupt":
                resume_value = render_interrupt(result["payload"])
                result = resume(conversation_id, DOCTOR, resume_value)

            print("=====================================")
            print(f"Assistant: {result['reply']}")
            if result.get("audio_path"):
                print(f"[audio: {result['audio_path']}]")
            print(end="\n")
    finally:
        close_driver()


if __name__ == "__main__":
    main()
