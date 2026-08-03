from ..config import DoctorContext

from .base_prompt import BasePrompt


class ConsultationExtractorPrompt(BasePrompt):
    BASE_PROMPT = (
        "You extract structured patient information from a conversation between "
        "an assistant and a doctor. The doctor is describing a specific patient "
        "they saw or treated. Extract the patient's details and what was "
        "recorded about the encounter."
    )

    PATIENT_FIELDS = (
        "Patient (required): the patient's name (required), and their age and "
        "sex if stated. Capture the full name exactly as given — do not "
        "truncate to the first name only:\n"
        "- If only a first name is given, use just that first name.\n"
        "- If a first and last name are both given, include both.\n"
        "- If a first name plus an initial is given (e.g. \"Uma R\"), include "
        "the initial as given.\n"
        "Give the bare name only — strip honorifics/titles such "
        'as Mr., Mrs., Ms., Miss, Master, Dr., or Prof. (e.g. "Saran G", not '
        '"Mr. Saran G").\n'
        "- diagnoses: the condition(s) the patient was diagnosed with, as a "
        "list of short names.\n"
        "- drugs: any medication given or prescribed, as a list of names "
        "(optional).\n"
        "- surgery_type: the type of surgery performed, if this was a surgical "
        "case."
    )

    CONDITIONAL_RULE = (
        "Guidance on diagnoses vs surgery_type:\n"
        "- If the encounter was a SURGERY, provide surgery_type (the procedure "
        "performed). diagnoses may be empty in that case.\n"
        "- If the encounter was NOT a surgery, provide the diagnoses. "
        "surgery_type should be null.\n"
        "Extract whichever the doctor actually stated; do not invent either."
    )

    EXTRACTION_RULE = (
        "Only extract what the doctor actually said. Do not guess or invent a "
        "name, age, sex, diagnosis, drug, or surgery type that was not stated. "
        "The patient's name is required — if no patient is clearly identified, "
        "still extract what was said but leave unknown fields null."
    )

    def _content(self, doctor: DoctorContext) -> list[str]:
        return [
            self.BASE_PROMPT,
            self.PATIENT_FIELDS,
            self.CONDITIONAL_RULE,
            self.EXTRACTION_RULE,
        ]
