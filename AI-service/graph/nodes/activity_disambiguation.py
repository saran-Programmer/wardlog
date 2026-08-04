from langchain_core.messages import HumanMessage

from langgraph.types import interrupt

from ..constants import CHOICE_QUERY, MAX_DISAMBIGUATION_CANDIDATES
from ..state import AssistantState


def resolve_candidates(state: AssistantState, node_name: str) -> dict:
    candidates = state["activity_candidates"]
    n = len(candidates)

    if n == 0:
        return {
            "activity_candidates": [],
            "return_to": None,
            "followup_messages": [
                "I couldn't find an activity matching that reference — "
                "could you give me a different date or description?"
            ],
        }

    if n == 1:
        return {"resolved_activity_id": candidates[0].id, "return_to": None}

    if n <= MAX_DISAMBIGUATION_CANDIDATES:
        payload = {
            "options": [
                {
                    "index": i,
                    "id": activity.id,
                    "type": activity.name,
                    "start": activity.start.isoformat() if activity.start else None,
                    "end": activity.end.isoformat() if activity.end else None,
                    "location": activity.location,
                    "notes": activity.notes,
                }
                for i, activity in enumerate(candidates)
            ],
            "allow_query": True,
        }
        resumed = interrupt(payload)

        if resumed.get("choice") == CHOICE_QUERY:
            return {
                "activity_candidates": [],
                "return_to": node_name,
                "messages": [HumanMessage(content=resumed["text"])],
            }

        return {"resolved_activity_id": resumed["choice"], "return_to": None}

    description = "; ".join(
        f"[{i}] {activity.name} on "
        f"{activity.start.date() if activity.start else 'an unknown date'}"
        for i, activity in enumerate(candidates)
    )
    return {
        "activity_candidates": [],
        "return_to": None,
        "followup_messages": [
            f"I found too many matching activities ({description}) — "
            "can you narrow it down further?"
        ],
    }
