from datetime import datetime
from uuid import uuid4

from langchain_core.runnables import RunnableConfig
from langgraph.types import interrupt

from db.activity_fetcher import find_overlapping_activities
from db.activity_saver import write_logged_activity

from ..config import DoctorContext
from ..models.activity import Activity
from ..models.blocked_activity import BlockedActivity
from ..state import AssistantState

NODE_NAME = "confirmation"


def confirmation_node(state: AssistantState, config: RunnableConfig):
    activities = state["activities"]
    if not activities:
        return {}

    doctor = DoctorContext(
        **{
            k: v
            for k, v in config["configurable"].items()
            if k in DoctorContext.model_fields
        }
    )

    payload = [
        {
            "index": i,
            "type": activity.name,
            "start": activity.start.isoformat() if activity.start else None,
            "end": activity.end.isoformat() if activity.end else None,
            "location": activity.location,
            "notes": activity.notes,
        }
        for i, activity in enumerate(activities)
    ]

    resumed = interrupt(payload)

    published: list[Activity] = []
    rejected: list[Activity] = []
    blocked: list[BlockedActivity] = []

    for decision in resumed["decisions"]:
        activity = activities[decision["index"]]
        outcome = decision["decision"]

        if outcome == "reject":
            rejected.append(activity)
            continue

        if outcome == "edit":
            activity = activity.model_copy()
            fields = decision.get("fields") or {}

            if "type" in fields:
                activity.name = fields["type"]
            if "start" in fields:
                activity.start = datetime.fromisoformat(fields["start"])
            if "end" in fields:
                activity.end = datetime.fromisoformat(fields["end"])
            if "location" in fields:
                activity.location = fields["location"]
            if "notes" in fields:
                activity.notes = fields["notes"]

        if activity.start is not None and activity.end is not None and activity.end <= activity.start:
            blocked.append(BlockedActivity(activity=activity, reason="zero_duration"))
            continue

        conflicts = find_overlapping_activities(doctor.id, activity.start, activity.end)
        if conflicts:
            blocked.append(BlockedActivity(activity=activity, reason="overlap", conflicts=conflicts))
            continue

        activity.id = str(uuid4())
        write_logged_activity(doctor, activity)
        published.append(activity)

        ## Here after writing to the Graph DB need to publish to kafka

    return {
        "published_activities": published,
        "rejected_activities": rejected,
        "blocked_activities": blocked,
    }
