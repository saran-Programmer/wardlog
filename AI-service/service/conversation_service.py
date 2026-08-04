from uuid import UUID, uuid4

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.types import Command

from db.conversation_repo import (
    create_conversation,
    get_conversation,
    get_max_sequence,
    insert_messages,
    set_title,
    touch_conversation,
)
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


def resume(conversation_id: UUID, doctor: DoctorContext, resume_value: dict) -> dict:
    config = {"configurable": {"thread_id": str(conversation_id), **doctor.model_dump()}}
    result = graph.invoke(Command(resume=resume_value), config)
    return _finalize(conversation_id, result)


def _generate_title(first_message: str) -> str:
    response = get_llm(temperature=0).invoke(
        [SystemMessage(content=TITLE_SYSTEM_PROMPT), HumanMessage(content=first_message)]
    )
    return response.content.strip()


def _finalize(conversation_id: UUID, result: dict) -> dict:
    if "__interrupt__" in result:
        return {"status": "interrupt", "payload": result["__interrupt__"][0].value}

    all_messages = result["messages"]
    already = get_max_sequence(conversation_id)

    delta = []
    for msg in all_messages[already:]:
        if isinstance(msg, HumanMessage):
            delta.append(("human", msg.content))
        elif isinstance(msg, AIMessage):
            delta.append(("ai", msg.content))

    insert_messages(conversation_id, delta)

    if get_conversation(conversation_id)["title"] is None:
        first_human = next((m for m in all_messages if isinstance(m, HumanMessage)), None)
        if first_human is not None:
            set_title(conversation_id, _generate_title(first_human.content))

    touch_conversation(conversation_id)

    last_ai_content = next((content for role, content in reversed(delta) if role == "ai"), "")
    return {"status": "reply", "reply": last_ai_content}


def get_messages(conversation_id: UUID) -> list[dict]:
    return repo_get_messages(conversation_id)


def list_conversations(doctor_id: str) -> list[dict]:
    return repo_list_conversations(doctor_id)
