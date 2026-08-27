from ..config import DoctorContext
from .base_prompt import BasePrompt


class AnswerPrompt(BasePrompt):
    BASE_PROMPT = (
        "You answer the doctor's question using ONLY the data provided below, "
        "which was just retrieved from their own records (logged activities "
        "and/or patient records, as applicable)."
    )

    ANSWER_RULE = (
        "Answer the doctor's actual question directly and completely — do not "
        "dump everything if they asked something narrow."
    )

    GROUNDING_RULE = (
        "Ground your answer strictly in the provided data. If the data does "
        "not contain the answer to what the doctor asked, say so plainly "
        "rather than guessing. Never invent activities, patients, diagnoses, "
        "drugs, surgeries, or findings that are not in the data below."
    )

    STYLE_RULE = (
        "Refer to dates and activity types naturally in your answer (e.g. "
        '"a clinic block on 14 July") rather than reciting raw fields.'
    )

    CONCISE_RULE = (
        "Keep it factual. The assistant's voice and tone are applied "
        "afterward by another step, so do not add greetings, sign-offs, or "
        "conversational filler here — just the factual answer content."
    )

    DETAIL_RULE = (
        "Be thorough, not terse — do not compress the answer into one or two "
        "sentences. Walk through the retrieved data point by point: call out "
        "each relevant activity or patient individually (dates, locations, "
        "diagnoses, drugs, surgery types, visit history, findings, etc., as "
        "available) rather than summarizing everything into a single line. "
        "If several records are relevant to the question, cover each one."
    )

    LIST_FORMAT_RULE = (
        "When the answer covers more than one activity or patient, format it "
        "as a bullet list — one bullet per activity or patient. Each bullet "
        "must go into detail on that one element specifically, using "
        "whatever is available in the retrieved data (dates, locations, "
        "diagnoses, drugs, surgery types, visit history, findings, etc.) — "
        "not just a one-line label."
    )

    NO_DATA_FALLBACK = "No matching data was found."

    DATA_TEMPLATE = "Retrieved data:\n{data}"

    def _content(self, doctor: DoctorContext, data: str) -> list[str]:
        return [
            self.BASE_PROMPT,
            self.ANSWER_RULE,
            self.GROUNDING_RULE,
            self.STYLE_RULE,
            self.CONCISE_RULE,
            self.DETAIL_RULE,
            self.LIST_FORMAT_RULE,
            self.DATA_TEMPLATE.format(data=data or self.NO_DATA_FALLBACK),
        ]

    def build(self, doctor: DoctorContext, data: str) -> str:
        parts = self._content(doctor, data)
        parts.append(self.assistant_name_block(doctor))
        parts.append(self.doctor_info_block(doctor))
        parts.append(self.current_datetime_block())
        return "\n\n".join(parts)
