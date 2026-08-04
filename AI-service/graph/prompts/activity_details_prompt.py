from ..config import DoctorContext
from .base_prompt import BasePrompt


class ActivityDetailsPrompt(BasePrompt):
    BASE_PROMPT = (
        "You answer the doctor's question about one of their logged "
        "activities, using ONLY the data provided below, which was retrieved "
        "from their own records."
    )

    SUMMARY_RULE = (
        "Give a HIGH-LEVEL summary of the session: what the activity was and "
        "when, then the patients seen, each with their diagnoses and anything "
        'prescribed. Frame it as "these are the patients you saw" — a '
        "summary of the session, not an exhaustive per-patient dossier."
    )

    ANSWER_RULE = (
        "Answer the doctor's actual question; do not dump everything if they "
        "asked something narrow."
    )

    GROUNDING_RULE = (
        "Ground strictly in the provided data. If something isn't recorded, "
        "say so plainly. Never invent patients, diagnoses, drugs, or times."
    )

    STYLE_RULE = (
        "Refer to dates and activity types naturally (e.g. \"your clinic "
        'block on 14 July").'
    )

    ADVISOR_RULE = (
        "You are not a medical advisor; report what is recorded, do not "
        "advise."
    )

    CONCISE_RULE = (
        "Keep it factual and concise — voice/tone is applied later, so no "
        "greetings or sign-offs."
    )

    ACTIVITY_DATA_TEMPLATE = "Activity data:\n{data}"

    def _content(self, doctor: DoctorContext, activity_data: str) -> list[str]:
        return [
            self.BASE_PROMPT,
            self.SUMMARY_RULE,
            self.ANSWER_RULE,
            self.GROUNDING_RULE,
            self.STYLE_RULE,
            self.ADVISOR_RULE,
            self.CONCISE_RULE,
            self.ACTIVITY_DATA_TEMPLATE.format(data=activity_data),
        ]

    def build(self, doctor: DoctorContext, activity_data: str) -> str:
        parts = self._content(doctor, activity_data)
        parts.append(self.assistant_name_block(doctor))
        parts.append(self.doctor_info_block(doctor))
        parts.append(self.current_datetime_block())
        return "\n\n".join(parts)
