from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import func, select
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
