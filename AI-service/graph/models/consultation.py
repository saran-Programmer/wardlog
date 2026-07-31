from typing import Optional

from pydantic import BaseModel, Field


class Patient(BaseModel):

    name: str = Field(description="the patient's name")

    age: Optional[int] = Field(default=None, description="the patient's age as stated")

    sex: Optional[str] = Field(
        default=None, 
        description=(
            "the patient's sex: 'male' or 'female'. Take it if the doctor states it "
            "directly, or infer it from clear gendered pronouns the doctor uses for the "
            "patient (e.g. 'she'/'her' → female, 'he'/'him' → male). If neither a stated "
            "sex nor a clear gendered pronoun is present, leave null — do not guess from "
            "the name alone."))


class Consultation(BaseModel):

    diagnoses: list[str] = Field(
        default_factory=list,
        description="the condition(s) diagnosed in this encounter",
    )

    drugs: list[str] = Field(
        default_factory=list,
        description="medication(s) given or prescribed in this encounter",
    )

    surgery_type: Optional[str] = Field(
        default=None,
        description="the type of surgery performed, when this was a surgical encounter",
    )

    patient: Patient = Field(description="the patient seen in this consultation")
