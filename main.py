from fastapi import FastAPI, Path, HTTPException, Query, status
from fastapi.responses import JSONResponse
from typing import Annotated, Literal
from src.services import load_data, save_data
from src.models import PatientCreate, PatientUpdate, PatientResponse

# Creating FastAPI app instance
app = FastAPI()


@app.get("/")  # Defining path operation decorator for root endpoint
@app.get("/about")
def about():  # Defining path operation function
    return {"message": "A fully functional API for managing patient records."}


@app.get(
    "/patients",
    response_model=list[PatientResponse],
    status_code=status.HTTP_200_OK,
)
def view_patients() -> list[PatientResponse]:
    data = load_data()
    return [PatientResponse(id=key, **value) for key, value in data.items()]


@app.get(
    "/patient/{patient_id}",
    response_model=PatientResponse,
    status_code=status.HTTP_200_OK,
)  # Path Parameter example
def view_patient(
    patient_id: Annotated[
        str,
        Path(
            description="The ID of the patient to retrieve",
            examples=["P001"],
            min_length=4,
        ),
    ],
) -> PatientResponse:
    data = load_data()

    if patient_id in data:
        return PatientResponse(id=patient_id, **data[patient_id])
    raise HTTPException(
        status_code=404,
        detail="Patient not found.",
    )


@app.get(
    "/sort",
    response_model=list[PatientResponse],
    status_code=status.HTTP_200_OK,
)
def sort_patients(
    sort_by: Annotated[
        Literal["height", "weight", "bmi"],
        Query(
            description="Sort patients on basis of 'height' or 'weight'or 'bmi'",
            examples=["height", "weight", "bmi"],
        ),
    ],
    order: Annotated[
        Literal["ascending", "descending"],
        Query(
            description="Sort by ascending or descending order",
            examples=["ascending", "descending"],
        ),
    ],
) -> list[PatientResponse]:
    data = load_data()
    patients = [PatientResponse(id=key, **value) for key, value in data.items()]
    patients.sort(
        key=lambda patient: getattr(patient, sort_by),
        reverse=(order == "descending"),
    )
    return patients


@app.post(
    "/create",
    response_model=PatientResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_patient(patient: PatientCreate):
    # Load existing data
    data = load_data()

    # check if patient with same ID already exists
    if patient.id in data:
        raise HTTPException(
            status_code=400, detail="Patient with same ID already exists."
        )

    # Add new patient to data
    data[patient.id] = patient.model_dump(exclude=["id"])

    # Save updated data back to file
    save_data(data)
    return PatientResponse(**patient.model_dump())


@app.patch(
    "/edit/{patient_id}",
    response_model=PatientResponse,
    status_code=status.HTTP_200_OK,
)
def update_patient(
    patient_update: PatientUpdate,
    patient_id: Annotated[
        str,
        Path(
            ..., description="Give ID of the patient to be updated", examples=["P001"]
        ),
    ],
) -> PatientResponse:
    data = load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404, detail="Patient not found.")

    existing_patient_info = data[patient_id]
    new_data = patient_update.model_dump(exclude_unset=True)

    # Updating the existing patient info with new details provided
    existing_patient_info.update(new_data)

    # Updated the patient info with new details, new bmi and verdict
    data[patient_id] = existing_patient_info

    # Save updated data back to file
    save_data(data)

    return PatientResponse(id=patient_id, **existing_patient_info)


@app.delete("/delete/{patient_id}")
def delete_patient(
    patient_id: Annotated[
        str,
        Path(
            ..., description="Give Id of the patient to be deleted", examples=["P001"]
        ),
    ],
):
    data = load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404, detail="Patient not found.")

    # Remove the patient from data
    del data[patient_id]

    # Save updated data back to file
    save_data(data)

    return JSONResponse(
        status_code=200, content={"message": "Patient record deleted successfully."}
    )
