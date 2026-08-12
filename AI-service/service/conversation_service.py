from typing import Optional
from uuid import UUID, uuid4

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.types import Command

from db.conversation_repo import (
    count_synced_messages,
    create_conversation,
    get_conversation,
    insert_activity_rows,
    insert_messages,
    resolve_activity_rows,
    set_title,
    touch_conversation,
)
from db.conversation_repo import delete_conversation as repo_delete_conversation
from db.conversation_repo import get_messages as repo_get_messages
from db.conversation_repo import list_conversations as repo_list_conversations
from graph.build_graph import graph
from graph.config import DoctorContext
from graph.constants import FILE_PATH_KEY
from graph.nodes.llm import get_llm
from graph.prompts.title_prompt import TITLE_SYSTEM_PROMPT


def start_conversation(doctor_id: str) -> UUID:
    conversation_id = uuid4()
    create_conversation(conversation_id, doctor_id)
    return conversation_id


def send_message(
    conversation_id: UUID, doctor: DoctorContext, text: str, file_path: str | None = None
) -> dict:
    config = {"configurable": {"thread_id": str(conversation_id), **doctor.model_dump()}}
    additional_kwargs = {FILE_PATH_KEY: file_path} if file_path else {}
    human_message = HumanMessage(content=text, additional_kwargs=additional_kwargs)
    result = graph.invoke({"messages": [human_message]}, config)
    return _finalize(conversation_id, result)


def resume(conversation_id: UUID, doctor: DoctorContext, decisions: list[dict]) -> dict:
    """`decisions` are id-keyed, as submitted by the frontend: [{"id", "decision", "fields"?}].
    Resolves the corresponding pending activity rows and translates them to the
    index-keyed shape the confirmation node's interrupt contract expects."""
    index_decisions = resolve_activity_rows(conversation_id, decisions)
    config = {"configurable": {"thread_id": str(conversation_id), **doctor.model_dump()}}
    result = graph.invoke(Command(resume={"decisions": index_decisions}), config)
    return _finalize(conversation_id, result)


def _generate_title(first_message: str) -> str:
    response = get_llm(temperature=0).invoke(
        [SystemMessage(content=TITLE_SYSTEM_PROMPT), HumanMessage(content=first_message)]
    )
    return response.content.strip()


def _finalize(conversation_id: UUID, result: dict) -> dict:
    all_messages = result["messages"]
    already = count_synced_messages(conversation_id)

    delta = []
    for msg in all_messages[already:]:
        if isinstance(msg, HumanMessage):
            delta.append(("human", msg.content))
        elif isinstance(msg, AIMessage):
            delta.append(("ai", msg.content))

    insert_messages(conversation_id, delta)

    if "__interrupt__" in result:
        activities = result["__interrupt__"][0].value
        rows = insert_activity_rows(conversation_id, activities)
        touch_conversation(conversation_id)
        return {
            "status": "interrupt",
            "activities": [
                {
                    "id": str(row["id"]),
                    "type": row["type"],
                    "start": row["start"],
                    "end": row["end"],
                    "location": row["location"],
                    "notes": row["notes"],
                }
                for row in rows
            ],
        }

    if get_conversation(conversation_id)["title"] is None:
        first_human = next((m for m in all_messages if isinstance(m, HumanMessage)), None)
        if first_human is not None:
            set_title(conversation_id, _generate_title(first_human.content))

    touch_conversation(conversation_id)

    last_ai_content = next((content for role, content in reversed(delta) if role == "ai"), "")
    return {
        "status": "reply",
        "reply": last_ai_content,
    }


def get_messages(conversation_id: UUID) -> list[dict]:
    return repo_get_messages(conversation_id)


def list_conversations(doctor_id: str) -> list[dict]:
    return repo_list_conversations(doctor_id)


def get_conversation_for_doctor(conversation_id: UUID, doctor_id: str) -> Optional[dict]:
    conversation = get_conversation(conversation_id)
    if conversation is None or conversation["doctor_id"] != doctor_id:
        return None
    return conversation


def rename_conversation(conversation_id: UUID, title: str) -> None:
    set_title(conversation_id, title)


def purge_conversation(conversation_id: UUID) -> None:
    graph.checkpointer.delete_thread(str(conversation_id))
    repo_delete_conversation(conversation_id)
