from fastapi import FastAPI, Path, HTTPException, Query, status
from fastapi.responses import JSONResponse
from typing import Annotated
from src.services import load_data, save_data
from src.models import PatientCreate, PatientUpdate, PatientResponse

# Creating FastAPI app instance
app = FastAPI()

@app.get("/")  # Defining path operation decorator for root endpoint
@app.get("/about")
def about():  # Defining path operation function
    return {"message": "A fully functional API for managing patient records."}


@app.get("/patients")
def view_patients():
    data = load_data()
    return data


@app.get("/patient/{patient_id}")  # Path Parameter example
def view_patient(
    patient_id: str = Path(
        ..., description="The ID of the patient to retrieve", examples="P001"
    ),
):
    data = load_data()

    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404, detail="Patient not found.")


@app.get("/sort")
def sort_patients(
    sort_by: str = Query(
        ..., description="Sort patients on basis of 'height' or 'weight'or 'bmi'"
    ),
    order: str = Query(
        "asc", description="Sort by ascending : 'asc' or descending : 'desc' order"
    ),
):
    valid_fields = ["height", "weight", "bmi"]

    if sort_by not in valid_fields:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sort_by field. Select from {valid_fields}.",
        )

    if order not in ["asc", "desc"]:
        raise HTTPException(
            status_code=400, detail="Invalid order. Choose 'asc' or 'desc'."
        )

    data = load_data()

    sorted_data = sorted(
        data.values(), key=lambda x: x[sort_by], reverse=(order == "desc")
    )

    return sorted_data


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
