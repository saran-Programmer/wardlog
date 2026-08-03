from datetime import date
from typing import Annotated, Optional

from pydantic import BaseModel, Field


class ReportExtraction(BaseModel):

    is_processable: Annotated[
        bool,
        Field(
            description=(
                "whether this is a readable MEDICAL document (report, prescription, "
                "lab result, imaging report, discharge summary). False for anything "
                "unreadable (too blurry, cropped beyond use) AND for anything that is "
                "not a medical document at all (e.g. a movie ticket, a random photo)."
            )
        ),
    ]

    rejection_reason: Annotated[
        Optional[str],
        Field(
            default=None,
            description=(
                "when is_processable is false, a short plain reason, e.g. 'the image "
                "is too blurry to read' or 'this is not a medical document'. Null "
                "otherwise."
            ),
        ),
    ]

    patient_name: Annotated[
        Optional[str],
        Field(
            default=None,
            description=(
                "the patient this report belongs to. PRIORITY: take it from the "
                "DOCUMENT if the name is printed there; otherwise take it from the "
                "doctor's message; otherwise leave null. Capture the full name "
                "exactly as given — do not truncate to the first name only. If "
                "only a first name is given, use just that. If a first and last "
                "name are both given, include both. If a first name plus an "
                'initial is given (e.g. "Uma R"), include the initial as given.'
            ),
        ),
    ]

    report_type: Annotated[
        Optional[str],
        Field(
            default=None,
            description=(
                "what kind of report this is, free text, as specific as the document "
                "allows, e.g. 'blood test', 'urine culture', 'MRI left knee', "
                "'discharge summary'."
            ),
        ),
    ]

    report_date: Annotated[
        Optional[date],
        Field(
            default=None,
            description=(
                "the date the report was issued, as stated on the document — NOT "
                "today's date. Null if not stated."
            ),
        ),
    ]

    findings: Annotated[
        Optional[str],
        Field(
            default=None,
            description="the clinical findings/conclusion of the report.",
        ),
    ]

    full_text: Annotated[
        Optional[str],
        Field(
            default=None,
            description="the complete text content extracted from the document.",
        ),
    ]

    doctor_notes: Annotated[
        Optional[str],
        Field(
            default=None,
            description=(
                "the doctor's own commentary from their message, e.g. \"her "
                "hemoglobin is low, started her on iron\". Null if they wrote "
                "nothing meaningful."
            ),
        ),
    ]
