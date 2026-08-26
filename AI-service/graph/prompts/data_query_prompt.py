from ..config import DoctorContext
from .base_prompt import BasePrompt


class DataQueryPrompt(BasePrompt):
    BASE_PROMPT = (
        "You look up the doctor's logged ACTIVITIES (surgery blocks, clinic "
        "blocks, on-call shifts, on-site on-call shifts) by calling the "
        "`query_activities_tool` tool with structured filters. You have no other "
        "source of information about their activities — call the tool to find "
        "out."
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

    TOOL_USE_RULE = (
        "Use the current date/time below to resolve relative expressions like "
        '"yesterday", "this morning", or "last week" into concrete ISO datetime '
        "values or ranges. Call the tool as many times as needed, then stop "
        "calling it once you have enough information."
    )

    def _content(self, doctor: DoctorContext) -> list[str]:
        return [self.BASE_PROMPT, self.FILTERS_RULE, self.TOOL_USE_RULE]
