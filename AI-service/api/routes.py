import os
import tempfile
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, Response, UploadFile
from pydantic import BaseModel

from auth.token import get_doctor_context
from graph.config import DoctorContext
from graph.nodes.llm import synthesize_speech, transcribe_audio
from service.conversation_service import (
    get_conversation_for_doctor,
    get_messages,
    list_conversations,
    purge_conversation,
    rename_conversation,
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


class RenameConversationRequest(BaseModel):
    title: str


def _with_request_flags(doctor: DoctorContext, rush: bool) -> DoctorContext:
    return doctor.model_copy(update={"rush": rush})


def _require_owned_conversation(conversation_id: UUID, doctor: DoctorContext) -> dict:
    conversation = get_conversation_for_doctor(conversation_id, doctor.id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


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


@router.put("/conversations/{conversation_id}")
def put_conversation(
    conversation_id: UUID,
    body: RenameConversationRequest,
    doctor: DoctorContext = Depends(get_doctor_context),
):
    _require_owned_conversation(conversation_id, doctor)
    rename_conversation(conversation_id, body.title)
    return {"conversation_id": str(conversation_id), "title": body.title}


@router.delete("/conversations/{conversation_id}", status_code=204)
def delete_conversation(
    conversation_id: UUID, doctor: DoctorContext = Depends(get_doctor_context)
):
    _require_owned_conversation(conversation_id, doctor)
    purge_conversation(conversation_id)
    return Response(status_code=204)


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


@router.post("/conversations/{conversation_id}/voice-message")
def post_voice_message(
    conversation_id: UUID,
    audio: UploadFile = File(...),
    rush: bool = Form(False),
    doctor: DoctorContext = Depends(get_doctor_context),
):
    full_doctor = _with_request_flags(doctor, rush)

    audio_bytes = audio.file.read()
    if not audio_bytes:
        raise HTTPException(status_code=422, detail="Audio file is empty")

    try:
        text = transcribe_audio(audio_bytes, audio.filename or "recording.webm")
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Transcription failed") from exc

    print(text)

    if not text:
        raise HTTPException(status_code=422, detail="Could not transcribe any speech from the audio")

    return send_message(conversation_id, full_doctor, text)


@router.post("/conversations/speech")
def create_speech(
    body: SpeechRequest, doctor: DoctorContext = Depends(get_doctor_context)
):
    try:
        audio_bytes = synthesize_speech(body.text)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Speech synthesis failed") from exc
    return Response(content=audio_bytes, media_type="audio/wav")
