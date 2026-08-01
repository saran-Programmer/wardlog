from datetime import date
from typing import Annotated, Literal, Optional

from pydantic import BaseModel, Field


# ActivityReference is used ONLY by the activity resolver — the reference it
# extracts from the conversation to identify which existing activity the
# doctor is referring to.


class ActivityReference(BaseModel):

    activity_type: Annotated[
        Optional[Literal["surgeryblock", "clinicblock", "oncall", "onsiteoncall"]],
        Field(
            default=None,
            description="the type of activity the doctor referred to, if they indicated "
            "one; leave null if the doctor did not specify a type (e.g. 'the one I did "
            "this morning')",
        ),
    ]
    start_date: Annotated[
        Optional[date],
        Field(
            default=None,
            description="The start of the date range the doctor referred to. The "
            "doctor gives this either as an explicit date (e.g. '2026-07-14', 'July "
            "14th') or as a day/period reference (e.g. 'last Wednesday', 'last week "
            "Monday', 'the start of last month'). Resolve it against the current date "
            "provided. For a single specific day, set this to that day. For a period "
            "reference, this is the FIRST day of that period — e.g. 'last month' -> the "
            "first day of last month; 'last week' -> the Monday of last week.",
        ),
    ]
    end_date: Annotated[
        Optional[date],
        Field(
            default=None,
            description="The end of the date range the doctor referred to. For a single "
            "specific day, set this to the SAME day as start_date. For a period, this is "
            "the LAST day of the period — e.g. 'last month' -> the last day of last "
            "month; 'last week' -> the Sunday of last week.",
        ),
    ]
    start_time: Annotated[
        Optional[str],
        Field(
            default=None,
            description="The start clock time of the referenced range, as 24-hour "
            "'HH:MM'. The doctor gives this either as an exact time (e.g. '8am' -> "
            "'08:00'), or as a time-of-day reference resolved to the START of that "
            "window using this mapping:\n"
            "- morning = 04:00 to 12:00 -> start_time 04:00\n"
            "- afternoon = 12:00 to 16:00 -> start_time 12:00\n"
            "- evening = 16:00 to 20:00 -> start_time 16:00\n"
            "- night = 20:00 to 04:00 (next day) -> start_time 20:00\n"
            "If the doctor stated an exact time, use that and leave end_time null. If no "
            "time or time-of-day was mentioned at all, leave this null.",
        ),
    ]
    end_time: Annotated[
        Optional[str],
        Field(
            default=None,
            description="The end clock time of the referenced range, as 24-hour "
            "'HH:MM'. Fill this ONLY for a time-of-day window, resolved to the END of "
            "the window:\n"
            "- morning -> end_time 12:00\n"
            "- afternoon -> end_time 16:00\n"
            "- evening -> end_time 20:00\n"
            "- night -> end_time 04:00 (the following morning)\n"
            "If the doctor stated an exact single time, leave this null. If no time or "
            "time-of-day was mentioned, leave this null.",
        ),
    ]

    @property
    def is_range(self) -> bool:
        return self.start_date is not None and self.end_date is not None