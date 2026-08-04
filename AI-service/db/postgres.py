import os
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Integer, Text, create_engine
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

engine = create_engine(os.environ["AI_DB_URL"])


class Base(DeclarativeBase):
    pass


class Conversation(Base):
    __tablename__ = "conversation"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True)
    doctor_id: Mapped[str] = mapped_column(Text, nullable=False)
    title: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class Message(Base):
    __tablename__ = "message"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True)
    conversation_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("conversation.id"), nullable=False
    )
    sequence_number: Mapped[int] = mapped_column(Integer, nullable=False)
    role: Mapped[str] = mapped_column(Text, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)


def create_tables() -> None:
    Base.metadata.create_all(engine)
