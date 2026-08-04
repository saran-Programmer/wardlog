from ..config import DoctorContext
from .base_prompt import BasePrompt


class PatientDetailsPrompt(BasePrompt):
    BASE_PROMPT = (
        "You answer the doctor's question about one of their patients, using "
        "ONLY the patient data provided below. This data was retrieved from "
        "the doctor's own records."
    )

    ANSWER_RULE = (
        "Answer the doctor's actual question — do not dump the patient's "
        "entire history unless they asked for a full history or overview."
    )

    GROUNDING_RULE = (
        "Ground your answer strictly in the provided data. If the data does "
        "not contain the answer to what the doctor asked, say plainly that "
        "it isn't recorded. Never invent visits, diagnoses, drugs, "
        "surgeries, or findings that are not in the data below."
    )

    STYLE_RULE = (
        "Refer to dates and activity types naturally in your answer (e.g. "
        '"a clinic block on 14 July") rather than reciting raw fields.'
    )

    ADVISOR_RULE = (
        "You are not a medical advisor; report what is recorded, do not "
        "give clinical or treatment advice."
    )

    CONCISE_RULE = (
        "Keep it factual and concise. The assistant's voice and tone are "
        "applied afterward by another step, so do not add greetings, "
        "sign-offs, or conversational filler here — just the factual answer "
        "content."
    )

    PATIENT_DATA_TEMPLATE = "Patient data:\n{data}"

    def _content(self, doctor: DoctorContext, patient_data: str) -> list[str]:
        return [
            self.BASE_PROMPT,
            self.ANSWER_RULE,
            self.GROUNDING_RULE,
            self.STYLE_RULE,
            self.ADVISOR_RULE,
            self.CONCISE_RULE,
            self.PATIENT_DATA_TEMPLATE.format(data=patient_data),
        ]

    def build(self, doctor: DoctorContext, patient_data: str) -> str:
        parts = self._content(doctor, patient_data)
        parts.append(self.assistant_name_block(doctor))
        parts.append(self.doctor_info_block(doctor))
        parts.append(self.current_datetime_block())
        return "\n\n".join(parts)
