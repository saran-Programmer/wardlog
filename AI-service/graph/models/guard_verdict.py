from typing import Literal

from pydantic import BaseModel


class GuardVerdict(BaseModel):

    processable: bool
    category: Literal["in_scope", "off_topic", "disallowed"]
    reason: str
