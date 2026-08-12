import json
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from .postgres import Conversation, Message, engine


def _conversation_to_dict(row: Conversation) -> dict:
    return {
        "id": row.id,
        "doctor_id": row.doctor_id,
        "title": row.title,
        "created_at": row.created_at,
        "updated_at": row.updated_at,
    }


def _message_to_dict(row: Message) -> dict:
    return {
        "id": row.id,
        "conversation_id": row.conversation_id,
        "sequence_number": row.sequence_number,
        "role": row.role,
        "content": row.content,
        "created_at": row.created_at,
        "event_status": row.event_status,
    }


def create_conversation(conversation_id: UUID, doctor_id: str) -> None:
    now = datetime.now(timezone.utc)
    with Session(engine) as session:
        session.add(
            Conversation(
                id=conversation_id,
                doctor_id=doctor_id,
                title=None,
                created_at=now,
                updated_at=now,
            )
        )
        session.commit()


def get_conversation(conversation_id: UUID) -> Optional[dict]:
    with Session(engine) as session:
        row = session.get(Conversation, conversation_id)
        return _conversation_to_dict(row) if row else None


def set_title(conversation_id: UUID, title: str) -> None:
    with Session(engine) as session:
        row = session.get(Conversation, conversation_id)
        row.title = title
        session.commit()


def touch_conversation(conversation_id: UUID) -> None:
    with Session(engine) as session:
        row = session.get(Conversation, conversation_id)
        row.updated_at = datetime.now(timezone.utc)
        session.commit()


def _max_sequence(session: Session, conversation_id: UUID) -> int:
    return (
        session.execute(
            select(func.max(Message.sequence_number)).where(
                Message.conversation_id == conversation_id
            )
        ).scalar()
        or 0
    )


def get_max_sequence(conversation_id: UUID) -> int:
    with Session(engine) as session:
        return _max_sequence(session, conversation_id)


def count_synced_messages(conversation_id: UUID) -> int:
    """Count of persisted human/ai rows (event_status IS NULL) — mirrors how many
    entries of the LangGraph `messages` state have already been written to Postgres.
    Activity rows are excluded since they don't correspond to LangChain messages."""
    with Session(engine) as session:
        return (
            session.execute(
                select(func.count(Message.id)).where(
                    Message.conversation_id == conversation_id,
                    Message.event_status.is_(None),
                )
            ).scalar()
            or 0
        )


def insert_messages(conversation_id: UUID, messages: list[tuple[str, str]]) -> None:
    if not messages:
        return

    now = datetime.now(timezone.utc)
    with Session(engine) as session:
        start = _max_sequence(session, conversation_id) + 1
        session.add_all(
            [
                Message(
                    id=uuid4(),
                    conversation_id=conversation_id,
                    sequence_number=start + offset,
                    role=role,
                    content=content,
                    created_at=now,
                )
                for offset, (role, content) in enumerate(messages)
            ]
        )
        session.commit()


def get_messages(conversation_id: UUID) -> list[dict]:
    with Session(engine) as session:
        rows = (
            session.execute(
                select(Message)
                .where(Message.conversation_id == conversation_id)
                .order_by(Message.sequence_number)
            )
            .scalars()
            .all()
        )
    return [_message_to_dict(row) for row in rows]


def insert_activity_rows(conversation_id: UUID, activities: list[dict]) -> list[dict]:
    """Insert one pending row per proposed activity. Each activity dict (as produced by
    the confirmation node) must carry its own `index` — that's stored in `content` and is
    the bridge back to the index-keyed decisions the graph expects on resume.
    Returns each row's id merged with its activity fields."""
    if not activities:
        return []

    now = datetime.now(timezone.utc)
    rows = []
    with Session(engine) as session:
        start = _max_sequence(session, conversation_id) + 1
        for offset, activity in enumerate(activities):
            row_id = uuid4()
            session.add(
                Message(
                    id=row_id,
                    conversation_id=conversation_id,
                    sequence_number=start + offset,
                    role="assistant",
                    event_status="pending",
                    content=json.dumps(activity),
                    created_at=now,
                )
            )
            rows.append({"id": row_id, **activity})
        session.commit()
    return rows


def resolve_activity_rows(conversation_id: UUID, decisions: list[dict]) -> list[dict]:
    """Resolve a batch of pending activity rows by id: `decisions` is
    [{"id": UUID, "decision": "accept"|"reject"|"edit", "fields"?: dict}].

    Updates each row's event_status (and content, for edits), then returns the
    equivalent index-keyed decisions the confirmation node's contract expects:
    [{"index": int, "decision": ..., "fields"?: ...}].

    Raises ValueError if any id doesn't belong to this conversation or isn't pending.
    """
    with Session(engine) as session:
        ids = [decision["id"] for decision in decisions]
        rows = (
            session.execute(
                select(Message).where(
                    Message.conversation_id == conversation_id,
                    Message.id.in_(ids),
                )
            )
            .scalars()
            .all()
        )
        rows_by_id = {row.id: row for row in rows}

        index_decisions = []
        for decision in decisions:
            row = rows_by_id.get(decision["id"])
            if row is None or row.event_status != "pending":
                raise ValueError(
                    f"Activity {decision['id']} is not a pending activity in this conversation"
                )

            activity = json.loads(row.content)
            outcome = decision["decision"]

            if outcome == "reject":
                row.event_status = "rejected"
            else:
                row.event_status = "accepted"
                fields = decision.get("fields") or {}
                if outcome == "edit" and fields:
                    activity.update(fields)
                    row.content = json.dumps(activity)

            index_decision = {"index": activity["index"], "decision": outcome}
            if outcome == "edit" and decision.get("fields"):
                index_decision["fields"] = decision["fields"]
            index_decisions.append(index_decision)

        session.commit()

    return index_decisions


def delete_conversation(conversation_id: UUID) -> None:
    with Session(engine) as session, session.begin():
        session.execute(delete(Message).where(Message.conversation_id == conversation_id))
        session.execute(delete(Conversation).where(Conversation.id == conversation_id))


def list_conversations(doctor_id: str) -> list[dict]:
    with Session(engine) as session:
        rows = (
            session.execute(
                select(Conversation)
                .where(Conversation.doctor_id == doctor_id)
                .order_by(Conversation.updated_at.desc())
            )
            .scalars()
            .all()
        )
    return [_conversation_to_dict(row) for row in rows]
