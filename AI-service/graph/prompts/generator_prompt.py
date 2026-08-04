from datetime import datetime

from ..config import DoctorContext
from ..models.activity import Activity
from ..models.consultation import Consultation
from ..models.report_extraction import ReportExtraction
from ..state import AssistantState
from .base_prompt import BasePrompt


ACTIVITY_LABELS = {
    "surgeryblock": "surgery block",
    "clinicblock": "clinic block",
    "oncall": "on-call",
    "onsiteoncall": "on-site on-call",
}


def _format_time(dt: datetime) -> str:
    return dt.strftime("%I:%M %p").lstrip("0")


def _format_day(dt: datetime) -> str:
    return dt.strftime("%A, %Y-%m-%d")


def describe_activity(activity: Activity) -> str:
    label = ACTIVITY_LABELS.get(activity.name, activity.name or "activity")
    start, end = activity.start, activity.end
    if start and end:
        if start.date() == end.date():
            when = f"on {_format_day(start)}, {_format_time(start)} to {_format_time(end)}"
        else:
            when = (
                f"from {_format_day(start)} {_format_time(start)} "
                f"to {_format_day(end)} {_format_time(end)}"
            )
    elif start:
        when = f"starting {_format_day(start)}, {_format_time(start)}"
    elif end:
        when = f"ending {_format_day(end)}, {_format_time(end)}"
    else:
        when = "with no time recorded"

    description = f"{label} {when}"
    if activity.location:
        description += f", at {activity.location}"
    if activity.notes:
        description += f" (notes: {activity.notes})"
    return description


def _activity_lines(activities: list[Activity]) -> str:
    return "\n".join(f"- {describe_activity(activity)}" for activity in activities)


def describe_report(report: ReportExtraction) -> str:
    """Render a saved report factually, so the reply names what was written."""
    lines = []

    if report.patient_name:
        lines.append(f"Patient: {report.patient_name}")
    if report.report_type:
        lines.append(f"Report type: {report.report_type}")
    if report.report_date:
        lines.append(f"Date: {report.report_date.isoformat()}")
    if report.findings:
        lines.append(f"Findings: {report.findings}")

    return "\n".join(f"- {line}" for line in lines)


def describe_consultation(consultation: Consultation) -> str:
    """Render a saved consultation factually, so the reply names what was written."""
    lines = []

    patient = consultation.patient
    if patient is not None and patient.name:
        who = patient.name
        details = []
        if patient.age is not None:
            details.append(f"{patient.age}")
        if patient.sex:
            details.append(patient.sex)
        if details:
            who += f" ({', '.join(details)})"
        lines.append(f"Patient: {who}")

    if consultation.diagnoses:
        lines.append("Diagnoses: " + ", ".join(consultation.diagnoses))

    if consultation.drugs:
        lines.append("Drugs: " + ", ".join(consultation.drugs))

    if consultation.surgery_type:
        lines.append(f"Surgery type: {consultation.surgery_type}")

    return "\n".join(f"- {line}" for line in lines)


class GeneratorPrompt(BasePrompt):
    ROLE = (
        "You are a personal assistant. You are speaking directly with the doctor "
        "you assist — they are the user in this conversation, and you address "
        'them directly as "you."\n\n'
        "Your role right now is to have a pleasant, natural conversation with the "
        "doctor. Be attentive, easy to talk to, and personable."
    )

    GUIDELINES = (
        "Guidelines:\n"
        "- Speak to the doctor directly and naturally.\n"
        "- Keep responses conversational and concise.\n"
        "- You are not a medical advisor; don't give clinical or treatment advice."
    )

    TONE_FRAGMENTS = {
        "warm": "Tone: warm and friendly. Speak with genuine warmth, like a supportive colleague.",
        "funny": "Tone: light and funny. Sprinkle in light humor during casual conversation, but drop it and stay clear and serious for anything that needs to be precise.",
        "professional": "Tone: professional. Be brisk, neutral, and businesslike. No humor.",
    }

    # Rush compresses only — it does NOT drop humor.
    RUSH_FRAGMENT = (
        "The doctor is in a rush right now. Maintain your current tone, just "
        "compressed: be as brief as possible and skip pleasantries and small talk."
    )

    FOLLOWUP_FRAGMENT_TEMPLATE = (
        "Missing information:\n"
        "While looking at what the doctor just told you, the following details "
        "could not be pinned down:\n"
        "{items}\n\n"
        "Naturally weave a request for this information into your reply, as part "
        'of normal conversation — for example "Nice, when did you wrap up?" '
        "rather than anything that sounds like a form or validation error (never "
        'say things like "ERROR", "required", or "field"). Ask about all of the '
        "missing items, but keep it conversational and in keeping with your tone "
        "and rush settings above."
    )

    CONFIRMED_ACTION_OVERRIDE = (
        "Confirmed system action — narrow exception to the grounding rules:\n"
        "The activities listed below were just written to the doctor's record by "
        "this system, during this exchange, after the doctor confirmed them. This "
        "is not external data you are guessing at; it is an action that genuinely "
        "completed.\n"
        "- Do NOT deny that the logging happened, and do NOT say you have no "
        "access to it or cannot log activities. You just did.\n"
        "- Speak about it in the past tense, as something that is done.\n"
        "- This exception covers ONLY the specific activities listed below. For "
        "anything else — the doctor's wider schedule, other appointments, patient "
        "records, past entries you were not just given — the grounding rules above "
        "still apply in full, and you must still say you don't have that "
        "information rather than invent it."
    )

    PUBLISHED_FRAGMENT_TEMPLATE = (
        "Just logged:\n"
        "{items}\n\n"
        "Confirm this to the doctor in your reply. Name what was logged "
        "specifically — the activity type and its times, as given above — rather "
        'than saying something vague like "that\'s been recorded." Then, in the '
        "same reply, invite them to tell you more about the session: how it went, "
        "what happened, which patients they saw — so their record can be updated "
        "with the detail. Phrase the invitation naturally and in keeping with your "
        "tone above; it is ordinary conversation, not a form to fill in."
    )

    PUBLISHED_RUSH_FRAGMENT_TEMPLATE = (
        "Just logged:\n"
        "{items}\n\n"
        "The doctor is in a rush. Give ONLY a terse confirmation that this was "
        'logged — a few words is enough (e.g. "Logged."). Do NOT invite them to '
        "share more, do NOT ask any follow-up questions, and do NOT add anything "
        "else."
    )

    CONSULTATION_SAVED_FRAGMENT_TEMPLATE = (
        "Confirmed system action — patient record just written:\n"
        "The details below were just written to the doctor's record by this system, "
        "during this exchange. This is not external data you are guessing at; it is "
        "an action that genuinely completed.\n"
        "{items}\n\n"
        "- Do NOT deny that this was recorded, and do NOT say you have no access to "
        "patient records or cannot record patient information. You just did.\n"
        "- Speak about it in the past tense, as something that is done.\n"
        "- Confirm it to the doctor by naming what was captured specifically — the "
        "patient, and any diagnoses, drugs, or surgery type listed above — rather "
        "than saying something vague like \"that's been recorded.\"\n"
        "- This exception covers ONLY what is listed above. For anything else — the "
        "patient's wider history, other records, past entries you were not just "
        "given — the grounding rules still apply in full.\n"
        "- You are not a medical advisor; do not give clinical or treatment advice "
        "about what was recorded."
    )

    DOCUMENT_REJECTED_FRAGMENT_TEMPLATE = (
        "Document could not be processed:\n"
        "The doctor just supplied a document, but it could not be read: {reason}\n\n"
        "Tell the doctor plainly that you couldn't process it and why, in your own "
        "words. Do not sound like an error message and do not apologise at length. "
        "It's fine to suggest they try a clearer photo or a different file."
    )

    REPORT_SAVED_FRAGMENT_TEMPLATE = (
        "Confirmed system action — report just written:\n"
        "The details below were just written to the doctor's record by this system, "
        "during this exchange. This is not external data you are guessing at; it is "
        "an action that genuinely completed.\n"
        "{items}\n\n"
        "- Do NOT deny that this was recorded, and do NOT say you have no access to "
        "reports or cannot save documents. You just did.\n"
        "- Speak about it in the past tense, as something that is done.\n"
        "- Confirm it to the doctor by naming what was captured specifically — the "
        "patient, report type, date, and key findings listed above — rather than "
        'saying something vague like "that\'s been saved."\n'
        "- This exception covers ONLY what is listed above. For anything else — the "
        "patient's wider history, other reports, past entries you were not just "
        "given — the grounding rules still apply in full.\n"
        "- You are not a medical advisor; do not give clinical or treatment advice "
        "about what was found."
    )

    PATIENT_DETAILS_FRAGMENT_TEMPLATE = (
        "Patient information retrieved from the doctor's records:\n"
        "This information came from the doctor's own records via this system, "
        "during this exchange. This is not external data you are guessing at.\n"
        "{content}\n\n"
        "Deliver this content to the doctor as your reply, in your own voice, "
        "applying your tone and rush settings above. Do NOT add facts beyond "
        "what is stated above, and do NOT contradict it. Do NOT deny having "
        "access to this information or say you can't look up patient records "
        "— you just did."
    )

    PATIENT_NOT_FOUND_FRAGMENT_TEMPLATE = (
        "Patient lookup — no result:\n"
        "{detail}\n\n"
        "Tell the doctor this plainly, in your own words, in keeping with "
        "your tone and rush settings above. Do not sound like an error "
        "message and do not apologise at length."
    )

    PATIENT_NOT_FOUND_DETAIL_TEMPLATE = (
        'There is no record for a patient named "{name}" in the doctor\'s data.'
    )

    PATIENT_NAME_MISSING_DETAIL = (
        "The doctor asked about a specific patient but did not say who — ask "
        "which patient they mean before you can look anything up."
    )

    ACTIVITY_DETAILS_FRAGMENT_TEMPLATE = (
        "Activity information retrieved from the doctor's records:\n"
        "This information came from the doctor's own records via this "
        "system, during this exchange. This is not external data you are "
        "guessing at.\n"
        "{content}\n\n"
        "Deliver this content to the doctor as your reply, in your own "
        "voice, applying your tone and rush settings above. Do NOT add "
        "facts beyond what is stated above, and do NOT contradict it. Do "
        "NOT deny having access to this information or say you can't look "
        "up activity records — you just did."
    )

    ACTIVITY_NOT_FOUND_FRAGMENT_TEMPLATE = (
        "Activity lookup — no result:\n"
        "No matching activity was found for what the doctor asked about.\n\n"
        "Tell the doctor this plainly, in your own words, in keeping with "
        "your tone and rush settings above, and invite them to give a "
        "different date or description. Do not sound like an error message "
        "and do not apologise at length."
    )

    REJECTED_FRAGMENT_TEMPLATE = (
        "Rejected by the doctor:\n"
        "{items}\n\n"
        "The doctor turned these down, so they were NOT logged. Acknowledge that "
        "in your reply, naming what was rejected specifically, and ask what the "
        "reason was or what should be changed so you can get it right. Keep it "
        "ordinary conversation in keeping with your tone and rush settings above "
        "— no apologising at length, and nothing that sounds like an error "
        "message."
    )

    def build(self, doctor: DoctorContext, state: AssistantState) -> str:
        parts = self._content(doctor, state)
        parts.append(self.doctor_info_block(doctor))
        parts.append(self.current_datetime_block())
        return "\n\n".join(parts)

    def _content(self, doctor: DoctorContext, state: AssistantState) -> list[str]:
        parts = [
            self.ROLE,
            self.GUIDELINES,
            self.GROUNDING_RULES,
            self.TONE_FRAGMENTS[doctor.tone],
        ]
        if doctor.rush:
            parts.append(self.RUSH_FRAGMENT)

        document_rejection_reason = state.get("document_rejection_reason")
        if document_rejection_reason:
            parts.append(
                self.DOCUMENT_REJECTED_FRAGMENT_TEMPLATE.format(
                    reason=document_rejection_reason
                )
            )

        report_saved = state.get("report_saved")
        if report_saved:
            parts.append(
                self.REPORT_SAVED_FRAGMENT_TEMPLATE.format(
                    items=describe_report(report_saved)
                )
            )

        consultation_saved = state.get("consultation_saved")
        if consultation_saved:
            parts.append(
                self.CONSULTATION_SAVED_FRAGMENT_TEMPLATE.format(
                    items=describe_consultation(consultation_saved)
                )
            )

        patient_generated_content = state.get("patient_generated_content")
        if patient_generated_content:
            parts.append(
                self.PATIENT_DETAILS_FRAGMENT_TEMPLATE.format(
                    content=patient_generated_content
                )
            )

        patient_not_found = state.get("patient_not_found")
        if patient_not_found is not None:
            detail = (
                self.PATIENT_NOT_FOUND_DETAIL_TEMPLATE.format(name=patient_not_found)
                if patient_not_found
                else self.PATIENT_NAME_MISSING_DETAIL
            )
            parts.append(
                self.PATIENT_NOT_FOUND_FRAGMENT_TEMPLATE.format(detail=detail)
            )

        activity_generated_content = state.get("activity_generated_content")
        if activity_generated_content:
            parts.append(
                self.ACTIVITY_DETAILS_FRAGMENT_TEMPLATE.format(
                    content=activity_generated_content
                )
            )

        activity_not_found = state.get("activity_not_found")
        if activity_not_found:
            parts.append(self.ACTIVITY_NOT_FOUND_FRAGMENT_TEMPLATE)

        followups = state.get("followup_messages") or []
        if followups:
            items = "\n".join(f"- {message}" for message in followups)
            parts.append(self.FOLLOWUP_FRAGMENT_TEMPLATE.format(items=items))

        published = state.get("published_activities") or []
        if published:
            template = (
                self.PUBLISHED_RUSH_FRAGMENT_TEMPLATE
                if doctor.rush
                else self.PUBLISHED_FRAGMENT_TEMPLATE
            )
            parts.append(self.CONFIRMED_ACTION_OVERRIDE)
            parts.append(template.format(items=_activity_lines(published)))

        rejected = state.get("rejected_activities") or []
        if rejected:
            parts.append(
                self.REJECTED_FRAGMENT_TEMPLATE.format(items=_activity_lines(rejected))
            )

        return parts
