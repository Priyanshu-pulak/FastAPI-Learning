from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal


class PatientBase(BaseModel):
    id: Annotated[
        str,
        Field(..., description="Unique ID of the patient", examples=['P001'])
    ]
    name: Annotated[
        str,
        Field(..., description="Full name of the patient", examples=["Priyanshu"])
    ]
    city: Annotated[
        str,
        Field(..., description="Current city of the patient.", examples=["Vellore"])
    ]
    age: Annotated[
        int,
        Field(..., gt=0, lt=110, description="Age of the patient", examples=[25])
    ]
    gender: Annotated[
        Literal['male', 'female', 'other'],
        Field(..., description="Gender of the patient", examples=['male'])
    ]
    height: Annotated[
        float,
        Field(..., gt=0, description="Height of the patient in m", examples=[1.75])
    ]
    weight: Annotated[
        float,
        Field(..., gt=0, description="Weight of the patient in kg", examples=[70.5])
    ]

class PatientCreate(PatientBase):
    pass

class PatientResponse(PatientBase):
    @computed_field
    @property
    def bmi(self) -> float:
        calculated_bmi = self.weight / (self.height ** 2)
        return round(calculated_bmi, 2)

    @computed_field
    @property
    def verdict(self) -> str:
        if self.bmi < 18.5:
            return 'Underweight'
        elif self.bmi < 25:
            return 'Normal'
        else:
            return 'Obese'
