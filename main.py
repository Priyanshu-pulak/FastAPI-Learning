from fastapi import FastAPI, Path, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal
import json

# Creating FastAPI app instance
app = FastAPI()

class Patient(BaseModel):
    id : Annotated[str, Field(..., description = "Unique ID of the patient", exampless = ['P001'])]
    name : Annotated[str, Field(..., description = "Full name of the patient")]
    city : Annotated[str, Field(..., description = "Current city of the patient.")]
    age : Annotated[int, Field(..., gt = 0, lt = 110, description = "Age of the patient")]
    gender : Annotated[Literal['male', 'female', 'other'], Field(..., description = "Gender of the patient")]
    height : Annotated[float, Field(..., gt = 0, description = "Height of the patient in m")]
    weight : Annotated[float, Field(..., gt = 0, description = "Weight of the patient in kg")]

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

class PatientUpdate(BaseModel):
    name : Annotated[str | None, Field(None, description = "Full name of the patient")]
    city : Annotated[str | None, Field(None, description = "Current city of the patient.")]
    age : Annotated[int | None, Field(None, gt = 0, lt = 110, description = "Age of the patient")]
    gender : Annotated[Literal['male', 'female', 'other'] | None, Field(None, description = "Gender of the patient")]
    height : Annotated[float | None, Field(None, gt = 0, description = "Height of the patient in m")]
    weight : Annotated[float | None, Field(None, gt = 0, description = "Weight of the patient in kg")]
    
def load_data():
    with open('patients.json', 'r') as file:
        data = json.load(file)
    return data

def save_data(data):
    with open('patients.json', 'w') as file:
        json.dump(data, file)

@app.get("/") # Defining path operation decorator for root endpoint
def hello(): # Defining path operation function
    return {"message": "Patient Management System"}

@app.get("/about")
def about():
    return {"message": "A fully functional API for managing patient records."}

@app.get("/patients")
def view_patients():
    data = load_data()
    return data

@app.get("/patient/{patient_id}") # Path Parameter example
def view_patient(patient_id : str = Path(..., description = "The ID of the patient to retrieve", examples = 'P001')):
    data = load_data()

    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code = 404, detail = "Patient not found.")

@app.get('/sort')
def sort_patients(sort_by : str = Query(..., description = "Sort patients on basis of 'height' or 'weight'or 'bmi'"), order : str = Query('asc', description = "Sort by ascending : 'asc' or descending : 'desc' order")):
    valid_fields = ['height', 'weight', 'bmi']

    if sort_by not in valid_fields:
        raise HTTPException(status_code = 400, detail = f"Invalid sort_by field. Select from {valid_fields}.")
    
    if order not in ['asc', 'desc']:
        raise HTTPException(status_code = 400, detail = "Invalid order. Choose 'asc' or 'desc'.")
    
    data = load_data()

    sorted_data = sorted(data.values(), key = lambda x : x[sort_by], reverse = (order == 'desc'))
    
    return sorted_data

@app.post('/create')
def create_patient(patient : Patient):
    # Load existing data
    data = load_data()

    # check if patient with same ID already exists
    if patient.id in data:
        raise HTTPException(status_code = 400, detail = "Patient with same ID already exists.")
    
    # Add new patient to data
    data[patient.id] = patient.model_dump(exclude = ['id'])

    # Save updated data back to file
    save_data(data)

    return JSONResponse(status_code = 201, content = {'message' : "Patient record created successfully."})

@app.put('/edit/{patient_id}')
def update_patient(
    patient_update : PatientUpdate,
    patient_id : Annotated[
        str,
        Path(..., description = "Give ID of the patient to be updated", examples = 'P001')
    ]
):
    data = load_data()

    if patient_id not in data:
        raise HTTPException(status_code = 404, detail = "Patient not found.")
    
    existing_patient_info = data[patient_id]
    updated_patient_info = patient_update.model_dump(exclude_unset = True)

    # Updating the existing patient info with new details provided
    for key, value in updated_patient_info.items():
        existing_patient_info[key] = value

    #Converting to Patient model to recalculate bmi and verdict if height or weight is updated
    updated_patient_info_pydantic = Patient(id = patient_id, **existing_patient_info)

    # Converting back to dictionary
    existing_patient_info = updated_patient_info_pydantic.model_dump(exclude = ['id'])
    
    # Updated the patient info with new details, new bmi and verdict
    data[patient_id] = existing_patient_info

    # Save updated data back to file
    save_data(data)

    return JSONResponse(status_code = 200, content = {'message' : "Patient record updated successfully."})

@app.delete('/delete/{patient_id}')
def delete_patient(
    patient_id : Annotated[
        str,
        Path(..., description = "Give Id of the patient to be deleted", examples = 'P001')
    ]
):
    data = load_data()

    if patient_id not in data:
        raise HTTPException(status_code = 404, detail = "Patient not found.")

    # Remove the patient from data
    del data[patient_id]

    # Save updated data back to file
    save_data(data)

    return JSONResponse(status_code = 200, content = {'message' : "Patient record deleted successfully."})