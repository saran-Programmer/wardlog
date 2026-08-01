from datetime import date, datetime, time
from typing import Annotated, Literal, Optional

from pydantic import BaseModel, Field


class Activity(BaseModel):

    id: Annotated[
        Optional[str],
        Field(
            default=None,
            description="permanent id of the activity, minted when the doctor confirms/publishes it; null until then",
        ),
    ]
    name: Annotated[
        Optional[Literal["surgeryblock", "clinicblock", "oncall", "onsiteoncall"]],
        Field(default=None, description="activity performed by the doctor"),
    ]
    start: Annotated[
        Optional[datetime],
        Field(default=None, description="start date/time of the activity"),
    ]
    end: Annotated[
        Optional[datetime],
        Field(default=None, description="end date/time of the activity"),
    ]
    notes: Annotated[
        Optional[str],
        Field(default=None, description="optional notes about the activity"),
    ]
    location: Annotated[
        Optional[str],
        Field(
            default=None,
            description="optional free-text location, e.g. '4th floor surgery block' or 'general ward 2nd room'",
        ),
    ]


class ActivityList(BaseModel):

    activities: Annotated[
        list[Activity],
        Field(
            default_factory=list,
            description="every activity found in the conversation; empty if none were found",
        ),
    ]

def check_incomplete(activity: Activity) -> bool:

    if(activity.name is None or activity.start is None or activity.end is None):
        return True

    return False


# ExtractedActivity / ExtractedActivityList / compose are used ONLY by the extractor
# node — everything downstream uses Activity.


class ExtractedActivity(BaseModel):

    name: Annotated[
        Optional[Literal["surgeryblock", "clinicblock", "oncall", "onsiteoncall"]],
        Field(default=None, description="activity performed by the doctor"),
    ]
    start_date: Annotated[
        Optional[date],
        Field(
            default=None,
            description="start date of the activity; may be resolved from a relative "
            "expression such as 'yesterday' or 'last Monday' against the current date",
        ),
    ]
    start_time: Annotated[
        Optional[str],
        Field(
            default=None,
            description="start clock time of the activity as 24-hour 'HH:MM' or "
            "'HH:MM:SS'; MUST be null if the doctor did not state or make "
            "derivable a clock time — never invent one",
        ),
    ]
    end_date: Annotated[
        Optional[date],
        Field(
            default=None,
            description="end date of the activity; may be resolved from a relative "
            "expression such as 'yesterday' or 'last Monday' against the current date",
        ),
    ]
    end_time: Annotated[
        Optional[str],
        Field(
            default=None,
            description="end clock time of the activity as 24-hour 'HH:MM' or "
            "'HH:MM:SS'; MUST be null if the doctor did not state or make "
            "derivable a clock time — never invent one",
        ),
    ]
    notes: Annotated[
        Optional[str],
        Field(default=None, description="optional notes about the activity"),
    ]
    location: Annotated[
        Optional[str],
        Field(
            default=None,
            description="optional free-text location, e.g. '4th floor surgery block' or 'general ward 2nd room'",
        ),
    ]


class ExtractedActivityList(BaseModel):

    activities: Annotated[
        list[ExtractedActivity],
        Field(
            default_factory=list,
            description="every activity found in the conversation; empty if none were found",
        ),
    ]


def _parse_time(value: Optional[str]) -> Optional[time]:
    if not value:
        return None

    for fmt in ("%H:%M:%S", "%H:%M"):
        try:
            return datetime.strptime(value, fmt).time()
        except ValueError:
            continue

    return None


def compose(extracted: ExtractedActivity) -> Activity:
    start_time = _parse_time(extracted.start_time)
    end_time = _parse_time(extracted.end_time)

    start = (
        datetime.combine(extracted.start_date, start_time)
        if extracted.start_date is not None and start_time is not None
        else None
    )
    end = (
        datetime.combine(extracted.end_date, end_time)
        if extracted.end_date is not None and end_time is not None
        else None
    )

    return Activity(
        name=extracted.name,
        start=start,
        end=end,
        notes=extracted.notes,
        location=extracted.location,
    )