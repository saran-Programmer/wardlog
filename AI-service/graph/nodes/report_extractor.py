import base64
import os
from typing import Optional
from uuid import uuid4

import fitz
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

from db.normalize import strip_honorifics
from storage.s3 import upload_document

from ..config import DoctorContext
from ..constants import (
    FILE_PATH_KEY,
    ROUTE_DETECTOR,
    ROUTE_GENERATOR,
    ROUTE_REPORT_EXTRACTOR,
    ROUTE_REPORT_SAVER,
)
from ..models.report_extraction import ReportExtraction
from ..prompts.report_extractor_prompt import ReportExtractorPrompt
from ..state import AssistantState
from .llm import get_llm, get_vision_llm

NODE_NAME = "report_extractor"

# Dev-only local folder documents are read from — no S3 in this environment.
DOCUMENTS_DIR = os.environ.get("REPORT_DOCUMENTS_DIR", "documents")

# Groq caps multimodal requests at 5 images; we only ever need the first few
# pages of a report to extract its content.
MAX_DOCUMENT_PAGES = 3

_PDF_EXTENSIONS = {".pdf"}
_IMAGE_MIME_TYPES = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png"}


def _clean_patient_name(name: Optional[str]) -> Optional[str]:
    """Strip honorifics defensively — the prompt asks the model to omit them,
    but LLM compliance isn't guaranteed, and Patient keys must stay consistent."""
    if not name:
        return None
    return strip_honorifics(name) or None


class PatientNameExtraction(BaseModel):
    patient_name: Optional[str] = Field(
        default=None,
        description=(
            "the patient's name, if the doctor's reply names one; otherwise "
            "null. Capture the full name exactly as given — do not truncate "
            "to the first name only. If only a first name is given, use just "
            "that. If a first and last name are both given, include both. If "
            'a first name plus an initial is given (e.g. "Uma R"), include '
            "the initial as given."
        ),
    )


def _resolve_path(file_path: str) -> str:
    if os.path.isabs(file_path):
        return file_path
    return os.path.join(DOCUMENTS_DIR, file_path)


def _render_pdf_pages(path: str) -> list[bytes]:
    images = []
    with fitz.open(path) as doc:
        for page in doc[:MAX_DOCUMENT_PAGES]:
            images.append(page.get_pixmap().tobytes("png"))
    return images


def _load_document_images(file_path: str) -> list[tuple[bytes, str]]:
    resolved = _resolve_path(file_path)
    ext = os.path.splitext(resolved)[1].lower()

    if ext in _PDF_EXTENSIONS:
        return [(png_bytes, "image/png") for png_bytes in _render_pdf_pages(resolved)]

    if ext in _IMAGE_MIME_TYPES:
        with open(resolved, "rb") as f:
            return [(f.read(), _IMAGE_MIME_TYPES[ext])]

    raise ValueError(f"Unsupported document type: {ext}")


def _image_content_blocks(images: list[tuple[bytes, str]]) -> list[dict]:
    blocks = []
    for data, mime in images:
        encoded = base64.b64encode(data).decode("utf-8")
        blocks.append(
            {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{encoded}"}}
        )
    return blocks


def _extract_from_document(file_path: str, doctor_message: str, doctor: DoctorContext) -> dict:
    resolved_path = _resolve_path(file_path)
    images = _load_document_images(file_path)
    system_prompt = ReportExtractorPrompt().build(doctor)
    human_message = HumanMessage(
        content=[
            {"type": "text", "text": doctor_message or "(no message provided)"},
            *_image_content_blocks(images),
        ]
    )

    extraction = (
        get_vision_llm()
        .with_structured_output(ReportExtraction, method="json_mode")
        .invoke([SystemMessage(content=system_prompt), human_message])
    )
    extraction = extraction.model_copy(
        update={"patient_name": _clean_patient_name(extraction.patient_name)}
    )

    if not extraction.is_processable:
        os.remove(resolved_path)
        return {"document_rejection_reason": extraction.rejection_reason}

    ext = os.path.splitext(resolved_path)[1].lower()
    file_url = upload_document(resolved_path, f"reports/{uuid4()}{ext}")
    os.remove(resolved_path)

    if extraction.patient_name:
        return {"pending_report": extraction, "pending_report_file_url": file_url}

    return {
        "pending_report": extraction,
        "pending_report_file_url": file_url,
        "followup_messages": ["Which patient does this report belong to?"],
    }


def _attach_patient_name(pending: ReportExtraction, reply_text: str) -> dict:
    result = (
        get_llm()
        .with_structured_output(PatientNameExtraction)
        .invoke(
            [
                SystemMessage(
                    content=(
                        "Extract the patient's name from the doctor's reply, if one "
                        "is given. Leave it null if no name is stated. Capture the "
                        "full name exactly as given — do not truncate to the first "
                        "name only. If only a first name is given, use just that. "
                        "If a first and last name are both given, include both. If "
                        'a first name plus an initial is given (e.g. "Uma R"), '
                        "include the initial as given."
                    )
                ),
                HumanMessage(content=reply_text),
            ]
        )
    )

    patient_name = _clean_patient_name(result.patient_name)
    if not patient_name:
        return {
            "pending_report": pending,
            "followup_messages": ["Sorry, which patient does this report belong to?"],
        }

    updated = pending.model_copy(update={"patient_name": patient_name})
    return {"pending_report": updated}


def report_extractor_node(state: AssistantState, config: RunnableConfig):
    doctor = DoctorContext(
        **{
            k: v
            for k, v in config["configurable"].items()
            if k in DoctorContext.model_fields
        }
    )

    messages = state["messages"]
    last = messages[-1] if messages else None
    file_path = (
        last.additional_kwargs.get(FILE_PATH_KEY)
        if isinstance(last, HumanMessage)
        else None
    )

    if file_path:
        return _extract_from_document(file_path, last.content, doctor)

    pending = state["pending_report"]
    return _attach_patient_name(pending, last.content)


def route_entry(state: AssistantState) -> str:
    if state.get("pending_report") is not None:
        return ROUTE_REPORT_EXTRACTOR

    messages = state["messages"]
    last = messages[-1] if messages else None
    if isinstance(last, HumanMessage) and last.additional_kwargs.get(FILE_PATH_KEY):
        return ROUTE_REPORT_EXTRACTOR

    return ROUTE_DETECTOR


def route_after_report_extractor(state: AssistantState) -> str:
    if state.get("document_rejection_reason"):
        return ROUTE_GENERATOR

    pending = state.get("pending_report")
    if pending is not None and pending.patient_name:
        return ROUTE_REPORT_SAVER

    return ROUTE_GENERATOR
