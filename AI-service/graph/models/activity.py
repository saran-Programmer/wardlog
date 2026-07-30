from datetime import datetime
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