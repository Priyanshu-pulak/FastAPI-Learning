import json
from pathlib import Path

DATA_FILE = Path(__file__).parent.parent.parent / "data/patients.json"

def load_data() -> dict:
    with open(DATA_FILE, "r") as file:
        data = json.load(file)
        return data

def save_data(data: dict) -> None:
    with open(DATA_FILE, "w") as file:
        json.dump(data, file)

