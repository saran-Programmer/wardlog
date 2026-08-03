from ..config import DoctorContext

from .base_prompt import BasePrompt


class ReportExtractorPrompt(BasePrompt):
    BASE_PROMPT = (
        "You extract structured data from a medical document the doctor has "
        "supplied (a report, prescription, lab result, imaging report, or "
        "discharge summary), together with any message the doctor wrote "
        "alongside it."
    )

    REJECTION_RULE = (
        "First decide if the document is processable:\n"
        "- Set is_processable to false if the document is unreadable — too "
        "blurry, cropped beyond use, or otherwise illegible.\n"
        "- Set is_processable to false if the document is not a medical "
        "document at all (e.g. a movie ticket, a random photo, an unrelated "
        "document).\n"
        "- When is_processable is false, give a short, plain rejection_reason "
        '(e.g. "the image is too blurry to read" or "this is not a medical '
        'document"). Leave every other field null in that case.'
    )

    PATIENT_NAME_RULE = (
        "patient_name: identify whose report this is.\n"
        "PRIORITY ORDER — take the name from the DOCUMENT if it is printed "
        "there; otherwise take it from the doctor's message; otherwise leave "
        "it null. Do not guess a name that appears in neither place.\n"
        "Capture the full name exactly as given — do not truncate to the "
        "first name only:\n"
        "- If only a first name is given, use just that first name.\n"
        "- If a first and last name are both given, include both.\n"
        "- If a first name plus an initial is given (e.g. \"Uma R\"), include "
        "the initial as given.\n"
        "Give the bare name only — strip honorifics/titles such as Mr., Mrs., "
        "Ms., Miss, Master, Dr., or Prof. (e.g. print \"Saran G\", not \"Mr. "
        'Saran G").'
    )

    FIELD_RULES = (
        "Other fields:\n"
        "- report_type: as specific as the document allows, e.g. 'blood "
        "test', 'urine culture', 'MRI left knee', 'discharge summary'.\n"
        "- report_date: the date the document itself was issued, as printed "
        "on it — NEVER today's date. Null if the document does not state "
        "one.\n"
        "- findings: the clinical findings or conclusion stated in the "
        "document.\n"
        "- full_text: the complete text content you can read from the "
        "document.\n"
        "- doctor_notes: the doctor's own commentary about the case, taken "
        "from their message alongside the document — not from the document "
        "itself. Null if they wrote nothing meaningful."
    )

    EXTRACTION_RULE = (
        "Do not invent values for any field. If something is not stated or "
        "legible, leave it null."
    )

    # The vision call uses Groq's JSON mode rather than tool-calling (the
    # vision model's tool-calling responses fail Groq's strict argument
    # validation, e.g. returning is_processable as a string). JSON mode does
    # not auto-inject a schema, so the exact shape must be spelled out here.
    JSON_FORMAT_RULE = (
        "Respond with ONLY a single JSON object — no markdown, no code "
        "fences, no commentary before or after it. It must have exactly "
        "these keys:\n"
        '- "is_processable": true or false\n'
        '- "rejection_reason": a string, or null\n'
        '- "patient_name": a string, or null\n'
        '- "report_type": a string, or null\n'
        '- "report_date": a date string "YYYY-MM-DD", or null\n'
        '- "findings": a string, or null\n'
        '- "full_text": a string, or null\n'
        '- "doctor_notes": a string, or null'
    )

    def _content(self, doctor: DoctorContext) -> list[str]:
        return [
            self.BASE_PROMPT,
            self.REJECTION_RULE,
            self.PATIENT_NAME_RULE,
            self.FIELD_RULES,
            self.EXTRACTION_RULE,
            self.JSON_FORMAT_RULE,
        ]
