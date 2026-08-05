from typing import Literal, Optional

from pydantic import BaseModel

from .activity import Activity


class BlockedActivity(BaseModel):

    activity: Activity
    reason: Literal["overlap", "zero_duration"]
    conflicts: Optional[list[Activity]] = None
