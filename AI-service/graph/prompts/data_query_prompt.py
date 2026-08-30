from ..config import DoctorContext
from .base_prompt import BasePrompt


class DataQueryPrompt(BasePrompt):
    BASE_PROMPT = (
        "You look up the doctor's logged ACTIVITIES (surgery blocks, clinic "
        "blocks, on-call shifts, on-site on-call shifts) by calling the "
        "`query_activities_tool` tool with structured filters, and their "
        "PATIENT records by calling the `query_patients_tool` tool with "
        "optional name/age/sex filters. You have no other source of "
        "information about their activities or patients — call the "
        "appropriate tool to find out."
    )

    FILTERS_RULE = (
        "Filters are AND-ed together when more than one is given:\n"
        '- field "name" (activity type): operators eq, neq, in. Values are one '
        'of "surgeryblock", "clinicblock", "oncall", "onsiteoncall" (a list of '
        'these for "in").\n'
        '- field "start" (start datetime): operators eq, before, after, between.\n'
        '- field "end" (end datetime): operators eq, before, after, between.\n'
        "For start/end, values are ISO 8601 datetime strings (e.g. "
        '"2026-08-25T08:00:00"). "between" takes a 2-item list [from, to].\n'
        "An empty filters list returns every logged activity."
    )

    INCLUDE_RULE = (
        "Optionally pass `include`, a list of related data to fetch alongside "
        "the matched activities, drawn from: \"consultations\", \"patients\", "
        '"diagnoses", "drugs", "surgery_type". Each matched activity comes back '
        "with its consultations nested under it; \"patients\"/\"diagnoses\"/"
        '"drugs"/"surgery_type" each populate that one field on every nested '
        'consultation (e.g. include=["patients"] returns each consultation '
        "with only its patient filled in, not diagnoses/drugs/surgery_type). "
        'Use this when the doctor asks about who/what happened during an '
        'activity, e.g. "what patients did I see in Tuesday\'s clinic block" -> '
        'filter activities to that clinic block and include=["patients"]. Omit '
        "or leave empty when only the activities themselves are needed."
    )

    PATIENT_RULE = (
        "To look up the doctor's PATIENT records, call `query_patients_tool` "
        "with optional filters:\n"
        '- name: fuzzy-matched against patient names.\n'
        "- age: soft-matched, favoring patients within a few years of the "
        "given age.\n"
        '- sex: soft-matched, "male" or "female".\n'
        "All three are optional and independent — omit any filter you don't "
        "have information for. Omitting all three returns a broad set of the "
        "doctor's patients."
    )

    TOOL_USE_RULE = (
        "Use the current date/time below to resolve relative expressions like "
        '"yesterday", "this morning", or "last week" into concrete ISO datetime '
        "values or ranges. Call the tools as many times as needed, then stop "
        "calling them once you have enough information."
    )

    GRAPH_STRUCTURE = (
        "How the doctor's data is organized (so you know what can be asked "
        "and how things connect):\n"
        "- An ACTIVITY is a logged work block (surgery block, clinic block, "
        "on-call, on-site on-call) with a start and end time.\n"
        "- During an activity, the doctor has CONSULTATIONS — each "
        "consultation is one patient encounter within that activity.\n"
        "- Each consultation is linked to one PATIENT (name, age, sex).\n"
        "- A consultation may record DIAGNOSES (conditions identified), "
        "DRUGS (medications prescribed), and a SURGERY TYPE (the operation "
        "performed, for surgical encounters).\n"
        "- A PATIENT may also have REPORTS (report type, date, findings, "
        "notes).\n"
        "In short: Activity -> its Consultations -> each Consultation's "
        "Patient, Diagnoses, Drugs, and Surgery type; and Patient -> Reports. "
        "Activities are the doctor's schedule; patients and their clinical "
        "details hang off the consultations inside those activities."
    )

    def _content(self, doctor: DoctorContext) -> list[str]:
        return [
            self.BASE_PROMPT,
            self.FILTERS_RULE,
            self.INCLUDE_RULE,
            self.PATIENT_RULE,
            self.TOOL_USE_RULE,
            self.GRAPH_STRUCTURE
        ]
