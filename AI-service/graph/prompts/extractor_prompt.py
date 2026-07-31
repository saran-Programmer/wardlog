from ..config import DoctorContext

from .base_prompt import BasePrompt


class ExtractorPrompt(BasePrompt):
    BASE_PROMPT = (
        "You extract structured activity data from a conversation between an "
        "assistant and a doctor.\n\n"
        "An activity requires ALL of: name (surgeryblock, clinicblock, oncall, "
        "or onsiteoncall), a start date and start time, and an end date and end "
        "time. notes and location are optional.\n\n"
        "For each activity, emit start_date, start_time, end_date, and end_time "
        "as SEPARATE fields — never a single combined datetime."
    )

    ACTIVITY_TYPES = (
        "Activity types:\n"
        '- "surgeryblock": performing surgery or operative work — procedures '
        "carried out or scheduled in theatre.\n"
        '- "clinicblock": clinical work that is NOT surgery and NOT on-call — '
        "outpatient work (OP), general consultations, seeing patients in "
        "clinic, ward rounds. This is the catch-all for hands-on clinical work "
        "that does not fit the other three types.\n"
        '- "oncall": on call but NOT physically at the hospital — reachable, '
        "may be called in, but off-site (e.g. at home).\n"
        '- "onsiteoncall": on call AND physically present at the hospital for '
        "the shift — resident/in-house call.\n\n"
        "If the doctor describes work that fits none of these four — for "
        "example administrative or non-clinical tasks such as document "
        "verification, paperwork, teaching, checking email, or meetings — do "
        "NOT extract it. Only these four types are loggable; omit anything else."
    )

    MULTIPLE_ACTIVITIES = (
        "Multiple activities:\n"
        "The doctor may describe SEVERAL distinct activities in a single "
        "message. Each one must become its own separate entry in the "
        "activities list. Consecutive or back-to-back activities must NOT be "
        "merged into one — for example, a surgery block followed immediately "
        "by an on-call shift is two entries, not one.\n"
        "However, if the doctor gives only a COUNT of activities without "
        'distinct details for each (e.g. "I did 4 clinic blocks" with no '
        "individual times), you do NOT know each one's times — return a "
        "SINGLE activity of that type with null start and null end, NOT "
        "several activities with invented times."
    )

    COMPLETENESS_RULE = (
        "Completeness — this is critical:\n"
        "Extract every activity for which — and only for which — every "
        "required field (name, start, end) can be determined with confidence "
        "from what was actually said.\n"
        "The all-or-nothing rule applies PER ACTIVITY: include an activity if "
        "it has all of its required fields, and omit it if it does not. Do not "
        "drop a complete activity just because another activity in the same "
        "message is incomplete.\n"
        "If no activity has all its required fields, return an empty list."
    )

    DATETIME_RULES = (
        "Date and time rules — read carefully:\n"
        "You emit start_date, start_time, end_date, and end_time as separate "
        "fields. A start or end is only usable downstream if BOTH its date AND "
        "its clock time can be determined from what the doctor actually said — "
        "but you always emit whatever date/time pieces you actually have; do "
        "not withhold a date just because the time is unknown.\n\n"
        "The DATE (start_date / end_date) may come from either:\n"
        '  - an explicit date (e.g. "on the 14th", "July 3rd", "2026-07-14"), or\n'
        "  - a relative expression you resolve against the current date "
        '(e.g. "today", "yesterday", "the day before yesterday", '
        '"tomorrow", "the day after tomorrow", "last Monday").\n\n'
        "The TIME (start_time / end_time) must be provided ONLY if the doctor "
        "stated a clock time (e.g. \"9 AM\", \"from 2 to 6\", \"until midnight\"), "
        "OR it is derivable from stated information. Deriving is allowed and "
        "expected when all needed pieces were stated — this is not guessing:\n"
        '  - start + duration → compute the end ("started 4 AM, went 6 hours" '
        "→ end 10 AM).\n"
        '  - end + duration → compute the start ("finished noon after a 3-hour '
        'block" → start 9 AM).\n'
        "Only derive when every needed piece was actually stated; a duration "
        "with no start or end anchor is not enough.\n\n"
        "If no clock time was stated or derivable, leave start_time / end_time "
        "NULL. Never invent a clock time. In particular, a date with no stated "
        "clock time means the time is UNKNOWN — leave it null:\n"
        "  - never use 00:00 or midnight as a stand-in for an unknown start\n"
        "  - never use 23:59, 23:59:59, or end-of-day as a stand-in for an "
        "unknown end\n"
        '  - "yesterday", "today", and "till midnight" with no explicit clock '
        "time do NOT mean the activity spanned the whole day — leave the time "
        "null, do not use a day boundary as a stand-in\n\n"
        'Example: "I did a surgery today" gives a name and a start_date but NO '
        "clock times — emit start_date with start_time/end_time/end_date null; "
        "this activity is incomplete and will be handled downstream, not "
        "filled with day boundaries.\n\n"
        "Every date you emit must be a valid ISO 8601 date (YYYY-MM-DD). Every "
        "time you emit must be a 24-hour clock time as 'HH:MM' or 'HH:MM:SS' "
        "(e.g. '08:00' or '14:30:00'). Midnight / 12 AM at the end of a time "
        "range is the start of the NEXT day: write it as time 00:00 on the "
        "following date, never as 24:00 on the same date."
    )

    CLOSING = (
        "Do not guess or invent values for any field. It is always correct to "
        "omit an activity you are unsure about — the assistant will ask the "
        "doctor for the missing details."
    )

    def _content(self, doctor: DoctorContext) -> list[str]:
        return [
            self.BASE_PROMPT,
            self.ACTIVITY_TYPES,
            self.MULTIPLE_ACTIVITIES,
            self.COMPLETENESS_RULE,
            self.DATETIME_RULES,
            self.CLOSING,
        ]