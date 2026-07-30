from datetime import datetime

from ..config import DoctorContext


class BasePrompt:
    """Holds instruction fragments and context blocks shared across node prompts."""

    GROUNDING_RULES = (
        "Grounding rules — this is critical:\n"
        "- You can ONLY use information explicitly provided to you in this "
        "conversation or in the doctor's information above.\n"
        "- You do NOT have access to the doctor's appointments, schedule, patient "
        "records, timesheets, or any external data unless it has been explicitly "
        "given to you here.\n"
        "- If the doctor asks about something you have not been given data for, "
        "do NOT make up an answer. Never invent appointments, patients, times, "
        "or events.\n"
        "- Instead, say clearly that you don't have that information yet. For "
        'example: "I don\'t have your appointment data available right now — I '
        'can only work with what\'s been shared with me in our conversation."\n'
        "- It is always better to admit you don't know than to guess."
    )

    CURRENT_DATETIME_TEMPLATE = (
        "Current date and time: {dt}. Use this to resolve relative dates and "
        'times mentioned in the conversation (e.g. "today", "tomorrow", "next '
        'Monday").'
    )

    def current_datetime_block(self) -> str:
        # Computed fresh at build time — never stored in config or state.
        return self.CURRENT_DATETIME_TEMPLATE.format(
            dt=datetime.now().strftime("%A, %Y-%m-%d %H:%M")
        )

    def doctor_info_block(self, doctor: DoctorContext) -> str:
        lines = [
            f"Doctor ID: {doctor.id}",
            f"Name: {doctor.name}",
            f"Age: {doctor.age}",
        ]
        if doctor.sex:
            lines.append(f"Sex: {doctor.sex}")
        return "Doctor's information:\n" + "\n".join(lines)

    def build(self, doctor: DoctorContext) -> str:
        parts = self._content(doctor)
        parts.append(self.doctor_info_block(doctor))
        parts.append(self.current_datetime_block())
        return "\n\n".join(parts)

    def _content(self, doctor: DoctorContext) -> list[str]:
        raise NotImplementedError
