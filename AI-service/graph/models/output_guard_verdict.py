from pydantic import BaseModel


class OutputGuardVerdict(BaseModel):

    passed: bool
    reason: str
