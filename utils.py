import json
import os

DATA_FILE = "data.json"


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            return json.load(file)

    return {
        "habits": [],
        "goals": {},
        "notes": "",
        "budget": 0
    }


def save_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)