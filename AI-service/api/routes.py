import os
import tempfile
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, Response, UploadFile
from pydantic import BaseModel

from auth.token import get_doctor_context
from graph.config import DoctorContext
from graph.nodes.llm import synthesize_speech
from service.conversation_service import (
    get_messages,
    list_conversations,
    resume,
    send_message,
    start_conversation,
)

router = APIRouter(prefix="/api/v1")


class SendMessageRequest(BaseModel):
    message: str
    rush: bool = False


class ActivityDecision(BaseModel):
    index: int
    decision: str  # "accept" | "reject" | "edit"
    fields: dict | None = None


class ResumeRequest(BaseModel):
    decisions: list[ActivityDecision]
    rush: bool = False


class SpeechRequest(BaseModel):
    text: str


def _with_request_flags(doctor: DoctorContext, rush: bool) -> DoctorContext:
    return doctor.model_copy(update={"rush": rush})


@router.post("/conversations")
def create_conversation(doctor: DoctorContext = Depends(get_doctor_context)):
    conversation_id = start_conversation(doctor.id)
    return {"conversation_id": str(conversation_id)}


@router.post("/conversations/{conversation_id}/messages")
def post_message(
    conversation_id: UUID,
    body: SendMessageRequest,
    doctor: DoctorContext = Depends(get_doctor_context),
):
    full_doctor = _with_request_flags(doctor, body.rush)
    return send_message(conversation_id, full_doctor, body.message)


@router.post("/conversations/{conversation_id}/resume")
def post_resume(
    conversation_id: UUID,
    body: ResumeRequest,
    doctor: DoctorContext = Depends(get_doctor_context),
):
    full_doctor = _with_request_flags(doctor, body.rush)
    resume_value = {
        "decisions": [d.model_dump(exclude_none=True) for d in body.decisions]
    }
    return resume(conversation_id, full_doctor, resume_value)


@router.get("/conversations/{conversation_id}/messages")
def get_conversation_messages(
    conversation_id: UUID, doctor: DoctorContext = Depends(get_doctor_context)
):
    return get_messages(conversation_id)


@router.get("/conversations")
def get_conversations(doctor: DoctorContext = Depends(get_doctor_context)):
    return list_conversations(doctor.id)


@router.post("/conversations/{conversation_id}/documents")
def post_document(
    conversation_id: UUID,
    file: UploadFile = File(...),
    message: str = Form(""),
    rush: bool = Form(False),
    doctor: DoctorContext = Depends(get_doctor_context),
):
    full_doctor = _with_request_flags(doctor, rush)

    suffix = os.path.splitext(file.filename or "")[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(file.file.read())
        temp_path = tmp.name

    return send_message(conversation_id, full_doctor, message, temp_path)


@router.post("/speech")
def create_speech(
    body: SpeechRequest, doctor: DoctorContext = Depends(get_doctor_context)
):
    try:
        audio_bytes = synthesize_speech(body.text)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Speech synthesis failed") from exc
    return Response(content=audio_bytes, media_type="audio/wav")
