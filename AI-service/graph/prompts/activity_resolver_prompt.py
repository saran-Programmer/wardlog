from ..config import DoctorContext

from .base_prompt import BasePrompt


class ActivityResolverPrompt(BasePrompt):
    BASE_PROMPT = (
        "You identify which existing activity the doctor is referring to in the "
        "conversation. Extract a reference to that activity — do NOT create a new "
        "activity, and do NOT invent anything. Fill only what the doctor actually "
        "indicated, and resolve dates and times against the current date/time "
        "provided below."
    )

    ACTIVITY_TYPE_RULE = (
        "activity_type:\n"
        "Fill this only if the doctor indicated a type — surgeryblock, clinicblock, "
        "oncall, or onsiteoncall. If they only referred to it by time (e.g. \"the one "
        "I did this morning\") with no type, leave it null."
    )

    DATE_RULES = (
        "start_date / end_date:\n"
        "The doctor refers to a day either explicitly (\"July 14th\", \"2026-07-14\") "
        "or by a relative expression (\"last Wednesday\", \"last week Monday\", \"the "
        "start of last month\"). Resolve these against the current date.\n"
        "- For a SPECIFIC single day, set BOTH start_date and end_date to that same "
        "day.\n"
        "- For a PERIOD/RANGE, set start_date to the FIRST day of the period and "
        "end_date to the LAST day of the period.\n"
        "Examples (assume today is Friday 2026-07-31):\n"
        '- "the surgery on the 14th" -> start_date 2026-07-14, end_date 2026-07-14\n'
        '- "last Wednesday" -> start_date 2026-07-29, end_date 2026-07-29\n'
        '- "last week" -> start_date 2026-07-20 (Mon), end_date 2026-07-26 (Sun)\n'
        '- "last month" -> start_date 2026-06-01, end_date 2026-06-30'
    )

    TIME_RULES = (
        "start_time / end_time (24-hour 'HH:MM'):\n"
        "The doctor gives either an exact time or a time-of-day word.\n"
        "- If the doctor gave an EXACT time (e.g. \"at 8am\"), set start_time to that "
        "time and leave end_time null.\n"
        "- If the doctor gave a TIME-OF-DAY word, resolve it to the START and END of "
        "the window using this mapping:\n"
        "    morning   = 04:00 to 12:00\n"
        "    afternoon = 12:00 to 16:00\n"
        "    evening   = 16:00 to 20:00\n"
        "    night     = 20:00 to 04:00 (the window ends at 04:00 the next morning)\n"
        "  start_time is the START of the window, end_time is the END of the window.\n"
        "- If no time or time-of-day was mentioned at all, leave both null.\n"
        "Examples:\n"
        '- "at 8am" -> start_time 08:00, end_time null\n'
        '- "from 9 to 1" -> start_time 09:00, end_time 13:00\n'
        '- "this morning" -> start_time 04:00, end_time 12:00\n'
        '- "yesterday evening" -> start_time 16:00, end_time 20:00\n'
        '- "last night" -> start_time 20:00, end_time 04:00'
    )

    COMBINED_EXAMPLES = (
        "Putting it together (today = Friday 2026-07-31):\n"
        '- "the surgery I did last Wednesday morning" -> activity_type surgeryblock, '
        "start_date 2026-07-29, end_date 2026-07-29, start_time 04:00, end_time 12:00\n"
        '- "what I did last week" -> activity_type null, start_date 2026-07-20, '
        "end_date 2026-07-26, start_time null, end_time null\n"
        '- "the clinic block on the 14th at 8am" -> activity_type clinicblock, '
        "start_date 2026-07-14, end_date 2026-07-14, start_time 08:00, end_time null"
    )

    CLOSING = (
        "Do not invent values. Leave any field null that the doctor did not indicate "
        "or that cannot be resolved from what they said."
    )

    def _content(self, doctor: DoctorContext) -> list[str]:
        return [
            self.BASE_PROMPT,
            self.ACTIVITY_TYPE_RULE,
            self.DATE_RULES,
            self.TIME_RULES,
            self.COMBINED_EXAMPLES,
            self.CLOSING,
        ]