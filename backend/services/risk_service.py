import json
import os

def load_risk_data():
    """Loads the destination risk dataset from JSON."""
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "insurance_risk_knowledge.json")
    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)

RISK_DATA = load_risk_data()

def get_destination_info(destination: str):
    """Finds and returns risk info for a destination (case-insensitive)."""
    for record in RISK_DATA:
        if record["destination"].lower() == destination.lower():
            return record
    return None
